import os
import sys
import math
import random

import pygame

from scripts.effects.spark import Spark
from scripts.tilemap import Tilemap
from scripts.utils import load_images, load_spritesheet, Animation
from scripts.effects.clouds import Clouds
from scripts.effects.particle import Particle
from scripts.entities.player import Player
from scripts.entities.enemy import Enemy


class Game:
    def __init__(self):
        pygame.init()

        self.screen_scale = 4

        pygame.display.set_caption("Samurai Game")
        self.screen = pygame.display.set_mode((320 * self.screen_scale, 240 * self.screen_scale))
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.assets = {
            'backgrounds': load_images('backgrounds'),  # Background Image
            'grass': load_images('tiles/grass'),  # Tile Images
            'stone': load_images('tiles/stone'),
            'large_decor': load_images('tiles/large_decor'),
            'decor': load_images('tiles/decor'),
            'clouds': load_images('clouds'),  # Clouds
            'player/idle': Animation(load_spritesheet('entities/player/idle.png', (13, 17), (18, 18), 22), img_dur=6),
            # Player Images
            'player/run': Animation(load_spritesheet('entities/player/run.png', (13, 17), (18, 18), 8), img_dur=3),
            'player/jump': Animation(load_spritesheet('entities/player/jump.png', (13, 17), (18, 18), 1)),
            'player/slide': Animation(load_spritesheet('entities/player/slide.png', (13, 17), (18, 18), 1)),
            'player/wall_slide': Animation(load_spritesheet('entities/player/wall_slide.png', (13, 17), (18, 18), 1)),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),  # Particles
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'enemy/bow': load_spritesheet('entities/enemies/bow.png', (6, 10), (10, 10), 1),
            'enemy/arrow': [
                pygame.transform.scale(load_spritesheet('entities/enemies/bow.png', (7, 1), (7, 7), 1)[0], [19, 2])],
            'enemy/red/idle': Animation(load_spritesheet('entities/enemies/red/idle.png', (13, 17), (18, 18), 16),
                                        img_dur=6),
            'enemy/red/run': Animation(load_spritesheet('entities/enemies/red/run.png', (13, 17), (18, 18), 7),
                                       img_dur=4),
            'enemy/orange/idle': Animation(load_spritesheet('entities/enemies/orange/idle.png', (13, 17), (18, 18), 16),
                                           img_dur=6),
            'enemy/orange/run': Animation(load_spritesheet('entities/enemies/orange/run.png', (13, 17), (18, 18), 7),
                                          img_dur=4),
            'enemy/yellow/idle': Animation(load_spritesheet('entities/enemies/yellow/idle.png', (13, 17), (18, 18), 16),
                                           img_dur=6),
            'enemy/yellow/run': Animation(load_spritesheet('entities/enemies/yellow/run.png', (13, 17), (18, 18), 7),
                                          img_dur=4),
            'enemy/green/idle': Animation(load_spritesheet('entities/enemies/green/idle.png', (13, 17), (18, 18), 16),
                                          img_dur=6),
            'enemy/green/run': Animation(load_spritesheet('entities/enemies/green/run.png', (13, 17), (18, 18), 7),
                                         img_dur=4),
            'enemy/blue/idle': Animation(load_spritesheet('entities/enemies/blue/idle.png', (13, 17), (18, 18), 16),
                                         img_dur=6),
            'enemy/blue/run': Animation(load_spritesheet('entities/enemies/blue/run.png', (13, 17), (18, 18), 7),
                                        img_dur=4),
            'enemy/purple/idle': Animation(load_spritesheet('entities/enemies/purple/idle.png', (13, 17), (18, 18), 16),
                                           img_dur=6),
            'enemy/purple/run': Animation(load_spritesheet('entities/enemies/purple/run.png', (13, 17), (18, 18), 7),
                                          img_dur=4),
        }

        # Getting sound effects and setting volume
        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'stab': pygame.mixer.Sound('data/sfx/stab.wav'),
            'slash': pygame.mixer.Sound('data/sfx/slash.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
        }
        self.sfx['ambience'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.3)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)
        self.sfx['slash'].set_volume(0.4)
        self.sfx['stab'].set_volume(0.5)

        # Setting up player data
        self.player = Player(self, [20, 40], (8, 15))
        self.movement = [False, False]
        self.dead = 0

        # Setting Up Enemies & Projectiles
        self.enemies = []
        self.projectiles = []

        # Tile map Data
        self.tilemap = Tilemap(self, tile_size=16)

        # Getting Current Level
        self.level = 0

        # Current Background
        self.background = self.assets['backgrounds'][0]

        # Clouds
        self.clouds = Clouds(self.assets['clouds'], count=16)

        # Camera Scroll
        self.scroll = [0, 0]

        # Screen Shake for effects
        self.screenshake = 0

        # Particles and Sparks
        self.particles = []
        self.sparks = []

        self.leaf_spawners = []

        self.transition = -30

        # Loading Level
        self.load_level(self.level)

    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        # Setting Background
        self.background = self.assets['backgrounds'][self.tilemap.background]

        # Tree Leaves
        self.leaf_spawners.clear()
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        # Spawning Enemies
        self.enemies.clear()
        self.projectiles.clear()
        for spawner in self.tilemap.extract(
                [('spawners', 0), ('spawners', 1), ('spawners', 2), ('spawners', 3), ('spawners', 4), ('spawners', 5),
                 ('spawners', 6), ('spawners', 7)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self,
                                          random.choice(['red', 'orange', 'yellow', 'green', 'blue', 'purple'])
                                          if spawner['variant'] == 1
                                          else ['red', 'orange', 'yellow', 'green', 'blue', 'purple'][spawner['variant']
                                                                                                      - 2],
                                          spawner['pos'], (8, 15)))
                self.enemies[-1].flip = random.randint(0, 1) == 1

        self.particles = []
        self.sparks = []

        self.player.reset()

        self.transition = -30

        self.screenshake = 0

        self.scroll = [0, 0]
        self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0])
        self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1])

        self.dead = 0

    def run(self):
        pygame.mixer.music.load('data/sfx/music.wav')
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play(-1)

        self.sfx['ambience'].play(-1)

        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.blit(self.background, (0, 0))

            # Getting Camera Scroll
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 20
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 27
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # Updating Screen shake
            self.screenshake = max(0, self.screenshake - 1)

            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(self.transition + 1, 30)
                if self.dead > 40:
                    self.load_level(self.level)

            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('data/maps')) - 1)
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition += 1

            # Updating Background clouds
            self.clouds.update()
            self.clouds.render(self.display_2, render_scroll)

            # Updating and Rendering Tile map
            self.tilemap.render(self.display, offset=render_scroll, optimize_offgrid=True, spawners=False)

            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['enemy/arrow'][0]
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0],
                                        projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(
                            Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0),
                                  2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.sfx['hit'].play()
                        self.dead += 1
                        self.screenshake = max(35, self.screenshake + 35)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center,
                                                           velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                     math.sin(angle + math.pi) * speed * 0.5],
                                                           frame=random.randint(0, 7)))

            # Updating and Rendering Enemies
            for enemy in self.enemies.copy():
                if ((self.player.pos[0] - enemy.pos[0]) ** 2 + (self.player.pos[1] - enemy.pos[1]) ** 2) ** 0.5 <= 310:
                    kill = enemy.update(self.tilemap, (0, 0))
                    enemy.render(self.display, offset=render_scroll)
                    if kill:
                        self.enemies.remove(enemy)

            # Updating & Rendering player
            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)

            # Updating Leaves from trees
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos,
                                                   velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

            # Updating and Rendering Particles / Sparks
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhoette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for pos in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.display_2.blit(display_sillhoette, pos)

            for particle in self.particles.copy():
                if ((self.player.pos[0] - particle.pos[0]) ** 2 + (self.player.pos[1] - particle.pos[1]) ** 2) ** 0.5 <= 310:
                    kill = particle.update()
                    particle.render(self.display, offset=render_scroll)
                    if particle.type == 'leaf':
                        particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                    if kill:
                        self.particles.remove(particle)

            for event in pygame.event.get():
                # Quiting game if window is closed
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Getting Key Down Presses
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_SPACE or event.key == pygame.K_LSHIFT:
                        self.player.dash()
                    if event.key == pygame.K_RSHIFT:
                        if self.player.flip:
                            self.player.slash(self.tilemap, (self.player.rect().center[0] - 15,
                                                             self.player.rect().center[1] + 3))
                        else:
                            self.player.slash(self.tilemap, (self.player.rect().center[0] + 15,
                                                             self.player.rect().center[1] + 3))
                    if event.key == pygame.K_SLASH:
                        if self.player.flip:
                            self.player.stab(self.tilemap, (self.player.rect().center[0] - 15,
                                                            self.player.rect().center[1] + 3))
                        else:
                            self.player.stab(self.tilemap, (self.player.rect().center[0] + 15,
                                                            self.player.rect().center[1] + 3))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_to_player = ((pygame.mouse.get_pos()[0] / self.screen_scale) + self.scroll[0],
                                           (pygame.mouse.get_pos()[1] / self.screen_scale) + self.scroll[1])
                        self.player.slash(self.tilemap, mouse_to_player)
                    if event.button == 3:
                        mouse_to_player = ((pygame.mouse.get_pos()[0] / self.screen_scale) + self.scroll[0],
                                           (pygame.mouse.get_pos()[1] / self.screen_scale) + self.scroll[1])
                        self.player.stab(self.tilemap, mouse_to_player)

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False

            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255),
                                   (self.display.get_width() // 2, self.display.get_height() // 2),
                                   (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            # Bliting images and displaying screenshake
            self.display_2.blit(self.display, (0, 0))

            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2,
                                  random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)
            pygame.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    Game().run()
