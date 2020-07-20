import json
import os
from typing import List, Optional

"""
用户文件存储说明：
默认路径：/users
存储格式：json
必须要含有的元素：
{
    "account":"..."  # 用户名
    "password":"..." # 密码
}

"""
user_addr = "users"  # 存放用户配置的文件夹


def check_user_dict(d: dict, is_raise=False) -> bool:
    """
    检查一个用户配置文件是否合法。
    :param d: 解析后的用户配置字典
    :param is_raise: 对于不合法的地方是否弹出错误
    :return: 是否合法
    """
    try:
        assert "account" in d, "必须含有account关键字以存储用户名！"
        assert "password" in d, "必须含有password关键字以存储密码！"
        return True
    except Exception as e:
        if is_raise:
            raise e
        else:
            return False


def list_all_users() -> List[str]:
    """
    列出user_addr文件夹下所有的.txt用户配置
    :return: 列表，包含全部合法的用户配置文件
    """
    ld = os.listdir(user_addr)
    users = []
    count = 0
    for i in ld:
        if not os.path.isdir(i) and i.endswith(".txt"):
            try:
                # 检查是否能打开文件，以及是否含有必要的参数
                target_name = "%s\\%s" % (user_addr, i)
                f = open(target_name, "r")
                d = json.load(f)
                check_user_dict(d, True)
                f.close()
                users += [target_name]
                print("用户配置", i, "加载成功！")
                count += 1
            except Exception as e:
                print("打开配置", i, "失败！", e)
    print("加载完成，一共加载成功", count, "个用户配置。")
    return users


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
        f = open(target_name, "w")
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
            f = open(jsonaddr, "r")
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
            f = open(jsonaddr, "w")
            json.dump(obj, f, indent=1)
            f.close()
            return True
        except Exception as e:
            print("保存json出现错误：", e)
            return False

    def getuser(self) -> dict:
        target_name = "%s\\%s.txt" % (user_addr, self.account)
        d = self._load(target_name)
        check_user_dict(d)
        return d

    def setuser(self, userobj: dict):
        target_name = "%s\\%s.txt" % (user_addr, self.account)
        if check_user_dict(userobj):
            self._save(target_name, userobj)
        else:
            print("用户文件不合法，保存失败")

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
        return self._load(target_name)

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
