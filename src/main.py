import sys
import time

import keyboard
import numpy as np
from model.opencv_model import ImageFinder
from model.pubg_model import PubgModel
from utils import win_util
import pydirectinput

game = PubgModel()

def on_home_key():
    print("Home key pressed. Exiting...")
    game.end_state = True


if __name__ == "__main__":
    # 监听Home键的按下
    keyboard.add_hotkey('home', on_home_key)

    time.sleep(2)

    game.define_now_state()


    while True:
        try:
            if game.end_state:
                sys.exit()
                
            if game.state == 'no_game':
                game.start_game()

            if game.state == 'lobby':
                game.start_match()

            if game.state == 'mathching':
                game.load()

            if game.state == 'mathching':
                game.nomatch()

            if game.state == 'loading_hall':
                game.mark()

            if game.state == 'loading_hall_ok':
                game.plane()

            if game.state == 'plane':
                game.ground()

            if game.state == 'ground':
                game.radom_action()

            if game.state == 'error':
                game.define_now_state()

            game.end()
            game.error()
            print(f'当前状态: {game.state}')

            time.sleep(2)
        except Exception:
            print('main error')