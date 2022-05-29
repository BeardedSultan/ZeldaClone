import pygame
from settings import *

class Upgrade:
    def __init__(self, player):
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.attrib_number = len(player.stats)
        self.attrib_names = list(player.stats.keys())
        self.max_values = list(player.max_stats.values())
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        #selection system
        self.selection_index = 0
        self.can_move = True
        self.selection_time = None
        self.selection_duration = 300

        #item creation
        self.height = self.display_surface.get_size()[1] * 0.8
        self.width = self.display_surface.get_size()[0] // 6
        self.create_items()

    def input(self):
        keys = pygame.key.get_pressed()

        if self.can_move:
            if keys[pygame.K_RIGHT] and self.selection_index < self.attrib_number - 1:
                self.selection_index += 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
            elif keys[pygame.K_LEFT] and self.selection_index >= 1:
                self.selection_index -= 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            if keys[pygame.K_SPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.item_list[self.selection_index].trigger(self.player)

    def selection_cooldown(self):
        current_time = pygame.time.get_ticks()

        if not self.can_move:
            if current_time - self.selection_time >= self.selection_duration:
                self.can_move = True

    def create_items(self):
        #draw boxes and label them
        #this is my implementation
        '''item = Item(0, 0, self.width, self.height, self.attrib_number, self.font, self.display_surface, self.attrib_names)
        item.draw_item()'''

        self.item_list = []

        for item, index in enumerate(range(self.attrib_number)):
            #horizontal pos
            full_width = self.display_surface.get_size()[0]
            increment = full_width // self.attrib_number
            left = (item * increment) + (increment - self.width) // 2
            #vertical pos
            top = self.display_surface.get_size()[1] * 0.1
            #create object
            item = Item(left, top, self.width, self.height, index, self.font)
            self.item_list.append(item)

    def display(self):
        self.input()
        self.selection_cooldown()

        for index, item in enumerate(self.item_list):
            #get attributes
            name = self.attrib_names[index]
            value = self.player.get_value_by_index(index)
            max_value = self.max_values[index]
            cost = self.player.get_cost_by_index(index)
            surface = self.display_surface
            item.draw_item(surface, self.selection_index, name, value, max_value, cost)

class Item:
    #this is my implementation of this class
    '''def __init__(self, left, top, width, height, index, font, display_surface, names):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.index = index
        self.font = font
        self.display_surface = display_surface
        self.attrib_names = names'''

    def __init__(self, left, top, width, height, index, font):
        self.rect = pygame.Rect(left, top, width, height)
        self.index = index
        self.font = font
    
    #my implementation
    '''def draw_item(self):
        s = pygame.Surface((self.width, self.height))
        s.set_alpha(128)
        s.fill('black')
        offset = 0
        for i in range(self.index):
            self.display_surface.blit(s, (30 + offset, 100))
            offset += WIDTH / 5

            text_surf = self.font.render(str(self.attrib_names[i]), False, TEXT_COLOR)
            text_rect = text_surf.get_rect(center = (offset - 195, 130))
            pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(70, 10))
            self.display_surface.blit(text_surf, text_rect)
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(70, 10), 3)'''

    def display_names(self, surface, name, cost, selected):
        #higlight color
        color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR

        #title
        title_surf = self.font.render(name, False, color)
        title_rect = title_surf.get_rect(midtop = self.rect.midtop + pygame.math.Vector2(0, 20))
        pygame.draw.rect(surface, 'black', title_rect.inflate(70, 10))
        surface.blit(title_surf, title_rect)
        pygame.draw.rect(surface, 'red', title_rect.inflate(70, 10), 3)
        
        #cost
        cost_surf = self.font.render(f'{int(cost)}', False, color)
        cost_rect = cost_surf.get_rect(midbottom = self.rect.midbottom + pygame.math.Vector2(0, -20))
        pygame.draw.rect(surface, 'black', cost_rect.inflate(70, 10))
        surface.blit(cost_surf, cost_rect)
        pygame.draw.rect(surface, 'red', cost_rect.inflate(70, 10), 3)

    def trigger(self, player):
        upgrade_attrib = list(player.stats.keys())[self.index]
        max_upgrade_cost = 240

        if player.exp >= list(player.upgrade_costs.values())[self.index]:
            player.stats[upgrade_attrib] *= 1.2
            player.exp -= list(player.upgrade_costs.values())[self.index]
            player.upgrade_costs[upgrade_attrib] *= 1.4
            if player.upgrade_costs[upgrade_attrib] > max_upgrade_cost:
                player.upgrade_costs[upgrade_attrib] = max_upgrade_cost
            if player.stats[upgrade_attrib] > player.max_stats[upgrade_attrib]:
                player.stats[upgrade_attrib] = player.max_stats[upgrade_attrib]


    def display_bar(self, surface, value, max_value, selected):
        #drawing setup
        top = self.rect.midtop + pygame.math.Vector2(0, 60)
        bottom = self.rect.midbottom + pygame.math.Vector2(0, -60)
        color = BAR_COLOR_SELECTED if selected else BAR_COLOR

        #draw line
        pygame.draw.line(surface, color, top, bottom, 5)

        #draw bar
        height = bottom[1] - top[1]
        relative_number = (value / max_value) * height
        bar = pygame.Rect(top[0] - 15, bottom[1] - relative_number, 30, 10)
        pygame.draw.rect(surface, color, bar)


    def draw_item(self, surface, selection_num, name, value, max_value, cost):
        if self.index == selection_num:
            pygame.draw.rect(surface, UPGRADE_BG_COLOR_SELECTED, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        else:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)

        self.display_names(surface, name, cost, self.index == selection_num)
        self.display_bar(surface, value, max_value, self.index == selection_num)