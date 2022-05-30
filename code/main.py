import pygame, sys
from settings import *
from level import Level

class Game:
    def __init__(self):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Zelda')
        self.clock = pygame.time.Clock()

        self.level = Level()



        #music
        music = pygame.mixer.Sound('audio\main.wav')
        music.set_volume(0.01)
        music.play(loops = -1)

    def run(self):  
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        self.level.toggle_menu()
            if self.level.respawn:
                audio = pygame.mixer.Sound('audio\playerdeath.wav')
                audio.set_volume(0.01)
                num = 1
                fade = pygame.Surface((WIDTH, HEIGHT))
                fade.fill((0, 0, 0))
                for alpha in range(0, 255):
                    while num == 1:
                        audio.play()
                        num -= 1
                    fade.set_alpha(alpha)
                    self.screen.fill((183, 14, 14))
                    self.screen.blit(fade, (0, 0))
                    pygame.display.update()
                
                self.level.__init__()




            self.screen.fill(WATER_COLOR)
            self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()

