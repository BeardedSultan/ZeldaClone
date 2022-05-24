import pygame
from settings import *
from support import import_folder

class Player(pygame.sprite.Sprite):
    #__INIT__#
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack):
        for group in groups:
            super().__init__(group)
        self.image = pygame.image.load('graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, -26)

        #graphics, animations
        self.import_player_assets()
        self.status = 'down'
        self.frame_index = 0
        self.animation_speed = 0.15

        #movement
        self.direction = pygame.math.Vector2() #(x, y)
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None

        self.obstacle_sprites = obstacle_sprites

        #weapon
        self.create_attack = create_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.destroy_attack = destroy_attack
        self.can_swtich_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200

        #stats
        self.stats = {'health' : 100, 'energy' : 60, 'attack' : 10, 'magic' : 4, 'speed' : 5}
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.exp = 123
        self.speed = self.stats['speed']

    def import_player_assets(self):
        character_path = 'graphics/player/'
        self.animations = \
        {
            'up' : [],
            'down' : [],
            'right' : [],
            'left' : [],

            'up_idle' : [],
            'down_idle' : [],
            'right_idle' : [],
            'left_idle' : [],

            'up_attack' : [],
            'down_attack' : [],
            'right_attack' : [],
            'left_attack' : []
        }

        for animation in self.animations.keys():
            full_animation_path = character_path + animation
            self.animations[animation] = import_folder(full_animation_path)

    def input(self):
        if not self.attacking:
            keys = pygame.key.get_pressed()

            #MOVEMENT_INPUT#
            if keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else: #key is not pressed
                self.direction.y = 0

            if keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            else: #key is not pressed
                self.direction.x = 0

            #ATTACK_INPUT#
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()
            
            #MAGIC_INPUT#
            if keys[pygame.K_r]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                print('firebolt')

            #WEAPON_SWAP#
            if keys[pygame.K_q] and self.can_swtich_weapon:
                self.can_swtich_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()
    
                if self.weapon_index < len(list(weapon_data.keys())) - 1:
                    self.weapon_index += 1
                else:
                    self.weapon_index = 0
                
                self.weapon = list(weapon_data.keys())[self.weapon_index]

    def get_status(self):
        #idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status: #don't want both idle and attack anim to play together
                self.status = self.status + '_idle'

        #attack status
        if self.attacking == True:
            self.direction.x = 0
            self.direction.y = 0
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('idle', 'attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:     
                self.status = self.status.replace('_attack', '') #don't want the attack animation to stick

    #MOVEMENT_&_SPEED#
    def move(self, speed):
        #normalize direction vector to keep diagonal speed the same
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center
        #self.rect.center += self.direction * speed
    
    #COLLISION#
    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: #moving right
                        self.hitbox.right = sprite.hitbox.left
                    elif self.direction.x < 0: #moving left
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: #moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    elif self.direction.y < 0: #moving up
                        self.hitbox.top = sprite.hitbox.bottom   
    
    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.destroy_attack()
        
        if not self.can_swtich_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_swtich_weapon = True

    def animate(self):
        animation = self.animations[self.status]

        #loop over frame indices
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        
        #set image for animation
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)

    #UPDATE_PLAYER#
    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)