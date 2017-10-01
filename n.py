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


def run_snes_emulator(game):
    return subprocess.Popen(r'C:\Users\corn8\Desktop\snes9x\snes9x-x64.exe ' + '"' + game + '"' + ' -fullscreen')


def shuffle_games(games):
    return sample(games, len(games)), 0


def start_the_first_game(games, seed_game):
    if seed_game:
        for game in games:
            if seed_game in game.game_path.lower():
                return game.emulator_function(game.game_path)
        else:
            return games[0].emulator_function(games[0].game_path)
    else:
        return games[0].emulator_function(games[0].game_path)


Game = namedtuple('game', 'game_path emulator_function')


def main(seed_game=None):
    pygame.init()
    screen = pygame.display.set_mode([1, 1])
    done = False
    clock = pygame.time.Clock()

    pygame.joystick.init()

    [press('volumedown') for _ in range(50)]
    volume = 'down'
    last_time = time.time()

    gba_files = glob(os.path.join(r'C:\Users\corn8\Desktop\roms\gba_roms', '*.zip'))
    gbc_files = glob(os.path.join(r'C:\Users\corn8\Desktop\roms\gbc_roms', '*.zip'))
    snes_files = glob(os.path.join(r'C:\Users\corn8\Desktop\roms\snes_roms', '*.zip'))
    games = [Game(gba_file, run_gba_emulator) for gba_file in gba_files]
    games += [Game(gbc_file, run_gba_emulator) for gbc_file in gbc_files]
    games += [Game(snes_file, run_snes_emulator) for snes_file in snes_files]
    games = sample(games, len(games))
    game_idx = 1
    emulator_process = start_the_first_game(games, seed_game)

    print('starting... press crtl c to quit')
    while done==False:
        time.sleep(.1)
        now = time.time()
        happened, done = something_happened(done, clock)
        volume, last_time = turn_it_up_or_down(happened, volume, last_time, now)
        if not happened and now - last_time > 60 * 60 * 3 and 3 < time.localtime().tm_hour < 5:
            if game_idx == len(games):
                games, game_idx = shuffle_games(games)
            emulator_process.terminate()
            time.sleep(1)
            game = games[game_idx]
            game_idx += 1
            print('Now playing: ' + game.game_path)
            emulator_process = game.emulator_function(game.game_path)
            last_time = now
    pygame.quit ()


fire.Fire(main)
