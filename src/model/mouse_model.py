import ctypes
from ctypes import wintypes
import time

import pydirectinput
from entity.mouse_instruct import MouseInstruct
from utils.win_util import mouse_scroll_up, mouse_scroll_down


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


def get_mouse_position():
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


class WindowApiMouse:

    def __init__(self):
        pass

    def move(self, x: int, y: int):
        """Move the mouse cursor by x and y."""
        pydirectinput.moveRel(x, y, _pause=False, relative=True)

    # 缩放滚轮
    def scroll(self, lines=10):
        if lines > 0:
            mouse_scroll_up(lines)
        else:
            mouse_scroll_down(lines)

    def move_to(self, x: int, y: int):
        pydirectinput.moveTo(x, y, _pause=False, relative=True)

    def click(self, button: int = 1):
        """Click the specified mouse button."""
        if button == 1:
            pydirectinput.leftClick(_pause=False)
        else:
            pydirectinput.rightClick(_pause=False)


class HIDMouse:

    def __init__(self, vid=0x046D, pid=0xC08B, ping_code=0xf9) -> None:
        self.mouse = MouseInstruct.getMouse(vid, pid, ping_code)
        pass

    def move(self, x: int, y: int):
        """Move the mouse cursor by x and y."""
        self.mouse.move(x, y)

    # 缩放滚轮
    def scroll(self, lines=10):
        WHEEL_DELTA = 120 if lines > 0 else -120
        for _ in range(abs(lines)):
            self.mouse.move(0, 0, WHEEL_DELTA)
            time.sleep(0.1)

    def move_to(self, x: int, y: int):
        """Move the mouse cursor by x and y."""
        cur_x, cur_y = get_mouse_position()
        self.mouse.move(x - cur_x, y - cur_y)

    def click(self, button: int = 1):
        """Click the specified mouse button."""
        self.mouse.click(button)
