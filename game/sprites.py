import pygame
import json
from util.setup import *
from game.ui import HealthBar

config = get_config()
SIZE = config['size']
SOUNDS = generate_eat_sound()
BLOCK_IMAGES = generate_block_images()

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
        self.name_font = pygame.font.SysFont('Courier', 16, bold=True)

        self.win = False

        self.extensions = {
            'up' : Extension(x+width//2, y+5),
            'down' : Extension(x+width//2, y+height+5),
            'left' : Extension(x-5, y+height//2),
            'right' : Extension(x+width+5, y+height//2)
        }

        self.health_bar_width = 400
        self.health_bar = HealthBar(x=SIZE[0]//2-self.health_bar_width//2,
         y=0, width=self.health_bar_width, height=15, max_value=self.health_bar_width)

        print(f'[Game] Player instance created at {x}, {y}')
    
    def draw(self, screen, camera, offset=(0, 0), name=False, score_location=(SIZE[0]-160, 30), draw_health=True, draw_score=True):
        new_rect = camera.apply_offset(self)
        new_rect.x += offset[0]
        new_rect.y += offset[1]

        if self.is_right:
            screen.blit(self.right, new_rect)
        elif self.is_left:
            screen.blit(self.left, new_rect)
        else:
            screen.blit(self.front, new_rect)
        
        if draw_health:
            self.health_bar.draw(screen, self)

        if draw_score:
            screen.blit(self.score_font.render(f'{self.name} Score:{self.score}', 1, (255, 23, 23)), score_location)

        if name:
            screen.blit(self.name_font.render(self.name, 1, (255, 0, 0)), (new_rect.x, new_rect.y - 20))
        # Draw extension hitboxes
        #for value in self.extensions.values():
            #value.draw(screen, camera)

        # Print player's coordinates.
        #print(f' [Game-Player] Rect: {self.rect.x}, {self.rect.y}')
        
    def update(self, clock, ground_level, gravity, deccel, blocks, move_x_limit_right=0, move_x_limit_left=0):
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
        if self.speed <= 0 and self.rect.x >= 0 + move_x_limit_left:
            self.rect.x = max(self.rect.x + self.speed * dt, 0 + move_x_limit_left)

        elif self.speed > 0 and self.rect.x <= move_x_limit_right + SIZE[0] - self.rect.width:
            self.rect.x = min(self.rect.x + self.speed * dt, move_x_limit_right + SIZE[0] - self.rect.width) 
        
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
        #print(self.rect.y)
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
        self.extensions['up'].rect.x, self.extensions['up'].rect.y = self.rect.x+self.rect.width//2, self.rect.y-self.extensions['up'].rect.height
        self.extensions['down'].rect.x, self.extensions['down'].rect.y = self.rect.x+self.rect.width//2, self.rect.y+self.rect.height
        self.extensions['left'].rect.x, self.extensions['left'].rect.y = self.rect.x-self.extensions['left'].rect.width, self.rect.y+self.rect.height//2
        self.extensions['right'].rect.x, self.extensions['right'].rect.y = self.rect.x+self.rect.width, self.rect.y+self.rect.height//2
    

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
        self.IMAGES = BLOCK_IMAGES
        self.health = 1
        self.type = -111
        self.god = False

    @classmethod
    def construct_block_from_type(cls, b, x, y, width, height):
        types = {
            0 : StandardBlock,
            1 : WinBlock,
            99 : InvisBlock,
            2 : ToughBlock,
            3 : EnergyBlock,
            4: ThornBlock,
            5: SlowBlock,
            6: FearBlock,
            7: SuperBlock,
            8: MushroomBlock,
            9: SteelBlock,
            10: RubyBlock
        }
        if b not in types.keys():
            return None 
        else:
            return types.get(b)(x, y, width, height)
        
    
    def draw_text(self, screen, camera, rendered_text):
        r = camera.apply_offset(self)
        screen.blit(rendered_text, (r.x, r.y - 20))

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
        self.image = self.IMAGES['invis']
        #self.image = pygame.Surface((100, 100))
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
            player.score += 25000
            player.win = True
            return True
        else:
            return False

class ToughBlock(Block):
    '''
    Takes more than one hit to break. The number of hits
    required can be adjusted by changing the health,
    but there is only support for 3 in the sprite images so far.
    '''
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = self.IMAGES['tough'][0]
        self.max_health = 3
        self.health = 3
        self.type = 2

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply_offset(self))

    def hit_interaction(self, player):
        if not self.god:
            if self.health == 1:
                player.score += 1200
            self.health -= 1
            player.health -= 10
            self.image = self.IMAGES['tough'][(self.max_health-self.health) if self.health > 0 else 0]
            return self.broken()
        else:
            return False

class EnergyBlock(Block):
    '''
    Restores energy when broken.
    '''
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = self.IMAGES['energy']
        self.max_health = 1
        self.health = 1
        self.type = 3

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply_offset(self))

    def hit_interaction(self, player):
        if not self.god:
            player.score += 200
            self.health -= 1
            player.health = min(player.health + 30, player.max_health)
            return self.broken()
        else:
            return False

class ThornBlock(Block):
    '''
    Does extra damage to player when hit.
    '''
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = self.IMAGES['thorns']
        self.max_health = 1
        self.health = 1
        self.type = 4

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply_offset(self))

    def hit_interaction(self, player):
        if not self.god:
            player.score += 500
            self.health -= 1
            player.health -= 30
            return self.broken()
        else:
            return False

class SlowBlock(Block):
    '''
    Reduces the player's max speed for the current session.
    '''
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = self.IMAGES['slow'][0]
        self.max_health = 2
        self.health = 2
        self.type = 5

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply_offset(self))

    def hit_interaction(self, player):
        if not self.god:
            if self.health == 1:
                player.score += 700
            self.health -= 1
            self.image = self.IMAGES['slow'][(self.max_health-self.health) if self.health > 0 else 0]
            player.health -= 10
            player.max_speed = max(2, player.max_speed - 2)
            return self.broken()
        else:
            return False

class FearBlock(Block):
    '''
    Scares the player and boosts jump for the current session.
    '''
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = self.IMAGES['fear']
        self.max_health = 1
        self.health = 1
        self.type = 6

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply_offset(self))

    def hit_interaction(self, player):
        if not self.god:
            player.score += 500
            self.health -= 1
            player.health -= 10
            player.jump_accel += 6
            return self.broken()
        else:
            return False

class SuperBlock(Block):
    '''
    Grants increased speed, health, max health, and increased hit range.
    May not extend hit range with another super block in the same stage.
    '''
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = self.IMAGES['super']
        self.max_health = 1
        self.health = 1
        self.type = 7

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply_offset(self))

    def hit_interaction(self, player):
        if not self.god:
            player.score += 2000
            self.health -= 1
            player.max_health += 100
            player.health = min(player.health + 50, player.max_health)
            player.max_speed += 2
            player.accel += 0.5
            player.extensions = {
            'up' : Extension(player.rect.x+player.rect.width//2, player.rect.y-50, height=150),
            'down' : Extension(player.rect.x+player.rect.width//2, player.rect.y+player.rect.height+50, height=150),
            'left' : Extension(player.rect.x-50, player.rect.y+player.rect.height//2, width=150),
            'right' : Extension(player.rect.x+player.rect.width+50, player.rect.y+player.rect.height//2, width=150)
        }
            return self.broken()
        else:
            return False

class MushroomBlock(Block):
    '''
    Makes the player bigger on hit.
    '''
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = self.IMAGES['mushroom']
        self.max_health = 1
        self.health = 1
        self.type = 8

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply_offset(self))

    def hit_interaction(self, player):
        if not self.god:
            player.score += 600
            self.health -= 1
            player.front = pygame.transform.scale(player.front, (player.rect.width*2, player.rect.height*2))
            player.left = pygame.transform.scale(player.left, (player.rect.width*2, player.rect.height*2))
            player.right = pygame.transform.scale(player.right, (player.rect.width*2, player.rect.height*2))
            player.rect.width *= 2
            player.rect.height *= 2
            
            player.jump_accel += 5
            player.max_speed += 2
            return self.broken()
        else:
            return False

class SteelBlock(Block):
    '''
    Takes many hits to destroy and does more damage on hit than normal.
    Not suggested to try to break.
    '''
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = self.IMAGES['steel'][0]
        self.max_health = 8
        self.health = 8
        self.type = 9

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply_offset(self))

    def hit_interaction(self, player):
        if not self.god:
            if self.health == 1:
                player.score += 2400
            self.health -= 1
            player.health -= 20
            self.image = self.IMAGES['steel'][(self.max_health-self.health)%2]
            return self.broken()
        else:
            return False

class RubyBlock(Block):
    '''
    Gives lots of points, increases max health and restores health.
    '''
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = self.IMAGES['ruby']
        self.max_health = 1
        self.health = 1
        self.type = 10

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply_offset(self))

    def hit_interaction(self, player):
        if not self.god:
            player.score += 2750
            self.health -= 1
            player.max_health += 100
            player.health = min(player.health + 150, player.max_health)
            return self.broken()
        else:
            return False

    
    

    
