import struct
import time
import hid

MOUSE_LEFT = 1
MOUSE_RIGHT = 2
MOUSE_MIDDLE = 4
MOUSE_ALL = MOUSE_LEFT | MOUSE_RIGHT | MOUSE_MIDDLE

def check_ping(dev, ping_code):
    dev.write([0, ping_code])
    try:
        resp = dev.read(max_length = 1, timeout_ms = 100)
    except OSError as e:
        return False
    else:
        return resp and resp[0] == ping_code

def find_mouse_device(vid, pid, ping_code):
    dev = hid.device()
    for dev_info in hid.enumerate(vid, pid):
        dev.open_path(dev_info['path'])
        found = check_ping(dev, ping_code)
        if found:
            return dev
        else:
            dev.close()
    return None

def limit_xy(xy):
    if xy < -32767:
        return -32767
    elif xy > 32767:
        return 32767
    else: return xy

def limit_byte(offset):
    if offset > 127:
        return 127
    elif offset < -127:
        return -127
    else:
        return offset

def low_byte(x):
    return x & 0xFF

def high_byte(x):
    return (x >> 8) & 0xFF

class MouseInstruct:
    def __init__(self, dev):
        self._buttons_mask = 0
        self._dev = dev
        self.move(0, 0)
    
    def getMouse(vid=0, pid=0, ping_code=0xf9):
        dev = find_mouse_device(vid, pid, ping_code)
        if not dev:
            vid_str = hex(vid) if vid else "Unspecified"
            pid_str = hex(pid) if pid else "Unspecified"
            ping_code_str = hex(ping_code) if pid else "Unspecified"
            error_msg = ("[-] Device "
                        f"Vendor ID: {vid_str}, Product ID: {pid_str} "
                        f"Pingcode: {ping_code_str} not found!")
            raise DeviceNotFoundError(error_msg)
        return MouseInstruct(dev)

    def _buttons(self, buttons):
        if buttons != self._buttons_mask:
            self._buttons_mask = buttons
            self.move(0, 0)

    def click(self, button = MOUSE_LEFT):
        self._buttons_mask = button
        self.move(0, 0)
        time.sleep(0.1)
        self._buttons_mask = 0
        self.move(0, 0)

    def press(self, button = MOUSE_LEFT):
        self._buttons(self._buttons_mask | button)

    def release(self, button = MOUSE_LEFT):
        self._buttons(self._buttons_mask & ~button)

    def is_pressed(self, button = MOUSE_LEFT):
        return bool(button & self._buttons_mask)

    def move(self, x, y, wheel=0):
        time.sleep(0.01)
        limited_x = limit_xy(x)
        limited_y = limit_xy(y)
        limited_w = limit_byte(wheel)
        self._sendRawReport(self._makeReport(limited_x, limited_y, limited_w))

    def _makeReport(self, x, y, wheel=0):
        
        # return report
        report_data = [0x01, self._buttons_mask, low_byte(x), high_byte(x),low_byte(y), high_byte(y), wheel]

        report = struct.pack('<BBhhb', 0x01, self._buttons_mask, x, y, wheel)

        return report


    def _sendRawReport(self, report_data):
        self._dev.write(report_data)

class DeviceNotFoundError(Exception):
        pass