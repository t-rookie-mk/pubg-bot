import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
import pyautogui


class ImageFinder:
    def __init__(self, imgopcv, search_area_percentages=(0, 0, 1920, 1080)):
        self.imgopcv = imgopcv
        self.search_area_percentages = search_area_percentages
        self.screen_width, self.screen_height = pyautogui.size()
        self.is_debug = False


    def get_contour_points(self, relative_area, hsv_lower=(10, 160, 172), hsv_upper=(66, 237, 251), area_threshold=50):
        try:
            # 计算截取区域的坐标
            left = int(self.search_area_percentages[0]) + relative_area[0]
            top = int(self.search_area_percentages[1]) + relative_area[1]

            # 截取屏幕图像的特定区域
            screenshot = pyautogui.screenshot(
                region=(left, top, relative_area[2] - relative_area[0], relative_area[3] - relative_area[1])
            )

            screen_np = np.array(screenshot)

            bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2HSV)
            mask = cv2.inRange(bgr, hsv_lower, hsv_upper)

            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.dilate(mask, kernel, iterations=1)

            if self.is_debug:
                cv2.imshow('test2', mask)
                cv2.waitKey(1)

            # 查找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            points = []
            for contour in contours:
                area = cv2.contourArea(contour)
                # print(f'面积大小{area}')
                if area < area_threshold:
                    continue
                # 计算每个轮廓的中心点
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    points.append((cx + left, cy + top))

            return points
        except Exception as e:
            print(f"An error occurred: {e}")
            return None



    # 相对于某个坐标系的屏幕截取
    def find_image_in_screen(self, image_path):
        try:
            # 计算截取区域的坐标
            left = int(self.search_area_percentages[0])
            top = int(self.search_area_percentages[1])
            right = int(self.search_area_percentages[2])
            bottom = int(self.search_area_percentages[3])

            # 截取屏幕图像的特定区域
            screenshot = pyautogui.screenshot(
                region=(left, top, right - left, bottom - top)
            )
            screen_np = np.array(screenshot)
            img_rgb = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
            template = cv2.imdecode(
                np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE
            )
            if template is None:
                print(
                    f"Error loading image '{image_path}'. Check the file path and integrity."
                )
                return None
            w, h = template.shape[::-1]

            # 将屏幕图像转换为灰度图
            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

            # 模板匹配
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

            # 设定匹配阈值
            threshold = self.imgopcv
            loc = np.where(res >= threshold)

            # 寻找最佳匹配位置
            if len(loc[0]) > 0:
                # 找到最大值的索引
                pt = np.unravel_index(
                    res.argmax(), res.shape
                )  # 使用 argmax 找到最大值的索引

                # 计算匹配区域的中心点坐标
                center_point = (
                    pt[1] + w / 2 + left,
                    pt[0] + h / 2 + top,
                )  # pt[1] 是列索引，pt[0] 是行索引
                return center_point
            # 如果没有找到匹配，则返回None
            return (None, None)
        except Exception as e:
            print(f"An error occurred: {e}")
            return (None, None)

    def find_any_image_in_screen(self, image_paths, threshold=0.9):
        try:
            # 计算截取区域的坐标
            left = int(self.search_area_percentages[0])
            top = int(self.search_area_percentages[1])
            right = int(self.search_area_percentages[2])
            bottom = int(self.search_area_percentages[3])

            # 截取屏幕图像的特定区域
            screenshot = pyautogui.screenshot(
                region=(left, top, right - left, bottom - top)
            )
            screen_np = np.array(screenshot)
            img_rgb = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

            for image_path in image_paths:
                template = cv2.imdecode(
                    np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE
                )
                if template is None:
                    print(
                        f"Error loading image '{image_path}'. Check the file path and integrity."
                    )
                    continue
                w, h = template.shape[::-1]

                # 模板匹配
                res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

                # 设定匹配阈值
                threshold = max(threshold, self.imgopcv)
                loc = np.where(res >= threshold)

                # 寻找最佳匹配位置
                if len(loc[0]) > 0:
                    # 找到最大值的索引
                    pt = np.unravel_index(
                        res.argmax(), res.shape
                    )

                    # 计算匹配区域的中心点坐标
                    center_point = (
                        pt[1] + w / 2 + left,
                        pt[0] + h / 2 + top,
                    )
                    # print(f"Image found at {center_point}")
                    return center_point

            # 如果没有找到任何匹配的图像，则返回False
            return (None, None)
        except Exception as e:
            print(f"An error occurred: {e}")
            return (None, None)

    # 相对于整个屏幕的屏幕截取
    def find_image_all(self, image_path):
        try:
            # 截取屏幕图像
            screenshot = pyautogui.screenshot()
            screen_np = np.array(screenshot)
            img_rgb = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
            # 读取目标图片并转换为灰度图
            image_path = f"{image_path}"
            template = cv2.imdecode(
                np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE
            )
            if template is None:
                print(
                    f"Error loading image '{image_path}'. Check the file path and integrity."
                )
                return None
            w, h = template.shape[::-1]
            # 将屏幕图像转换为灰度图
            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
            # 模板匹配
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            # 设定匹配阈值
            threshold = self.imgopcv
            loc = np.where(res >= threshold)
            # 寻找最佳匹配位置
            if len(loc[0]) > 0:
                # 找到最大值的索引
                pt = np.unravel_index(
                    res.argmax(), res.shape
                )  # 使用 argmax 找到最大值的索引

                # 计算匹配区域的中心点坐标
                center_point = (
                    pt[1] + w / 2,
                    pt[0] + h / 2,
                )  # pt[1] 是列索引，pt[0] 是行索引
                return center_point
            # 如果没有找到匹配，则返回None
            return (None, None)
        except Exception as e:
            print(f"An error occurred: {e}")
            return (None, None)

    # 相对于整个屏幕截取找多张图
    def find_images_all(self, image_paths):
        try:
            # 计算截取区域的坐标
            left = int(self.search_area_percentages[0])
            top = int(self.search_area_percentages[1])
            right = int(self.search_area_percentages[2])
            bottom = int(self.search_area_percentages[3])
            # 截取屏幕图像的特定区域
            screenshot = pyautogui.screenshot(
                region=(left, top, right - left, bottom - top)
            )
            screen_np = np.array(screenshot)
            img_rgb = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

            # 循环遍历提供的图片路径列表
            for image_path in image_paths:
                # image_path = plt.imread(image_path)
                # 读取目标图片并转换为灰度图
                image_path = f"{image_path}"
                template = cv2.imdecode(
                    np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE
                )
                if template is None:
                    print(
                        f"Error loading image '{image_path}'. Check the file path and integrity."
                    )
                    continue  # 如果图片加载失败，跳过这张图片

                w, h = template.shape[::-1]  # 获取图片的宽度和高度

                # 将屏幕图像转换为灰度图
                img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

                # 模板匹配
                res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

                # 设定匹配阈值
                threshold = self.imgopcv
                loc = np.where(res >= threshold)

                # 寻找最佳匹配位置
                if len(loc[0]) > 0:
                    # 找到最大值的索引
                    pt = np.unravel_index(res.argmax(), res.shape)

                    # 计算匹配区域的中心点坐标
                    center_point = (pt[1] + w // 2, pt[0] + h // 2)
                    return center_point  # 返回第一张找到的图片的中心点坐标

            # 如果没有找到匹配，则返回None
            return (None, None)
        except Exception as e:
            print(f"An error occurred: {e}")
            return (None, None)

    def find_color_pos(self, realative_x, realative_y, intervals=[(10, 66), (169, 237), (172, 251)], range_radius=5) -> bool:
        try:
            x = int(realative_x)
            y = int(realative_y)

            # x 方向固定，y 方向基于 range_radius 调整
            left = int(self.search_area_percentages[0]) + x
            right = left + 1  # x 方向只包含单个像素列

            if range_radius > 0:
                top = max(int(self.search_area_percentages[1]) + y - range_radius, 0)
                bottom = min(int(self.search_area_percentages[1]) + y + range_radius, int(self.search_area_percentages[3]))
            else:
                # 如果 range_radius 为 0，直接检查单个像素点
                top = int(self.search_area_percentages[1]) + y
                bottom = top + 1

            # 截取屏幕图像的特定区域，只包含 x 列和 y 范围
            screenshot = pyautogui.screenshot(
                region=(left, top, right - left, bottom - top)
            )
            screen_np = np.array(screenshot)
            img_rgb = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
            if self.is_debug:
                cv2.imshow('test1', img_rgb)
                cv2.waitKey(1)

            if img_rgb is not None:
                # 在指定范围内遍历 y 方向上的像素
                for i in range(img_rgb.shape[0]):  # y 方向范围
                    color = img_rgb[i, 0]  # 这里的 j 固定为 0，因为我们只截取了单列
                    match = True
                    for k, value in enumerate(color):
                        if not (intervals[k][0] <= value <= intervals[k][1]):
                            match = False
                            break
                    if match:
                        return True

                return False
            else:
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
