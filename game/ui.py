import pygame
from util.setup import generate_button_sound

'''
ui elements mostly independent from camera movement.
'''

SOUNDS = generate_button_sound()

class TextBox:
    '''
    Represents a box where text may be written.
    '''
    def __init__(self, x, y, width, height, initial_text):
        self.rect = pygame.Rect(x, y, width, height)
        self.initial_width = width
        self.width_tracker = 0
        self.color = (255, 255, 255)
        self.alt_color = (129, 230, 179)
        self.active = False
        self.font = pygame.font.SysFont('Courier', 18)
        self.rendered_text = self.font.render(initial_text, True, (0, 0, 0))
        self.ready = False
        self.text = initial_text
        self.enable_write = True
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.rendered_text, (self.rect.x + 10, self.rect.y + 10))
        
    def update(self):
        self.width_tracker = self.rect.width

        self.rect.width = max(self.initial_width, self.rendered_text.get_width() + 20)
        if self.rect.width - self.width_tracker != 0:
            self.rect.x -= (self.rect.width - self.width_tracker) / 2
    
    def events(self, events, max_chars=None):
        if self.enable_write:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.rect.collidepoint(event.pos):
                        self.text = ''
                        self.rendered_text = self.font.render('', True, (0, 0, 0))  
                        self.active = not self.active
                    else:
                        self.active = False
                
                if self.active:
                    self.color = (255, 255, 255)
                else:
                    self.color = self.alt_color
                
                if event.type == pygame.KEYDOWN and self.active:
                    if event.key == pygame.K_ESCAPE:
                        self.text = ''
                    elif event.key == pygame.K_RETURN:
                        return self.text
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                        if self.rect.width - self.initial_width != 0:
                            self.rect.x += (self.rect.width - self.width_tracker) / 2
                    else:
                        if max_chars:
                            if len(self.text) + 1 <= max_chars:
                                self.text += event.unicode
                        else:
                            self.text += event.unicode

        self.rendered_text = self.font.render(self.text, True, (0, 0, 0))
        return ''

class Button:
    '''
    Represents a clickable button.
    '''
    def __init__(self, x, y, width, height, text=None, font='Calibri',\
    size=32, color=(50, 0, 0), alt_color=(100, 0, 0), text_color=(0, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_name = font
        self.font_size = size
        self.text_color = text_color
        self.rendered = pygame.font.SysFont(self.font_name, self.font_size).render(self.text, True, self.text_color)
        self.text_size = self.rendered.get_size()
        self.color = color
        self.alt_color = alt_color
    
    def draw(self, screen, overwrite_text=None):
        pygame.draw.rect(screen, self.color, self.rect)

        if self.check_area():
            pygame.draw.rect(screen, self.alt_color, (self.rect.x - 5, self.rect.y - 5, self.rect.width + 10, self.rect.height+10))

        if overwrite_text:
            new_text = pygame.font.SysFont(self.font_name, self.font_size).render(overwrite_text, True, self.text_color)
            new_text_size = new_text.get_size()
            screen.blit(new_text, (self.rect.x + self.rect.width//2 - new_text_size[0]//2,
             self.rect.y + self.rect.height//2 - new_text_size[1]//2))
        else:
            screen.blit(self.rendered, (self.rect.x + self.rect.width//2 - self.text_size[0]//2,
             self.rect.y + self.rect.height//2 - self.text_size[1]//2))

    def check_area(self):
        mouse = pygame.mouse.get_pos()

        x_check = self.rect.x < mouse[0] < self.rect.x + self.rect.width
        y_check = self.rect.y < mouse[1] < self.rect.y + self.rect.height

        if x_check and y_check:
            return True

    def check_click(self, events):
        area = self.check_area()
        for event in events:
            if area and (event.type == pygame.MOUSEBUTTONDOWN):
                SOUNDS['button_pass'].play()
                return True

class Tab:
    '''
    Represents a single tab. Text is displayed on the "label"
    of the tab and there is space for a surface to blitted
    (eg. some more text) and another button.

    Events can be triggered through both buttons of the tab.

    Modify the tab contents through the instance methods before drawing.
    '''
    def __init__(self, x, y, width, height, text=None, font='Calibri',\
    size=32, color=(50, 0, 0), alt_color=(100, 0, 0), text_color=(0, 0, 0)):
        self.rect = pygame.Rect(0, y+50, width, height-50)
        self.text = text
        self.font_name = font
        self.font_size = size
        self.text_color = text_color
        self.rendered = pygame.font.SysFont(self.font_name, self.font_size).render(self.text, True, self.text_color)
        self.text_size = self.rendered.get_size()
        self.color = color
        self.alt_color = alt_color
        self.inner_tab_button = None
        self.inner_text = []
        self.active = False
        self.image = False

        self.tab_button = Button(x, y, 80, 50, text, font, size, color, alt_color, text_color)
    
    def draw_label_only(self, screen):
        self.tab_button.draw(screen)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        self.tab_button.draw(screen)

        if self.inner_text:
            for i, txt in enumerate(self.inner_text):
                screen.blit(txt, (50, self.rect.y+(i * 50)))
        
        if self.inner_tab_button:
            self.inner_tab_button.draw(screen)
        
        if self.image:
            screen.blit(self.image, (50, 250))
    
    def check_click(self, events):
        if self.tab_button.check_click(events):
            return True
    
    def content_events(self, events):
        if self.inner_tab_button:
            return self.inner_tab_button.check_click(events)

    def construct_inner_button(self, x, y, width, height, text=None, font='Calibri',\
    size=32, color=(50, 0, 0), alt_color=(100, 0, 0), text_color=(0, 0, 0)):
        self.inner_tab_button = Button(x, y, width, height, text=text, font=font,\
    size=size, color=color, alt_color=alt_color, text_color=text_color)

    def construct_inner_text(self, text, font, size, color):
        self.inner_text.append(pygame.font.SysFont(font, size).render(text, True, color))
    
    def construct_inner_image(self, image):
        self.image = image

class TabGroup:
    '''
    Represents a collection of tabs.
    '''
    def __init__(self, tabs):
        self.tabs = tabs
    
    def draw(self, screen):
        for t in self.tabs:
            if t.active:
                t.draw(screen)
            else:
                t.draw_label_only(screen)

    def events(self, events):
        lvl = -1
        for i, t in enumerate(self.tabs):
            if t.check_click(events):
                flipped = t.active
                self.deactivate_all_tabs()
                t.active = not flipped
            
            if t.active and t.content_events(events):
                lvl = i

        return lvl
    
    def deactivate_all_tabs(self):
        for t in self.tabs:
            t.active = False

class HealthBar(pygame.sprite.Sprite):
    '''
    The player's healthbar.
    '''
    def __init__(self, x, y, width, height, max_value):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.max_value = max_value
        self.current = max_value
    
    def draw(self, screen, player):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)
        pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, self.rect.y,
            player.health / (player.max_health/player.health_bar_width), self.rect.height))





        
