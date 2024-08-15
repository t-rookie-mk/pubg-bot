import win32gui
import win32api
import win32con
import time

# 缩放滚轮
def mouse_scroll_up(self, lines=10):
    """
    模拟鼠标向上滚动指定的行数。

    :param lines: 要滚动的行数
    """
    WHEEL_DELTA = 120
    for _ in range(lines):
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, WHEEL_DELTA, 0)
        time.sleep(0.1)

def mouse_scroll_down(self, lines=10):
    """
    模拟鼠标向上滚动指定的行数。

    :param lines: 要滚动的行数
    """
    WHEEL_DELTA = -120
    for _ in range(lines):
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, WHEEL_DELTA, 0)
        time.sleep(0.1)

def get_window_client_area(window_title):
    hwnd = win32gui.FindWindow(None, window_title)  # 通过窗口标题获取窗口句柄
    if hwnd:
        # 获取窗口客户区的左上角和右下角相对屏幕的坐标
        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        
        # 将客户区坐标转换为屏幕坐标
        left, top = win32gui.ClientToScreen(hwnd, (left, top))
        right, bottom = win32gui.ClientToScreen(hwnd, (right, bottom))

        print(f"客户区坐标: 左上角 ({left}, {top}), 右下角 ({right}, {bottom})")
        return left ,top, right, bottom
    else:
        print("窗口未找到")

def get_window_coordinates(window_title):
    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) == window_title:
            rect = win32gui.GetWindowRect(hwnd)
            extra.append((rect[0], rect[1], rect[2], rect[3]))
    
    coordinates = []
    win32gui.EnumWindows(callback, coordinates)
    
    if coordinates:
        return coordinates[0]  # 返回找到的第一个匹配窗口的坐标和大小 (x, y, width, height)
    else:
        return None  # 如果没有找到匹配的窗口，返回 None