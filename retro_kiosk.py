import pygame
import time
import subprocess
import fire
import psutil
from lib import runners, timing
from config import locs
from box import Box
from pyautogui import press
from pygame import JOYAXISMOTION, JOYHATMOTION, JOYBUTTONDOWN, JOYBUTTONUP
from random import sample
from glob import glob
from collections import namedtuple
from os.path import basename, join


def handle_buttons(btns):
    btns.something_happened = False
    done = False
    btn_val_map = {'a':0, 'b':1, 'x':2, 'y':3, 'l':4, 'r':5, 'select':6, 'start':7}
    val_btn_map = {v: k for k, v in btn_val_map.items()}
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit ()
            import sys; sys.exit() #meh, it's not exiting nicely, screw it
            done=True
        if event.type in [JOYAXISMOTION, JOYHATMOTION, JOYBUTTONDOWN, JOYBUTTONUP]:
            if event.type == JOYBUTTONDOWN and event.button < 8:
                btn = val_btn_map[event.button]
                btns[btn] = 1
            elif event.type == JOYBUTTONUP and event.button < 8:
                btn = val_btn_map[event.button]
                btns[btn] = 0
            btns.something_happened = True
    init_joysticks()
    return btns, done


def init_joysticks():
    joystick_count = pygame.joystick.get_count()
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()


def turn_it_up_or_down(happened, volume, timings):
    if happened:
        if volume == 'down':
            [press('volumeup') for _ in range(11)]
            volume = 'up'
        timings.last_time_idle = timings.current_time
    else:
        if timings.current_time - timings.last_time_idle > 23 and volume == 'up':
            [press('volumedown') for _ in range(30)]
            volume = 'down'
    return volume, timings


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


def time_to_swap_games(timings):
    been_8_hours_since_change = timings.current_time - timings.last_time_swapped > 60 * 60 * 8
    been_20_mins_since_idle = timings.current_time - timings.last_time_idle > 60 * 20
    between_3_and_5am = 3 < time.localtime().tm_hour < 5
    return been_3_hours_since_change and between_3_and_5am and been_1_min_since_idle


def swap_games(games, game_idx, emulator_process, timings):
    games, game_idx = shuffle_games_if_last_one(games, game_idx)
    old_emulator_process = emulator_process
    game = games[game_idx]
    game_idx += 1
    print('Now playing: ' + game.game_path)
    emulator_process = game.emulator_function(game.game_path)
    time.sleep(1)
    old_emulator_process.terminate()
    timings.last_time_idle = current_time
    timings.last_time_swapped = current_time
    return games, game_idx, emulator_process, timings


def pid_is_running(pid):
    psutil.pid_exists(pid)


def main(seed_game=None):
    pygame.init()
    screen = pygame.display.set_mode([1, 1])
    done = False
    clock = pygame.time.Clock()
    buttons = Box({'something_happened':False, 'a':0, 'b':0, 'x':0, 'y':0, 'l':0, 'r':0, 'select':0, 'start':0})

    pygame.joystick.init()

    [press('volumedown') for _ in range(50)]
    volume = 'down'
    timings = timing.init_timings()
    current_time = time.time()
    last_time_idle = current_time
    last_time_swapped = current_time

    gba_files = glob(join(locs['gba_games'], '*.zip'))
    gbc_files = glob(join(locs['gbc_games'], '*.zip'))
    snes_files = glob(join(locs['snes_games'], '*.zip'))
    games = [Game(gba_file, runners.run_gba_emulator) for gba_file in gba_files]
    games += [Game(gbc_file, runners.run_gba_emulator) for gbc_file in gbc_files]
    games += [Game(snes_file, runners.run_snes_emulator) for snes_file in snes_files]
    games = sample(games, len(games))
    multiplayer_games = [Game(r"C:\Program Files (x86)\Steam\steamapps\common\TowerFall\TowerFall.exe", runners.run_steam_exe_game)]
    game_idx = 1
    emulator_process = start_the_first_game(multiplayer_games, seed_game)

    print('starting... press crtl c to quit')
    while not done:
        time.sleep(.1)
        clock.tick(20)
        timings.current_time = time.time()
        buttons, done = handle_buttons(buttons)
        volume, timings = turn_it_up_or_down(buttons.something_happened, volume, timings)

        if not buttons.something_happened and time_to_swap_games(timings):
            games, game_idx, emulator_process, timings = swap_games(games, game_idx, emulator_process, timings)
        if all([buttons[x] for x in ['something_happened', 'a', 'b', 'l', 'r', 'start']]):
            print('---forcing game override because the last game sucked')
            games, game_idx, emulator_process = swap_games(games, game_idx, emulator_process)
            last_time_swapped = current_time
            time.sleep(2)
            for key in buttons.keys():
                buttons[key] = 0
                buttons.something_happened = False
        elif all([buttons[x] for x in ['something_happened', 'a', 'b', 'l', 'r', 'select']]):
            print('---starting multiplayer')
            _, _, emulator_process = swap_games(multiplayer_games, 0, emulator_process)
            last_time_swapped = current_time
            time.sleep(2)
            for key in buttons.keys():
                buttons[key] = 0
                buttons.something_happened = False
    pygame.quit ()


fire.Fire(main)
