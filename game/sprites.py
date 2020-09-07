import pygame
import json
from util.setup import *
from game.ui import HealthBar

config = get_config()
SIZE = config['size']
SOUNDS = generate_eat_sound()

class Player(pygame.sprite.Sprite):
    '''
    Represents a player
    '''
    def __init__(self, x, y, width, height, speed, accel, jump_accel, name=''):
        super().__init__()
        self.IMAGES = generate_player_images()
        self.rect = pygame.Rect(x, y, width, height)
        self.front = self.IMAGES['playerfront']
        self.left = self.IMAGES['playerleft']
        self.right = self.IMAGES['playerright']
        self.name = name
        self.is_left = False
        self.is_right = False
        self.speed = speed
        self.speed_y = 0
        self.accel = accel
        self.is_jump = False
        self.max_speed = 10
        self.relative_y = y
        self.cooldown = 0
        self.jump_accel = jump_accel

        self.health = 200
        self.max_health = 200

        self.score = 0
        self.score_font = pygame.font.SysFont('Calibri', 24, bold=True, italic=True)

        self.win = False

        self.extensions = {
            'up' : Extension(x+width//2, y+5),
            'down' : Extension(x+width//2, y+height+5),
            'left' : Extension(x-5, y+height//2),
            'right' : Extension(x+width+5, y+height//2)
        }

        self.health_bar_width = 400
        self.health_bar = HealthBar(SIZE[0]//2-self.health_bar_width//2, 0, self.health_bar_width, 15, self.max_health)

        print(f'[Game] Player instance created at {x}, {y}')
    
    def draw(self, screen, camera):
        if self.is_right:
            screen.blit(self.right, camera.apply_offset(self))
        elif self.is_left:
            screen.blit(self.left, camera.apply_offset(self))
        else:
            screen.blit(self.front, camera.apply_offset(self))
        
        self.health_bar.draw(screen, self)

        screen.blit(self.score_font.render(f'Score:{self.score}', 1, (255, 23, 23)), (SIZE[0]-160, 30))

        # Draw extension hitboxes
        #for value in self.extensions.values():
            #value.draw(screen, camera)

        # Print player's coordinates.
        #print(f' [Game-Player] Rect: {self.rect.x}, {self.rect.y}')
        
    def update(self, clock, ground_level, gravity, deccel, blocks):
        dt = clock.get_time() / 30

        #### Keys
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.speed = max(-self.max_speed, self.speed - self.accel)
            self.is_left = True
            self.is_right = False
    
        elif keys[pygame.K_RIGHT]:
            self.speed = min(self.max_speed, self.speed + self.accel)
            self.is_left = False
            self.is_right = True
        
        else:
            self.is_left = False
            self.is_right = False
            if self.speed < 0:
                self.speed = min(0, self.speed + deccel)
            elif self.speed > 0:
                self.speed = max(0, self.speed - deccel)    

        #### Fall - gravity
        if self.rect.y < ground_level - self.rect.height:
            self.speed_y = self.speed_y - gravity * dt
           
        

        #### Move x, y
        # MOVE FIRST, then CHECK COLLISION AFTER

        # moving player x-axis
        if self.speed <= 0 and self.rect.x >= 0:
            self.rect.x = max(self.rect.x + self.speed * dt, 0)
            
        elif self.speed > 0 and self.rect.x <= SIZE[0] - self.rect.width:
            self.rect.x = min(self.rect.x + self.speed * dt, SIZE[0] - self.rect.width) 
        
        # check collisions x-axis
        self.check_collisions(blocks, check_x=True)

        # moving player y-axis
        if self.speed_y > 0 and self.rect.y >= 0:
            self.rect.y -= self.speed_y * dt
            #print('up')

        elif self.speed_y < 0 and self.rect.y <= ground_level - self.rect.height:
            self.rect.y = min(ground_level -self.rect.height, self.rect.y - self.speed_y * dt)
            #print('down')
        
        # check collisions y-axis
        self.check_collisions(blocks, check_x=False)

        
        #### ground_level check
        if self.rect.y >= ground_level - self.rect.height:
            self.is_jump = False
            self.speed_y = 0
            #print('landed')
        
        #### update player extensions
        self.update_extensions()

    def events(self, events, blocks, camera):
        keys = pygame.key.get_pressed()

        for event in events:
            if event.type == pygame.KEYDOWN:
                #### Jump
                if event.key == pygame.K_UP:
                    if not self.is_jump:
                        self.speed_y += self.jump_accel
                        self.is_jump = True
        
                #### Breaks
                if event.key == pygame.K_SPACE:
                    if keys[pygame.K_UP]:
                        self.check_block_break(blocks, 'up')
                    elif keys[pygame.K_DOWN]:
                        self.check_block_break(blocks, 'down')
                    elif keys[pygame.K_LEFT]:
                        self.check_block_break(blocks, 'left')
                    elif keys[pygame.K_RIGHT]:
                        self.check_block_break(blocks, 'right')
        
        #### Failure condition
        return ((self.rect.y + self.rect.height < -camera.rect.y) or not (self.health >= 0))
                
    
    def update_extensions(self):
        self.extensions['up'].rect.x, self.extensions['up'].rect.y = self.rect.x+self.rect.width//2, self.rect.y-10
        self.extensions['down'].rect.x, self.extensions['down'].rect.y = self.rect.x+self.rect.width//2, self.rect.y+self.rect.height+10
        self.extensions['left'].rect.x, self.extensions['left'].rect.y = self.rect.x-10, self.rect.y+self.rect.height//2
        self.extensions['right'].rect.x, self.extensions['right'].rect.y = self.rect.x+self.rect.width+10, self.rect.y+self.rect.height//2
    

    def check_collisions(self, group, check_x=True):
        sprites_hit = pygame.sprite.spritecollide(self, group, False)

        for sprite in sprites_hit:
            if check_x:
                if self.speed > 0:
                    self.rect.right = sprite.rect.left 
                elif self.speed < 0:
                    self.rect.left = sprite.rect.right
                break
            else:
                if self.speed_y > 0:
                    self.rect.top = sprite.rect.bottom
                elif self.speed_y < 0:
                    self.rect.bottom = sprite.rect.top
                
                self.speed_y = 0
                if self.rect.top != sprite.rect.bottom: 
                    self.is_jump = False
                break
    
    def check_block_break(self, group, direction):
        sprites_hit = pygame.sprite.spritecollide(self.extensions[direction], group, False)

        for sprite in sprites_hit:
            if sprite.hit_interaction(self):
                SOUNDS['munch'].play()
                sprite.kill()
                break


class Extension(pygame.sprite.Sprite):
    '''
    Extensions of the Player that act as hitboxes.
    Has a Surface so that it may be drawn for debugging.
    '''
    def __init__(self, x, y, width=5, height=5):
        super().__init__()
        self.surf = pygame.Surface([width, height])
        self.surf.fill((255, 0, 0))
        self.rect = self.surf.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def draw(self, screen, camera):
        screen.blit(self.surf, camera.apply_offset(self))


class Block(pygame.sprite.Sprite):
    '''
    Represents a block in the game.
    '''
    def __init__(self):
        super().__init__()
        self.IMAGES = generate_block_images()
        self.health = 1
        self.type = -111
        self.god = False

    @classmethod
    def construct_block_from_type(cls, b, x, y, width, height):
        if b == 0:
            return StandardBlock(x, y, width, height)
        elif b == 1:
            return WinBlock(x, y, width, height)
        elif b == 99:
            return InvisBlock(x, y, width, height)
        else:
            return None

    def draw(self, screen, camera):
        pass

    def update(self):
        pass

    def events(self, events):
        pass

    def broken(self):
        return self.health == 0
    
    def check_position(self, camera):
        return self.rect.y + self.rect.height < -camera.rect.y


class StandardBlock(Block):
    '''
    The most common block in the game.
    '''
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = self.IMAGES['normal']
        self.relative_y = y
        self.health = 1
        self.type = 0
    
    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply_offset(self))
    
    def hit_interaction(self, player):
        if not self.god:
            self.health -= 1
            player.health -= 10
            player.score += 300
            
            return self.broken()
        else:
            return False

class InvisBlock(Block):
    '''
    A block with a transparent image.
    (Can be used to track the position of a row of blocks
    when it goes out of the scope of the camera.)
    '''
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        #self.image = self.IMAGES['invis']
        self.image = pygame.Surface((100, 100))
        self.health = 99999
        self.type = 99
        
    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply_offset(self))
    
    def hit_interaction(self, player):
        return False

class WinBlock(Block):
    '''
    Reach this block to win the game level.
    '''
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = self.IMAGES['win']
        self.health = 99999
        self.type = 1
    
    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply_offset(self))
    
    def hit_interaction(self, player):
        if not self.god:
            player.score += 5000
            player.win = True
            return True
        else:
            return False
    

    
