import pygame
import random
from game.levels import LEVELS
from game.sprites import *

class LevelConstructor:
    '''
    Creates the different levels for the game,
    as well as returning the generator for the endless mode.
    '''
    def __init__(self, mode):
        self.ground_settings = {
            'endless' : 100000000, # pseudo-infinite
            '0' : 600,
            '1' : 600,
            '2' : 800,
            '3' : 800,
            '4' : 3200,
            '5' : 2000,
            '6' : 2000,
            '7' : 2000,
            '8' : 4000,
            '9' : 4900,
            '10' : 4000,
            '9999' : 2100
        }
        self.levels = LEVELS
        self.mode = mode
        self.blocks = pygame.sprite.Group()
        self.chunk_y_pos = 0
        self.chunk_size = 800
        self.start_y_offset = 200
    
    def get_random_chunk(self, x_offset=0):
        '''
        Used with endless mode.
        Generate a random chunk of blocks, and add it to the Group.
        eg. One chunk = [800x800] space, filled with 100x100 blocks.
        '''
        self.x_offset = x_offset

        for i in range((self.chunk_size//100)):
            for j in range((self.chunk_size//100) - 1, -1, -1):
                #b = StandardBlock(i*100 + self.x_offset, self.start_y_offset + j*100 + self.chunk_y_pos, 100, 100)
                b = Block.construct_block_from_type(self.random_block(), i*100 + self.x_offset, self.start_y_offset + j*100 + self.chunk_y_pos, 100, 100 )
                self.blocks.add(b)
                #print(b.rect.x, b.rect.y)
        self.blocks.add(InvisBlock(-100 + self.x_offset, self.start_y_offset + self.chunk_y_pos, 100, 100))

        self.chunk_y_pos += self.chunk_size # go to next chunk position.
        #print('returning chunk with offset', x_offset)
        #print(self.blocks.sprites()[0].rect.x)
        return self.blocks

    def update_block_chunks(self, camera):
        '''
        Used with endless mode.
        Check and delete any blocks outside of camera.
        Also generate new chunk when needed.
        '''
        for block in self.blocks:
            if block.check_position(camera):
                if block.type == 99:
                    #print('[Game] Generating new chunk at', self.chunk_y_pos)
                    self.get_random_chunk()
                
                block.kill()
        
        return self.blocks

    def random_block(self):
        '''
        Returns an integer representing the type of block.
        Win blocks, mushroom and invisible blocks are excluded.
        '''
        roll = random.randint(1, 100)

        if roll <= 50:
            return 0
        elif roll <= 65:
            return 3
        elif roll <= 75:
            return 2
        elif roll <= 88:
            return 4
        elif roll <= 90:
            return 10
        elif roll <= 97:
            return 9
        elif roll <= 98:
            return 5
        elif roll <= 99:
            return 6
        else:
            return 7

    @classmethod
    def get_endless(cls):
        '''
        Returns the endless mode.
        '''
        level = cls('endless')
        level.ground_level = level.ground_settings[level.mode]
        return level
    
    @classmethod
    def get_level(cls, l):
        '''
        Returns the appropriate level.
        '''
        level = cls(l)
        level.ground_level = level.ground_settings[level.mode]
       
        blocks_data = LEVELS[l]

        level.blocks.add(cls.read_level(blocks_data))

        return level
    
    @staticmethod
    def read_level(blocks_data):
        return [
            block for block in [
                Block.construct_block_from_type(b, i*100, j*100, 100, 100) if rows or b >= 0 else b
                for j, rows in enumerate(blocks_data) for i, b in enumerate(rows)
            ] if isinstance(block, Block)
        ]
