import pygame
from util.setup import get_config

config = get_config()
size = config['size']

# Camera starts at player but scrolls up.
def simple_camera_follow_auto_up(camera, rect, y_offset=1, ground_level=None):
    new_rect = pygame.Rect(-rect.left + size[0]//2, camera.height//2 - y_offset, camera.width, camera.height)
    return new_rect

# Camera follows player at center of the screen.
def simple_camera_follow_center(camera, rect, y_offset=0, ground_level=None):
    return pygame.Rect(-rect.left + size[0]//2, -rect.top + size[1]//2, camera.width, camera.height)


####################################################
# Below: experimental cameras - may not work correctly

# Camera centered at player with smooth scrolling, will not overextend on vertical axis.
def camera_follow_center_vertical_lock(camera, rect, y_offset=0, ground_level=0):
    center_x = -rect.center[0] + size[0]/2
    center_y = -rect.center[1] + size[1]/2

    camera.x += (center_x - camera.x) * 0.05
    camera.y += (center_y - camera.y) * 0.05
    
    camera.y = max(camera.height - ground_level, min(0, camera.y))
    
    return camera

# A variant of the camera that scrolls up automatically.
def camera_follow_center_auto_up(camera, rect, y_offset=1, ground_level=0):
    center_x = -rect.left + size[0]/2
    center_y = size[1]/2

    camera.x += (center_x - camera.x)
    camera.y += (center_y - camera.y)

    camera.y = max(camera.height - ground_level, min(0, camera.y - y_offset))
    
    return camera


class Camera():
    '''
    Represents the camera that follows the player
    '''
    def __init__(self, mode, width, height, up, ground_level, x=0, y=0):
        self.mode = mode
        self.rect = pygame.Rect(x, y, width, height)
        self.y_offset = 0
        self.increment = 1
        self.up = up
        self.ground_level = ground_level
    
    def apply_offset(self, target):
        # Moves the target's rect to this camera's.
        # Call on most objects when drawing.
        # Returns the modified rect. 
        return target.rect.move(self.rect.topleft)
    
    def update_camera(self, target, clock=None):
        # Moves the camera's rect to the target depending on mode set.
        # Call on object to follow.
        dt = clock.get_time() / 30

        if not self.up:
            self.rect = self.mode(self.rect, target.rect)
        else:
            self.rect = self.mode(self.rect, target.rect, self.y_offset, self.ground_level)
            self.y_offset += self.increment * dt
        