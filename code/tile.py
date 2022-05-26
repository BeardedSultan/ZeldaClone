import pygame
from settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, surface = pygame.Surface((TILESIZE, TILESIZE))):
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.image = surface
        if sprite_type == 'object':
            #offset up, cause larger objects are twice height
            self.rect = self.image.get_rect(topleft = (pos[0], pos[1] - TILESIZE))
            self.hitbox = self.rect.inflate(-80, -105)
        else:
            self.rect = self.image.get_rect(topleft = pos)
            self.hitbox = self.rect.inflate(-20, -20)
        