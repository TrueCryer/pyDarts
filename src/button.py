# -*- coding: utf-8 -*-

"""  pyDarts. Drunk darts written on Python and PyGame
     Copyright (C) 2014  Sergey Ozerov aka TrueCryer

  This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

  This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>. """

import pygame
from utils import get_res_path


class Button(pygame.sprite.Sprite):

    def __init__(self, loc, image_master, image_covered):
        self.image_master = pygame.image.load(get_res_path(image_master))
        self.image_covered = pygame.image.load(get_res_path(image_covered))
        self.image = self.image_master
        self.loc = loc
        self.rect = self.image.get_rect()
        self.rect.center = self.loc

    def render(self, surface):
        if self.covered():
            self.image = self.image_covered
        else:
            self.image = self.image_master
        self.rect = self.image.get_rect()
        self.rect.center = self.loc
        surface.blit(self.image, (self.rect.x, self.rect.y))

    def covered(self):
        pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(pos)
