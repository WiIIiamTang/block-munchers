import pygame
import json
import subprocess
import threading
from game.ui import Button, Tab, TabGroup, TextBox
from game.sprites import *
from game.camera import *
from game.level_constructor import *
from server.game_server import *
from util.setup import get_path, get_config, generate_menu_sounds, generate_level_thumbnails



c = get_config()
SIZE = c['size']
SOUNDS = generate_menu_sounds()

class State():
    '''
    Base class for a state of the game.
    '''
    def __init__(self, name='', images={}):
        self.name = name
        self.IMAGES = images
        self.game_types = {
            'endless-single' : State.make_endless_single,
            'level-single' : State.make_level_single
        }

    def __str__(self):
        return self.name

    def draw_screen(self, screen):
        raise NotImplementedError

    def update_objects(self, clock):
        raise NotImplementedError

    def handle_events(self, events):
        raise NotImplementedError
    
    @staticmethod
    def make_endless_single(images, level=None):
        return EndlessSingle(images=images)
    
    @staticmethod
    def make_level_single(images, level):
        return LevelSingle(images=images, level=level)

class StateManager():
    '''
    Manages switching between the different states of the game.
    Initially begins at the main menu.
    '''
    def __init__(self, images, volume, music):
        self.switch(Menu(images=images))
        self.volume = volume # Volume for the global music played across all states.
        self.music = music

    def switch(self, state):
        self.state = state
        self.state.manager = self # assign the manager to the state itself.
        print(f'[Game] On state {self.state}')

##########################################################################

class Menu(State):
    '''
    Represents the main menu when opening up the game.
    '''
    def __init__(self, name='Main Menu', images={}):
        super().__init__(name=name, images=images)
        self.image = self.IMAGES['menu']
        self.title_font = pygame.font.SysFont('Calibri', 64)
        self.button_font = pygame.font.SysFont('Calibri', 32)
        self.title = self.title_font.render('Block Muncher', True, (218, 242, 245))
        self.title_size = self.title.get_size()

        self.play_button = Button(SIZE[0]//2 - 50, 200, 100, 50, 'Play',
         'Calibri', 32, (66, 227, 245), (161, 232, 240))
        self.index_button = Button(SIZE[0]//2 - 50, 300, 100, 50, 'Index', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))
        self.help_button = Button(SIZE[0]//2 - 50, 400, 100, 50, 'Help', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))
        self.settings_button = Button(SIZE[0]//2 - 70, 500, 140, 50, 'Settings', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))

        self.buttons = []
        self.buttons.extend([
            self.play_button,
            self.index_button,
            self.help_button,
            self.settings_button
        ])

    def draw_screen(self, screen):
        screen.blit(self.image, (0, 0))
        screen.blit(self.title, (SIZE[0]//2 - self.title_size[0]//2, 50))

        for b in self.buttons:
            b.draw(screen)
        
    def update_objects(self, clock):
        pass

    def handle_events(self, events):
        if self.play_button.check_click(events):
            self.manager.switch(PlayMenu(images=self.IMAGES))
        
        if self.help_button.check_click(events):
            self.manager.switch(Help(images=self.IMAGES))
        
        if self.index_button.check_click(events):
            self.manager.switch(Index(images=self.IMAGES))
        
        if self.settings_button.check_click(events):
            self.manager.switch(Settings(images=self.IMAGES))

class Help(State):
    '''
    Represents the Help menu for the game.
    '''
    def __init__(self, name='Settings', images={}):
        super().__init__(name=name, images=images)
        self.title_font = pygame.font.SysFont('Calibri', 64)
        self.title = self.title_font.render('How to Play', True, (218, 242, 245))
        self.title_size = self.title.get_size()

        self.help_text0 = pygame.font.SysFont('Arial', 24, bold=True).render(
            'Welcome to Block Muncher.',
            True, (0, 0, 0)
        )
        self.help_text1 = pygame.font.SysFont('Arial', 24, bold=True).render(
            'Use the arrow keys to move and ESC to pause.',
            True, (0, 0, 0)
        )
        self.help_text2 = pygame.font.SysFont('Arial', 24, bold=True).render(
            'Press space while holding one of the arrow keys to break blocks!',
            True, (0, 0, 0)
        )
        
        
        self.back_button = Button(SIZE[0]//2 - 120, 500, 240, 50, 'Back', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))

        self.buttons = []
        self.buttons.extend([
            self.back_button
        ])
    
    def draw_screen(self, screen):
        screen.fill((61, 120, 128))
        screen.blit(self.title, (SIZE[0]//2 - self.title_size[0]//2, 50))

        for b in self.buttons:
            b.draw(screen)
        
        screen.blit(self.help_text0, (SIZE[0]//2 - 130, 200))
        screen.blit(self.help_text1, (SIZE[0]//2 - 220, 250))
        screen.blit(self.help_text2, (SIZE[0]//2 - 280, 300))

    
    def update_objects(self, clock):
        pass

    def handle_events(self, events):  
        if self.back_button.check_click(events):
            self.manager.switch(Menu(images=self.IMAGES))


class Settings(State):
    '''
    Represents the Settings menu for the game.
    '''
    def __init__(self, name='Settings', images={}):
        super().__init__(name=name, images=images)
        self.title_font = pygame.font.SysFont('Calibri', 64)
        self.title = self.title_font.render('Settings', True, (218, 242, 245))
        self.title_size = self.title.get_size()
        c = get_config()
        self.fps = c['fps']
        self.experimental_cam = c['experimental_camera']

        self.fps_button = Button(SIZE[0]//2 - 120, 200, 240, 50, 'FPS', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))
        self.camera_button = Button(SIZE[0]//2 - 255, 300, 510, 50, 'Cameras', 'Calibri', 26,
        (66, 227, 245), (161, 232, 240))
        self.volume_button = Button(SIZE[0]//2 - 130, 400, 260, 50, 'Volume', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))
        self.back_button = Button(SIZE[0]//2 - 120, 500, 240, 50, 'Back', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))

        self.buttons = []
        self.buttons.extend([
            self.back_button
        ])
    
    def draw_screen(self, screen):
        screen.fill((61, 120, 128))
        screen.blit(self.title, (SIZE[0]//2 - self.title_size[0]//2, 50))

        for b in self.buttons:
            b.draw(screen)
        
        if self.fps != -1:
            fps_text = self.fps
        else:
            fps_text = 'Uncapped'

        self.fps_button.draw(screen, overwrite_text=f'FPS: {fps_text}')
        self.camera_button.draw(screen, 
         overwrite_text=f'Use smoother cameras on level stages: {"[ON]" if self.experimental_cam else "[OFF]"}')
        self.volume_button.draw(screen,
         overwrite_text=f'Music volume:{self.manager.volume}')
    
    def update_objects(self, clock):
        pass

    def handle_events(self, events):
        if self.fps_button.check_click(events):
            fps_switch = {
                30 : 60,
                60 : 120,
                120 : -1,
                -1 : 30
            }

            self.fps = fps_switch[self.fps]
            print(f'[Game] fps changed to {self.fps}')

            with open(get_path('config.json'), 'r+') as f:
                config = json.load(f)
                config['fps'] = self.fps
                f.seek(0)
                json.dump(config, f)
                f.truncate()
        
        if self.camera_button.check_click(events):
            with open(get_path('config.json'), 'r+') as f:
                config = json.load(f)
                self.experimental_cam = int(not config['experimental_camera'])
                config['experimental_camera'] = self.experimental_cam
                f.seek(0)
                json.dump(config, f)
                f.truncate()
            print(f'[Game] Toggled experimental cameras')
        

        if self.volume_button.check_click(events):
            volume_switch = {
                0.0 : 0.25,
                0.25 : 0.5,
                0.5 : 0.75,
                0.75 : 1.0,
                1.0 : 0
            }
            self.manager.volume = volume_switch[self.manager.volume]
            print(f'[Game] music volume changed to {self.manager.volume}')

            with open(get_path('config.json'), 'r+') as f:
                config = json.load(f)
                config['volume'] = self.manager.volume
                f.seek(0)
                json.dump(config, f)
                f.truncate()

        

        if self.back_button.check_click(events):
            self.manager.switch(Menu(images=self.IMAGES))

class Paused(State):
    '''
    Represents the pause menu when in-game.
    '''
    def __init__(self, name='Pause menu', images={}, state=None, from_index=False):
        super().__init__(name=name, images=images)
        SOUNDS['pause'].play()
        
        self.image = self.IMAGES['pause']
        self.title_font = pygame.font.SysFont('Calibri', 64)
        self.button_font = pygame.font.SysFont('Calibri', 32)
        self.title = self.title_font.render('Paused', True, (218, 242, 245))
        self.title_size = self.title.get_size()
        self.from_index = from_index
        self.paused_game = state

        self.resume_button = Button(SIZE[0]//2 - 120, 200, 240, 50, 'Resume', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))
        self.quit_button = Button(SIZE[0]//2 - 120, 300, 240, 50, 'Quit', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))

        self.buttons = []
        self.buttons.extend([
            self.resume_button,
            self.quit_button
        ])
    
    def draw_screen(self, screen):
        screen.blit(self.image, (0, 0))
        screen.blit(self.title, (SIZE[0]//2 - self.title_size[0]//2, 50))

        for b in self.buttons:
            b.draw(screen)

    def update_objects(self, clock):
        pass

    def handle_events(self, events):
        if self.resume_button.check_click(events):
            self.manager.switch(self.paused_game)
        
        if self.quit_button.check_click(events):
            if not self.from_index:
                self.manager.switch(PlayMenu(images=self.IMAGES))
            else:
                self.manager.switch(Menu(images=self.IMAGES))

class GameOver(State):
    '''
    Represents the game over menu when the player fails.
    '''
    def __init__(self, name='Game over menu', images={}, prev_game='', player=None):
        super().__init__(name=name, images=images)
        self.image = self.IMAGES['pause']
        self.title_font = pygame.font.SysFont('Calibri', 64)
        self.button_font = pygame.font.SysFont('Calibri', 32)
        self.title = self.title_font.render('Game Over', True, (241, 0, 50))
        self.title_size = self.title.get_size()

        self.player = player
        self.prev_game = prev_game

        self.restart_button = Button(SIZE[0]//2 - 120, 200, 240, 50, 'Restart', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))
        self.quit_button = Button(SIZE[0]//2 - 120, 300, 240, 50, 'Quit', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))

        self.buttons = []
        self.buttons.extend([
            self.restart_button,
            self.quit_button
        ])
    
    def draw_screen(self, screen):
        screen.blit(self.image, (0, 0))
        screen.blit(self.title, (SIZE[0]//2 - self.title_size[0]//2, 50))

        for b in self.buttons:
            b.draw(screen)
        
        screen.blit(self.player.score_font.render(f'Final score:{self.player.score}', 1, (255, 23, 23)), (SIZE[0]//2-125, 125))
        screen.blit(self.player.front, (150, 300))

    def update_objects(self, clock):
        pass

    def handle_events(self, events):
        if self.restart_button.check_click(events):
            self.manager.switch(self.game_types[self.prev_game](images=self.IMAGES))
        
        if self.quit_button.check_click(events):
            self.manager.switch(Menu(images=self.IMAGES))

class Win(State):
    '''
    Represents the win menu when the player fails. Is similar to the game over.
    '''
    def __init__(self, name='Win menu', images={}, prev_game='', player=None, level=0):
        super().__init__(name=name, images=images)
        self.image = self.IMAGES['pause']
        self.title_font = pygame.font.SysFont('Calibri', 64)
        self.button_font = pygame.font.SysFont('Calibri', 32)
        self.title = self.title_font.render('Win!', True, (241, 0, 50))
        self.title_size = self.title.get_size()
        self.level = level
        self.player = player
        self.prev_game = prev_game

        self.restart_button = Button(SIZE[0]//2 - 120, 200, 240, 50, 'Restart', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))
        self.quit_button = Button(SIZE[0]//2 - 120, 300, 240, 50, 'Quit', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))

        self.buttons = []
        self.buttons.extend([
            self.restart_button,
            self.quit_button
        ])
    
    def draw_screen(self, screen):
        screen.blit(self.image, (0, 0))
        screen.blit(self.title, (SIZE[0]//2 - self.title_size[0]//2, 50))

        for b in self.buttons:
            b.draw(screen)
        
        screen.blit(self.player.score_font.render(f'Final score:{self.player.score}', 1, (255, 23, 23)), (SIZE[0]//2-125, 125))
        screen.blit(self.player.front, (150, 300))

    def update_objects(self, clock):
        pass

    def handle_events(self, events):
        if self.restart_button.check_click(events):
            self.manager.switch(self.game_types[self.prev_game](images=self.IMAGES, level=self.level))
        
        if self.quit_button.check_click(events):
            self.manager.switch(PlayMenu(images=self.IMAGES))

class PlayMenu(State):
    '''
    Represents the menu after clicking on play from the main menu.
    Select the game mode here.
    '''
    def __init__(self, name='Play Menu', images={}):
        super().__init__(name=name, images=images)
        self.image = self.IMAGES['menu']
        self.title_font = pygame.font.SysFont('Calibri', 64)
        self.title = self.title_font.render('Play', True, (218, 242, 245))
        self.title_size = self.title.get_size()

        self.levels_button = Button(SIZE[0]//2 - 50, 200, 100, 50, 'Levels', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))
        self.endless_button = Button(SIZE[0]//2 - 70, 300, 140, 50, 'Endless', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))
        self.online_button = Button(SIZE[0]//2 - 85, 400, 170, 50, 'Multiplayer', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))
        self.back_button = Button(SIZE[0]//2 - 70, 500, 140, 50, 'Back', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))

        self.buttons = []
        self.buttons.extend([
            self.levels_button,
            self.endless_button,
            self.online_button,
            self.back_button
        ])

    def draw_screen(self, screen):
        screen.blit(self.image, (0, 0))
        screen.blit(self.title, (SIZE[0]//2 - self.title_size[0]//2, 50))

        for b in self.buttons:
            b.draw(screen)
        
    def update_objects(self, clock):
        pass

    def handle_events(self, events):
        if self.levels_button.check_click(events):
            self.manager.switch(LevelSelect(images=self.IMAGES))
        
        if self.endless_button.check_click(events):
            self.manager.switch(EndlessSingle(images=self.IMAGES))
        
        if self.online_button.check_click(events):
            self.manager.switch(MultiPlayerMenu(images=self.IMAGES))
        
        if self.back_button.check_click(events):
            self.manager.switch(Menu(images=self.IMAGES))

class LevelSelect(State):
    '''
    Represents the menu to choose the level to play.
    '''
    def __init__(self, name='Level Select', images={}):
        super().__init__(name=name, images=images)
        self.image = self.IMAGES['menu']
        self.title_font = pygame.font.SysFont('Calibri', 64)
        self.title = self.title_font.render('Level Select', True, (218, 242, 245))
        self.title_size = self.title.get_size()
        self.thumbnails = generate_level_thumbnails()

        self.back_button = Button(SIZE[0]//2 - 70, 500, 140, 50, 'Back', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))

        self.buttons = []
        self.buttons.extend([
            self.back_button
        ])

        tab_colors = {
            0 : (3, 252, 20),
            1 : (53, 252, 3),
            2 : (90, 252, 3),
            3 : (120, 252, 3),
            4 : (161, 252, 3),
            5 : (231, 252, 3),
            6 : (252, 202, 3),
            7 : (252, 169, 3),
            8 : (252, 132, 3),
            9 : (252, 86, 3),
            10 : (252, 49, 3)
        }

        lvl_desc = {
            0 : '[T0] Welcome to the game.',
            1 : '[T1] There are different types of blocks...',
            2 : '[T2] Watch out for your health.',
            3 : '[T3] Don\'t forget about jumping!',
            4 : 'Big Cavern',
            5 : 'Galaxy Brain',
            6 : '6D Chess',
            7 : 'Marathon',
            8 : 'Haha spacebar go brrrrr',
            9 : 'Final Destination'
        }

        lvl_images = { i : f'res/bg/l_{i}.png' for i in range(10)}

        self.level_tabs = TabGroup([Tab(i*80, 150, SIZE[0], SIZE[1]-300, f'Level {i}', 'Calibri', 18,
         tab_colors[i], (3, 252, 102)) for i in range(10)])
        
        
        for i, t in enumerate(self.level_tabs.tabs):
            t.construct_inner_button(600, 350, 100, 50, 'Start', 'Calibri', 24, (0, 0, 0), (30, 30, 30), (255, 0, 0))
            t.construct_inner_text(lvl_desc[i], 'Courier', 28, (0, 0, 255))
            t.construct_inner_image(self.thumbnails[i])

    def draw_screen(self, screen):
        screen.blit(self.image, (0, 0))
        screen.blit(self.title, (SIZE[0]//2 - self.title_size[0]//2, 50))

        for b in self.buttons:
            b.draw(screen)
        
        self.level_tabs.draw(screen)
        
    def update_objects(self, clock):
        pass

    def handle_events(self, events):
        if self.back_button.check_click(events):
            self.manager.switch(PlayMenu(images=self.IMAGES))
        
        l = self.level_tabs.events(events)
        if l != -1:
            self.manager.switch(LevelSingle(images=self.IMAGES, level=str(l)))



class SinglePlayerGame(State):
    '''
    Represents an instance of a single player game.
    '''
    def __init__(self, name=None, images={}):
        super().__init__(name=name, images=images)
        self.image = self.IMAGES['game']
        self.player = Player(x=SIZE[0]//2, y=50, width=32, height=32, speed=0, accel=3, jump_accel=15)
        self.ground = 800 # will be changed in levels.
        self.gravity = 1
        self.deccel = 2

        print(f'[Game] Single player game created with gravity {self.gravity}, deccel {self.deccel}')
    
    def draw_screen(self, screen):
        pass

    def update_objects(self, clock):
        pass

    def handle_events(self, events):
        pass


class EndlessSingle(SinglePlayerGame):
    '''
    Represents the endless mode in single player.
    '''
    def __init__(self, name='Endless single player', images={}):
        super().__init__(name=name, images=images)
        self.blocks = pygame.sprite.Group()
        self.level_constructor = LevelConstructor.get_endless()
        self.blocks = self.level_constructor.get_random_chunk()

        self.ground = self.level_constructor.ground_level

        self.camera = Camera(simple_camera_follow_auto_up, SIZE[0], SIZE[1], True, self.ground)
        self.time = pygame.time.get_ticks()

    def draw_screen(self, screen):
        screen.blit(self.image, (0, 0))

        for block in self.blocks:
            block.draw(screen, self.camera)

        self.player.draw(screen, self.camera)
    
    def update_objects(self, clock):
        self.player.update(clock, self.ground, self.gravity, self.deccel, self.blocks)
        self.camera.update_camera(self.player, clock)

        self.blocks = self.level_constructor.update_block_chunks(self.camera)
        
        if pygame.time.get_ticks() - self.time >= 10 * 1000:
            self.time = pygame.time.get_ticks()
            self.camera.increment += 1
        
        

    def handle_events(self, events):
        if self.player.events(events, self.blocks, self.camera):
            self.manager.music.stop()
            SOUNDS['gameover'].play()
            pygame.time.wait(3000)
            self.manager.music.play(-1)
            self.manager.switch(GameOver(images=self.IMAGES, prev_game='endless-single', player=self.player))

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.switch(Paused(images=self.IMAGES, state=self))
    

class LevelSingle(SinglePlayerGame):
    '''
    Represents a level of a single player game.
    '''
    def __init__(self, name='Level', images={}, level='0'):
        super().__init__(name=name, images=images)
        self.level = level
        self.blocks = pygame.sprite.Group()
        self.level_constructor = LevelConstructor.get_level(self.level)
        self.blocks = self.level_constructor.blocks
        self.ground = self.level_constructor.ground_level
        
        self.restart_button = Button(50, 20, 50, 50, text='Restart', size=18, color=(200, 150, 0), alt_color=(255, 255, 150))

        c = get_config()
        if c['experimental_camera']:
            self.camera_f = camera_follow_center_vertical_lock
        else:
            self.camera_f = simple_camera_follow_center

        self.camera = Camera(self.camera_f, SIZE[0], SIZE[1], True, self.ground)
        self.time = pygame.time.get_ticks()

    def draw_screen(self, screen):
        screen.blit(self.image, (0, 0))

        for block in self.blocks:
            block.draw(screen, self.camera)

        self.player.draw(screen, self.camera)
        self.restart_button.draw(screen)
    
    def update_objects(self, clock):
        self.player.update(clock, self.ground, self.gravity, self.deccel, self.blocks)
        self.camera.update_camera(self.player, clock)

    def handle_events(self, events):
        if self.player.events(events, self.blocks, self.camera):
            self.manager.music.stop()
            SOUNDS['gameover'].play()
            pygame.time.wait(3000)
            self.manager.music.play(-1)
            self.manager.switch(GameOver(images=self.IMAGES, prev_game='level-single', player=self.player))

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.switch(Paused(images=self.IMAGES, state=self))
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_r) or self.restart_button.check_click(events):
                self.manager.switch(LevelSingle(images=self.IMAGES, level=self.level))
        
        if self.player.win:
            self.manager.switch(Win(images=self.IMAGES, prev_game='level-single', player=self.player, level=self.level))


class Index(SinglePlayerGame):
    '''
    Represents the index menu showing block types.
    '''
    def __init__(self, name='Index', images={}, level='9999'):
        super().__init__(name=name, images=images)
        self.player = Player(x=SIZE[0]//2, y=50, width=32, height=32, speed=0, accel=3, jump_accel=30)
        self.gravity = 2
        self.player.max_speed = 15
        self.level = level
        self.blocks = pygame.sprite.Group()
        self.level_constructor = LevelConstructor.get_level(self.level)
        self.blocks = self.level_constructor.blocks
        self.ground = self.level_constructor.ground_level

        c = get_config()
        if c['experimental_camera']:
            self.camera_f = camera_follow_center_vertical_lock
        else:
            self.camera_f = simple_camera_follow_center

        self.camera = Camera(self.camera_f, SIZE[0], SIZE[1], True, self.ground)
        self.time = pygame.time.get_ticks()

        for b in self.blocks:
            b.god = True

    def draw_screen(self, screen):
        screen.blit(self.image, (0, 0))

        for block in self.blocks:
            block.draw(screen, self.camera)

        self.player.draw(screen, self.camera)
    
    def update_objects(self, clock):
        self.player.update(clock, self.ground, self.gravity, self.deccel, self.blocks)
        self.camera.update_camera(self.player, clock)
        

    def handle_events(self, events):
        self.player.events(events, self.blocks, self.camera)

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.switch(Paused(images=self.IMAGES, state=self, from_index=True))


class MultiPlayerMenu(State):
    '''
    Represents the menu where you start muliplayer games.
    '''
    def __init__(self, name='Multiplayer menu', images={}, client=None, server=None):
        super().__init__(name=name, images=images)
        self.image = self.IMAGES['menu']
        self.title_font = pygame.font.SysFont('Calibri', 64)
        self.button_font = pygame.font.SysFont('Calibri', 32)
        self.title = self.title_font.render('Multiplayer (1v1)', True, (218, 242, 245))
        self.title_size = self.title.get_size()

        self.connect_button = Button(70, 300, 170, 50, 'Connect', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))
        self.host_button = Button(70, 400, 170, 50, 'Host', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))
        self.start_button = Button(500, 380, 250, 80, 'Start', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))
        self.ready_button = Button(500, 480, 250, 80, 'Ready', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))
        self.back_button = Button(70, 500, 150, 50, 'Quit', 'Calibri', 32,
         (66, 227, 245), (161, 232, 240))

        self.buttons = [
            self.back_button
        ]

        self.instructions = 'Enter {ip}:{port} right here. Then click the host/connect buttons.'
        self.text_box = TextBox(SIZE[0]//2 - 35, 200, 70, 40, self.instructions)
        self.name_box = TextBox(SIZE[0]//2 - 35, 150, 70, 40, 'Type name here (max 12 chars).')
        self.status_box = TextBox(500, 300, 250, 40, 'This will show connected players')
        self.quit_box = TextBox(255, 510, 250, 40, '<<< Quit to reset and exit out of any hosted/joined servers!')

        self.status_box.enable_write = False
        self.quit_box.enable_write = False
        self.quit_box.font = pygame.font.SysFont('Calibri', 12)

        self.draw_quit_box = False

        self.players_in_room = {}
        self.full = False
        
        self.server = server
        self.client = client
        self.active_client = True if client else False
        self.active_server = True if server else False

        self.to_send = {'type' : 'menu',
         'name' : '',
         'ready' : False,
         'started' : False
        }
    
    def host(self):
        job = threading.Thread(target=self.server.handle_connections, daemon=True)
        job.start()

    def connect_client(self):
        try:
            self.id = int(self.client.connect())
            self.active_client = True
        except:
            pass

    def draw_screen(self, screen):
        screen.blit(self.image, (0, 0))
        screen.blit(self.title, (SIZE[0]//2 - self.title_size[0]//2, 50))

        self.text_box.draw(screen)
        self.name_box.draw(screen)
        self.status_box.draw(screen)
        if self.draw_quit_box:
            self.quit_box.draw(screen)

        for b in self.buttons:
            b.draw(screen)
        
        self.host_button.draw(screen, overwrite_text=f'{"(Hosting)" if self.active_server else "Host"}')
        self.connect_button.draw(screen, overwrite_text=f'{"(Connected)" if self.active_client else "Connect"}')

        if self.full:
            self.start_button.draw(screen)
            self.ready_button.draw(screen,
             overwrite_text=f'{"Lock in" if not self.to_send["ready"] else "Ready "+str(sum(self.server_reply["ready"].values()))+"/2"}')
        
        
        
    def update_objects(self, clock):
        self.text_box.update()
        self.name_box.update()
        self.status_box.update()
        if self.draw_quit_box:
            self.quit_box.update()

        if self.active_client:
            try:
                self.to_send['type'] = 'menu'
                self.to_send['name'] = self.name_box.text
                self.server_reply = self.client.update(self.to_send)
                self.players_in_room = self.server_reply['players']
                self.full = self.server_reply['full']
                #print(self.id)
                #print('[Game] Client got reply', self.server_reply)
                #print(full, self.id not in self.players_in_room.keys())

                if self.full and self.id not in self.players_in_room.keys():
                    self.status_box.text = 'That room is already full!'
                    self.active_client = False
                else:
                    try:
                        self.status_box.text = ' | '.join([player['name'] for player in self.players_in_room.values()])
                    except TypeError:
                        self.status_box.text = ' | '.join([name for name in self.players_in_room.values()])
            except Exception as e:
                self.status_box.font = pygame.font.SysFont('Courier', 14)
                self.status_box.text = '[ERROR] Connection to server interrupted'
                self.full = False
                print(e)
            

    def handle_events(self, events):
        self.text_box.events(events)
        self.name_box.events(events, max_chars=12)
        self.status_box.events(events)
        if self.draw_quit_box:
            self.quit_box.events(events)

        if self.connect_button.check_click(events):
            if not self.active_client:
                if self.text_box.text:
                    data = self.text_box.text.strip().split(':')
                    try:
                        data[0] = '127.0.0.1' if not data[0] else data[0]
                        self.client = Client(ip=data[0], port=int(data[1]))
                        self.connect_client()

                        self.name_box.enable_write = False
                        print('[Game] Connected to', data[0])
                    except Exception as e:
                        self.text_box.text = f'{type(e)}'

                else:
                    self.text_box.text = 'No address input'

        if self.host_button.check_click(events):
            if not self.active_server:
                if self.text_box.text:
                    data = self.text_box.text.strip().split(':')
                    try:
                        self.server = Server(ip=data[0], port=int(data[1]))
                        self.host()

                        self.active_server = True
                        #self.text_box.enable_write = False

                    except Exception as e:
                        self.text_box.text = f'{type(e)}'
                        print(e)
                else:
                    self.text_box.text = 'No address input'

        if self.back_button.check_click(events):
            if self.active_server:
                self.server.running = False
                self.server.shutdown()
            if self.active_client:
                self.client.close()
            self.manager.switch(PlayMenu(images=self.IMAGES))
        
        if self.full:
            if self.ready_button.check_click(events):
                self.to_send['ready'] = not self.to_send['ready']

            if self.start_button.check_click(events) or sum(self.server_reply['started'].values()) > 0:    
                if self.server_reply['start']:
                    self.to_send['started'] = True
                    self.client.update(self.to_send)
                    self.manager.switch(EndlessMultiPlayer(images=self.IMAGES,
                     client=self.client, server=self.server, id=self.id))
        
        if self.back_button.check_area():
            self.draw_quit_box = True
        else:
            self.draw_quit_box = False



class EndlessMultiPlayer(State):
    '''
    Represents the multiplayer in-game state.
    '''
    def __init__(self, name='Endless multi player', images={}, client=None, server=None, id=-1):
        super().__init__(name=name, images=images)
        self.image = self.IMAGES['game']
        self.ground = 600
        self.gravity = 1
        self.deccel = 2
        self.blocks = pygame.sprite.Group()
        self.blocks2 = pygame.sprite.Group()
        self.client = client
        self.server = server
        self.id = id

        # Get the initial players setup from server.
        self.to_send = {
            'type' : 'ingame',
            'setup' : True,
            'init-blocks' : False,
            'player' : None,
            'blocks' : set()
        }

        self.server_reply = self.client.update(self.to_send)
        print('[Game] Multiplayer - Initial server reply:', self.server_reply)
        # setting up the two players from the server.
        # see comments for differences when rendering online multiplayer.
        kwargs = self.server_reply['players'][self.server_reply['p1']]
        self.player = Player(**kwargs)

        kwargs = self.server_reply['players'][self.server_reply['p2']]
        self.player2 = Player(**kwargs)

        self.camera = Camera(simple_camera_follow_center, SIZE[0], SIZE[1], True, self.ground)

        # blocks are generated client-side, and are processed client-side (breaks/collisions)
        self.level_constructor = LevelConstructor.get_endless()
        
        self.blocks =  self.level_constructor.get_random_chunk()

        self.alive_blocks = set([(b.rect.x, b.rect.y) for b in self.blocks.sprites()])

        self.ground = self.level_constructor.ground_level
        self.time = pygame.time.get_ticks()

        self.to_send['setup'] = False

        self.send_initial_blocks()

        self.separator = StandardBlock(800, 0, 3, 1200)
        self.separator.image = pygame.Surface((3, 600))
        self.separator.god = True

        self.player.score_font = pygame.font.SysFont('Calibri', 18, bold=True, italic=True)
        self.player2.score_font = pygame.font.SysFont('Calibri', 18, bold=True, italic=True)
        
    def send_initial_blocks(self):
        self.to_send['init-blocks'] = True
        self.to_send['blocks'].update(self.alive_blocks)
        
        self.server_reply = self.client.update(self.to_send)

        self.to_send['init-blocks'] = False

    def draw_screen(self, screen):
        screen.blit(self.image, (0, 0))

        for b in self.blocks:
            b.draw(screen, self.camera)
        
        self.separator.draw(screen, self.camera)

        if self.id == self.server_reply['p1']:
            self.player.draw(screen, self.camera, name=True, score_location=(SIZE[0]-200, 45))
            self.player2.draw(screen, self.camera, name=True, score_location=(SIZE[0]-200, 60), draw_health=False)
        else:
            self.player.draw(screen, self.camera, name=True, score_location=(SIZE[0]-200, 45), draw_health=False)
            self.player2.draw(screen, self.camera, name=True, score_location=(SIZE[0]-200, 60))
        

    def update_alive_blocks(self):
        for block in self.blocks:
            if (block.rect.x, block.rect.y) not in self.alive_blocks:
                block.kill()
        
        print('blocks:', len(self.blocks), 'alive:', len(self.alive_blocks))
                
        self.alive_blocks = {(b.rect.x, b.rect.y) for b in self.blocks}
        

    def update_objects(self, clock):
        if pygame.time.get_ticks() - self.time >= 10 * 1000:
            self.time = pygame.time.get_ticks()
            self.camera.increment += 1
        
        #self.blocks = self.level_constructor.update_block_chunks(self.camera)
        #self.alive_blocks.update({(b.rect.x, b.rect.y) for b in self.blocks})

        # Update players: ONLY the player that you are controlling.
        # Note for p2:
        # add extra kwarg to move p2 over 800 units to the right of p1.
        # p2 will spawn in their zone too, so there is no need to modify drawing.
        #
        # Then, send our update packet every frame and update the other player with the server reply.
        if self.id == self.server_reply['p1']:
            self.player.update(clock, self.ground, self.gravity, self.deccel, self.blocks)
            
            self.update_alive_blocks()

            self.to_send['player'] = {'x': self.player.rect.x, 'y': self.player.rect.y}
            self.to_send['blocks'] = self.alive_blocks

            self.server_reply = self.client.update(self.to_send)

            self.player2.rect.x = self.server_reply['players'][self.server_reply['p2']]['x']
            self.player2.rect.y = self.server_reply['players'][self.server_reply['p2']]['y']

            self.alive_blocks = self.server_reply['blocks']
            #print(len(self.alive_blocks2))
            self.camera.update_camera(self.player, clock)
            #print(self.player.rect.x, self.player.rect.y)
            
        else:
            self.player2.update(clock, self.ground, self.gravity, self.deccel, self.blocks, move_x_limit=800)
            
            self.update_alive_blocks()

            self.to_send['player'] = {'x': self.player2.rect.x, 'y': self.player2.rect.y}
            self.to_send['blocks'] = self.alive_blocks

            self.server_reply = self.client.update(self.to_send)

            self.player.rect.x = self.server_reply['players'][self.server_reply['p1']]['x']
            self.player.rect.y = self.server_reply['players'][self.server_reply['p1']]['y']

            self.alive_blocks = self.server_reply['blocks']
            #print(len(self.alive_blocks))
            self.camera.update_camera(self.player2, clock)

            


        self.separator.rect.y += 10 if self.separator.rect.y < -self.camera.rect.y else 0 

        

              
        

    def handle_events(self, events):
        # events handled only for the player you are controlling.
        if self.id == self.server_reply['p1']:
            self.player.events(events, self.blocks, self.camera)
        else:
            self.player2.events(events, self.blocks, self.camera)