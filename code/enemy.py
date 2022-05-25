import pygame
from settings import *
from entity import Entity
from support import *

class Enemy(Entity):
    def __init__(self, monster_name, pos, groups, obstacle_sprites):
        #general setup
        super().__init__(groups)
        self.sprite_type = 'enemy'

        #graphics setup
        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image = self.animations[self.status][self.frame_index]

        #movement
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites

        #enemy stats
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.exp = monster_info['exp']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.resistance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']


    def import_graphics(self, name):
        self.animations = \
        {
            'idle' : [],
            'move' : [],
            'attack' : [],
        }

        #subfolders inside folder monsters
        main_path = f'graphics/monsters/{name}/'
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation) #animation is either idle, move or attack

    def get_status(self, player):
        distance_to_player = ???

        if distance_to_player <= self.attack_radius:
            self.status = 'attack'
        elif distance_to_player <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'
    
    def update(self):
        self.move(self.speed)
