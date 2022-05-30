import pygame
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice, randint
from weapon import *
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade

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
        self.upgrade = Upgrade(self.player)

        #particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

        self.game_paused = False

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

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == 'boundary': #create boundary tile
                            Tile((x, y), [self.obstacle_sprites], 'invisible')
                        if style == 'grass': #create grass tile
                            random_grass_image = choice(graphics['grass'])
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites], 'grass', random_grass_image)

                        if style == 'object': #create object tile
                            surface = graphics['objects'][int(col)]
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'object', surface)

                        if style == 'entities': #create entities tile
                            if col == '394':
                                #create player
                                self.player = Player(
                                    (x, y), 
                                    [self.visible_sprites], 
                                    self.obstacle_sprites, 
                                    self.create_attack, 
                                    self.destroy_attack,
                                    self.create_magic)
                            else:
                                if col == '390': monster_name = 'bamboo'
                                elif col == '391': monster_name = 'spirit'
                                elif col == '392': monster_name = 'raccoon'
                                elif col == '393': monster_name = 'squid'

                                Enemy(monster_name, 
                                      (x, y), 
                                      [self.visible_sprites, self.attackable_sprites], 
                                      self.obstacle_sprites, 
                                      self.damage_player, 
                                      self.trigger_death_particles, 
                                      self.gain_xp)

    #attack is inside Player, but weapon needs to be in level, so we're making this method to circumvent that
    def create_attack(self): 
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def create_enemy_attack(self): 
        self.current_attack = WeaponEnemy(self.enemy, [self.visible_sprites, self.attack_sprites])

    def create_magic(self, style, strength, cost): 
        if style == 'heal':
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])

        if style == 'flame':
            self.magic_player.flame(self.player, strength, cost, [self.visible_sprites, self.attack_sprites])

        if style == 'ice':
            self.magic_player.ice(self.player, strength, cost, [self.visible_sprites, self.attack_sprites])
    
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
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0, 50)
                            for leaf in range(randint(3, 6)):
                                self.animation_player.create_grass_particles(pos - offset, [self.visible_sprites])
                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(self.player, attack_sprite.sprite_type)

    def damage_player(self, amount, attack_type): #forgot to access player in some places, its why flicker wasn't working
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])

    def trigger_death_particles(self, pos, particle_type):
        self.animation_player.create_particles(particle_type, pos, [self.visible_sprites]) #list?
    
    def check_player_death(self):
        if self.player.health <= 0:
            self.player.kill()
            
            audio = pygame.mixer.Sound('audio\playerdeath.wav')
            audio.set_volume(0.05)

            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            alpha = 255
            fade = pygame.Surface((WIDTH, HEIGHT))
            fade.fill((183, 14, 14))
            while alpha != 0:
                if alpha == 255:
                    audio.play()
                fade.set_alpha(alpha)
                screen.fill((0, 0, 0))
                screen.blit(fade, (0, 0))
                pygame.display.update()
                alpha -= 1
            
            self.__init__()

    def gain_xp(self, amount):
        self.player.exp += amount

    def toggle_menu(self):
        self.game_paused = not self.game_paused

    def run(self):
        #update and draw level
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)

        if self.game_paused:
            #pause game and display upgrade menu
            self.upgrade.display()
        else:
            #run game
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.player_attack_logic()
            self.check_player_death()

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
