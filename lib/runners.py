from config import locs
from os import join


def run_gba_emulator(game):
    return subprocess.Popen(locs['gba_emu'] + ' "' + game + '"' + ' -f')


def run_snes_emulator(game):
    return subprocess.Popen(locs['snes_emu'] + ' "' + game + '"' + ' -fullscreen')


def run_steam_exe_game(game):
    subprocess.Popen(game)
    time.sleep(1)
    for x in psutil.process_iter():
        if basename(game) in x.name():
            return x
