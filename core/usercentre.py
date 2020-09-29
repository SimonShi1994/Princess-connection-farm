import json
import os
from typing import List, Optional

from core.constant import USER_DEFAULT_DICT as UDD
from core.valid_task import VALID_TASK

"""
用户文件存储说明：
默认路径：/users
存储格式：json
必须要含有的元素：
{
    "account":"..."  # 用户名
    "password":"..." # 密码
    # "taskfile":"..." #任务配置文件名 如果为""则不进行任务。 <- 已经不需要了
}

任务配置文件存储说明：
默认路径：/tasks
存储格式：json
必须要含有的元素：
{"tasks":
[
        {
            "type":"..."  # 任务代号缩写
            "param1":...  # 参数1的key与value
            "param2":...  # 参数2的key与value
            ...
        },
        {...},...
]
}

组说明：
默认路径：/groups
存储格式：txt
组名：.txt文件的文件名
每个组包含的成员：
    txt文件每行一个account，表示这个account包含于该组中。

批处理说明：
默认路径： /batches
存储格式：json
必须含有的元素：
{"batch":
[
        {
            "account":"..."    # 账号名称
            "group":"..."      # 组名（和账号名称只能出现一个）
            "taskfile":"..."   # 所用任务文件
            "priority":int     # 整数，优先级。 
                # 注：同优先级任务同批次执行，优先级高优先执行（但若有模拟器空余，仍然和其它任务同时执行）
        },
        {...},...
]
}

计划文件说明：
默认路径： /schedules
存储格式：json
必须含有的元素：
{"schedules"
[
        # 立刻执行计划
        # schedule被执行时，如果condition满足，则立刻将该batch解析放入任务队列
        # 如果condition不满足，则跳过该batch。
        # 例子：制定两个schedule，一个早上执行，一个晚上执行
        # 希望早上start schedule时执行早上任务，晚上start schedule时执行晚上任务
        # 则可以创建两个asap计划，其中一个的condition定在5~12，一个定在12~29
        # 此时若早上执行，第一个计划condition满足，立刻执行；第二个不满足，不执行。
        # 若晚上执行，第一个计划contidion不满足，不执行，第二个满足，执行。
        {
            "type":"asap"  # As soon as possible
            "name":"..."
            "batchfile":"..."  # batch文件所在位置
            "batchlist":[
                # 为40 to 1设计，多个batch依次执行，两个batch之间清空记录
                # 若一个batch未成功运行，则后一个batch也不会运行。
                # batchlist和batchfile只应该存在一个。
                "...",
                "...",
                ...
            ]
            ”condition”:{
                # condition为条件，对asap任务，只有condition全部满足，才会执行。
                # condition可以是一个空字典，表示不设置条件
                "start_hour":int  # 小时开始，只有小时数>start_hour时才会执行任务
                "end_hour":int  # 小时结束，只有小时数<end_hour时才会执行任务
                "can_juanzeng":account  # account可以发起捐赠了
                "_last_rec":dir  # 用户无法编辑、查看此条。_last_rec文件夹下无_fin文件时执行。
                # 还可以补充其它condition，但暂时没想到。
            }
            "record":int  # 记录模式
        }
        
        # 等待执行计划
        # schedule执行时，首先将所有的asap计划加入任务队列
        # 如果有等待执行计划，则schedule持续运行，直到指定条件出现。
        # 应用场景 1：自动发起捐赠。可以设置condition为can_juanzeng，则
        # 当指定账号可以捐赠时，自动将该batch放入任务队列。
        # 发起捐赠可以设置为高优先级，从而可以插队执行。
        # 应用场景 2：24h挂机。可以设置condition为时间段，则
        # 当到达指定时间段后，自动将该batch加入任务队列。
        {
            "type":"wait"
            "name":"..."
            "batchfile":"..."
            "batchlist":["...","...",...]
            "condition":{...}
            "record":int
        }
        
        # schedule控制代码
        # 如果要实现24小时自动，那么必须每天5:00清除schedule的记录。
        {
            "type":"config"
            "restart":int  # 整数，表示每天清理记录的时间
            # 其它有关控制的任务都可以放在这里
        }
]
}


"""
user_addr = "users"  # 存放用户配置的文件夹
task_addr = "tasks"  # 存放任务配置的文件夹
group_addr = "groups"  # 存放用户组的文件夹
batch_addr = "batches"  # 存放批任务的文件夹
schedule_addr = "schedules"  # 存放计划的文件夹


def check_user_dict(d: dict, is_raise=False) -> bool:
    """
    检查一个用户配置文件是否合法。
    :param d: 解析后的用户配置字典
    :param is_raise: 对于不合法的地方是否弹出错误
    :return: 是否合法
    """
    try:
        assert "account" in d, "必须含有account关键字以存储用户名！"
        assert type(d["account"]) is str, f"account必须为字符串类型而不应是{type(d['account'])}"
        assert "password" in d, "必须含有password关键字以存储密码！"
        assert type(d["password"]) is str, f"password必须为字符串类型而不应是{type(d['password'])}"
        # assert "taskfile" in d, "必须含有任务列表taskfile！"
        # assert type(d["taskfile"]) is str, f"tasks必须为字符串类型而不应是{type(d['tasks'])}"
        return True
    except Exception as e:
        if is_raise:
            raise e
        else:
            return False


def check_task_dict(d: dict, is_raise=False) -> bool:
    """
    检查一个任务配置文件是否合法。
    :param d: 解析后的任务配置字典
    :param is_raise: 对于不合法的地方是否弹出错误
    :return: 是否合法
    """
    try:
        assert "tasks" in d, "必须含有任务列表tasks！"
        assert type(d["tasks"]) is list, f"tasks必须为列表类型而不应是{type(d['tasks'])}"
        for i in d["tasks"]:
            assert type(i) is dict, f"tasks中的每一个task必须为字典类型，但是{i}是{type(i)}。"
            assert "type" in i, f"tasks中的每一个task都必须有type键存放任务代号，但是{i}没有"
            assert i["type"] in VALID_TASK.T, f"任务代号{i['type']}不存在！"
            params = VALID_TASK.T[i["type"]]["params"]

            for j in params:
                if j.default is None:
                    assert j.key in i, f"任务 {i['type']} 必须含有参数 {j.key}！"

            v_k = [i.key for i in params]
            v_p = [i for i in params]
            for k in i:
                if k == "type":
                    continue
                if k == "__disable__":
                    continue
                assert k in v_k, f"任务 {i['type']} 含有未知的参数 {k}！"
                ind = v_k.index(k)
                v_p[ind].check(i[k])
        return True
    except Exception as e:
        if is_raise:
            raise e
        else:
            return False


def list_all_users(verbose=1) -> List[str]:
    """
    列出user_addr文件夹下所有的.txt用户配置
    :param verbose: 0:不显示print 1:显示print
    :return: 列表，包含全部合法的用户配置文件
    """
    if not os.path.exists(user_addr):
        os.makedirs(user_addr)
    ld = os.listdir(user_addr)
    users = []
    count = 0
    for i in ld:
        if not os.path.isdir(i) and i.endswith(".txt"):
            try:
                # 检查是否能打开文件，以及是否含有必要的参数
                target_name = "%s/%s" % (user_addr, i)
                f = open(target_name, "r", encoding="utf-8")
                d = json.load(f)
                check_user_dict(d, True)
                f.close()
                users += [i[:-4]]
                if verbose:
                    print("用户配置", i, "加载成功！")
                count += 1
            except Exception as e:
                if verbose:
                    print("打开配置", i, "失败！", e)
    if verbose:
        print("加载完成，一共加载成功", count, "个用户配置。")
    return users


def list_all_tasks(verbose=1) -> List[str]:
    """
    列出task_addr文件夹下所有.txt的任务配置
    :param verbose: 0:不显示print 1:显示print
    :return: 列表，包含全部任务配置文件
    """
    if not os.path.exists(task_addr):
        os.makedirs(task_addr)
    ld = os.listdir(task_addr)
    tasks = []
    count = 0
    for i in ld:
        if not os.path.isdir(i) and i.endswith(".txt"):
            try:
                # 检查是否能打开文件，以及是否含有必要的参数
                target_name = "%s/%s" % (task_addr, i)
                f = open(target_name, "r", encoding="utf-8")
                d = json.load(f)
                check_task_dict(d, True)
                f.close()
                tasks += [i[:-4]]
                if verbose:
                    print("任务配置", i, "加载成功！")
                count += 1
            except Exception as e:
                if verbose:
                    print("打开配置", i, "失败！", e)
    if verbose:
        print("加载完成，一共加载成功", count, "个任务配置。")
    return tasks


def check_users_exists(users: List[str], is_raise=True) -> bool:
    all_users = list_all_users(0)
    for i in users:
        if i not in all_users:
            if is_raise:
                raise Exception(f"用户 {i} 不存在！")
            else:
                return False
    return True


def list_all_groups(verbose=1) -> List[str]:
    if not os.path.exists(group_addr):
        os.makedirs(group_addr)
    ld = os.listdir(group_addr)
    groups = []
    count = 0
    for i in ld:
        if not os.path.isdir(i) and i.endswith(".txt"):
            try:
                users = AutomatorRecorder.getgroup(i[:-4])
                check_users_exists(users)
                if verbose:
                    print("组配置", i, "加载成功！")
                count += 1
            except Exception as e:
                if verbose:
                    print("打开组配置", i, "失败！", e)
    if verbose:
        print("加载完成，一共加载成功", count, "个组配置。")
    return groups


def check_valid_batch(batch: dict, is_raise=True) -> bool:
    try:
        assert "batch" in batch
        B = batch["batch"]
        assert type(B) is list
        for i in B:
            f1 = "account" in i
            f2 = "group" in i
            if f1 + f2 == 0:
                raise Exception("必须至少含有account,group中的一个！")
            if f1 + f2 == 2:
                raise Exception("account和group键只能出现其中一个！")
            assert "taskfile" in i
            assert type("taskfile") is str
            assert "priority" in i

    except Exception as e:
        if is_raise:
            raise e
        else:
            return False
    return True


def list_all_batches(verbose=1) -> List[str]:
    if not os.path.exists(batch_addr):
        os.makedirs(batch_addr)
    ld = os.listdir(batch_addr)
    batches = []
    count = 0
    for i in ld:
        if not os.path.isdir(i) and i.endswith(".txt"):
            nam = ""
            try:
                nam = i[:-4]
                batch = AutomatorRecorder.getbatch(nam)
                check_valid_batch(batch)
                batches += [nam]
                if verbose:
                    print("批配置", nam, "加载成功！")
                count += 1
            except Exception as e:
                if verbose:
                    print("打开批配置", nam, "失败！", e)
    if verbose:
        print("加载完成，一共加载成功", count, "个批配置。")
    return batches


def check_valid_schedule(schedule: dict, is_raise=True) -> bool:
    try:
        assert "schedules" in schedule
        S = schedule["schedules"]
        assert type(S) is list
        for i in S:
            assert "type" in i
            assert i["type"] in ["asap", "wait", "config"]
            if i["type"] in ["asap", "wait"]:
                f1 = "batchfile" in i
                f2 = "batchlist" in i
                assert (f1 + f2) == 1, "batchfile 和 batchlist关键字只能存在其一！"
                if "batchfile" in i:
                    assert type(i["batchfile"]) is str
                if "batchlist" in i:
                    assert type(i["batchlist"]) is list
                assert "condition" in i
                assert type(i["condition"]) is dict
                if "record" not in i:
                    i["record"] = 0
                assert "record" in i
                assert type(i["record"]) is int
                

    except Exception as e:
        if is_raise:
            raise e
        else:
            return False
    return True


def list_all_schedules(verbose=1) -> List[str]:
    if not os.path.exists(schedule_addr):
        os.makedirs(schedule_addr)
    ld = os.listdir(schedule_addr)
    schedules = []
    count = 0
    for i in ld:
        if not os.path.isdir(i) and i.endswith(".txt"):
            nam = ""
            try:
                nam = i[:-4]
                schedule = AutomatorRecorder.getschedule(nam)
                check_valid_schedule(schedule)
                schedules += [nam]
                if verbose:
                    print("计划配置", nam, "加载成功！")
                count += 1
            except Exception as e:
                if verbose:
                    print("打开计划配置", nam, "失败！", e)
    if verbose:
        print("加载完成，一共加载成功", count, "个计划配置。")
    return schedules


def init_user(account: str, password: str) -> bool:
    """
    以account和password在user_addr下新增一条用户记录
    :param account: 用户名
    :param password: 密码
    :return: 是否成功创建
    """
    target_name = "%s/%s.txt" % (user_addr, account)
    if os.path.exists(target_name):
        print("配置", account, "已经存在。")
        return False
    try:
        f = open(target_name, "w", encoding="utf-8")
        d = dict(account=account, password=password)
        json.dump(d, f, indent=1)
        f.close()
    except Exception as e:
        print("存储配置时遇到错误：", e)
        return False
    return True

def parse_batch(batch: dict):
    """
    解析batch，统一转化为Tuple(priority, account, taskfile task)
    并且装入优先级队列中。
    其中task为解析后的dict
    :param batch: 合法的batch字典
    :return: Tuple(priority, account, taskfile,task)
    """
    B = batch["batch"]
    L = []
    for cur in B:
        task = AutomatorRecorder.gettask(cur["taskfile"])
        if "account" in cur:
            L += [(cur["priority"], cur["account"], cur["taskfile"], task)]
        elif "group" in cur:
            G = AutomatorRecorder.getgroup(cur["group"])
            for mem in G:
                L += [(cur["priority"], mem, cur["taskfile"], task)]
    L.sort(reverse=True)
    return L

class AutomatorRecorder:
    """
    在Automator中提供静态存储空间
    含有多个分区，名称为XXX的分区将在user_addr内创建一个名称为XXX的文件夹
        注：分区user在user_addr根目录下
    每一个分区内，创建一条%account%.txt的记录文件，均为json格式
    """

    def __init__(self, account, rec_addr="users/run_status"):
        """
        :param account: 账号名称
        :param rec_addr: 记录位置（只影响run_status的获取）
        """
        self.account = account
        self.rec_addr = rec_addr

    @staticmethod
    def _load(jsonaddr) -> Optional[dict]:
        """
        读取json文件。输出字典类型
        :param jsonaddr: json地址
        :return: 一个字典，json的内容
        """
        try:
            f = open(jsonaddr, "r", encoding="utf-8")
            d = json.load(f)
            f.close()
            return d
        except Exception as e:
            print("读取json出现错误：", e)
            return None

    @staticmethod
    def _save(jsonaddr, obj) -> bool:
        """
        将obj保存进jsonaddr
        :param jsonaddr: json地址
        :param obj: 要保存的obj类型
        :return: 是否保存成功
        """
        dir = os.path.dirname(jsonaddr)
        if not os.path.isdir(dir):
            os.makedirs(dir)
        try:
            f = open(jsonaddr, "w", encoding="utf-8")
            json.dump(obj, f, indent=1)
            f.close()
            return True
        except Exception as e:
            print("保存json出现错误：", e)
            return False

    def getuser(self) -> dict:
        target_name = "%s/%s.txt" % (user_addr, self.account)
        d = self._load(target_name)
        check_user_dict(d, True)
        return d

    @staticmethod
    def gettask(taskfile) -> dict:
        target_name = "%s/%s.txt" % (task_addr, taskfile)
        d = AutomatorRecorder._load(target_name)
        check_task_dict(d, True)
        return d

    @staticmethod
    def getgroup(groupfile) -> list:
        target_name = "%s/%s.txt" % (group_addr, groupfile)
        users = []
        with open(target_name, "r", encoding="utf-8") as f:
            for j in f:
                line = j.strip()
                if line == "":
                    continue
                if line[0] == "#":
                    continue
                users += [line]
        check_users_exists(users)
        return users

    @staticmethod
    def getbatch(batchfile) -> dict:
        target_name = "%s/%s.txt" % (batch_addr, batchfile)
        d = AutomatorRecorder._load(target_name)
        check_valid_batch(d)
        return d

    @staticmethod
    def getschedule(schedulefile):
        target_name = "%s/%s.txt" % (schedule_addr, schedulefile)
        d = AutomatorRecorder._load(target_name)
        check_valid_schedule(d)
        return d

    def setuser(self, userobj: dict):
        target_name = "%s/%s.txt" % (user_addr, self.account)
        if check_user_dict(userobj, is_raise=False):
            AutomatorRecorder._save(target_name, userobj)
        else:
            print("用户文件不合法，保存失败")

    @staticmethod
    def settask(taskfile, taskobj: dict):
        target_name = "%s/%s.txt" % (task_addr, taskfile)
        if check_task_dict(taskobj, is_raise=False):
            AutomatorRecorder._save(target_name, taskobj)
        else:
            print("任务文件不合法，保存失败")

    @staticmethod
    def setbatch(batchfile, batchobj: dict):
        target_name = "%s/%s.txt" % (batch_addr, batchfile)
        if check_valid_batch(batchobj, is_raise=False):
            AutomatorRecorder._save(target_name, batchobj)
        else:
            print("批配置不合法，保存失败")

    @staticmethod
    def setschedule(schedulefile, scheduleobj: dict):
        target_name = "%s/%s.txt" % (schedule_addr, schedulefile)
        if check_valid_schedule(scheduleobj, is_raise=False):
            AutomatorRecorder._save(target_name, scheduleobj)
        else:
            print("计划配置不合法，保存失败")

    @staticmethod
    def get_user_state(acc, rec_addr):
        """
        以字符串的形式返回某一个账号的状态
        """
        rs = AutomatorRecorder(acc, rec_addr).get_run_status()
        if rs["error"] is not None:
            state = f"执行于 {rs['current']} 时发生错误：{rs['error']}"
        else:
            if rs["finished"]:
                state = "完成"
            else:
                state = f"执行中：{rs['current']}"
        return state

    @staticmethod
    def get_batch_state(batch, rec_addr):
        """
        返回某一个batch中所有涉及到的账号的状态
        {
            detail[acc]:{
                state_str: 字符串表示的状态
                current：  正在执行
                error：    产生错误
                finished： 完成表只
            }
            total:   batch内acc总数
            finish:  完成的acc总数
            error:   出错的acc总数
        }

        """
        parsed = parse_batch(AutomatorRecorder.getbatch(batch))
        ALL = {}
        D = {}
        tot = 0
        err_cnt = 0
        finish_cnt = 0
        for _, acc, _, _ in parsed:
            if acc not in D:
                tot += 1
                d = {}
                rs = AutomatorRecorder(acc, rec_addr).get_run_status()
                d["state_str"] = AutomatorRecorder.get_user_state(acc, rec_addr)
                d["current"] = rs["current"]
                d["error"] = rs["error"]
                d["finished"] = rs["finished"]
                if rs["error"] is not None:
                    err_cnt += 1
                elif rs["finished"] is True:
                    finish_cnt += 1
                D[acc] = d
        ALL["detail"] = D
        ALL["total"] = tot
        ALL["error"] = err_cnt
        ALL["finish"] = finish_cnt
        return ALL

    def get(self, key: str, default: Optional[dict] = None) -> dict:
        """
        获取某一个分区对应的记录
        :param key: 分区名称
        :param default: 默认值，如果获取的记录不存在，则以default创建该记录
        :return: 该分区的dict
        """
        target_name = "%s/%s/%s.txt" % (user_addr, key, self.account)
        dir = os.path.dirname(target_name)
        if default is not None and (not os.path.isdir(dir) or not os.path.exists(target_name)):
            self._save(target_name, default)

        now = self._load(target_name)
        flag = False
        # 检查缺失值，用默认值填充
        for k, v in default.items():
            if k not in now:
                now[k] = v
                flag = True
        if flag:
            self._save(target_name, now)
        return now

    def set(self, key: str, obj: dict) -> bool:
        """
        保存某一个分区对应的记录
        :param key: 分区名称
        :param obj: 要保存的dict
        :return: 是否保存成功
        """
        target_name = "%s/%s/%s.txt" % (user_addr, key, self.account)
        return self._save(target_name, obj)

    def get_run_status(self):
        """
        获取运行时状态
        :return: run_status
        """
        target_name = os.path.join(self.rec_addr, "run_status", f"{self.account}.txt")
        dir = os.path.dirname(target_name)
        default = UDD["run_status"]
        if not os.path.isdir(dir) or not os.path.exists(target_name):
            self._save(target_name, default)
        now = self._load(target_name)
        flag = False
        # 检查缺失值，用默认值填充
        for k, v in default.items():
            if k not in now:
                now[k] = v
                flag = True
        if flag:
            self._save(target_name, now)
        return now

    def set_run_status(self, rs):
        """
        设置运行时状态
        """
        target_name = os.path.join(self.rec_addr, "run_status", f"{self.account}.txt")
        return self._save(target_name, rs)
