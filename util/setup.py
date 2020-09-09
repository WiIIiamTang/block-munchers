import pygame
import os, sys, json


def get_config():
    config = {}
    with open(get_path('config.json'), 'r') as f:
        config = json.load(f)
    
    return config

def generate_state_images():
    config = get_config()
    SIZE = config['size']

    images = {
        'menu' : pygame.transform.scale(pygame.image.load(get_path('res/bg/bg_menu.jpg')), (SIZE[0], SIZE[1])),
        'game' : pygame.transform.scale(pygame.image.load(get_path('res/bg/bg_game.jpg')), (SIZE[0], SIZE[1])),
        'pause' : pygame.transform.scale(pygame.image.load(get_path('res/bg/bg_pause.jpg')), (SIZE[0], SIZE[1]))
    }

    return images

def generate_player_images():
    images = {
        'playerfront' : pygame.image.load(get_path('res/sprites/player_small_front1.png')),
        'playerleft' : pygame.image.load(get_path('res/sprites/player_small_left1.png')),
        'playerright' : pygame.image.load(get_path('res/sprites/player_small_right1.png'))
    }

    return images

def generate_level_thumbnails():
    images = { i : pygame.image.load(get_path(f'res/bg/l_{i}.png')) for i in range(10)}

    return images

def generate_block_images():
    images = {
        'normal' : pygame.image.load(get_path('res/sprites/block_big1.png')),
        'invis' : pygame.image.load(get_path('res/sprites/transparent.png')),
        'win' : pygame.image.load(get_path('res/sprites/win_block.png')),
        'tough' : [
            pygame.image.load(get_path('res/sprites/block_tough1.png')),
            pygame.image.load(get_path('res/sprites/block_tough2.png')),
            pygame.image.load(get_path('res/sprites/block_tough3.png'))
        ],
        'energy' : pygame.image.load(get_path('res/sprites/block_energy.png')),
        'thorns' : pygame.image.load(get_path('res/sprites/block_thorns.png')),
        'slow' : [
            pygame.image.load(get_path('res/sprites/block_slow1.png')),
            pygame.image.load(get_path('res/sprites/block_slow2.png'))
        ],
        'fear' : pygame.image.load(get_path('res/sprites/block_fear.png')),
        'super' : pygame.image.load(get_path('res/sprites/block_super.png')),
        'mushroom' : pygame.image.load(get_path('res/sprites/block_mushroom.png')),
        'steel' : [
            pygame.image.load(get_path('res/sprites/block_steel1.png')),
            pygame.image.load(get_path('res/sprites/block_steel2.png'))
        ],
        'ruby' : pygame.image.load(get_path('res/sprites/block_ruby.png'))
    }

    return images

def generate_button_sound():
    sounds = {
        'button_pass' : pygame.mixer.Sound(get_path('res/sounds/button_pass.wav'))
    }

    return sounds

def generate_eat_sound():
    sounds = {
        'munch' : pygame.mixer.Sound(get_path('res/sounds/munch.wav'))
    }

    return sounds

def generate_menu_sounds():
    sounds = {
        'pause' : pygame.mixer.Sound(get_path('res/sounds/pause.wav')),
        'gameover' : pygame.mixer.Sound(get_path('res/sounds/gameover.wav'))
    }

    return sounds


def get_path(path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, path)