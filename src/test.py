# 计算截取区域的坐标
import os
import time
import cv2
import numpy as np
import pyautogui
import pydirectinput

from model.pubg_model import PubgModel

print(os.getcwd())  # 打印当前工作目录

from model.opencv_model import ImageFinder
from utils import win_util
from model.mouse_model import HIDMouse


time.sleep(2)


# # 获取窗口大小
# coord = win_util.get_window_client_area('PUBG：绝地求生 ')

# if coord:
#     image_finder = ImageFinder(imgopcv=0.8, search_area_percentages=coord)

#     left = int(coord[0])
#     top = int(coord[1])
#     right = int(coord[2])
#     bottom = int(coord[3])

model = PubgModel()

# 转向
move_x = 2000
step = 50
while abs(move_x) > abs(step):
    model.mouse.move(step, 0)
    time.sleep(0.1)
    move_x -= step

# model.mouse.move(-100, -100)
# model.mouse.click()

# model.marking()

# model.goto_bp()
# model.map_scroll()
# # 指定目标点
# model.mark_map_pos_second(model.cesuo_pos[6], model.cesuo_pos[7])
# # 指定目标点
# model.mark_map_pos_second(model.cesuo_pos[4], model.cesuo_pos[5])

# model.end()

# pydirectinput.moveRel(100, 0, relative=True, _pause=False)

# move_x= 4000
# step = 50
# while abs(move_x) > abs(step):
#     pydirectinput.moveRel(step, 0, relative=True, _pause=False)
#     move_x -= step

# model.direction_finding()
# while True:
#     dis = image_finder.get_contour_points(relative_area=(549,19,993,33))
#     print(dis)



# model.mark_pos_action()

# x, y = image_finder.find_image_in_screen(model.pic_dict['ground'])

# model.cesuo_pos = [876, 456, 890, 460, 887, 472, 879, 500]
# # model.check_arrive_pos_way_finding()
# model.marking()
# model.goto_bp()
