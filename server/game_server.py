import socket
import pygame
import sys
import pickle
import threading
import time
from multiprocessing.connection import Listener, Client

class GClient:
    '''
    Represents a game client that connects to the server.
    '''
    def __init__(self, ip='', port=6969):
        self.ip = ip
        self.port = port
        self.address = (self.ip, self.port)
        self.s = None
         
    def connect(self):
        '''
        Connects to the server and returns the id for the client.
        '''
        try:
            self.s = Client(self.address)

            return self.s.recv()

        except Exception as e:
            self.s.close()
    
    def send(self, to_send):
        '''
        Sends the object seralized by pickle.
        '''
        try:
            self.s.send(to_send)

        except Exception as e:
            self.s.close()
    
    def receive(self):
        '''
        Receives data sent by the server and returns it.
        '''
        try:
            return self.s.recv()
        except Exception as e:
            self.s.close()
    
    def update(self, to_send):
        '''
        Sends the object in the argument, and returns the reply from the server.
        '''
        self.send(to_send)
        return self.receive()
    
    def close(self):
        self.s.close()


class GServer:
    '''
    Represents a game server that hosts multiplayer games.
    '''
    def __init__(self, ip='', port=6969):
        # The ip should be left empty to accept all incoming connections.
        self.ip = ip
        self.port = port
        self.address = (self.ip, self.port)
        self.s = Listener(self.address)
    
        self.running = True
        self.id_count = int(round(time.time()))

        self.BUFFER_SIZE = 1024 * 14

        self.player_names = {}
        self.server_data = {
            'full' : False,
            'mode' : True,
            'players' : {},
            'players-endless': {},
            'players-race': {},
            'blocks' : set(),
            'ready' : {},
            'start' : False,
            'started' : {},
            'p1' : 0,
            'p2' : 0,
            'quit' : {},
            'win' : {}
        }
        
        print('[Server] Started')
    
    def shutdown(self):
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
                connection = self.s.accept()

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
        s.send(pid) 
        
        ############################
        # handle updates from client.
        # client sends different dicts depending on the state. check type first.
        while self.running:
            try:
                received = s.recv()
            
                if not received:
                    self.server_data['players'].pop(pid)
                    self.server_data['players-endless'].pop(pid)
                    self.server_data['players-race'].pop(pid)
                    self.server_data['ready'].pop(pid)
                    self.server_data['started'].pop(pid)
                    self.server_data['quit'].pop(pid)
                    self.server_data['win'].pop(pid)
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

                    if received['changemode']:
                        self.server_data['mode'] = received['mode']


                # Ingame updates
                # note there are only two players in the game.
                elif received['type'] == 'ingame-race':
                    if received['setup']:
                        print('[Server] Setting up for', pid)
                        self.server_data['quit'][pid] = False
                        self.server_data['win'][pid] = False
                        alternate = True
                        for key, value in self.server_data['players'].items():
                            if alternate:
                                self.server_data['players-race'][key] = {
                                    'x' : 64,
                                    'y' : 50,
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
                                self.server_data['players-race'][key] = {
                                    'x' : 1100,
                                    'y' : 50,
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
                        self.server_data['players-race'][pid]['x'] = received['player']['x']
                        self.server_data['players-race'][pid]['y'] = received['player']['y']

                        self.server_data['blocks'].intersection_update(received['blocks'])

                        self.server_data['quit'][pid] = received['quit']
                        self.server_data['win'][pid] = received['win']
                
                elif received['type'] == 'ingame-endless':
                    self.server_data['players-endless'][pid] = [received['player-y'], received['player-score'], self.player_names[pid], received['lose']]

                
                
                # Send server data at the end regardless of type of update.
                s.send(self.server_data)
            
            except Exception as e:
                self.server_data['players'].pop(pid)
                self.server_data['players-endless'].pop(pid)
                self.server_data['players-race'].pop(pid)
                self.server_data['ready'].pop(pid)
                self.server_data['started'].pop(pid)
                self.server_data['quit'].pop(pid)
                self.server_data['win'].pop(pid)
                print('Interrupted, breaking', pid)
                print(e)
                break
        
        print(f'[Server] (Thread for {pid}) Closing connection')
        s.close()

