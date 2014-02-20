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

import math

import pygame

from utils import get_res_path
from globals import CLR_WHITE


SECTORS = {
    20: (351, 9),
     1: (9, 27),
    18: (27, 45),
     4: (45, 63),
    13: (63, 81),
     6: (81, 99),
    10: (99, 117),
    15: (117, 135),
     2: (135, 153),
    17: (153, 171),
     3: (171, 189),
    19: (189, 207),
     7: (207, 225),
    16: (225, 243),
     8: (243, 261),
    11: (261, 279),
    14: (279, 297),
     9: (297, 315),
    12: (315, 333),
     5: (333, 351),
}


class Score(object):
    """ Object to help keeping score.
    """

    def __init__(self):
        self.total = 0
        self.drops = []
        self.font = pygame.font.Font(get_res_path('EraserRegular.ttf'), 24)

    def get_multiplier(self, dist):
        """ Returns multiplier for gotten distant 
        """
        if dist < 7 or dist > 78:
            return 0
        elif dist > 43 and dist < 49:
            return 3
        elif dist > 73 and dist < 78:
            return 2
        else:
            return 1

    def keep(self, turn, dart):
        """ Methon to keeping score.

        Gets current turn and dart (position), calculates score and
        put it inside.
        """
        if len(self.drops) == turn:
            self.drops.append(list())
        center = (300, 264)
        pos = dart.get_pos()
        dist = math.hypot(pos[0] - center[0], pos[1] - center[1])
        if turn < 20:
            multiplier = self.get_multiplier(dist)
            angle = math.degrees(
                math.atan2(center[0] - pos[0], pos[1] - center[1])
            )
            angle = angle + 180
            sector = SECTORS[turn + 1]
            if angle > sector[0] and angle < sector[1]:
                score = turn + 1
            elif turn == 19 and (angle > sector[0] or angle < sector[1]):
                score = turn + 1
            else:
                score = 0
            score *= multiplier
        else:
            if dist < 4:
                score = 50
            elif dist < 7:
                score = 25
            else:
                score = 0
        self.drops[turn].append(score)
        self.total += score

    def render(self, surface):
        """ Render scores on gotten surface (surfaca should be 200x600)
        """
        surface.blit(
            self.font.render('Scores:', 1, CLR_WHITE), (10, 10)
        )
        for i in range(len(self.drops)):
            surface.blit(
                self.font.render('%s: ' % (i + 1), 1, CLR_WHITE),
                (10, 40 + 20 * i),
            )
            for j in range(len(self.drops[i])):
                surface.blit(
                    self.font.render(str(self.drops[i][j]), 1, CLR_WHITE),
                    (50 + 40 * j, 40 + 20 * i),
                )
        surface.blit(
            self.font.render('Total: %s' % self.total, 1, CLR_WHITE),
            (10, 500),
        )



