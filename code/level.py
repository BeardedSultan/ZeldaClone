import pygame
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice
from weapon import *
from ui import *
from enemy import Enemy

class Level:
    def __init__(self):
        #get display surface
        self.display_surface = pygame.display.get_surface()
        #sprite group
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        #attack sprites
        self.current_attack = None
        #when player attacks, weapon goes into attack sprite, and whatever its colliding with goes into attackable sprites
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        self.create_map()

        #user interface
        self.ui = UI()

    def create_map(self):

        #map dictionary
        layouts = \
        {
            'boundary' : import_csv_layout('map/map_FloorBlocks.csv'),
            'grass' : import_csv_layout('map/map_Grass.csv'),
            'object' : import_csv_layout('map/map_Objects.csv'),
            'entities' : import_csv_layout('map/map_Entities.csv')
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
                            Tile((x, y), tuple([self.visible_sprites, self.obstacle_sprites, self.attackable_sprites]), 'grass', random_grass_image)

                        if style == 'object': #create object tile
                            surface = graphics['objects'][int(col)]
                            Tile((x, y), tuple([self.visible_sprites, self.obstacle_sprites]), 'object', surface)

                        if style == 'entities': #create entities tile
                            if col == '394':
                                #create player
                                self.player = Player(
                                    (x, y), 
                                    tuple([self.visible_sprites]), 
                                    self.obstacle_sprites, 
                                    self.create_attack, 
                                    self.destroy_attack,
                                    self.create_magic)
                            else:
                                if col == '390': monster_name = 'bamboo'
                                elif col == '391': monster_name = 'spirit'
                                elif col == '392': monster_name = 'raccoon'
                                elif col == '393': monster_name = 'squid'

                                Enemy(monster_name, (x, y), tuple([self.visible_sprites, self.attackable_sprites]), self.obstacle_sprites)

    #attack is inside Player, but weapon needs to be in level, so we're making this method to circumvent that
    def create_attack(self): 
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def create_magic(self, style, strength, cost): 
        # print(style)
        # print(strength)
        # print(cost)
        pass
    
    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill();
        self.current_attack = None

    def player_attack_logic(self):
        #cycle through attack sprites and check if they are colliding with attackable
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == 'grass':
                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(self.player, attack_sprite.sprite_type)

    def run(self):
        #update and draw level
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.visible_sprites.enemy_update(self.player)
        self.player_attack_logic()
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

    def enemy_update(self, player):
        enemy_sprites = [sprite for sprite in self.sprites() 
                         if hasattr(sprite, 'sprite_type') 
                         and sprite.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.enemy_update(player)
