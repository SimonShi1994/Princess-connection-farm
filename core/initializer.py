"""
新的启动函数，支持Batch，schedule操作等。
"""
import time
import traceback
from multiprocessing import Process
from multiprocessing.managers import SyncManager
from queue import PriorityQueue
from typing import List, Tuple, Optional, Dict

import adbutils
import keyboard

from automator_mixins._base import Multithreading
from core import log_handler
from core.Automator import Automator
from emulator_port import *
from pcr_config import enable_auto_find_emulator, emulator_ports, selected_emulator, max_reboot, \
    trace_exception_for_debug

acclog = log_handler.pcr_acc_log()


def _connect():  # 连接adb与uiautomator
    try:
        if enable_auto_find_emulator:
            port_list = check_known_emulators()
            print("自动搜寻模拟器：" + str(port_list))
            for port in port_list:
                os.system('cd adb & adb connect ' + emulator_ip + ':' + str(port))
        if len(emulator_ports) != 0:
            for port in emulator_ports:
                os.system('cd adb & adb connect ' + emulator_ip + ':' + str(port))
        # os.system 函数正常情况下返回是进程退出码，0为正常退出码，其余为异常
        if os.system('cd adb & adb connect ' + selected_emulator) != 0:
            pcr_log('admin').write_log(level='error', message="连接模拟器失败")
            exit(1)
    except Exception as e:
        pcr_log('admin').write_log(level='error', message='连接失败, 原因: {}'.format(e))
        exit(1)


# https://blog.csdn.net/qq_45587822/article/details/105950260
class MyManager(SyncManager):
    pass


class MyPriorityQueue(PriorityQueue):
    def get_attribute(self, name):
        return getattr(self, name)


def _get_manager():
    MyManager.register("PriorityQueue", MyPriorityQueue)
    m = MyManager()
    m.start()
    return m


class Device:
    """
    设备类，存储设备状态等。
    之后可以扩充雷电的开关操作
    """
    # 设备状态
    DEVICE_OFFLINE = 0  # 离线
    DEVICE_AVAILABLE = 1  # 可用
    DEVICE_BUSY = 2  # 正忙

    def __init__(self, d: adbutils.AdbDevice):
        self.serial = d.serial
        self.d = d
        self.state = 0
        self._in_process = False  # 是否已经进入多进程

    def init(self):
        self.state = self.DEVICE_AVAILABLE

    def start(self):
        self.state = self.DEVICE_BUSY

    def stop(self):
        self.state = self.DEVICE_AVAILABLE

    def offline(self):
        self.state = self.DEVICE_OFFLINE

    @staticmethod
    def device_is_connected(d: adbutils.AdbDevice):
        try:
            d.say_hello()
        except adbutils.errors.AdbError:
            return False
        else:
            return True

    def is_connected(self):
        return self.device_is_connected(self.d)


class AllDevices:
    """
    全部设备控制类，包含了包括connect在内的一些操作。
    """

    def __init__(self, device_type="雷电"):
        self.device_type = device_type
        self.devices: Dict[str, Device] = {}  # serial : device

    def add_device(self, d: adbutils.AdbDevice):
        """
        添加一个设备，若该设备不存在，则添加；若该设备的状态为offline但已连接，更新状态为available
        """
        s = d.serial
        if Device.device_is_connected(d):
            if s in self.devices:
                if self.devices[s].state == Device.DEVICE_OFFLINE:
                    self.devices[s].init()
            else:
                self.devices[s] = Device(d)
                self.devices[s].init()
        else:
            if s in self.devices:
                if self.devices[s].state != Device.DEVICE_OFFLINE:
                    self.devices[s].offline()
            else:
                self.devices[s] = Device(d)
                self.devices[s].offline()

    def connect(self):
        _connect()
        dl = adbutils.adb.device_list()
        for d in dl:
            self.add_device(d)

    def get(self):
        """
        获取一个空闲的设备，若获取失败，返回None
        若获取成功，返回device serial，并且该设备被标记为busy
        """
        for s, d in self.devices.items():
            if d.state == Device.DEVICE_AVAILABLE:
                d.start()
                return s
        return None

    def full(self):
        """
        判断是否所有设备均空闲
        """
        for d in self.devices.values():
            if d.state == Device.DEVICE_BUSY:
                return False
        return True

    def put(self, s):
        """
        放回一个用完的设备，更新该设备状态
        :param s: 设备的Serial
        """
        if self.devices[s].is_connected():
            self.devices[s].stop()
        else:
            self.devices[s].offline()

    def count(self):
        """
        返回当前busy状态的设备数
        """
        cnt = 0
        for i in self.devices.values():
            if i.state == Device.DEVICE_BUSY:
                cnt += 1
        return cnt

    def list_all_free_devices(self) -> List[Device]:
        """
        返回当前全部空闲的设备
        """
        L = []
        for i in self.devices.values():
            if i.state == Device.DEVICE_AVAILABLE:
                L += [i]
        return L


class PCRInitializer:
    """
    PCR启动器，包含进程池逻辑、任务调度方法等。
    """

    def __init__(self):
        """
        self.available_devices：multiprocessing.queue类型
            用于多进程，存放当前已连接但是空闲中的设备。queue[str]
        self.devices_state：字典类型，存储设备信息。
            {device_str : state_dict}
        self.tasks：queue.PriorityQueue类型，按优先级从高到低排序一系列任务
        """
        self.devices = AllDevices()
        self.mgr = _get_manager()
        self.tasks: MyPriorityQueue = self.mgr.__getattribute__("PriorityQueue")()  # 优先级队列

    def connect(self):
        """
        连接设备，初始化设备
        """
        self.devices.connect()
        if os.system('python -m uiautomator2 init') != 0:
            pcr_log('admin').write_log(level='error', message="初始化 uiautomator2 失败")
            exit(1)

    def add_task(self, task: Tuple[int, str, dict], continue_):
        """
        向优先级队列中增加一个task
        该task为四元组，(priority, account, task, continue_)
        """
        task = (0 - task[0], task[1], task[2], continue_)  # 最大优先队列
        self.tasks.put(task)

    def add_tasks(self, tasks: list, continue_):
        """
        向优先级队列中增加一系列tasks
        该tasks为一个列表类型，每个元素为四元组，(priority, account, task, continue_)
        """
        for task in tasks:
            self.add_task(task, continue_)

    @staticmethod
    def run_task(device, account, task, continue_):
        """
        让device执行任务：account做task
        :param device: 设备名
        :param account:  账户名
        :param task:  任务名
        :param continue_:  是否继续上次中断的位置
        :return 是否成功执行
        """
        a: Optional[Automator] = None
        try:
            keyboard.release('p')
            Multithreading({}).state_sent_resume()
            a = Automator(device)
            a.init_account(account)
            a.start()
            user = a.AR.getuser()
            account = user["account"]
            password = user["password"]
            a.log.write_log("info", f"即将登陆： 用户名 {account}")  # 显然不需要输出密码啊喂！
            a.start_th()
            a.start_async()
            a.start_shuatu()
            a.login_auth(account, password)
            acclog.Account_Login(account)
            a.RunTasks(task, continue_, max_reboot)
            a.change_acc()
            acclog.Account_Logout(account)
            return True
        except Exception as e:
            pcr_log(account).write_log('error', message=f'initialize-检测出异常：{type(e)} {e}')
            if trace_exception_for_debug:
                tb = traceback.format_exc()
                pcr_log(account).write_log('error', message=tb)
            try:
                a.fix_reboot(False)
            except Exception as e:
                pcr_log(account).write_log('error', message=f'initialize-自动重启失败：{type(e)} {e}')
                if trace_exception_for_debug:
                    tb = traceback.format_exc()
                    pcr_log(account).write_log('error', message=tb)
                return False
        finally:
            a.stop_th()

    @staticmethod
    def _do_process(device: Device, queue):
        """
        执行run_task的消费者进程
        """
        while True:
            task = queue.get()
            if task is None:
                break
            serial = device.serial
            priority, account, task, continue_ = task
            res = PCRInitializer.run_task(serial, account, task, continue_)
            if not res and not device.is_connected():
                # 可能模拟器断开
                device.offline()
            else:
                device.stop()
        device._in_process = False

    def start(self):
        """
        进入分配任务给空闲设备的循环
        """
        device_list = self.devices.list_all_free_devices()
        for d in device_list:
            if not d._in_process:
                d._in_process = True
                Process(target=PCRInitializer._do_process, kwargs=dict(device=d, queue=self.tasks), daemon=True).start()

    def stop(self, join=False):
        if join:
            while not self.devices.full():
                time.sleep(1)
