#!/usr/bin/env python
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

from pygame.locals import QUIT, MOUSEBUTTONDOWN, KEYDOWN, K_ESCAPE

from utils import get_res_path

from dart import Dart
from score import Score
from hiscores import HiScores
from button import Button

from globals import CLR_RED


FPS = 30

IMG_DARTSBOARD = pygame.image.load(get_res_path('dartsboard.png'))
IMG_DARTSBOARD_OFF = pygame.image.load(get_res_path('dartsboard_off.png'))
IMG_CHALKBOARD = pygame.image.load(get_res_path('chalkboard.png'))


class GameInterruptedError(BaseException):
    pass


class GameEscapedError(BaseException):
    pass


class Game(object):

    def __init__(self, screen):
        self.screen = screen
        self.game_surface = pygame.Surface((600, 600), 0, self.screen)
        self.score_surface = pygame.Surface((200, 600), 0, self.screen)
        self.score = Score()

    def play(self):
        pygame.mouse.set_visible(False)
        for i in range(21):
            turn = Turn(
                i,
                self.screen,
                self.game_surface,
                self.score_surface,
                self.score,
            )
            turn.play()
        hiscores = HiScores()
        hiscores.check_and_save(self.score.total)


class Turn(object):

    def __init__(self, turn_number, screen, game_surface, score_surface, score):
        # top-level properties
        self.screen = screen
        self.game_surface = game_surface
        self.score_surface = score_surface
        self.score = score
        # self properties
        self.turn_number = turn_number
        self.active_dart = Dart()
        self.darts_remain = 2  # one is already active
        self.dropped_darts = []
        self.font = pygame.font.Font(get_res_path('EraserRegular.ttf'), 32)
        self.splash_font = pygame.font.Font(
            get_res_path('EraserRegular.ttf'), 52
        )

    def get_turn_name(self):
        if self.turn_number == 20:
            return "Bull's eye"
        else:
            return '%s' % (self.turn_number + 1)

    def play(self):
        clock = pygame.time.Clock()
        # render score
        self.score_surface.blit(IMG_CHALKBOARD, (0, 0))
        self.score.render(self.score_surface)
        # render start splash
        self.game_surface.blit(IMG_DARTSBOARD, (0, 0))
        splash1 = self.splash_font.render(
           'Next target:', 1, CLR_RED
        )
        splash2 = self.splash_font.render(
            '%s' % self.get_turn_name(), 1, CLR_RED
        )
        self.game_surface.blit(splash1, (300 - splash1.get_width() / 2, 200))
        self.game_surface.blit(splash2, (300 - splash2.get_width() / 2, 280))
        self.screen.blit(self.game_surface, (0, 0))
        self.screen.blit(self.score_surface, (600, 0))
        pygame.display.update()
        clock.tick(0.8)
        # turn loop
        while True:
            # pause
            clock.tick(FPS)
            # initial fill
            self.game_surface.blit(IMG_DARTSBOARD, (0, 0))
            # check dropped dart
            if self.active_dart.dropped:
                self.score.keep(self.turn_number, self.active_dart)
                self.dropped_darts.append(self.active_dart)
                if self.darts_remain > 0:
                    self.active_dart = Dart()
                    self.darts_remain -= 1
                    # re-render score cause it changed
                    self.score_surface.blit(IMG_CHALKBOARD, (0, 0))
                    self.score.render(self.score_surface)
                else:
                    break
            # render dropped darts
            for dart in self.dropped_darts:
                dart.render(self.game_surface)
            # handle events
            for e in pygame.event.get():
                if e.type == QUIT:
                    raise GameInterruptedError
                elif e.type == KEYDOWN and e.key == K_ESCAPE:
                    raise GameEscapedError
                elif e.type == MOUSEBUTTONDOWN:
                    self.active_dart.drop()
            # handle and render active dart
            self.active_dart.handle()
            self.active_dart.move()
            self.active_dart.render(self.game_surface)
            # render turn number
            self.game_surface.blit(
                self.font.render('Target: %s' % self.get_turn_name(), 1, CLR_RED),
                (60, 540),
            )
            # draw game surfaces
            self.screen.blit(self.game_surface, (0, 0))
            self.screen.blit(self.score_surface, (600, 0))
            # update
            pygame.display.update()


def main_screen(screen):
    clock = pygame.time.Clock()
    game_surface = pygame.Surface((600, 600), 0, screen)
    score_surface = pygame.Surface((200, 600), 0, screen)
    start_button = Button((180, 430), 'start.png', 'start_covered.png')
    exit_button = Button((420, 430), 'exit.png', 'exit_covered.png')
    hiscores = HiScores()
    while True:
        clock.tick(FPS)
        game_surface.blit(IMG_DARTSBOARD_OFF, (0, 0))
        score_surface.blit(IMG_CHALKBOARD, (0, 0))
        for e in pygame.event.get():
            if e.type == QUIT:
                raise GameInterruptedError
            elif e.type == MOUSEBUTTONDOWN:
                if start_button.covered():
                    return
                if exit_button.covered():
                    raise GameInterruptedError
        start_button.render(game_surface)
        exit_button.render(game_surface)
        hiscores.render(score_surface)
        screen.blit(game_surface, (0, 0))
        screen.blit(score_surface, (600, 0))
        # update
        pygame.display.update()


if __name__ == '__main__':

    pygame.init()

    screen = pygame.display.set_mode((800, 600), 0, 32)
    pygame.display.set_caption('Drunk darts')

    # main loop
    while True:
        pygame.mouse.set_visible(True)
        try:
            main_screen(screen)
            game = Game(screen)
            game.play()
        except GameEscapedError:
            continue
        except GameInterruptedError:
            break

    pygame.quit()
