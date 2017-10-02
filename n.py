import pygame
import os
import time
import subprocess
import fire
from box import Box
from pyautogui import press
from pygame import JOYAXISMOTION, JOYHATMOTION, JOYBUTTONDOWN, JOYBUTTONUP
from random import sample
from glob import glob
from collections import namedtuple


def handle_buttons(btns):
    btns.something_happened = False
    done = False
    btn_val_map = {'a':0, 'b':1, 'x':2, 'y':3, 'l':4, 'r':5, 'select':6, 'start':7}
    val_btn_map = {v: k for k, v in btn_val_map.items()}
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit ()
            import sys; sys.exit() #meh
            done=True
        if event.type in [JOYAXISMOTION, JOYHATMOTION, JOYBUTTONDOWN, JOYBUTTONUP]:
            if event.type == JOYBUTTONDOWN and event.button < 8:
                btn = val_btn_map[event.button]
                btns[btn] = 1
            elif event.type == JOYBUTTONUP and event.button < 8:
                btn = val_btn_map[event.button]
                btns[btn] = 0
            btns.something_happened = True
    joystick_count = pygame.joystick.get_count()
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
    return btns, done


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


def shuffle_games_if_last_one(games, game_idx):
    if game_idx == len(games):
        return sample(games, len(games)), 0
    else:
        return games, game_idx


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


def time_to_swap_games(now, last_time):
    return now - last_time > 60 * 60 * 3 and 3 < time.localtime().tm_hour < 5


def swap_games(games, game_idx, emulator_process):
    games, game_idx = shuffle_games_if_last_one(games, game_idx)
    old_emulator_process = emulator_process
    game = games[game_idx]
    game_idx += 1
    print('Now playing: ' + game.game_path)
    emulator_process = game.emulator_function(game.game_path)
    time.sleep(1.5)
    old_emulator_process.terminate()
    return games, game_idx, emulator_process


def main(seed_game=None):
    pygame.init()
    screen = pygame.display.set_mode([1, 1])
    done = False
    clock = pygame.time.Clock()
    buttons = Box({'something_happened':False, 'a':0, 'b':0, 'x':0, 'y':0, 'l':0, 'r':0, 'select':0, 'start':0})

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
        clock.tick(20)
        now = time.time()
        buttons, done = handle_buttons(buttons)
        volume, last_time = turn_it_up_or_down(buttons.something_happened, volume, last_time, now)
        if not buttons.something_happened and time_to_swap_games(now, last_time):
            games, game_idx, emulator_process = swap_games(games, game_idx, emulator_process)
            last_time = now
        if all(buttons.values()):
            print('---forcing game override because the last game sucked')
            games, game_idx, emulator_process = swap_games(games, game_idx, emulator_process)
            for key in buttons.keys():
                buttons[key] = 0
                buttons.something_happened = False
    pygame.quit ()


fire.Fire(main)
