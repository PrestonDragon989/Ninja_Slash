import random
import math

import pygame

from scripts.entities.entity import PhysicsEntity
from scripts.effects.particle import Particle


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)

        # Getting Movement / Action Vars
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.time_since_wall_slide = 0
        self.dashing = 0

        self.last_slash = 0
        self.slash_points = []

        # Getting HP and Defense
        self.max_health = 100
        self.health = self.max_health
        self.health_bar_color_phase = 0
        self.defense = 10  # Attack Formula = attack * (100/ (100 + defense))

    def safe_blocks_below(self, tilemap):
        # Getting Points inbetween
        x1, y1 = self.pos[0], self.pos[1] + 144
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
                return True
        return False

    def update(self, tilemap, movement=(0, 0)):
        movement = [movement[0] * 1.4, movement[1] * 1.4]

        super().update(tilemap, movement=movement)

        self.air_time += 1

        if self.air_time > 180:
            if not self.wall_slide and self.time_since_wall_slide <= 0:
                if not self.safe_blocks_below(tilemap):
                    self.game.dead += 1
                    self.game.screenshake = max(35, self.game.screenshake)

        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1

        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.time_since_wall_slide = 121
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')
        self.time_since_wall_slide = max(0, self.time_since_wall_slide - 1)

        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')

        if abs(self.dashing) in {60, 50}:
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(
                    Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(
                Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

        self.last_slash = max(0, self.last_slash - 1)
        if self.last_slash <= 16 and self.slash_points:
            self.slash_points.clear()

    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing) <= 50:
            super().render(surf, offset=offset)

    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.25
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.25
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True

        elif self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5

    def dash(self):
        if not self.dashing:
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60

    def slash(self, tilemap, mouse_pos):
        if not self.last_slash:
            direction_degrees = math.degrees(math.atan2(mouse_pos[1] - (self.pos[1] + 10), mouse_pos[0] - (self.pos[0] + 7))) % 360

            self.slash_points.clear()
            starting_point = self.rect().center
            for i in range(-10, 10):
                # Getting Point and new Direction (Degrees & Radians)
                point = [0, 0]
                new_direction = (direction_degrees + (i * 4.2)) % 360
                direction_radians = math.radians(new_direction)

                # Finding New points based on 26 away
                point[0] = starting_point[0] + 26 * math.cos(direction_radians)
                point[1] = starting_point[1] + 26 * math.sin(direction_radians)

                # Adding to new list, & Creating Particles
                self.slash_points.append(point)
                if tilemap.can_see_point(self.rect().center, point):
                    self.game.particles.append(
                        Particle(self.game, 'particle', point, velocity=(0, 0), frame=random.randint(0, 7)))

            for i in range(-5, 5):
                # Getting Point and new Direction (Degrees & Radians)
                point = [0, 0]
                new_direction = (direction_degrees + (i * 4.2)) % 360
                direction_radians = math.radians(new_direction)

                # Finding New points based on 26 away
                point[0] = starting_point[0] + 12 * math.cos(direction_radians)
                point[1] = starting_point[1] + 12 * math.sin(direction_radians)

                # Adding to new list, & Creating Particles
                self.slash_points.append(point)
            for i in range(-5, 5):
                # Getting Point and new Direction (Degrees & Radians)
                point = [0, 0]
                new_direction = (direction_degrees + (i * 4.2)) % 360
                direction_radians = math.radians(new_direction)

                # Finding New points based on 26 away
                point[0] = starting_point[0] + 3 * math.cos(direction_radians)
                point[1] = starting_point[1] + 3 * math.sin(direction_radians)

                # Adding to new list, & Creating Particles
                self.slash_points.append(point)

            self.last_slash = 20

    def render_health(self, surf):
        surf.blit(self.game.assets['player/background_health'][0], (3, 3))
        if self.health > 0:
            self.game.assets['player/foreground_health'].update()
            current_hp_image = self.game.assets['player/foreground_health'].img().copy()
            surf.blit(pygame.transform.scale(current_hp_image, (
                current_hp_image.get_width() * (self.health / self.max_health), current_hp_image.get_height())), (7, 7))