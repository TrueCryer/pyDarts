#!/usr/bin/env python

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

import os
import csv
import pygame

import Tkinter, tkSimpleDialog

from utils import get_res_path, GAME_DIR

from globals import CLR_WHITE


class HiScores(object):

    def __init__(self):
        self.font = pygame.font.Font(get_res_path('EraserRegular.ttf'), 24)
        self.scores = []
        for i in range(10):
            self.scores.append({'name': 'Unknown', 'score': 0})
        self.read()

    def read(self):
        f = open(os.path.join(GAME_DIR, 'scores'), 'r')
        reader = csv.reader(f.readlines())
        while reader.line_num <= 10:
            try:
                line = reader.next()
            except StopIteration:
                break
            self.scores[reader.line_num - 1]['name'] = line[0]
            self.scores[reader.line_num - 1]['score'] = int(line[1])

    def write(self):
        f = open(os.path.join(GAME_DIR, 'scores'), 'w')
        scores = self.scores[:10]
        writer = csv.writer(f)
        for i in scores:
            writer.writerow((i['name'], i['score']))
        f.close()

    def sort(self):
        self.scores.sort(key=lambda scr: scr['score'])
        self.scores.reverse()

    def get_name(self):
        root = Tkinter.Tk()
        root.withdraw()
        return tkSimpleDialog.askstring('New Record!', 'Wow! You made a new record! What is your name?')

    def check_and_save(self, score):
        if score > self.scores[-1]['score']:
            name = self.get_name()
            self.scores.append({'name': name, 'score': score})
            self.sort()
            self.write()

    def render(self, surface):
        surface.blit(
            self.font.render('HI-SCORES:', 1, CLR_WHITE), (10, 80)
        )
        for i in range(len(self.scores)):
            score = self.scores[i]
            surface.blit(
                self.font.render(
                    '%s: %s:' % (i + 1, score['name']),
                    1,
                    CLR_WHITE),
                (10, 110 + 40 * i),
            )
            surface.blit(
                self.font.render(
                    '%s' % score['score'],
                    1,
                    CLR_WHITE,
                ),
                (120, 130 + 40 * i)
            )
