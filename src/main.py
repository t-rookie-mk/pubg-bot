import datetime
import sys
import threading
import time

import keyboard
import numpy as np
from model.opencv_model import ImageFinder
from model.pubg_model import PubgModel
from utils import win_util
import pydirectinput



def on_home_key(game: PubgModel):
    keyboard.wait('home')
    print("Home key pressed. Exiting...")
    game.running = False


if __name__ == "__main__":
    game = PubgModel()

    # 监听Home键的按下
    key_listener_thread = threading.Thread(target=on_home_key, args=(game,))
    key_listener_thread.setDaemon(True)
    key_listener_thread.start()

    time.sleep(2)

    game.define_now_state()
    
    while True:
        try:
            if not game.running:
                sys.exit()

            # 获取当前时间
            now = datetime.datetime.now()
            # 定义工作时间范围
            start_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
            end_time = now.replace(hour=17, minute=0, second=0, microsecond=0)

            # # 判断当前时间是否在 10:00 到 17:00 之间
            # if start_time <= now <= end_time:
            #     print("当前时间在 10:00 - 17:00 之间，开始睡眠 10 分钟...")
            #     time.sleep(10 * 60)  # 睡眠 10 分钟（600秒）
            #     print("睡眠结束")
            #     continue
                
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