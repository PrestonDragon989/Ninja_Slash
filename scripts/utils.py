import os

import pygame

BASE_IMG_PATH = 'data/images/'


def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img


def load_images(path, flip=False):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + "/" + img_name))
    if flip:
        images.reverse()
    return images


def load_spritesheet(path, sprite_size=(0, 0), cell_size=(0, 0), sprites=1, flip=False):
    images = []
    spritesheet_image = load_image(path)
    for i in range(sprites):
        images.append(spritesheet_image.subsurface(pygame.Rect(cell_size[0] * i, 0, sprite_size[0], sprite_size[1])))
    if flip:
        images.reverse()
    return images


class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)

    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.img_duration)]