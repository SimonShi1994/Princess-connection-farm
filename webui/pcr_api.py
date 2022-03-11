"""
控制台部分的API代码
"""
import datetime
import subprocess
import time
from typing import List

import core.usercentre as uc
from core.emulator_port import check_known_emulators
from core.initializer import PCRInitializer, Schedule, Device
from core.pcr_config import *
from core.usercentre import AutomatorRecorder, parse_batch, \
    check_users_exists, check_valid_batch, check_task_dict

script_version = "Ver 2.8.20220209"  # 显示的版本号


class MustEndPCRException(Exception):
    def __init__(self, *args):
        super().__init__("必须停止脚本才能执行此命令！", *args)


class MustStartPCRException(Exception):
    def __init__(self, *args):
        super().__init__("必须启动脚本才能执行此命令！", *args)


class MustBindScheduleException(Exception):
    def __init__(self, *args):
        super().__init__("必须绑定计划才能执行此命令！", *args)


class PCRAPI:
    def __init__(self):
        self.PCR: Optional[PCRInitializer] = None
        self.SCH: Optional[Schedule] = None
        self.last_schedule = self.get_last_schedule()

    def _check_end(self, *args):
        # 脚本没停止时，报错
        if self.PCR is not None:
            raise MustEndPCRException(*args)

    def _check_start(self, *args):
        # 脚本没启动时，报错
        if self.PCR is None:
            raise MustStartPCRException(*args)

    def _check_schedule(self, *args):
        # 没有绑定schedule，报错
        if self.last_schedule == "":
            raise MustBindScheduleException(*args)

    def bind_schedule(self, schedule):
        """
        绑定一个计划，此后first,continue等都会执行这一计划。
        绑定的计划存储在bind_schedule.txt中，API打开后，会自动加载最后一次绑定的计划。
            schedule - 计划名称（不能为空）
            return - None
        """
        self._check_end()
        assert schedule != "", "计划名称不能为空！"
        with open("../bind_schedule.txt", "w", encoding="utf-8") as f:
            f.write(schedule)
        self.last_schedule = schedule

    def unbind_schedule(self):
        """
        取消绑定当前的计划，此后first将以空计划模式运行。
        return - None
        """
        self._check_end()
        with open("../bind_schedule.txt", "w", encoding="utf-8") as f:
            f.write("")
        self.last_schedule = ""

    @staticmethod
    def get_last_schedule():
        """
        查看bind_schedule.txt，获取最后一次绑定的计划
        return - last_schedule
        """
        if not os.path.exists("../bind_schedule.txt"):
            return ""
        with open("../bind_schedule.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            if len(lines) > 0:
                return lines[0]
        return ""

    @staticmethod
    def run_adb(f: str):
        """
        运行adb命令 f
        return - 运行结果
        """
        return subprocess.run(f"{os.path.join(adb_dir, '../adb')} {f}", capture_output=True).stdout

    @staticmethod
    def run_init():
        """
        运行初始化
        return - None
        """
        if enable_auto_find_emulator:
            emulator_ip = "127.0.0.1"
            port_list = set(check_known_emulators())
            os.system("taskkill /im adb.exe /f")
            # print(port_list)
            print("自动搜寻模拟器：" + str(port_list))
            for port in port_list:
                os.system(f'cd {adb_dir} & adb connect ' + emulator_ip + ':' + str(port))
        else:
            os.system(f"cd {adb_dir} & adb start-server")
        os.system('python -m uiautomator2 init')
        os.system(f"cd batches & ren *.txt *.json")
        os.system(f"cd groups & ren *.txt *.json")
        os.system(f"cd schedules & ren *.txt *.json")
        os.system(f"cd tasks & ren *.txt *.json")
        os.system(f'cd users & for /r %a in (*.txt) do ren "%a" "%~na.json"')
        if os.system('python -m uiautomator2 init') != 0:
            # pcr_log('admin').write_log(level='error', message="初始化 uiautomator2 失败")
            print("初始化 uiautomator2 失败,请检查是否有模拟器没有安装上ATX")
            exit(1)
        else:
            print("初始化 uiautomator2 成功")
            os.system(f"cd {adb_dir} & adb kill-server")

    def start_pcr(self, schedule_mode: int):
        """
        启动脚本核心，连接模拟器。
        连接前会执行 adb kill-server，来刷新旧adb连接。
        schedule_mode - schedule接入的模式
            0 - 不使用schedule
            1 - 使用first模式接入schedule （等效于restart，然后再continue）
            2 - 使用continue模式接入schedule
        return - None
        """
        self._check_end()
        self.run_adb("kill-server")
        self.PCR = PCRInitializer()
        self.PCR.connect()
        self.PCR.devices.add_from_config()
        self.PCR.start()
        self.SCH = Schedule(self.last_schedule, self.PCR)
        if schedule_mode == 0:
            pass
        elif schedule_mode == 1:
            self.SCH.run_first_time()
        elif schedule_mode == 2:
            self.SCH.run_continue()
        else:
            raise ValueError("schedule_mode 只能为 0，1，2， 而不是", schedule_mode)

    def stop_pcr(self, force=False):
        """
        停止脚本。
        如果设置了force=True，会强制中断当前进行的任务。
        return - None
        """
        self._check_start()
        if self.SCH is not None:
            self.SCH.stop(force)

        self.PCR = None
        self.SCH = None

    def schedule_clear_error(self, name: Optional[str] = None):
        """
        清除名称为name的subschedule的错误
        如果不指定name，则清除全部错误
        return - None
        """
        self._check_end()
        self._check_schedule()
        Schedule(self.last_schedule, None).clear_error(name)

    def schedule_finish(self, name: Optional[str] = None):
        """
        将某一个子subschedule设为完成。
        如果不指定name，则直接完成全部schedule
        return - None
        """
        self._check_end()
        self._check_schedule()
        Schedule(self.last_schedule, None).finish_schedule(name)

    def schedule_restart(self, name: Optional[str] = None):
        """
        重新开始某一个subschedule
        如果不指定name，则重置全部计划，！除了永久执行的计划！
        return - None
        """
        self._check_end()
        self._check_schedule()
        Schedule(self.last_schedule, None).restart(name)

    def device_reconnect(self):
        """
        重新搜索设备并连接
        """
        self._check_start()
        self.PCR.connect()
        self.PCR.start()

    @staticmethod
    def get_datacenter_time():
        """
        获取干炸里脊数据库的最新更新时间
        return - 字符串形式的时间
        """
        from DataCenter import LoadPCRData
        data = LoadPCRData()
        return datetime.datetime.fromtimestamp(data.last_update_time).strftime("%Y-%m-%d %H:%M:%S")

    def add_batch_to_pcr(self, batch: dict, continue_=False):
        """
        中途向任务队列中增加一条batch
        batch - 合法的batch字典
        continue_ - 是否以continue模式运行该batch
        return - None
        """
        check_valid_batch(batch)
        parsed = parse_batch(batch)
        self.PCR.add_tasks(parsed, continue_, f"rec/__batch__/{batch}")

    def add_task_to_pcr(self, accs: List[str], taskname: str, task: Optional[dict] = None, priority: int = 0,
                        rand: bool = False, continue_: bool = False):
        """
        中途向任务队列中增加一个谁做谁
        accs - 用户列表，接受新任务的对象。
        taskname - 显示在任务队列中的任务名称
        task - 合法的task字典，若不指定，则自动在tasks目录下找taskname的任务文件载入。
        priority - 任务优先级
        rand - 是否随机accs的顺序
        continue_ - 是否以continue模式运行该任务
        """
        check_users_exists(accs, is_raise=True)
        if task is not None:
            check_task_dict(task, is_raise=True)
            for acc in accs:
                self.PCR.add_task((priority, acc, taskname, task), False, "rec/__directly__", rand_pri=rand)
        else:
            for acc in accs:
                self.PCR.add_task((priority, acc, taskname), False, "rec/__directly__", rand_pri=rand)

    def get_device_status(self):
        """
        Status:
        List of all devices: [{
            serial - 串口字符串
            device_time - 开机时间(秒，int)
            work_time - 连续工作时间(秒，int)
            state - 状态字符串
                - offline 离线
                - busy    正忙
                - free    空闲

            * 当state为busy时：
            current_acc 当前正在运行的账号名称
            current_acc_status 当前正在运行的账号的状态字符串（见AutomatorRecorder.get_user_state）
            use_launcher bool类型，是否使用模拟器自启动控制
        }]
        """
        self._check_start()
        S = []
        for i, j in self.PCR.devices.devices.items():
            D = {}
            D["serial"] = i
            D["device_time"] = 0
            D["work_time"] = 0
            tm = time.time()
            if j.state == Device.DEVICE_OFFLINE:
                D["state"] = "offline"
            elif j.state == Device.DEVICE_BUSY:
                D["state"] = "busy"
                D["work_time"] = tm - j.time_busy
                D["device_time"] = tm - j.time_wake
                D["current_acc"] = j.cur_acc
                D["current_acc_status"] = AutomatorRecorder.get_user_state(j.cur_acc, j.cur_rec)
                D["use_launcher"] = j.emulator_launcher is not None
            elif j.state == Device.DEVICE_AVAILABLE:
                D["state"] = "free"
                D["device_time"] = tm - j.time_wake
            S.append(D)
        return S

    def get_task_queue(self):
        """
        Status:
        List of 任务信息五元组[(
            任务队列中的当前序号:int,
            用户名:str,
            任务名称:str，
            任务记录路径:pathstr，
            任务运行状态字符串:str
        )]

        """
        self._check_start()
        L = self.PCR.get_status()
        return L

    def get_schedule_status(self):
        """
        Status:
        List Of 每个子sub的状态[{
            name:      子sub的名称
            mode:      "batch"或者"batches"，表示是单批模式还是多批顺序模式
            status:    状态字符串
                - fin:  已完成
                - skip：已跳过
                - busy: 正在执行
                - last: 未完成
                    （非fin,skip,err，但由于PCR未启动，无法进一步判断其当前状态.
                    当PCR启动后，last可能变为skip、busy或wait三者之一。）
                - wait: 待执行
                - err:  有错误
            cnt:       该子任务中已经结束的用户总数（出错总数+完成总数）
            tol:       该子任务中的全部用户数
            error:  dict(出错用户名:出错原因）
            detail: 见usercenter/get_batch_state的返回值
                特别的，detail["detail"][用户名]["current"] 某一用户当前的任务进度字符串

            * 当mode为batches时，cnt,tol,error,detail均为当前批次的状态，且增加以下条目
            current:   当前批次的批名称
            batch_fin： 已经完成的批次数
            batch_tot： 总批次数
        }]
        """
        if self.SCH is None:
            # 未执行
            return Schedule(self.last_schedule, None).get_status(True)
        else:
            return self.SCH.get_status(False)

    # Clone All UserCenter Functions To API
    list_all_users = uc.list_all_users
    list_all_tasks = uc.list_all_tasks
    list_all_groups = uc.list_all_groups
    list_all_batches = uc.list_all_batches
    list_all_schedules = uc.list_all_schedules
    list_all_switches = uc.list_all_switches

    def read_user(self, s: str) -> dict:
        D = AutomatorRecorder(s).getuser()
        return {
            "account": D["account"],
            "password": D["password"]
        }

    read_group = AutomatorRecorder.getgroup
    read_task = AutomatorRecorder.gettask
    read_batch = AutomatorRecorder.getbatch
    read_schedule = AutomatorRecorder.getschedule
    read_switch = AutomatorRecorder.getswitch

    def write_user(self, s: str, userdict: dict):
        AutomatorRecorder(s).setuser(userdict)

    write_group = AutomatorRecorder.setgroup
    write_task = AutomatorRecorder.settask
    write_batch = AutomatorRecorder.setbatch
    write_schedule = AutomatorRecorder.setschedule
    write_switch = AutomatorRecorder.setswitch


if __name__ == "__main__":
    API = PCRAPI()
    API.start_pcr(1)  # first
    D = API.get_device_status()
