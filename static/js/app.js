const socket = io();

const homeScreen = document.querySelector("#home-screen");
const lobbyScreen = document.querySelector("#lobby-screen");
const gameScreen = document.querySelector("#game-screen");
const nameInput = document.querySelector("#player-name");
const codeInput = document.querySelector("#room-code");
const homeMessage = document.querySelector("#home-message");
const lobbyMessage = document.querySelector("#lobby-message");
const toast = document.querySelector("#toast");

let currentRoom = null;
let isHost = false;

function showScreen(screen) {
  [homeScreen, lobbyScreen, gameScreen].forEach(item => item.classList.add("hidden"));
  screen.classList.remove("hidden");
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 2800);
}

function playerName() {
  return nameInput.value.trim() || "Jogador";
}

function renderRoom(room) {
  currentRoom = room;
  document.querySelector("#room-code-display").textContent = room.code;
  document.querySelector("#player-count").textContent = room.players.length;

  const list = document.querySelector("#player-list");
  list.replaceChildren();
  room.players.forEach(player => {
    const item = document.createElement("li");
    const dot = document.createElement("span");
    dot.className = "player-dot";
    const name = document.createElement("strong");
    name.textContent = player.name;
    item.append(dot, name);
    if (player.is_host) {
      const host = document.createElement("span");
      host.className = "host-tag";
      host.textContent = "ANFITRIÃO";
      item.append(host);
    }
    list.append(item);
  });

  document.querySelector("#start-button").classList.toggle("hidden", !isHost);
  lobbyMessage.textContent = room.started ? "Partida em andamento." : "Aguardando jogadores...";
}

document.querySelector("#create-button").addEventListener("click", () => {
  homeMessage.textContent = "";
  socket.emit("create_room", { name: playerName() });
});

document.querySelector("#join-button").addEventListener("click", () => {
  homeMessage.textContent = "";
  socket.emit("join_room", { name: playerName(), code: codeInput.value });
});

document.querySelector("#room-code").addEventListener("input", event => {
  event.target.value = event.target.value.toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 5);
});

document.querySelector("#start-button").addEventListener("click", () => {
  socket.emit("start_game");
});

document.querySelector("#leave-button").addEventListener("click", () => {
  socket.emit("leave_room");
});

socket.on("connect", () => {
  homeMessage.textContent = "";
});

socket.on("connect_error", () => {
  homeMessage.textContent = "Não foi possível conectar ao servidor. Confira se ele está ligado.";
});

socket.on("room_joined", data => {
  if (!data.ok) return;
  isHost = data.is_host;
  renderRoom(data.room);
  showScreen(lobbyScreen);
});

socket.on("action_result", result => {
  if (result && !result.ok) {
    if (homeScreen.classList.contains("hidden")) lobbyMessage.textContent = result.message;
    else homeMessage.textContent = result.message;
  }
});

socket.on("room_update", room => {
  renderRoom(room);
});

socket.on("game_started", data => {
  showScreen(gameScreen);
  const players = document.querySelector("#game-players");
  players.replaceChildren();
  (data.room?.players || []).forEach(player => {
    const tag = document.createElement("span");
    tag.textContent = player.name;
    players.append(tag);
  });
});

socket.on("notice", data => showToast(data.message));

socket.on("left_room", () => {
  currentRoom = null;
  isHost = false;
  showScreen(homeScreen);
});

document.querySelector("#player-name").addEventListener("keydown", event => {
  if (event.key === "Enter") document.querySelector("#create-button").click();
});
