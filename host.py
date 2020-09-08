from server.game_server import Server
import sys

if len(sys.argv) == 2:
    server = Server('', int(sys.argv[1]))
elif len(sys.argv) == 3:
    server = Server(sys.argv[1], int(sys.argv[2]))
else:
    ip = input('ip address:')
    port = input('port:')
    server = Server(ip='' if not ip else ip, port=int(port))

server.handle_connections()