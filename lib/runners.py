import time
from config import locs
from os.path import basename
from subprocess import Popen
from psutil import process_iter, Process


def run_gba_emulator(game):
    p = Popen(locs['gba_emu'] + ' "' + game + '"' + ' -f')
    return Process(p.pid)


def run_snes_emulator(game):
    p = Popen(locs['snes_emu'] + ' "' + game + '"' + ' -fullscreen')
    return Process(p.pid)



def run_steam_exe_game(game):
    Popen(game)
    time.sleep(1)
    for x in process_iter():
        if basename(game) in x.name():
            return x
