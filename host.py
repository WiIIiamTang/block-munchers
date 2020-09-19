from server.game_server import GServer
import sys

if len(sys.argv) == 2:
    server = GServer('', int(sys.argv[1]))
else:
    port = input('port:')
    server = GServer(ip='', port=int(port))

server.handle_connections()