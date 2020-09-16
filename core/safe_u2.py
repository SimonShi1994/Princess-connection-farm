import os
import subprocess
import time

import adbutils
import requests
import uiautomator2

from core.pcr_config import adb_dir


def run_adb(cmd: str, timeout=None):
    try:
        subprocess.check_output(f"{adb_dir}/adb {cmd}", timeout=timeout)
    except Exception as e:
        print("adb启动失败，", e, "试图修复。")
        os.system("taskkill /im adb.exe /f")
        subprocess.check_output(f"{adb_dir}/adb {cmd}", timeout=timeout)

class OfflineException(Exception):
    def __init__(self, *args):
        super().__init__()
        self.args = args


class ReadTimeoutException(Exception):
    def __init__(self, *args):
        super().__init__()
        self.args = args


def safe_u2_connect(serial: str):
    last_e = None
    for retry in range(3):
        try:
            return uiautomator2.connect(serial)
        except adbutils.errors.AdbError as e:
            last_e = e
            if e.args[0] == "unknown host service":
                # 重连
                run_adb("kill-server", timeout=60)
                run_adb("start-server", timeout=60)
        except RuntimeError as e:
            last_e = e
            if e.args[0].endswith("is offline"):
                # 因为掉线所以无法进行
                raise OfflineException(*e.args)
        except requests.exceptions.ReadTimeout as e:
            raise ReadTimeoutException(e)
    raise last_e


def safe_wraper(fun, *args, **kwargs):
    last_e = None
    for retry in range(3):
        try:
            return fun(*args, **kwargs)
        except ConnectionResetError as e:
            # 试者重连
            last_e = e
            run_adb("start-server", timeout=60)
        except requests.exceptions.ConnectionError as e:
            last_e = e
            time.sleep(1)  # 这个问题是多开了一个，只会爆一次错
        except adbutils.errors.AdbError as e:
            last_e = e
            if e.args[0] == "unknown host service":
                # 重连
                run_adb("kill-server", timeout=60)
                run_adb("start-server", timeout=60)
        except RuntimeError as e:
            last_e = e
            if e.args[0].endswith("is offline"):
                # 因为掉线所以无法进行
                raise OfflineException(*e.args)
        except requests.exceptions.ReadTimeout as e:
            raise ReadTimeoutException(e)
    raise last_e


class SafeU2HandleBase:
    def __init__(self, obj, safe_items=[], safe_subobjs={}):
        self.obj = obj
        self.safe_items = safe_items
        self.safe_subobjs = safe_subobjs

    def __getattribute__(self, item):
        if item in super(SafeU2HandleBase, self).__getattribute__("safe_items"):
            def fun(*args, **kwargs):
                return safe_wraper(super(SafeU2HandleBase, self).__getattribute__("obj").__getattribute__(item), *args,
                                   **kwargs)

            return fun
        elif item in super(SafeU2HandleBase, self).__getattribute__("safe_subobjs"):
            return super(SafeU2HandleBase, self).__getattribute__("safe_subobjs")[item](
                super(SafeU2HandleBase, self).__getattribute__("obj").__getattribute__(item)
            )
        else:
            return super(SafeU2HandleBase, self).__getattribute__("obj").__getattribute__(item)


class SafeU2Object(SafeU2HandleBase):
    def __init__(self, obj: uiautomator2.UiObject):
        super().__init__(obj, ["click", "exists"])


class SafeU2Touch(SafeU2HandleBase):
    def __init__(self, obj):
        super().__init__(obj, ['down', 'move', 'up', 'sleep'])


class SafeU2Handle(SafeU2HandleBase):
    def __init__(self, obj: uiautomator2.Device):
        super().__init__(obj,
                         ["app_wait", "session", "clear_text", "send_keys",
                          "click", "drag", "screenshot", "app_stop"],
                         {'touch': SafeU2Touch})

    def __call__(self, *args, **kwargs):
        # next_obj=safe_wraper(super(SafeU2HandleBase,self).__getattribute__("obj").__call__,*args,**kwargs)
        next_obj = super(SafeU2HandleBase, self).__getattribute__("obj").__call__(*args, **kwargs)
        return SafeU2Object(next_obj)
