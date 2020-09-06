import pygame
import json
from game.ui import Button, Tab, TabGroup
from game.sprites import *
from game.camera import *
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
            'endless-single' : State.make_endless_single
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
    def make_endless_single(images):
        return EndlessSingle(images=images)

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
            print('in-game index instance!')
        
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
        self.camera_button = Button(SIZE[0]//2 - 250, 300, 500, 50, 'Cameras', 'Calibri', 24,
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
         overwrite_text=f'Use experimental cameras (may break game): {"on" if self.experimental_cam else "off"}')
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
    def __init__(self, name='Pause menu', images={}, state=None):
        super().__init__(name=name, images=images)
        SOUNDS['pause'].play()
        
        self.image = self.IMAGES['pause']
        self.title_font = pygame.font.SysFont('Calibri', 64)
        self.button_font = pygame.font.SysFont('Calibri', 32)
        self.title = self.title_font.render('Paused', True, (218, 242, 245))
        self.title_size = self.title.get_size()

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
            self.manager.switch(PlayMenu(images=self.IMAGES))

class GameOver(State):
    '''
    Represents the game over menu when the player fails.
    '''
    def __init__(self, name='Game over menu', images={}, prev_game=''):
        super().__init__(name=name, images=images)
        self.image = self.IMAGES['pause']
        self.title_font = pygame.font.SysFont('Calibri', 64)
        self.button_font = pygame.font.SysFont('Calibri', 32)
        self.title = self.title_font.render('Game Over', True, (241, 0, 50))
        self.title_size = self.title.get_size()

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

    def update_objects(self, clock):
        pass

    def handle_events(self, events):
        if self.restart_button.check_click(events):
            self.manager.switch(self.game_types[self.prev_game](images=self.IMAGES))
        
        if self.quit_button.check_click(events):
            self.manager.switch(Menu(images=self.IMAGES))

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
        self.online_button = Button(SIZE[0]//2 - 70, 400, 140, 50, 'Online', 'Calibri', 32,
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
            print('online!')
        
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
            print('going to level', l)



class SinglePlayerGame(State):
    '''
    Represents an instance of a single player game.
    '''
    def __init__(self, name=None, images={}):
        super().__init__(name=name, images=images)
        self.image = self.IMAGES['game']
        self.player = Player(x=SIZE[0]//2, y=100, width=32, height=32, speed=0, accel=3, jump_accel=15)
        self.ground = 800
        self.gravity = 1
        self.deccel = 2

        print(f'[Game] Single player game created with ground {self.ground}, gravity {self.gravity}, deccel {self.deccel}')
    
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
        self.ground = 100000000
        self.blocks = pygame.sprite.Group()

        for i in range(8):
            for j in range(-2, 7):
                self.blocks.add(StandardBlock(i*100, 800-(j*100), 100, 100))
        
        self.blocks.add(InvisBlock(-100, 200, 100, 100))

        c = get_config()
        if c['experimental_camera']:
            self.camera_f = camera_follow_center_auto_up
        else:
            self.camera_f = simple_camera_follow_auto_up

        self.camera = Camera(self.camera_f, SIZE[0], SIZE[1], True, self.ground)
        self.time = pygame.time.get_ticks()

    def draw_screen(self, screen):
        screen.blit(self.image, (0, 0))

        for block in self.blocks:
            block.draw(screen, self.camera)

        self.player.draw(screen, self.camera)
    
    def update_objects(self, clock):
        self.player.update(clock, self.ground, self.gravity, self.deccel, self.blocks)
        self.camera.update_camera(self.player, clock)

        for block in self.blocks:
            if block.check_position(self.camera):
                if block.type == 99:
                    for i in range(8):
                        for j in range(-2, 7):
                            self.blocks.add(StandardBlock(i*100, 800-(j*100) - self.camera.rect.y + 599, 100, 100))
                    self.blocks.add(InvisBlock(-100, 200 - self.camera.rect.y + 599, 100, 100))
                
                block.kill()
        
        if pygame.time.get_ticks() - self.time >= 10 * 1000:
            self.time = pygame.time.get_ticks()
            self.camera.increment += 1
        
        

    def handle_events(self, events):
        if self.player.events(events, self.blocks, self.camera):
            self.manager.music.stop()
            SOUNDS['gameover'].play()
            pygame.time.wait(3000)
            self.manager.music.play(-1)
            self.manager.switch(GameOver(images=self.IMAGES, prev_game='endless-single'))

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.switch(Paused(images=self.IMAGES, state=self))
