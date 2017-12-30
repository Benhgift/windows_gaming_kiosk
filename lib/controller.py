import pygame
from pygame import JOYAXISMOTION, JOYHATMOTION, JOYBUTTONDOWN, JOYBUTTONUP


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
    return btns, done


def init_joysticks():
    joystick_count = pygame.joystick.get_count()
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
