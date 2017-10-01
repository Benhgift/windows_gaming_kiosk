import pygame
import os
import time
import subprocess
import delegator
import fire
from pyautogui import press
from pygame import JOYAXISMOTION, JOYHATMOTION, JOYBUTTONDOWN, JOYBUTTONUP
from random import sample
from glob import glob
from collections import namedtuple


def something_happened(done, clock):
    event_happened = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit ()
            import sys; sys.exit()
            done=True
        if event.type in [JOYAXISMOTION, JOYHATMOTION, JOYBUTTONDOWN, JOYBUTTONUP]:
            event_happened = True
    joystick_count = pygame.joystick.get_count()
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
    clock.tick(20)
    return event_happened, done


def turn_it_up_or_down(happened, volume, last_time, now):
    if happened:
        if volume == 'down':
            [press('volumeup') for _ in range(11)]
            volume = 'up'
        last_time = now
    else:
        if now - last_time > 23 and volume == 'up':
            [press('volumedown') for _ in range(30)]
            volume = 'down'
    return volume, last_time


def run_gba_emulator(game):
    return subprocess.Popen(r'C:\Users\corn8\Desktop\mGBA-0.6.0-2017-07-16-win32\mGBA.exe ' + '"' + game + '"' + ' -f')


def shuffle_games(games):
    return shuffle(games, len(games)), 0


Game = namedtuple('game', 'game_path emulator_function')


def main():
    pygame.init()
    screen = pygame.display.set_mode([1, 1])
    done = False
    clock = pygame.time.Clock()

    pygame.joystick.init()

    [press('volumedown') for _ in range(50)]
    volume = 'down'
    last_time = time.time()

    glob_pattern = os.path.join(r'C:\Users\corn8\Downloads\gba_roms', '*.zip')
    gba_files = sorted(glob(glob_pattern), key=os.path.getctime)
    games = [Game(gba_file, run_gba_emulator) for gba_file in gba_files]
    games = sample(games, len(games))
    game_idx = 1
    game = games[0]
    vba = game.emulator_function(game.game_path)

    print('starting... press crtl c to quit')
    while done==False:
        time.sleep(.1)
        now = time.time()
        happened, done = something_happened(done, clock)
        volume, last_time = turn_it_up_or_down(happened, volume, last_time, now)
        if not happened and now - last_time > 60 * 60 * 3 and 3 < time.localtime().tm_hour < 5:
            if game_idx == len(games):
                games, game_idx = shuffle_games(games)
            vba.terminate()
            time.sleep(1)
            game = games[game_idx]
            game_idx += 1
            print('Now playing: ' + game.game_path)
            vba = game.emulator_function(game.game_path)
            last_time = now


main()
pygame.quit ()
