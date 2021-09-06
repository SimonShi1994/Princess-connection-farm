"""
启动模拟器的程序
"""
import subprocess
import time
from abc import abstractmethod, ABCMeta

from core.pcr_config import emulator_console, emulator_id, emulator_address, auto_emulator_address, wait_for_launch_time


class LauncherBase(metaclass=ABCMeta):
    @abstractmethod
    def id_to_serial(self, id: int) -> str:
        """
        给定一个模拟器序号ID，获得其对应的端口号
        :param id:
        :return: 端口Serial
        """
        pass

    @abstractmethod
    def launch(self, id: int, block: bool) -> None:
        """
        启动编号为id的模拟器,是否阻塞直到启动
        """
        pass

    @abstractmethod
    def quit(self, id: int) -> None:
        """
        关闭编号为id的模拟器
        """
        pass

    @abstractmethod
    def is_running(self, id: int) -> bool:
        """
        判断编号为id的模拟器是否处于启动状态
        """
        pass

    def restart(self, id: int, block=False):
        """
        重启
        """
        self.quit(id)
        time.sleep(3)
        self.launch(id, block)

    def wait_for_launch(self, id: int, timeout=wait_for_launch_time):
        last_time = time.time()
        while not self.is_running(id):
            time.sleep(1)
            if time.time() - last_time > timeout:
                return False
        return True

    def wait_for_all(self):
        for i in emulator_id:
            while not self.is_running(i):
                time.sleep(1)

    def start_all(self):
        for i in emulator_id:
            self.launch(i, False)
        self.wait_for_all()

    def quit_all(self):
        for i in emulator_id:
            self.quit(i)


class DnPlayer:
    def __init__(self, info: list):
        # 索引，标题，顶层窗口句柄，绑定窗口句柄，是否进入android，进程PID，VBox进程PID
        self.index = int(info[0])
        self.name = info[1]
        self.top_win_handler = int(info[2])
        self.bind_win_handler = int(info[3])
        self.is_in_android = True if int(info[4]) == 1 else False
        self.pid = int(info[5])
        self.vbox_pid = int(info[6])

    def is_running(self) -> bool:
        return self.is_in_android

    def __str__(self):
        index = self.index
        name = self.name
        r = str(self.is_in_android)
        twh = self.top_win_handler
        bwh = self.bind_win_handler
        pid = self.pid
        vpid = self.vbox_pid
        return "\nindex:%d name:%s top:%08X bind:%08X running:%s pid:%d vbox_pid:%d\n" % (
            index, name, twh, bwh, r, pid, vpid)

    def __repr__(self):
        index = self.index
        name = self.name
        r = str(self.is_in_android)
        twh = self.top_win_handler
        bwh = self.bind_win_handler
        pid = self.pid
        vpid = self.vbox_pid
        return "\nindex:%d name:%s top:%08X bind:%08X running:%s pid:%d vbox_pid:%d\n" % (
            index, name, twh, bwh, r, pid, vpid)


class LDLauncher(LauncherBase):
    def __init__(self):
        self.console_str = emulator_console

    def id_to_serial(self, id: int) -> str:
        if auto_emulator_address:
            return f"emulator-{5554 + id * 2}"
        else:
            return emulator_address[id]

    def launch(self, id: int, block: bool = False) -> None:
        cmd = f"{self.console_str} globalsetting --audio 0 --fastplay 1 --cleanmode 1"
        subprocess.check_call(cmd)
        cmd = f"{self.console_str} launch --index {id}"
        subprocess.check_call(cmd)
        cmd = f"{self.console_str} downcpu --index {id} --rate 50"
        subprocess.check_call(cmd)

        if len(emulator_id) == 0:
            block = False

        if block:
            last_time = time.time()
            while not self.is_running(id) and time.time() - last_time < wait_for_launch_time:
                time.sleep(1)

    def quit(self, id: int) -> None:
        cmd = f"{self.console_str} quit --index {id}"
        subprocess.check_call(cmd)
        time.sleep(3)

    def get_list(self):
        # 获取模拟器列表
        cmd = f"{self.console_str} list2"
        text = subprocess.check_output(cmd).decode("gbk")
        info = text.split('\n')
        result = list()
        for line in info:
            if len(line) > 1:
                dnplayer = line.split(',')
                result.append(DnPlayer(dnplayer))
        return result

    def is_running(self, id: int) -> bool:
        try:
            all = self.get_list()
        except Exception as e:
            print("WARNING: ", e)
            return False
        if id >= len(all):
            return False
        else:
            return all[id].is_running()



class BSLauncher(LauncherBase):
    def __init__(self):
        self.console_str = emulator_console

    def id_to_serial(self, id: int) -> str:
        if auto_emulator_address:
            return f"emulator-{5554 + id * 10}"
        else:
            return emulator_address[id]

    def launch(self, id: int, block: bool = False) -> None:
        cmd = f"{self.console_str} launch --index {id}"
        subprocess.check_call(cmd)

        if len(emulator_id) == 0:
            block = False

        if block:
            last_time = time.time()
            while not self.is_running(id) and time.time() - last_time < wait_for_launch_time:
                time.sleep(1)

    def quit(self, id: int) -> None:
        cmd = f"{self.console_str} quit --index {id}"
        subprocess.check_call(cmd)
        time.sleep(3)

    def get_list(self):
        # 获取模拟器列表
        cmd = f"{self.console_str} list"
        text = subprocess.check_output(cmd).decode("gbk")
        info_list = text.split('\n')
        device_list = []
        for i in info_list:
            if len(i)>0:
                device_list.append(i)  # Careful: Empty Lines.
        return device_list

    def get_running_list(self):
        # 获取运行中模拟器列表
        cmd = f"{self.console_str} runninglist"
        text = subprocess.check_output(cmd).decode("gbk")
        info_list = text.split('\n')
        device_list = []
        for i in info_list:
            if len(i)>0:
                device_list.append(i)  # Careful: Empty Lines.
        return device_list

    def is_running(self, id: int) -> bool:
        running_ids = {}
        try:
            all = self.get_list()
            run = self.get_running_list()
            for ind,device_name in enumerate(all):
                running_ids[ind]=device_name in run
            if id >= len(all):
                return False
            else:
                return running_ids[id]

        except Exception as e:
            print("WARNING: ", e)
            return False


EMULATOR_DICT = {
    "雷电": LDLauncher,
    "蓝叠": BSLauncher,
}
