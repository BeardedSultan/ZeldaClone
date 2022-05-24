import pygame
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice
from weapon import *
from ui import *

class Level:
    def __init__(self):
        #get display surface
        self.display_surface = pygame.display.get_surface()
        #sprite group
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        #attack sprites
        self.current_attack = None

        self.create_map()

        #user interface
        self.ui = UI()

    def create_map(self):

        #map dictionary
        layouts = \
        {
            'boundary' : import_csv_layout('map/map_FloorBlocks.csv'),
            'grass' : import_csv_layout('map/map_Grass.csv'),
            'object' : import_csv_layout('map/map_Objects.csv')
        }

        #graphics dictionary
        graphics = \
        {
            'grass' : import_folder('graphics/grass'),
            'objects' : import_folder('graphics/objects')
        }
    
        '''
        for row_index, row in enumerate(WORLD_MAP):
            for col_index, col in enumerate(row):
                x = col_index * TILESIZE
                y = row_index * TILESIZE
                if col == 'x':
                    Tile((x, y), tuple([self.visible_sprites, self.obstacle_sprites]))
                if col == 'p':
                    self.player = Player((x, y), tuple([self.visible_sprites]), self.obstacle_sprites)
        '''

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == 'boundary': #create boundary tile
                            Tile((x, y), tuple([self.obstacle_sprites]), 'invisible')
                        if style == 'grass': #create grass tile
                            random_grass_image = choice(graphics['grass'])
                            Tile((x, y), tuple([self.visible_sprites]), 'grass', random_grass_image)
                        if style == 'object': #create object tile
                            surface = graphics['objects'][int(col)]
                            Tile((x, y), tuple([self.visible_sprites, self.obstacle_sprites]), 'object', surface)

        self.player = Player((2000, 1430), tuple([self.visible_sprites]), self.obstacle_sprites, self.create_attack, self.destroy_attack)

    #attack is inside Player, but weapon needs to be in level, so we're making this method to circumvent that
    def create_attack(self): 
        self.current_attack = Weapon(self.player, [self.visible_sprites])
    
    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill();
        self.current_attack = None

    def run(self):
        #update and draw level
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        #debug(self.player.direction)
        #debug(self.player.status)
        self.ui.display(self.player)

#CAMERA_AND_OVERLAP#
class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        #camera offset as (x, y)
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        #creating the floor
        self.ground = pygame.image.load('graphics/tilemap/ground.png').convert()
        self.ground_rect = self.ground.get_rect(topleft = (0, 0))

    def custom_draw(self, player):
        #get offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        #drawing the floor
        ground_offset_position = self.ground_rect.topleft - self.offset
        self.display_surface.blit(self.ground, ground_offset_position)

        #for sprite in self.sprites():
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_position = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_position)
