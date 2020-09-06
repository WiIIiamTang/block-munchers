import pygame
import json
import os

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
pygame.mixer.init()

from game.states import *
from util.fps import *
from util.setup import *


def main():
    config = get_config()
    fps = config['fps']
    volume = config['volume']
    WIDTH, HEIGHT = config['size'][0], config['size'][1]
    
    pygame.display.set_caption('Block Muncher')
    pygame.display.set_icon(pygame.image.load(get_path('res/icon/game_icon.png')))
    info = pygame.display.Info()
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    print(f'[Game] Running screen at {WIDTH} x {HEIGHT}')

    bgm = pygame.mixer.Sound(get_path('res/sounds/bgm.wav'))
    bgm.set_volume(volume)
    bgm.play(-1)

    state_manage = StateManager(images=generate_state_images(), volume=volume, music=bgm)
    
    running = True

    while running:
        bgm.set_volume(volume)

        if fps != -1:
            clock.tick_busy_loop(fps)
        else:
            clock.tick_busy_loop()
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        state_manage.state.handle_events(events)
        state_manage.state.update_objects(clock)
        state_manage.state.draw_screen(screen)
        draw_fps(screen, clock)

        pygame.display.update()

        fps = update_fps(state_manage.state, fps)

        volume = state_manage.volume
        


if __name__ == '__main__':
    main()
    pygame.quit()
