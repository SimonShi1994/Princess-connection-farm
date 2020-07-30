import json
import os
from typing import List, Optional

from core.valid_task import VALID_TASK

"""
用户文件存储说明：
默认路径：/users
存储格式：json
必须要含有的元素：
{
    "account":"..."  # 用户名
    "password":"..." # 密码
    "taskfile":"..." #任务配置文件名 如果为""则不进行任务。
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
"""
user_addr = "users"  # 存放用户配置的文件夹
task_addr = "tasks"  # 存放任务配置的文件夹


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
        assert "taskfile" in d, "必须含有任务列表taskfile！"
        assert type(d["taskfile"]) is str, f"tasks必须为字符串类型而不应是{type(d['tasks'])}"
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
                if j.default is not None:
                    assert j.key in i, f"任务 {i['type']} 必须含有参数 {j.key}！"

            v_k = [i.key for i in params]
            v_p = [i for i in params]
            for k in i:
                if k == "type":
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
                target_name = "%s\\%s" % (user_addr, i)
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
                target_name = "%s\\%s" % (task_addr, i)
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


def init_user(account: str, password: str) -> bool:
    """
    以account和password在user_addr下新增一条用户记录
    :param account: 用户名
    :param password: 密码
    :return: 是否成功创建
    """
    target_name = "%s\\%s.txt" % (user_addr, account)
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


class AutomatorRecorder:
    """
    在Automator中提供静态存储空间
    含有多个分区，名称为XXX的分区将在user_addr内创建一个名称为XXX的文件夹
        注：分区user在user_addr根目录下
    每一个分区内，创建一条%account%.txt的记录文件，均为json格式
    """

    def __init__(self, account):
        """
        :param account: 账号名称
        """
        self.account = account

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
        target_name = "%s\\%s.txt" % (user_addr, self.account)
        d = self._load(target_name)
        check_user_dict(d, True)
        return d

    @staticmethod
    def gettask(taskfile) -> dict:
        target_name = "%s\\%s.txt" % (task_addr, taskfile)
        d = AutomatorRecorder._load(target_name)
        check_task_dict(d, True)
        return d

    def setuser(self, userobj: dict):
        target_name = "%s\\%s.txt" % (user_addr, self.account)
        if check_user_dict(userobj):
            AutomatorRecorder._save(target_name, userobj)
        else:
            print("用户文件不合法，保存失败")

    @staticmethod
    def settask(taskfile, taskobj: dict):
        target_name = "%s\\%s.txt" % (task_addr, taskfile)
        if check_task_dict(taskobj):
            AutomatorRecorder._save(target_name, taskobj)
        else:
            print("任务文件不合法，保存失败")

    def get(self, key: str, default: Optional[dict] = None) -> dict:
        """
        获取某一个分区对应的记录
        :param key: 分区名称
        :param default: 默认值，如果获取的记录不存在，则以default创建该记录
        :return: 该分区的dict
        """
        target_name = "%s\\%s\\%s.txt" % (user_addr, key, self.account)
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
        target_name = "%s\\%s\\%s.txt" % (user_addr, key, self.account)
        return self._save(target_name, obj)


if __name__ == "__main__":
    # 测试
    AR = AutomatorRecorder("testaccount")
    init_user("testaccount", "testpassword")
    init_user("abc", "def")
    init_user("cde", "fff")
    print(list_all_users())
    print(AR.getuser())
    test_info = {"time": 0, "lv": 60}
    TI = AR.get("test_info", test_info)
    TI["lv"] += 10
    AR.set("test_info", TI)
