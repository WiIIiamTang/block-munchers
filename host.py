from server.game_server import Server

server = Server('', 5554)

server.handle_connections()