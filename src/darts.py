#!/usr/bin/env python
import os
import csv
import math
import random
import pygame
import Tkinter, tkSimpleDialog
from pygame.locals import QUIT, MOUSEBUTTONDOWN, KEYDOWN, K_ESCAPE


GAME_DIR = ''

IN_GAME = 0
IN_FLY = 1
DROPPED = 2

FPS = 100

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


def get_res_path(name):
    return os.path.join(GAME_DIR, 'share', name)

IMG_DART = pygame.image.load(get_res_path('dart.png'))
IMG_DART_DROPPED = pygame.image.load(get_res_path('dart_dropped.png'))
IMG_DARTSBOARD = pygame.image.load(get_res_path('dartsboard.png'))
IMG_DARTSBOARD_OFF = pygame.image.load(get_res_path('dartsboard_off.png'))
IMG_CHALKBOARD = pygame.image.load(get_res_path('chalkboard.png'))

WHITE = (255, 255, 255)
RED = (255, 0, 0)


class GameInterruptedError(BaseException):
    pass


class GameEscapedError(BaseException):
    pass


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


class Dart(pygame.sprite.Sprite):

    def __init__(self):
        self.image = IMG_DART
        self.base = (0, 0)
        self.loc = (0., 0.)
        self.radius = 30
        self.path = []
        self.status = IN_GAME
        self.fly_frame = 0

    def make_new_path(self):
        dest = random.choice(
            ((20., 0.), (-20., 0.), (0., 20.), (0., -20.),
             (-16., 12.), (-12., 16.), (16., 12.), (12., 16.),
             (16., -12.), (12., -16.), (-16., -12.), (-12., -16.),)
        )
        length = (dest[0] - self.loc[0], dest[1] - self.loc[1])
        self.path = []
        step = FPS * 3 / 5
        for i in range(step):
            self.path.append(
                (
                    self.loc[0] + length[0] * i / step,
                    self.loc[1] + length[1] * i / step,
                )
            )
        self.path.append(dest)
        self.path.reverse()

    @property
    def dropped(self):
        if self.status == DROPPED:
            return True
        return False

    def drop(self):
        if self.status == IN_GAME:
            self.status = IN_FLY

    def handle(self):
        if self.status == IN_GAME:
            self.base = pygame.mouse.get_pos()

    def move(self):
        if self.status == IN_GAME:
            if len(self.path) == 0:
                self.make_new_path()
            self.loc = self.path.pop()
        elif self.status == IN_FLY:
            self.fly_frame += 1
            self.image = IMG_DART_DROPPED
            if self.fly_frame == 25:
                self.status = DROPPED

    def render(self, surface):
        self.rect = self.image.get_rect()
        if self.status == IN_GAME:
            self.rect.left = self.base[0] + self.loc[0]
            self.rect.top = self.base[1] + self.loc[1]
        else:
            self.rect.left = self.base[0] + self.loc[0]
            self.rect.bottom = self.base[1] + self.loc[1]
        surface.blit(self.image, (self.rect.x, self.rect.y))

    def get_pos(self):
        return (self.base[0] + self.loc[0], self.base[1] + self.loc[1])


class Score(object):

    def __init__(self):
        self.total = 0
        self.drops = []
        self.font = pygame.font.Font(get_res_path('EraserRegular.ttf'), 24)

    def keep(self, turn, dart):
        if len(self.drops) == turn:
            self.drops.append(list())
        center = (300, 264)
        pos = dart.get_pos()
        dist = math.hypot(pos[0] - center[0], pos[1] - center[1])
        if turn < 20:
            if dist < 7 or dist > 78:
                multiplier = 0
            elif dist > 43 and dist < 49:
                multiplier = 3
            elif dist > 73 and dist < 78:
                multiplier = 2
            else:
                multiplier = 1
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
        surface.blit(
            self.font.render('Scores:', 1, WHITE), (10, 10)
        )
        for i in range(len(self.drops)):
            surface.blit(
                self.font.render('%s: ' % (i + 1), 1, WHITE),
                (10, 40 + 20 * i),
            )
            for j in range(len(self.drops[i])):
                surface.blit(
                    self.font.render(str(self.drops[i][j]), 1, WHITE),
                    (50 + 40 * j, 40 + 20 * i),
                )
        surface.blit(
            self.font.render('Total: %s' % self.total, 1, WHITE),
            (10, 500),
        )


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
        print hiscores.scores
        hiscores.check_and_save(self.score.total)
        print hiscores.scores


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

    def play(self):
        clock = pygame.time.Clock()
        # turn loop
        while True:
            # pause
            time = clock.tick(FPS)
            # initial fill
            self.game_surface.blit(IMG_DARTSBOARD, (0, 0))
            self.score_surface.blit(IMG_CHALKBOARD, (0, 0))
            # check dropped dart
            if self.active_dart.dropped:
                self.score.keep(self.turn_number, self.active_dart)
                self.dropped_darts.append(self.active_dart)
                if self.darts_remain > 0:
                    self.active_dart = Dart()
                    self.darts_remain -= 1
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
            if self.turn_number == 20:
                tgt = "Bull's eye"
            else:
                tgt = '%s' % (self.turn_number + 1)
            self.game_surface.blit(
                self.font.render('Target: %s' % tgt, 1, RED),
                (20, 20),
            )
            # render score
            self.score.render(self.score_surface)
            # draw game surfaces
            self.screen.blit(self.game_surface, (0, 0))
            self.screen.blit(self.score_surface, (600, 0))
            # update
            pygame.display.update()


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
            self.font.render('HI-SCORES:', 1, WHITE), (10, 80)
        )
        for i in range(len(self.scores)):
            score = self.scores[i]
            surface.blit(
                self.font.render(
                    '%s: %s:' % (i + 1, score['name']),
                    1,
                    WHITE),
                (10, 110 + 40 * i),
            )
            surface.blit(
                self.font.render(
                    '%s' % score['score'],
                    1,
                    WHITE,
                ),
                (120, 130 + 40 * i)
            )


def main_screen(screen):
    clock = pygame.time.Clock()
    game_surface = pygame.Surface((600, 600), 0, screen)
    score_surface = pygame.Surface((200, 600), 0, screen)
    start_button = Button((180, 430), 'start.png', 'start_covered.png')
    exit_button = Button((420, 430), 'exit.png', 'exit_covered.png')
    hiscores = HiScores()
    while True:
        time = clock.tick(FPS)
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


def select_difficulty(screen):
    return 1


if __name__ == '__main__':

    pygame.init()

    screen = pygame.display.set_mode((800, 600), 0, 32)
    pygame.display.set_caption('Drunk darts')

    # main loop
    while True:
        pygame.mouse.set_visible(True)
        try:
            main_screen(screen)
            difficulty = select_difficulty(screen)
            game = Game(screen)
            game.play()
        except GameEscapedError:
            continue
        except GameInterruptedError:
            break

    pygame.quit()
