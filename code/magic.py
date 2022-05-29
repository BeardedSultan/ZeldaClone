import pygame
from settings import *
from particles import *
from random import randint

class MagicPlayer:
    def __init__(self, animation_player):
        self.animation_player = animation_player

    def heal(self, player, strength, cost, groups):
        #heal mechanic
        if player.energy >= cost:
            if player.health < player.max_health:
                if player.health + strength > player.max_health:
                    player.health += player.max_health - player.health
                else:
                    player.health += strength
            player.energy -= cost

        #heal animation
            self.animation_player.create_particles('aura', player.rect.center, groups)
            self.animation_player.create_particles('heal', player.rect.center + pygame.math.Vector2(0, -30), groups)

    def flame(self, player, strength, cost, groups):
        #cast flames in direction player is facing 
        #flames mechaninc

        if player.energy >= cost:
            player.energy -= cost

        #flame animation
            if player.status.split('_')[0] == 'right': direction = pygame.math.Vector2(1, 0)
            elif player.status.split('_')[0] == 'left': direction = pygame.math.Vector2(-1, 0)
            elif player.status.split('_')[0] == 'up': direction = pygame.math.Vector2(0, -1)
            elif player.status.split('_')[0] == 'down': direction = pygame.math.Vector2(0, 1)

            for i in range(1, 6):
                if direction.x:
                    offset_x = direction.x * i * TILESIZE
                    self.animation_player.create_particles('flame', player.rect.center + pygame.math.Vector2(offset_x + randint(-TILESIZE // 3, TILESIZE // 3), randint(-TILESIZE // 3, TILESIZE // 3)), groups)
                else:
                    offset_y = direction.y * i * TILESIZE
                    self.animation_player.create_particles('flame', player.rect.center + pygame.math.Vector2(randint(-TILESIZE // 3, TILESIZE // 3), offset_y + randint(-TILESIZE // 3, TILESIZE // 3)), groups)