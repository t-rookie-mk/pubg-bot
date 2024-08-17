import random
import pyautogui
from transitions import Machine
from model.opencv_model import ImageFinder
from utils.pic_util import get_images_map
import utils.win_util as win_util
import pydirectinput
import time
import numpy as np

class PubgModel:

    def __init__(self) -> None:
        states = ['no_game', 'lobby', 'mathching', 'loading_hall', 'loading_hall_ok', 'plane', 'ground', 'end', 'error']
        self.machine = Machine(model=self, states=states, initial='no_game');
        self.machine.add_transition(trigger='start_game', source='no_game', dest='lobby', conditions=['check_lobby'])
        self.machine.add_transition(trigger='start_match', source='lobby', dest='mathching', conditions=['match'])
        self.machine.add_transition(trigger='nomatch', source='mathching', dest='lobby', conditions=['check_no_match'])

        self.machine.add_transition(trigger='load', source='mathching', dest='loading_hall', conditions=['check_loading'])
        self.machine.add_transition(trigger='mark', source='loading_hall', dest='loading_hall_ok', conditions=['check_marking'], prepare=['marking'])
        self.machine.add_transition(trigger='plane', source='loading_hall_ok', dest='plane', conditions=['check_plane'], after='plane_find_pos')
        self.machine.add_transition(trigger='ground', source='plane', dest='ground', conditions=['check_ground'], after='goto_bp')
        
        self.machine.add_transition(trigger='end', source='*', dest='end', conditions=['check_end'], after='return_lobby')

        self.machine.add_transition(trigger='error', source='*', dest='error', conditions=['check_error'], after='mix_error')
        # 获取窗口大小
        self.coord = win_util.get_window_client_area('PUBG：绝地求生 ')

        self.image_finder = ImageFinder(imgopcv=0.8, search_area_percentages=self.coord)
        self.pic_dict = get_images_map()

        self.cesuo_pos = [876, 456, 890, 460, 887, 472, 879, 500]

        self.min_map_area = [1360,660,1570,870]

        self.check_relative_x = (self.coord[2] - self.coord[0]) / 2 + 1;
        self.check_relative_y = 27

        self.running = True

        self.error_image_list = [self.pic_dict['error'], self.pic_dict['error1'], self.pic_dict['error2'], self.pic_dict['error3']]

        pass

    def define_now_state(self):
        if self.check_lobby():
            self.state = 'lobby'
        elif self.check_loading():
            self.state = 'loading_hall'
        elif self.check_plane():
            self.state = 'palne'
        elif self.check_ground():
            self.state = 'ground'

        print(f'当前状态: {self.state}')

    def check_lobby(self) -> bool:
        x, y = self.image_finder.find_image_in_screen(self.pic_dict['at_lobby'])
        return x is not None
    
    def check_no_match(self) -> bool:
        x, y = self.image_finder.find_image_in_screen(self.pic_dict['start_match'])
        return x is not None


    def match(self) -> bool:
        x, y = self.image_finder.find_image_in_screen(self.pic_dict['start_match'])
        if x is None:
            return False
        pydirectinput.moveTo(int(x), int(y), duration=0.5)
        pydirectinput.click()
        time.sleep(1)
        x, y = self.image_finder.find_image_in_screen(self.pic_dict['start_match'])
        return x is None
    
    def check_loading(self) -> bool:
        x, y = self.image_finder.find_image_in_screen(self.pic_dict['loading'])
        return x is not None
    
    def check_end(self) -> bool:
        x, y = self.image_finder.find_any_image_in_screen([self.pic_dict['return1'],
                                                           self.pic_dict['return2'],
                                                           self.pic_dict['return3']])
        return x is not None
    
    def return_lobby(self):
        x, y = self.image_finder.find_any_image_in_screen([self.pic_dict['return1'],
                                                           self.pic_dict['return2'],
                                                           self.pic_dict['return3']])
        if x is None:
            return
        pydirectinput.moveTo(int(x), int(y), duration=0.5)
        pydirectinput.click()
        time.sleep(1)
        self.state='lobby'


    def marking(self):
        # 点位获取
        relative_x = self.cesuo_pos[0]
        relative_y = self.cesuo_pos[1]
        self.mark_map_pos_first(relative_x, relative_y)

        # 切换第一人称
        pydirectinput.press("v")
        
        return

    def check_marking(self) -> bool:
        if self.cur_mark_pos is None:
            return False
        
        pydirectinput.press('m')

        # 点位获取
        relative_x = self.cur_mark_pos[0]
        relative_y = self.cur_mark_pos[1]

        result = self.image_finder.find_color_pos(relative_x, relative_y, range_radius = 10)

        # 关闭地图
        pydirectinput.press("m")
        time.sleep(1)

        return result
    
    def check_plane(self) -> bool:
        x, y = self.image_finder.find_image_in_screen(self.pic_dict['plane'])
        return x is not None
    
    def check_ground(self) -> bool:
        x, y = self.image_finder.find_image_in_screen(self.pic_dict['ground'])
        return x is not None
    
    def check_error(self) -> bool:
        x, y = self.image_finder.find_any_image_in_screen(self.error_image_list, threshold=0.9)
        if x is not None:
            return True
        
        x, y = self.image_finder.find_image_in_screen(self.pic_dict['refresh'])
        return x is not None
    
    def direction_finding(self) -> bool:
        result = self.image_finder.find_color_pos(self.check_relative_x, self.check_relative_y, range_radius=3)
        print(f'direction_finding-firstcheck寻找目标点{result}')
        if result:
            return True

        # 顺时针旋转
        step = 50

        # 先判定附近有没有 快速修正一下
        points = self.image_finder.get_contour_points(relative_area=(549,19,993,33))
        print(f'direction_finding:{points}')
        if points is not None and len(points) == 1:
            move_x = int(points[0][0] - ((self.coord[2] + self.coord[0]) / 2)) * 9
                
            if move_x < 0:
                step = -50
            
            print(f'快速修正{move_x}')

            while abs(move_x) > abs(step):
                pydirectinput.moveRel(step, 0, relative=True,  _pause=False)
                move_x -= step
            

        # 寻找方向
        start_time = time.time()
        while self.running:
            if time.time() - start_time > 15:
                print('寻找目标点失败')
                return False
            
            result = self.image_finder.find_color_pos(self.check_relative_x, self.check_relative_y, range_radius=3)
            print(f'direction_finding寻找目标点{result}')
            if result:
                break
            else:
                pydirectinput.moveRel(step, 0, relative=True, _pause=False)
        return True

    
    def way_finding(self, relative_x, relative_y) -> bool:

        if not self.running:
            return True
        
        # 指定目标点
        self.mark_map_pos_second(relative_x, relative_y)

        start_time = time.time()
        # 检测到点
        while self.running:
            if time.time() - start_time > 60:
                print('way_finding失败')
                return False

            if self.check_end():
                return False

            # 寻找方向
            result = self.direction_finding()
            if not result:
                return False
            
            # 检测小地图距离 没有直接开始跑
            dis = self.get_cur_target_distance(relative_area=self.min_map_area)
            if dis:
                pydirectinput.keyDown('w')
                pydirectinput.keyDown('shift')
                time.sleep(2)
                pydirectinput.keyUp('w')
                pydirectinput.keyUp('shift')
            else:
                pydirectinput.keyDown('w')
                time.sleep(0.5)
                pydirectinput.keyUp('w')

            time.sleep(0.5)


            if not self.image_finder.find_color_pos(self.check_relative_x, self.check_relative_y, range_radius=3):
                print('判断下有没有到')
                # 导航栏没有图标才结束
                if self.check_arrive_pos_way_finding():
                    print('结束寻路')
                    break
        return True

    def pick(self):
        # 开始拾取
        pydirectinput.press('tab')
        pydirectinput.moveTo(150 + self.coord[0], 120 + self.coord[1])

        pydirectinput.rightClick()
        time.sleep(1)
        pydirectinput.rightClick()
        time.sleep(1)
        pydirectinput.rightClick()
        time.sleep(1)

        pydirectinput.press('tab')
    
    def goto_bp(self):
        if not self.running:
            return

        self.map_scroll()

        # 寻路门口
        if not self.way_finding(self.cesuo_pos[6], self.cesuo_pos[7]):
            pydirectinput.keyDown('a')
            time.sleep(5)
            pydirectinput.keyUp('a')
            self.way_finding(self.cesuo_pos[6], self.cesuo_pos[7])
        
        # 寻路厕所
        self.way_finding(self.cesuo_pos[4], self.cesuo_pos[5])

        # 进厕所方向
        self.mark_map_pos_second(self.cesuo_pos[2], self.cesuo_pos[3])
       
        start_time = time.time()
        while self.running:
            if time.time() - start_time > 10:
                print('way_finding失败')
                return False
            
            self.direction_finding()
            pydirectinput.keyDown('w')
            time.sleep(0.3)
            pydirectinput.keyUp('w')

            # 检测开门
            x, y = self.image_finder.find_image_in_screen(self.pic_dict['bp_start'])
            if x is not None:
                pydirectinput.press('f')
                break
        
        # 进厕所
        if self.running:
            pydirectinput.keyDown('w')
            time.sleep(3)
            pydirectinput.keyUp('w')

            # 开始拾取
            self.pick()

            pydirectinput.keyDown('a')
            time.sleep(1)
            pydirectinput.keyUp('a')

            # 开始拾取
            self.pick()

            pydirectinput.keyDown('s')
            time.sleep(1)
            pydirectinput.keyUp('s')
            
            # 转向
            move_x= 4000
            step = 50
            while abs(move_x) > abs(step):
                pydirectinput.moveRel(step, 0, relative=True)
                move_x -= step

            pydirectinput.keyDown('w')
            time.sleep(1)
            pydirectinput.keyUp('w')

            pydirectinput.press('f')

            pydirectinput.keyDown('s')
            time.sleep(1)
            pydirectinput.keyUp('s')


        return
    
    def mix_error(self):
        x, y = self.image_finder.find_image_in_screen(self.pic_dict['refresh'])
        if x is not None:
            # 重启大厅
            pydirectinput.moveTo(int(x), int(y), duration=0.5)
            time.sleep(1)
            pydirectinput.click()
            time.sleep(1)
            pydirectinput.moveTo(150 + self.coord[0], 540 + + self.coord[1])
            time.sleep(1)
            pydirectinput.click()
            time.sleep(1)

        x, y = self.image_finder.find_any_image_in_screen(self.error_image_list, threshold=0.9)
        
        if x is not None:
            pydirectinput.moveTo(int(x), int(y), duration=0.5)
            time.sleep(0.5)
            pydirectinput.click()
            time.sleep(0.5)
    
        
    
    def plane_find_pos(self):
        start_time = time.time()
        # 首先计算可以飞的距离
        print('plane_find_pos 打开地图')
        
        # 打开地图
        while self.running:
            if time.time() - start_time > 10:
                print('打开地图失败')
                return
            x, y = self.image_finder.find_image_in_screen(self.pic_dict['map_ok'])
            if x is None:
                pydirectinput.press('m')
            else:
                break
        
        start_time = time.time()
        min_dis = 100000
        while self.running:
            if time.time() - start_time > 30:
                print('起飞超时')
                return
            dis = self.get_cur_target_distance(relative_area=(350,10,1250,890))
            if dis :
                if dis <= 180 or dis - min_dis > 10:
                    print('可以起飞了')
                    break;
                min_dis = min(min_dis, dis)
            
        
        # 关闭地图
        start_time = time.time()
        print('plane_find_pos 关闭地图')
        while self.running:
            if time.time() - start_time > 10:
                print('关闭地图失败')
                return
            x, y = self.image_finder.find_image_in_screen(self.pic_dict['map_ok'])
            if x is not None:
                pydirectinput.press('m')
                
            else:
                break
        
        self.direction_finding()

        # 跳伞
        pydirectinput.press("f")

         # 向目标点飞行
        pydirectinput.keyDown("ctrl")
        pydirectinput.keyDown("w")

        time.sleep(10)

        self.direction_finding()

        start_time = time.time()
        min_dis = 100000
        while self.running:
            if time.time() - start_time > 120:
                print('飞行到目标超时')
                pydirectinput.press("shift")
                pydirectinput.press("w")
                pydirectinput.press("ctrl")
                pydirectinput.press('a')
                return
            
            dis = self.get_cur_target_distance(relative_area=self.min_map_area)
            if dis:
                if dis < 30:
                    break
                else:
                    # 如果落地了
                    x, y = self.image_finder.find_image_in_screen(self.pic_dict['ground'])
                    if x is not None:
                        pydirectinput.keyUp("ctrl")
                        pydirectinput.keyDown("shift")

                min_dis = min(min_dis, dis)

        pydirectinput.press('f')
        start_time = time.time()
        while self.running:
            if time.time() - start_time > 120:
                print('降落超时')
                pydirectinput.press("shift")
                pydirectinput.press("w")
                pydirectinput.press("ctrl")
                pydirectinput.press('a')
                return
            # 如果没落地
            x, y = self.image_finder.find_image_in_screen(self.pic_dict['ground'])
            if x is None:
                pydirectinput.keyUp('w')
                pydirectinput.keyUp("ctrl")

                pydirectinput.keyDown("shift")
                pydirectinput.keyDown('a')

                time.sleep(1)
            else:
                break
        
        pydirectinput.press("shift")
        pydirectinput.press("w")
        pydirectinput.press("ctrl")
        pydirectinput.press('a')


    def check_arrive_pos_way_finding(self) -> bool:
        # 导航栏
        points = self.image_finder.get_contour_points(relative_area=(549,19,993,33))
        print(f'check_arrive_pos_way_finding:{points}')
        if points is not None and len(points) == 0:
            return True
        return False

    def check_arrive_pos(self, threshold = 20) -> bool:
        # 小地图截图
        dis = self.get_cur_target_distance(relative_area=self.min_map_area)
        if dis and dis < threshold:
            print("已到达目标点")
            return True
        else:
            print("未到达目标点")
            return False


    def get_cur_target_distance(self, relative_area):
        # 小地图截图
        points = self.image_finder.get_contour_points(relative_area)
        if points and len(points) == 2:
            point1 = points[0]
            point2 = points[1]
            # 计算两点之间的距离
            distance = np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
            print(f'{point1}-{point2}当前距离{distance}')
            return distance
        
        return None

    def mark_map_pos_first(self, relative_x, relative_y):

        x = self.coord[0] + relative_x;
        y = self.coord[1] + relative_y;

        self.cur_mark_pos = [relative_x, relative_y]

        pydirectinput.press("m")
        win_util.mouse_scroll_down(30)

        # 清除之前的标记
        pydirectinput.moveTo(self.coord[0] + 500, self.coord[1] + 100)
        time.sleep(0.5)
        pydirectinput.rightClick()
        time.sleep(0.5)
        pydirectinput.rightClick()
        time.sleep(0.5)
        
        pydirectinput.moveTo(x, y)
        pydirectinput.click()
        time.sleep(1)
        # 右键标记目标点
        pydirectinput.rightClick()
        time.sleep(1)
        # 关闭地图
        pydirectinput.press("m")

    def map_scroll(self):
        x = self.coord[0] + self.cur_mark_pos[0];
        y = self.coord[1] + self.cur_mark_pos[1];
    
        pydirectinput.press("m")

        pydirectinput.moveTo(x, y)
        pydirectinput.click()
        # 放大
        win_util.mouse_scroll_up(30)

        pydirectinput.press("m")


    def mark_map_pos_second(self, relative_x, relative_y):
        pydirectinput.press("m")

        # 清除之前的标记
        pydirectinput.moveTo(self.coord[0] + 500, self.coord[1] + 100)
        time.sleep(0.5)
        pydirectinput.rightClick()
        time.sleep(0.5)
        pydirectinput.rightClick()
        time.sleep(0.5)
        

        x = self.coord[0] + relative_x;
        y = self.coord[1] + relative_y;

        pydirectinput.moveTo(x, y)
        pydirectinput.click()
        # 右键标记目标点
        pydirectinput.rightClick()
        time.sleep(1)
        # 关闭地图
        pydirectinput.press("m")

    def mark_pos_action(self):
        result = []
        # 清除点位
        pyautogui.moveTo(int(self.coord[0]) +500, int(self.coord[1] + 100), duration=1)
        time.sleep(1)
        pydirectinput.rightClick()
        time.sleep(1)
        pydirectinput.rightClick()


        time.sleep(1)
        points = self.image_finder.get_contour_points((0,0, 1600,900))

        x = points[0][0]
        y = points[0][1]
        pyautogui.moveTo(x, y, duration=1)
        time.sleep(1)

        print(f'0 : {points[0]}')
        result.extend([x - self.coord[0], y-self.coord[1]])

        time.sleep(1)
        pydirectinput.click()
        win_util.mouse_scroll_up(30)


        time.sleep(1)
        points = self.image_finder.get_contour_points((0,0, 1600,900))
        x = points[0][0]
        y = points[0][1]
        pyautogui.moveTo(x, y, duration=1)
        print(f'1 : {points[0]}')
        result.extend([x - self.coord[0], y - self.coord[1]])

        time.sleep(1)

        pydirectinput.keyDown('s')
        time.sleep(2)
        pydirectinput.keyUp('s')
        time.sleep(1)
        points = self.image_finder.get_contour_points((0,0, 1600,900))
        x = points[0][0]
        y = points[0][1]
        pyautogui.moveTo(x, y, duration=1)
        print(f'3 : {points[0]}')
        result.extend([x - self.coord[0], y-self.coord[1]])


        pydirectinput.keyDown('s')
        time.sleep(5)
        pydirectinput.keyUp('s')
        time.sleep(1)
        points = self.image_finder.get_contour_points((0,0, 1600,900))
        x = points[0][0]
        y = points[0][1]
        pyautogui.moveTo(x, y, duration=1)
        print(f'4 : {points[0]}')
        result.extend([x - self.coord[0], y-self.coord[1]])

        print(f'points:{result}')

    def random_movement(self):
        # 随机选择一个方向键
        direction = random.choice(['w', 'a', 's', 'd'])
        # 随机按下和释放时间
        press_time = random.uniform(0.1, 1.5)
        
        pydirectinput.keyDown(direction)
        time.sleep(press_time)
        pydirectinput.keyUp(direction)

    def random_jump(self):
        # 随机时间内跳跃
        if random.random() > 0.8:  # 20%概率跳跃
            pydirectinput.keyDown('space')
            time.sleep(0.2)
            pydirectinput.keyUp('space')

    def random_shoot(self):
        # 随机瞄准和射击
        if random.random() > 0.9:  # 10%概率射击
            pydirectinput.rightClick()
            time.sleep(random.uniform(0.1, 0.5))
            pydirectinput.rightClick()

    def random_treat(self):
        time.sleep(random.uniform(0.1, 0.5))
        list = ['0', '8', '9', '7']
        pydirectinput.press(random.choice(list))


    def random_look_around(self):
        # 随机移动鼠标以模拟查看四周
        x_move = random.randint(-100, 100)
        y_move = random.randint(-100, 100)
        pydirectinput.moveRel(x_move, y_move, relative=True)

    def radom_action(self):
        actions = [self.random_movement, self.random_jump, self.random_shoot, self.random_look_around]
        action = random.choice(actions)
        action()
        time.sleep(random.uniform(0.5, 1.0))
        self.random_treat()
