# Tripulação — jogo multiplayer 2D

Projeto inicial de um jogo multiplayer 2D inspirado em jogos de dedução social.

## O que já funciona

- Criar uma sala com código de 5 caracteres.
- Entrar em uma sala usando o código.
- Até 10 jogadores por sala.
- Lista de jogadores atualizada em tempo real.
- Identificação do anfitrião.
- O anfitrião pode iniciar quando houver pelo menos 2 jogadores.
- Se o anfitrião sair, outro jogador assume a função.

## Tecnologias

- HTML, CSS e JavaScript
- Python + Flask
- Flask-SocketIO para comunicação em tempo real
- SQLite será adicionado posteriormente para dados permanentes.

## Executar na rede local (LAN)

É necessário ter Python instalado no computador que será o servidor.

1. Abra um terminal na pasta do projeto.
2. Instale as dependências:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Inicie o servidor:

   ```bash
   python app.py
   ```

4. No computador servidor, abra `http://localhost:5000`.
5. Descubra o endereço IP local do computador servidor.
6. Os amigos conectados à mesma rede Wi-Fi/rede local abrem `http://IP-DO-SERVIDOR:5000` no navegador.
7. Um jogador cria a sala e compartilha o código com os outros.

### Encontrar o IP local

- Windows: no Prompt de Comando, execute `ipconfig` e procure o IPv4 da conexão ativa.
- Linux: execute `hostname -I`.
- Chromebook com ambiente Linux: execute `hostname -I` no terminal Linux. Para outros dispositivos acessarem o servidor, a rede e o encaminhamento de portas do Chromebook precisam permitir essa conexão.

Se o firewall perguntar, permita conexões privadas na porta 5000. Use apenas em uma rede local confiável.

## Observações importantes

- Esta versão é uma base de salas e lobby, não o jogo completo ainda.
- As salas ficam na memória do servidor e são apagadas quando ele é desligado.
- A página carrega a biblioteca Socket.IO por CDN, então o primeiro acesso precisa de internet para baixar essa biblioteca.
- O servidor deve continuar ligado durante a partida.
- O SQLite será útil para guardar estatísticas, configurações e histórico; ele não substitui o servidor em tempo real.

## Próximas etapas

1. Criar personagens 2D e um mapa.
2. Sincronizar a movimentação dos jogadores.
3. Criar tarefas e objetivos.
4. Implementar papéis secretos, reuniões e votação.
5. Adicionar SQLite para dados permanentes.
