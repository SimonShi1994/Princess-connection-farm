import sys

import ctypes
import datetime
import functools
import inspect
import os
import queue
import random
import subprocess
import time
from threading import Thread

import adbutils
import requests
import uiautomator2

from core import log_handler
from core.pcr_config import adb_dir, debug, disable_timeout_raise, u2_record_size, u2_record_filter, \
    force_timeout_reboot, global_adb_restart
# log
__log = log_handler.pcr_log("safe_u2")


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


# Timeout Error: https://stackoverflow.com/questions/21827874/timeout-a-function-windows
class TimeoutError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


def timeout(seconds, error_info):
    def deco(func):
        if force_timeout_reboot:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                res = [TimeoutError('函数 [%s] 超时 [%s 秒] ！ %s' % (func.__name__, seconds, error_info))]

                def newFunc():
                    try:
                        try:
                            from automator_mixins._async import block_sw
                            if block_sw == 1:
                                # print("time_out的脚本暂停中~")
                                while block_sw == 1:
                                    from automator_mixins._async import block_sw
                                    time.sleep(1)
                                return deco
                        except Exception as error:
                            __log.write_log('error', f'暂停-错误:{error}')
                        res[0] = func(*args, **kwargs)
                    except Exception as e:
                        res[0] = e

                t = Thread(target=newFunc)
                t.daemon = True
                try:
                    t.start()
                    t.join(seconds)
                except Exception as e:
                    __log.write_log('error','error starting thread')
                    raise e
                ret = res[0]
                try:
                    from automator_mixins._async import block_sw
                    if block_sw == 1:
                        # print("time_out2的脚本暂停中~")
                        while block_sw == 1:
                            from automator_mixins._async import block_sw
                            time.sleep(1)
                        return deco
                except Exception as error:
                    __log.write_log('error', f'暂停-错误: {error}')
                if isinstance(ret, BaseException):
                    if debug:
                        __log.write_log('debug', f"!!!{id(ret)}{type(ret)}{ret}")
                    if isinstance(ret, TimeoutError):
                        try:
                            _async_raise(t.ident, SystemExit)
                        except:
                            pass
                    raise ret
                return ret

            if not disable_timeout_raise:
                return wrapper
            else:
                return func
        else:
            return func

    return deco


def run_adb(cmd: str, timeout=None, use_os_instead_of_subprocess=False):
    try:
        if sys.platform == "win32":
            if use_os_instead_of_subprocess:
                os.system(f"{adb_dir}/adb {cmd}")
            else:
                subprocess.check_output(f"{adb_dir}/adb {cmd}", timeout=timeout)
        else:
            if use_os_instead_of_subprocess:
                os.system(f"adb {cmd}")
            else:
                subprocess.check_output(f"adb {cmd}", timeout=timeout, shell=True)
    except Exception as e:
        __log.write_log('error', f"adb启动失败,{e},试图修复。")
        try:
            if sys.platform == "win32":
                os.system("taskkill /im adb.exe /f")
                subprocess.check_output(f"{adb_dir}/adb {cmd}", timeout=timeout)
            else:
                os.system("pkill adb")
                subprocess.check_output(f"adb {cmd}", timeout=timeout, shell=True)
        except Exception as e:
            __log.write_log('error', f"执行adb命令{cmd}失败了：{e}")


class OfflineException(Exception):
    def __init__(self, *args):
        super().__init__()
        self.args = args


class ReadTimeoutException(Exception):
    def __init__(self, *args):
        super().__init__()
        self.args = args


def random_sleep():
    time.sleep(random.random())


def safe_u2_connect(serial: str, adb_restart_fun=None):
    last_e = None
    for retry in range(3):
        try:
            return uiautomator2.connect(serial)
        except adbutils.errors.AdbError as e:
            last_e = e
            if e.args[0] == "unknown host service":
                # 重连
                if adb_restart_fun is not None:
                    adb_restart_fun()
                else:
                    random_sleep()
                    run_adb("kill-server", timeout=60)
                    random_sleep()
                    run_adb("start-server", timeout=60)
        except RuntimeError as e:
            last_e = e
            if e.args[0].endswith("is offline"):
                # 因为掉线所以无法进行
                raise OfflineException(*e.args)
        except requests.exceptions.ReadTimeout as e:
            raise ReadTimeoutException(e)
    raise last_e


@timeout(300, "u2命令执行超时")
def safe_wraper(fun, *args, adb_restart_fun=None, **kwargs):
    last_e = None
    for retry in range(3):
        try:
            return fun(*args, **kwargs)
        except ConnectionResetError as e:
            # 试者重连
            last_e = e
            random_sleep()
            run_adb("devices", timeout=60)
        except requests.exceptions.ConnectionError as e:
            last_e = e
            time.sleep(1)  # 这个问题是多开了一个，只会爆一次错
        except adbutils.errors.AdbError as e:
            last_e = e
            if e.args[0] == "unknown host service":
                # 重连
                if global_adb_restart and adb_restart_fun is not None:
                    adb_restart_fun()
                else:
                    random_sleep()
                    run_adb("kill-server", timeout=60)
                    random_sleep()
                    run_adb("start-server", timeout=60)
        except uiautomator2.exceptions.BaseError as e:
            last_e = e
            if global_adb_restart and adb_restart_fun is not None:
                adb_restart_fun()
            else:
                random_sleep()
                run_adb("kill-server", timeout=60)
                random_sleep()
                run_adb("start-server", timeout=60)
        except RuntimeError as e:
            last_e = e
            if e.args[0].endswith("is offline"):
                # 因为掉线所以无法进行
                raise OfflineException(*e.args)
        except requests.exceptions.ReadTimeout as e:
            raise ReadTimeoutException(e)
    raise last_e


class U2Record:
    def __init__(self, record_size):
        self.Q = queue.Queue(record_size)

    def gettime(self):
        cur_time = time.time()
        time_str = datetime.datetime.fromtimestamp(cur_time).strftime("%H%M%S")
        return time_str

    def add(self, item="()", *args, **kwargs):
        cur = {"cmd": f"{item} -- {args} -- {kwargs}", "start": self.gettime(), "end": None}
        if not item in u2_record_filter:
            if self.Q.full():
                self.Q.get()
            self.Q.put(cur)
        return cur

    def get(self):
        L = self.Q.queue
        out = []
        for l in L:
            if l['end'] is None:
                out += [f"{l['start']} : {l['cmd']}"]
            else:
                out += [f"{l['start']} ~ {l['end']} : {l['cmd']}"]
        return out

class SafeU2HandleBase:
    def __init__(self, obj, safe_items=[], safe_subobjs={}, adb_restart_fun=None):
        self.R = U2Record(u2_record_size)
        self.obj = obj
        self.safe_items = safe_items
        self.safe_subobjs = safe_subobjs
        self.adb_restart_fun = adb_restart_fun

    def __getattr__(self, item):
        if item in self.safe_items:
            def fun(*args, **kwargs):
                cur = self.R.add(item, *args, **kwargs)
                output = safe_wraper(getattr(self.obj, item), *args, adb_restart_fun=self.adb_restart_fun,
                                     **kwargs)
                cur['end'] = self.R.gettime()
                return output

            return fun
        elif item in self.safe_subobjs:
            return self.safe_subobjs[item](
                getattr(self.obj, item)
            )
        else:
            return getattr(self.obj, item)


class SafeU2Object(SafeU2HandleBase):
    def __init__(self, obj: uiautomator2.UiObject, adb_restart_fun=None):
        super().__init__(obj, ["click", "exists"], adb_restart_fun=adb_restart_fun)


class SafeU2Touch(SafeU2HandleBase):
    def __init__(self, obj, adb_restart_fun=None):
        super().__init__(obj, ['down', 'move', 'up', 'sleep'], adb_restart_fun=adb_restart_fun)

class SafeU2Handle(SafeU2HandleBase):
    def __init__(self, obj: uiautomator2.Device, adb_restart_fun=None):
        super().__init__(obj,
                         ["app_wait", "session", "clear_text", "send_keys",
                          "click", "drag", "screenshot", "app_stop"],
                         {'touch': SafeU2Touch}, adb_restart_fun=adb_restart_fun)

    def __call__(self, *args, **kwargs):
        self.R.add(item="()", *args, **kwargs)
        # next_obj=safe_wraper(super(SafeU2HandleBase,self).__getattribute__("obj").__call__,*args,**kwargs)
        next_obj = self.obj(*args, **kwargs)
        return SafeU2Object(next_obj, adb_restart_fun=self.adb_restart_fun)
