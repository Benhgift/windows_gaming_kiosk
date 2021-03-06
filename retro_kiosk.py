import pygame
import time
import subprocess
import fire
import psutil
from lib import runners, timing, controller
from config import locs
from box import Box
from pyautogui import press
from random import sample
from glob import glob
from collections import namedtuple
from os.path import basename, join


def pause_or_resume_game(happened, game_paused, timings, running_game):
    if happened:
        if game_paused:
            running_game.game_process.resume()
            game_paused = False
    else:
        if not game_paused and timings.current_time - timings.last_time_idle > 600:
            running_game.game_process.suspend()
            game_paused = True
    return game_paused


def turn_it_up_or_down(happened, volume, timings):
    if happened:
        if volume == 'down':
            [press('volumeup') for _ in range(11)]
            volume = 'up'
    else:
        if timings.current_time - timings.last_time_idle > 30 and volume == 'up':
            [press('volumedown') for _ in range(30)]
            volume = 'down'
    return volume


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


def swap_games(running_game, timings, buttons):
    games, game_idx, emulator_process = running_game.games, running_game.game_idx, running_game.game_process
    print('---forcing override')
    games, game_idx = shuffle_games_if_last_one(games, game_idx)
    old_emulator_process = emulator_process
    game = games[game_idx]
    game_idx += 1
    print('Now playing: ' + game.game_path)
    emulator_process = game.emulator_function(game.game_path)
    time.sleep(1)
    try:
        old_emulator_process.terminate()
    except:
        print('===couldn\'t find the game')
    timings.last_time_idle = timings.current_time
    timings.last_time_swapped = timings.current_time
    for key in buttons.keys():
        buttons[key] = 0
        buttons.something_happened = False
    running_game.games = games
    running_game.game_idx = game_idx
    running_game.game_process = emulator_process
    return running_game, timings, buttons


def pid_is_running(pid):
    psutil.pid_exists(pid)


def main(seed_game=None):
    pygame.init()
    screen = pygame.display.set_mode([1, 1])
    done = False
    clock = pygame.time.Clock()
    buttons = Box({'something_happened':False, 'a':0, 'b':0, 'x':0, 'y':0, 'l':0, 'r':0, 'select':0, 'start':0})

    controller.init_joysticks()

    [press('volumedown') for _ in range(50)]
    volume = 'down'
    game_paused = False
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
    emulator_process = start_the_first_game(games, seed_game)
    running_game = Box({'games': games, 'game_idx': 1, 'game_process': emulator_process})

    print('starting... press crtl c to quit')
    loop_num = 1
    while not done:
        clock.tick(15)
        timings.current_time = time.time()
        buttons, done = controller.handle_buttons(buttons)
        volume = turn_it_up_or_down(buttons.something_happened, volume, timings)
        game_paused = pause_or_resume_game(buttons.something_happened, game_paused, timings, running_game)

        if not buttons.something_happened and timing.time_to_swap_games(timings):
            running_game, timings, buttons = swap_games(running_game, timings, buttons)
        if all([buttons[x] for x in ['something_happened', 'a', 'b', 'l', 'r', 'start']]):
            running_game, timings, buttons = swap_games(running_game, timings, buttons)
        elif all([buttons[x] for x in ['something_happened', 'a', 'b', 'l', 'r', 'select']]):
            running_game_temp = Box({'games': multiplayer_games, 'game_idx': 0, 'game_process': running_game.game_process})
            running_game_temp, timings, buttons = swap_games(running_game_temp, timings, buttons)
            running_game.game_process = running_game_temp.game_process
        loop_num += 1
        if buttons.something_happened:
            timings.last_time_idle = timings.current_time
        if loop_num > 90000: 
            loop_num = 1
    pygame.quit ()


fire.Fire(main)
