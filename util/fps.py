import pygame
from game.states import Settings

def update_fps(state, original):
    if isinstance(state, Settings):
        return state.fps
    else:
        return original

def draw_fps(screen, clock, x=0, y=0):
    '''
    Draw the fps onto the screen.
    '''
    COURIER = pygame.font.SysFont('Courier', 16)
    fps_overlay = COURIER.render(str(int(clock.get_fps())), True, pygame.Color("Red"))
    screen.blit(fps_overlay, (x, y))