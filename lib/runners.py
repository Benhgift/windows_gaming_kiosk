import time
from config import locs
from os.path import basename
from subprocess import Popen
from psutil import process_iter


def run_gba_emulator(game):
    return Popen(locs['gba_emu'] + ' "' + game + '"' + ' -f')


def run_snes_emulator(game):
    return Popen(locs['snes_emu'] + ' "' + game + '"' + ' -fullscreen')


def run_steam_exe_game(game):
    Popen(game)
    time.sleep(1)
    for x in process_iter():
        if basename(game) in x.name():
            return x
