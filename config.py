import time
from os.path import dirname, realpath, join


root = 'games_and_emulators'
root = join(dirname(realpath(__file__)), root)

locs = {
    'gba_emu': join(root, 'mGBA-0.6.0-2017-07-16-win32', 'mGBA.exe'),
    'gba_games': join(root, 'roms', 'gba_roms'),
    'gbc_games': join(root, 'roms', 'gbc_roms'),

    'snes_emu': join(root, 'snes9x', 'snes9x-x64.exe'),
    'snes_games': join(root, 'roms', 'snes_roms'),

