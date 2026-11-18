import secrets
import string
from threading import RLock

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "troque-esta-chave-antes-de-publicar"
socketio = SocketIO(app, cors_allowed_origins="*")

# As salas ficam na memória do servidor. Elas desaparecem quando o servidor
# é desligado; o SQLite poderá guardar dados permanentes em uma próxima etapa.
rooms = {}
players_by_sid = {}
rooms_lock = RLock()
MAX_PLAYERS = 10


def clean_name(value):
    name = " ".join(str(value or "").split()).strip()
    return name[:16] or "Jogador"


def make_room_code():
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(5))
        if code not in rooms:
            return code


def room_snapshot(code):
    room = rooms.get(code)
    if not room:
        return None
    return {
        "code": code,
        "players": [
            {"name": player["name"], "is_host": player["sid"] == room["host"]}
            for player in room["players"].values()
        ],
        "max_players": MAX_PLAYERS,
        "started": room["started"],
    }


def publish_room(code):
    snapshot = room_snapshot(code)
    if snapshot:
        socketio.emit("room_update", snapshot, to=code)


def remove_player(sid):
    info = players_by_sid.pop(sid, None)
    if not info:
        return

    code = info["code"]
    room = rooms.get(code)
    if not room:
        return

    room["players"].pop(sid, None)
    if not room["players"]:
        rooms.pop(code, None)
        return

    if room["host"] == sid:
        room["host"] = next(iter(room["players"]))
        socketio.emit(
            "notice",
            {"message": "O anfitrião saiu. Um novo anfitrião foi escolhido."},
            to=code,
        )

    publish_room(code)


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("create_room")
def create_room(data):
    name = clean_name((data or {}).get("name"))
    with rooms_lock:
        code = make_room_code()
        rooms[code] = {
            "host": request.sid,
            "players": {request.sid: {"sid": request.sid, "name": name}},
            "started": False,
        }
        players_by_sid[request.sid] = {"code": code}

    join_room(code)
    emit("room_joined", {"ok": True, "room": room_snapshot(code), "is_host": True})


@socketio.on("join_room")
def join_existing_room(data):
    data = data or {}
    code = str(data.get("code", "")).strip().upper()
    name = clean_name(data.get("name"))

    with rooms_lock:
        room = rooms.get(code)
        if not room:
            emit("action_result", {"ok": False, "message": "Sala não encontrada. Confira o código."})
            return
        if room["started"]:
            emit("action_result", {"ok": False, "message": "Essa partida já começou."})
            return
        if len(room["players"]) >= MAX_PLAYERS:
            emit("action_result", {"ok": False, "message": "A sala já está cheia (10 jogadores)."})
            return

        room["players"][request.sid] = {"sid": request.sid, "name": name}
        players_by_sid[request.sid] = {"code": code}

    join_room(code)
    emit("room_joined", {"ok": True, "room": room_snapshot(code), "is_host": False})
    publish_room(code)


@socketio.on("start_game")
def start_game(data):
    info = players_by_sid.get(request.sid)
    if not info:
        emit("action_result", {"ok": False, "message": "Entre em uma sala primeiro."})
        return

    code = info["code"]
    room = rooms.get(code)
    if not room or room["host"] != request.sid:
        emit("action_result", {"ok": False, "message": "Somente o anfitrião pode iniciar."})
        return
    if len(room["players"]) < 2:
        emit("action_result", {"ok": False, "message": "É preciso ter pelo menos 2 jogadores."})
        return

    room["started"] = True
    socketio.emit("game_started", {"message": "A partida começou!", "room": room_snapshot(code)}, to=code)
    publish_room(code)


@socketio.on("leave_room")
def leave_current_room():
    info = players_by_sid.get(request.sid)
    if info:
        leave_room(info["code"])
        remove_player(request.sid)
    emit("left_room")


@socketio.on("disconnect")
def on_disconnect():
    with rooms_lock:
        remove_player(request.sid)


if __name__ == "__main__":
    print("\nServidor iniciado!")
    print("No próprio computador: http://localhost:5000")
    print("Em outros dispositivos: http://IP-DO-COMPUTADOR:5000\n")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
