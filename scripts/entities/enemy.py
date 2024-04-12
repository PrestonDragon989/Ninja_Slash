import random
import math

import pygame

from scripts.entities.entity import PhysicsEntity
from scripts.effects.particle import Particle
from scripts.effects.spark import Spark


class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)

        # Getting AI Info
        self.see_player = False
        self.see_player_timer = 0
        self.last_shot = 0

        self.walking = 0

    def can_see_point(self, point, tilemap):
        # Getting Points inbetween
        x1, y1 = point
        x2, y2 = self.pos
        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        total_time = distance / 15
        ratio = 15 / distance
        points = []
        for t in range(int(total_time) + 1):
            x = x1 + (x2 - x1) * ratio * t
            y = y1 + (y2 - y1) * ratio * t
            points.append((x, y))

        # Checking for blocks
        for point in points:
            if tilemap.solid_check(point):
                return False
        return True

    def can_see_player(self, tilemap, y_range=16):
        distance_from_player = [self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1]]

        if self.flip and 0 > distance_from_player[0] > -128 and abs(distance_from_player[1]) <= y_range:
            return self.can_see_point(self.game.player.pos, tilemap)
        elif not self.flip and 0 < distance_from_player[0] < 128 and abs(distance_from_player[1]) <= y_range:
            return self.can_see_point(self.game.player.pos, tilemap)
        return False

    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if self.collisions['right'] or self.collisions['left']:
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                self.shoot()
        elif random.random() < 0.015:
            self.walking = random.randint(30, 120)

        super().update(tilemap=tilemap, movement=movement)

        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        if random.randint(1, 14500) == 1:
            self.shoot()

        """  if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.screenshake = max(17, self.game.screenshake + 1)
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.game.player.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'particle', self.game.player.rect().center,
                                                        velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                  math.sin(angle + math.pi) * speed * 0.5],
                                                        frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                return True  """

        if self.game.player.last_slash in {20, 14}:
            enemy_rect = self.rect()
            for point in self.game.player.slash_points:
                if enemy_rect.collidepoint(*point):
                    self.die()
                    return True

        if self.game.player.last_stab in {50, 37}:
            enemy_rect = self.rect()
            for point in self.game.player.stab_points:
                if enemy_rect.collidepoint(*point):
                    self.die()
                    return True

    def die(self):
        self.game.sfx['hit'].play()
        enemy_rect = self.rect()
        self.game.screenshake = max(17, self.game.screenshake + 1)
        for i in range(25):
            angle = random.random() * math.pi * 2
            speed = random.random() * 5
            self.game.sparks.append(Spark(enemy_rect.center, angle, 2 + random.random()))
            self.game.particles.append(Particle(self.game, 'particle', enemy_rect.center,
                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                          math.sin(angle + math.pi) * speed * 0.5],
                                                frame=random.randint(0, 7)))
        self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
        self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))

    def shoot(self):
        dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
        if abs(dis[1]) < 16:
            if self.flip and dis[0] < 0:
                self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                self.game.sfx['shoot'].play()
                for i in range(4):
                    self.game.sparks.append(
                        Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
            if not self.flip and dis[0] > 0:
                self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                self.game.sfx['shoot'].play()
                self.game.sparks.append(
                    Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)

        if self.flip:
            surf.blit(pygame.transform.flip(self.game.assets['enemy/bow'][0], True, False), (
                self.rect().centerx - 3 - self.game.assets['enemy/bow'][0].get_width() - offset[0],
                self.rect().centery - offset[1] - 3))
        else:
            surf.blit(self.game.assets['enemy/bow'][0],
                      (self.rect().centerx + 3 - offset[0], self.rect().centery - offset[1] - 3))
