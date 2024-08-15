import sys
import time

import keyboard
import numpy as np
from model.opencv_model import ImageFinder
from model.pubg_model import PubgModel
from utils import win_util
import pydirectinput


if __name__ == "__main__":
    game = PubgModel()

    time.sleep(2)

    game.define_now_state()


    while True:
        try:
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
                pydirectinput.press('x')
                pydirectinput.click()
                pydirectinput.press('c')

            if game.state == 'error':
                game.define_now_state()

            game.end()
            game.error()
            print(f'当前状态: {game.state}')

            time.sleep(2)
        except KeyboardInterrupt:
            print("Program terminated by user.")
            sys.exit()

    