import pygame
from settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, surface = pygame.Surface((TILESIZE, TILESIZE))):
        for group in groups:
            super().__init__(group)
        self.sprite_type = sprite_type
        self.image = surface
        if sprite_type == 'object':
            #offset up, cause larger objects are twice height
            self.rect = self.image.get_rect(topleft = (pos[0], pos[1] - TILESIZE))
        else:
            self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, -10)