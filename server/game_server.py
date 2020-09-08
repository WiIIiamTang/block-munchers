import socket
import pygame
import sys
import pickle
import threading
import time
from game.sprites import *

class Client:
    '''
    Represents a game client that connects to the server.
    '''
    def __init__(self, ip='', port=6969):
        self.ip = ip
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.BUFFER_SIZE = 1024 * 14

        self.address = (self.ip, self.port)
    
    def connect(self):
        '''
        Connects to the server and returns the id for the client.
        '''
        try:
            self.s.connect(self.address)

            return pickle.loads(self.s.recv(self.BUFFER_SIZE))
        except Exception as e:
            self.close()
    
    def send(self, to_send):
        '''
        Sends the object seralized by pickle.
        '''
        try:
            self.s.send(pickle.dumps(to_send))        
        except Exception as e:
            self.close()
    
    def receive(self):
        '''
        Receives data sent by the server and returns it.
        '''
        try:
            return pickle.loads(self.s.recv(self.BUFFER_SIZE))
        except Exception as e:
            self.close()
    
    def update(self, to_send):
        '''
        Sends the object in the argument, and returns the reply from the server.
        '''
        self.send(to_send)
        return self.receive()
    
    def close(self):
        self.s.close()


class Server:
    '''
    Represents a game server that hosts multiplayer games.
    '''
    def __init__(self, ip='', port=6969):
        # The ip should be left empty to accept all incoming connections.
        self.ip = ip
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.id_count = int(round(time.time()))

        self.BUFFER_SIZE = 1024 * 14

        self.player_names = {}
        self.server_data = {
            'full' : False,
            'players' : {},
            'blocks' : set(),
            'ready' : {},
            'start' : False,
            'started' : {},
            'p1' : 0,
            'p2' : 0
        }

        try:
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.bind((self.ip, self.port))
        except socket.error as e:
            print(e)
        
        # Starting listening on the socket.
        self.s.listen()
        print('[Server] Started')
    
    def shutdown(self):
        try:
            self.s.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            pass
        self.s.close()

        print('[Server] Closing main socket and shutting down')

    def handle_connections(self):
        '''
        Start listening and accepting connections to the server.
        Will run in a loop until interrupted
        '''
        print('[Server] Looking for connections..')
        
        while self.running:
            try:
                connection, address = self.s.accept()

                if not self.running:
                    self.s.close()
                    break

                print(f'[Server] Starting new thread for {self.id_count} on {connection}')
                job = threading.Thread(target=self.game_connection, args=(connection, self.id_count), daemon=True, name=str(self.id_count))
                job.start()

                self.id_count += 1
            except Exception as e:
                pass
            

    def game_connection(self, s, pid):
        '''
        A game connection to the server, represented by the socket.
        Should be kept alive as long as the game is connected to the server.
        '''
        ############################
        # assign pid when client connects.
        s.send(pickle.dumps(pid)) 
        
        ############################
        # handle updates from client.
        # client sends different dicts depending on the state. check type first.
        while self.running:
            try:
                received = pickle.loads(s.recv(self.BUFFER_SIZE))
            
                if not received:
                    self.server_data['players'].pop(pid)
                    print('Did not receive data from client')
                    break

                # Menu updates.
                elif received['type'] == 'menu':
                    #print(f'[Server] Received {received}')
                    if len(self.server_data['players']) == 2:
                        self.server_data['full'] = True
                    else:
                        self.server_data['players'][pid] = received['name']
                        self.server_data['full'] = False  
                        self.player_names[pid] = received['name']

                    self.server_data['ready'][pid] = received['ready']

                    self.server_data['start'] = sum([status for status in self.server_data['ready'].values()]) == 2
                    
                    self.server_data['started'][pid] = received['started']


                # Ingame updates
                # note there are only two players in the game.
                elif received['type'] == 'ingame':
                    if received['setup']:
                        print('[Server] Setting up for', pid)
                        alternate = True
                        for key, value in self.server_data['players'].items():
                            if alternate:
                                self.server_data['players'][key] = {
                                    'x' : 64,
                                    'y' : 0,
                                    'width' : 32,
                                    'height' : 32,
                                    'speed' : 0,
                                    'accel' : 3,
                                    'jump_accel' : 15,
                                    'name' : self.player_names[key]
                                }
                                self.server_data['p1'] = key
                                alternate = not alternate
                            else:
                                self.server_data['players'][key] = {
                                    'x' : SIZE[0]-64,
                                    'y' : 0,
                                    'width' : 32,
                                    'height' : 32,
                                    'speed' : 0,
                                    'accel' : 3,
                                    'jump_accel' : 15,
                                    'name' : self.player_names[key]
                                }
                                self.server_data['p2'] = key
                    
                    elif received['init-blocks']:
                        self.server_data['blocks'].update(received['blocks'])
                        #print('[Server] blocks', self.server_data['blocks'])
                        
                    else:
                        self.server_data['players'][pid]['x'] = received['player']['x']
                        self.server_data['players'][pid]['y'] = received['player']['y']

                        self.server_data['blocks'].intersection_update(received['blocks'])

                
                
                # Send server data at the end regardless of type of update.
                s.sendall(pickle.dumps(self.server_data))
            
            except Exception as e:
                self.server_data['players'].pop(pid)
                print('Interrupted, breaking', pid)
                print(e)
                break
        
        print(f'[Server] (Thread for {pid}) Closing connection')
        s.close()

