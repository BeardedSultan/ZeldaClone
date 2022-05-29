import pygame
from settings import *
from support import import_folder
from entity import Entity

class Player(Entity):
    #__INIT__#
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic):
        #had unnecessary for loop slowed the whole thing
        super().__init__(groups)
        self.image = pygame.image.load('graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET['player'])

        #graphics, animations
        self.import_player_assets()
        self.status = 'down'

        #movement
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None
        self.obstacle_sprites = obstacle_sprites

        #weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200

        #magic
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]
        self.can_switch_magic = True
        self.magic_switch_time = None

        #stats
        self.stats = {'health' : 100, 'energy' : 60, 'attack' : 10, 'magic' : 4, 'speed' : 5}
        self.max_stats = {'health' : 300, 'energy' : 140, 'attack' : 20, 'magic' : 10, 'speed' : 10}
        self.upgrade_costs = {'health' : 100, 'energy' : 100, 'attack' : 100, 'magic' : 100, 'speed' : 100}
        self.max_health = self.stats['health']
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.exp = 0
        self.speed = self.stats['speed']

        #invulnerability timer
        self.vulnerable = True  
        self.hurt_time = None
        self.invulnerability_duration = 500

        #import sounds
        self.weapon_attack_sound = pygame.mixer.Sound('audio\sword.wav')
        self.weapon_attack_sound.set_volume(0.01)

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
                self.weapon_attack_sound.play()
            
            #MAGIC_INPUT#
            if keys[pygame.K_r]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                style = list(magic_data.keys())[self.magic_index]
                strength = list(magic_data.values())[self.magic_index]['strength'] + self.stats['magic']
                cost = list(magic_data.values())[self.magic_index]['cost']
                self.create_magic(style, strength, cost)

            #WEAPON_SWAP#
            if keys[pygame.K_q] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()
    
                if self.weapon_index < len(list(weapon_data.keys())) - 1:
                    self.weapon_index += 1
                else:
                    self.weapon_index = 0
                
                self.weapon = list(weapon_data.keys())[self.weapon_index]

            #MAGIC_SWAP#
            if keys[pygame.K_e] and self.can_switch_magic:
                self.can_switch_magic = False
                self.magic_switch_time = pygame.time.get_ticks()
    
                if self.magic_index < len(list(magic_data.keys())) - 1:
                    self.magic_index += 1
                else:
                    self.magic_index = 0
                
                self.magic = list(magic_data.keys())[self.magic_index]

    def get_status(self):
        #idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status: #don't want both idle and attack anim to play together
                self.status = self.status + '_idle'

        #attack status
        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('_idle', '_attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:     
                self.status = self.status.replace('_attack', '') #don't want the attack animation to stick

    '''
    #copy to Entity class
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
    '''

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]['cooldown']:
                self.attacking = False
                self.destroy_attack()
        
        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True

        if not self.can_switch_magic:
            if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
                self.can_switch_magic = True

        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True

    def animate(self):
        animation = self.animations[self.status]

        #loop over frame indices
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        
        #set image for animation
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)

        #flicker on hit
        #TODO this is buggy, idk why but first if statment is not entered
        #TODO solved
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255) #transparency

    def get_full_weapon_damage(self):
        base_damage = self.stats['attack']
        weapon_damage = weapon_data[self.weapon]['damage']
        full_damage = base_damage + weapon_damage
        return full_damage

    def get_full_magic_damage(self):
        base_damage = self.stats['magic']
        magic_damage = magic_data[self.magic]['strength']
        full_damage = base_damage + magic_damage
        return full_damage

    def get_value_by_index(self, index):
        return list(self.stats.values())[index]

    def get_cost_by_index(self, index):
        return list(self.upgrade_costs.values())[index]

    def energy_recovery(self):
        if self.energy < self.stats['energy']:
            self.energy += 0.01 * self.stats['magic']
        else:
            self.energy = self.stats['energy']

    #UPDATE_PLAYER#
    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.stats['speed'])
        self.energy_recovery()