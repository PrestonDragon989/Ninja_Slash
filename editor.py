import sys
import os

import pygame

from tkinter import filedialog

from scripts.utils import load_images, load_spritesheet
from scripts.tilemap import Tilemap

RENDER_SCALE = 4.0  # USED TO BE 2.0


class Editor:
    def __init__(self):
        self.tilemap = Tilemap(self, tile_size=16)

        self.file, contin = self.get_file()
        print(f"Opened file: {self.file}")

        if not contin:
            return
        pygame.init()

        pygame.display.set_caption("editor")
        self.screen = pygame.display.set_mode((1280, 960))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'spawners': load_images('tiles/spawners')
        }
        # Adding the rest of the spawners
        self.assets['spawners'][1] = self.assets['spawners'][1].subsurface(pygame.Rect(3, 2, 9, 16))
        self.assets['spawners'].append(load_spritesheet('entities/enemies/red/idle.png', (18, 18), (18, 18), 1)[0]
                                       .subsurface(pygame.Rect(3, 2, 9, 16)))
        self.assets['spawners'].append(load_spritesheet('entities/enemies/orange/idle.png', (18, 18), (18, 18), 1)[0]
                                       .subsurface(pygame.Rect(3, 2, 9, 16)))
        self.assets['spawners'].append(load_spritesheet('entities/enemies/yellow/idle.png', (18, 18), (18, 18), 1)[0]
                                       .subsurface(pygame.Rect(3, 2, 9, 16)))
        self.assets['spawners'].append(load_spritesheet('entities/enemies/green/idle.png', (18, 18), (18, 18), 1)[0]
                                       .subsurface(pygame.Rect(3, 2, 9, 16)))
        self.assets['spawners'].append(load_spritesheet('entities/enemies/blue/idle.png', (18, 18), (18, 18), 1)[0]
                                       .subsurface(pygame.Rect(3, 2, 9, 16)))
        self.assets['spawners'].append(load_spritesheet('entities/enemies/purple/idle.png', (18, 18), (18, 18), 1)[0]
                                       .subsurface(pygame.Rect(3, 2, 9, 16)))

        self.movement = [False, False, False, False]

        self.backgrounds = load_images('backgrounds')

        self.scroll = [0, 0]

        self.tile_list = list(self.assets)

        self.tile_group = 0
        self.tile_variant = 0

        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True

        self.run()

    def get_file(self):
        file = filedialog.asksaveasfilename(initialdir='data/maps',
                                            title="Select JSON Map", confirmoverwrite=False)
        print(f"Opening {file}")
        try:
            if os.path.exists(file):
                self.tilemap.load(file)
                return file, True
        except TypeError:
            pass
        except KeyError:
            return file, True
        try:
            f = open(file, 'w')
            f.write('{\n\n}')
            f.close()
            print(f"Creating {file}")
            return file, True
        except TypeError or FileNotFoundError:
            return 'N/A', False

    def run(self):
        while True:
            self.display.blit(self.backgrounds[self.tilemap.background], (0, 0))

            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.tilemap.render(self.display, offset=render_scroll, optimize_offgrid=False, spawners=True)

            current_tile_image = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_image.set_alpha(100)

            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size),
                        int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))

            if self.ongrid:
                self.display.blit(current_tile_image, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0],
                                                       tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_image, mpos)

            if self.clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = \
                    {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}
            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1],
                                         tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)

            self.display.blit(current_tile_image, (5, 5))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group],
                                                               'variant': self.tile_variant, 'pos': (mpos[0]
                                                                                                     + self.scroll[0],
                                                                                                     mpos[1] +
                                                                                                     self.scroll[1])})
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(
                                self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(
                                self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_o:
                        self.tilemap.save(self.file)
                        print(f"Saving {self.file}")
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                    if event.key == pygame.K_c:
                        self.tilemap = Tilemap(self, tile_size=16)
                        self.file, null = self.get_file()

                    if event.key == pygame.K_n:
                        self.tilemap.background = (self.tilemap.background - 1) % len(self.backgrounds)
                    if event.key == pygame.K_m:
                        self.tilemap.background = (self.tilemap.background + 1) % len(self.backgrounds)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    Editor()
    print(f"Closing {__file__}")
