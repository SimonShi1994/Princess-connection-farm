import abc
import importlib
from math import inf
from typing import List, Type, Any, Optional, Union

from core import log_handler
from core.constant import NORMAL_COORD, HARD_COORD, MAX_MAP
from core.pcr_config import debug


class InputBoxBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def create(self) -> Union[int, float, list, dict, str]:
        pass

    @abc.abstractmethod
    def check(self, obj) -> str:
        """
        传入obj，如果没有问题输出""，否则输出错误信息
        """
        pass

    def edit(self, obj):
        """
        默认编辑=重新写一个
        """
        return self.create()


def RangeStr(min, max):
    if min == -inf and max == inf:
        return ""
    elif min == -inf:
        return f"( <={max} )"
    elif max == inf:
        return f"( >={min} )"
    else:
        return f"( {min}~{max} )"


class IntInputer(InputBoxBase):
    def __init__(self, min=-inf, max=inf, ):
        self.min = min
        self.max = max

    def create(self) -> int:
        while True:
            a = input("请输入一个整数" + RangeStr(self.min, self.max))
            try:
                a = int(a)
                if self.min <= int(a) <= self.max:
                    return int(a)
                else:
                    print("输入错误，请重新输入")
            except:
                print("输入错误，清重新输入")

    def check(self, obj):
        if not isinstance(obj, int):
            return f"应是int类型，而不是{type(obj)}"
        return ""


class FloatInputer(InputBoxBase):
    def create(self) -> float:
        while True:
            a = input("请输入一个实数 ")
            try:
                return float(a)
            except:
                print("输入错误，请重新输入")

    def check(self, obj):
        if not isinstance(obj, (float, int)):
            return f"应是float类型，而不是{type(obj)}"
        return ""


class StrInputer(InputBoxBase):
    def __init__(self, desc=""):
        self.desc = desc

    def create(self) -> str:
        if self.desc != "":
            print(self.desc)
        a = input("请输入一个字符串 ")
        return a

    def check(self, obj):
        if not isinstance(obj, str):
            return f"应是str类型，而不是{type(obj)}"
        return ""


class BoolInputer(InputBoxBase):
    def create(self) -> bool:
        while True:
            a = input("请输入True或False ")
            if a == "True":
                return True
            elif a == "False":
                return False
            else:
                print("输入错误，请重新输入")

    def check(self, obj):
        if not isinstance(obj, bool):
            return f"应是str类型，而不是{type(str)}"
        return ""


STANDARD_INPUTBOX = {
    int: IntInputer(),
    float: FloatInputer(),
    str: StrInputer(),
    bool: BoolInputer()
}


# 合法Task参数
class TaskParam:
    def __init__(self, key: str, typ: Optional[Type] = None, title: Optional[str] = None,
                 desc: Optional[str] = None,
                 default: Optional[Any] = None, inputbox=None):
        """
        构建一个合法Task的参数
        :param key:
            参数的名字，最终调用Automator的函数时，与函数参数的名字一一对应。
        :param typ:
            参数的类型，如果不是指定类型则判定不合法。
            默认为None，则任何类型均可
            可以指定为某一个type，则必须要求该参数类型为type
        :param title:
            参数的标题，显示给用户看。
        :param desc:
            参数的描述，显示给用户看。
        :param default:
            参数的默认值，默认为None，则表示强制输入该参数。
            如果设置了默认值，则该参数将以default进行初始化。
        :param inputbox:
            如果typ非int,float,bool，则需要专门制定inputbox。
            用来输入该类型
        """
        self.key = key
        self.typ = typ
        if title is None:
            self.title = self.key
        else:
            self.title = title
        if desc is None:
            self.desc = "没有描述"
        else:
            self.desc = desc
        self.default = default
        if inputbox is None:
            if typ in STANDARD_INPUTBOX:
                self.inputbox = STANDARD_INPUTBOX[typ]
            else:
                raise Exception(f"参数{key}必须为类型{typ}指定输入方法！")
        else:
            self.inputbox = inputbox

    def check(self, obj, is_raise=True):
        s = self.inputbox.check(obj)
        if s != "":
            if is_raise:
                raise Exception(f"参数{self.key}填写错误：{s}")
            else:
                return False
        return True


class ConstantInputer(InputBoxBase):
    def __init__(self, c):
        self.c = c

    def create(self):
        return self.c

    def check(self, obj):
        # if obj != self.c:
        #     return "必须是 " + str(self.c) + " !"
        return ""


class ValidTask:
    def __init__(self):
        self.__log = log_handler.pcr_log("ValidTask")
        self.T = {}  # 存放合法Task记录

    def add_custom(self, pymodule: str):
        py = None
        try:
            if debug:
                self.__log.write_log('debug', f"Loading pymodule:{pymodule}")
            py = getcustomtask(pymodule)
        except Exception as e:
            if debug:
                self.__log.write_log('debug', f"读取自定义模块失败！ {e}")
            return
        if not getattr(py, "__enable__", False):
            return
        valid = getattr(py, "__valid__", ValidTask())
        custom_T = valid.T
        for abbr in custom_T:
            if debug:
                self.__log.write_log('debug', f"添加自定义：{abbr}")
            for illegal in ["self", "var", "funcname", "pymodule"]:
                assert illegal not in custom_T[abbr]["param_dict"], "自定义变量中不能出现" + illegal + "!"
            self.T[abbr] = custom_T[abbr].copy()
            self.T[abbr]["funname"] = "run_custom_task"
            self.T[abbr]["params"] += [
                TaskParam("pymodule", str, "自定义模块名", "自动生成", pymodule, ConstantInputer(pymodule))]
            self.T[abbr]["params"] += [TaskParam("funcname", str, "函数名称", "自动生成", custom_T[abbr]["funname"],
                                                 ConstantInputer(custom_T[abbr]["funname"]))]

    def add(self, abbr: str, funname: str, title: str, desc: str, params: Optional[List[TaskParam]] = None):
        """
        增加一条Task规则
        :param abbr:
            Task的简写，在json文件中唯一表示一个Task。
        :param funname:
            对应到Automator中指定函数的名称
        :param title:
            Task的标题，显示给用户看
        :param desc:
            Task的描述，显示给用户看
        :param params:
            Task的参数，如果为None，则没有参数
            或者为List[TaskParam]，一个列表，里面为TaskParam类型。
            表示所有合法的参数
        """
        if params is None:
            params = []
        param_dict = {}
        for par in params:
            param_dict[par.key] = par
        self.T[abbr] = {
            "funname": funname,
            "title": title,
            "desc": desc,
            "params": params,
            "param_dict": param_dict
        }
        return self


def ShuatuToTuple(lst: list, NEED_T=True) -> list:
    l = []
    for i in lst:
        try:
            ss = i.strip().split("-")
            if NEED_T:
                l += [(int(ss[0]), int(ss[1]), int(ss[2]))]
            else:
                l += [(int(ss[0]), int(ss[1]))]

        except:
            pass
    l.sort()
    return l


class ShuatuBaseBox(InputBoxBase):
    def __init__(self):
        self.NEED_T = True
        self.tu_dict = {}

    def transform(self):
        d = []
        if self.NEED_T:
            for (A, B), T in self.tu_dict.items():
                d += [f"{A}-{B}-{T}"]
        else:
            for (A, B), T in self.tu_dict.items():
                d += [f"{A}-{B}"]
        return d

    def inversetransform(self, d):
        for i in d:
            if self.NEED_T:
                A, B, T = i.split("-")
                A = int(A)
                B = int(B)
                T = int(T)
            else:
                A, B = i.split("-")
                A = int(A)
                B = int(B)
                T = 1
            self.tu_dict[(A, B)] = T

    def Help(self):
        print("帮助（命令用空格隔开）：")
        print("add (A) (B) (Times): 增加刷图：A-B Times次")
        print("add (A) all (Times): 增加刷图：A-全部 Times次")
        print("del (A) (B) (Times): 减少刷图：A-B Times次")
        print("file (FileAddress): 从文件导入")
        print("   该文件由多行组成，每行三个整数A,B,T，表示刷A-B T次")
        print("clear: 清空记录")
        print("show: 显示当前记录")
        print("end: 保存并退出编辑")

    def check(self, obj) -> str:
        if not isinstance(obj, list):
            return f"应是list类型，而不是{type(obj)}"
        for i in obj:
            if not isinstance(i, str):
                return f"list的每一项都应是str类型，但检测到{type(i)}"
            if '-' not in i:
                return f"list的每一项都应是A-B-T的格式，但{i}中不含'-'。"
            ii = i.split('-')
            if len(ii) != 3:
                return f"必须用-分割三个整数，但检测到{i}不符合要求"
            try:
                A = int(ii[0])
                B = int(ii[1])
                T = int(ii[2])
            except:
                return f"必须用-分割三个整数，但检测到{i}不符合要求"
        return ""

    @abc.abstractmethod
    def add(self, A, B, T):
        pass

    @abc.abstractmethod
    def del_(self, A, B, T):
        pass

    def create(self, clear=True) -> list:
        if clear:
            self.tu_dict = {}
        print("输入图号 (help 查看帮助)")
        while True:
            try:
                cmd = input("> ")
                cmds = cmd.split(" ")
                order = cmds[0]
                if order == "clear":
                    self.tu_dict = {}
                elif order == "add":
                    if self.NEED_T:
                        self.add(cmds[1], cmds[2], cmds[3])
                    else:
                        self.add(cmds[1], cmds[2], "1")
                elif order == "del":
                    if self.NEED_T:
                        self.del_(cmds[1], cmds[2], cmds[3])
                    else:
                        self.del_(cmds[1], cmds[2], "1")
                elif order == "show":
                    if self.NEED_T:
                        for A, B, T in ShuatuToTuple(self.transform()):
                            print(f"{A}-{B} {T} 次")
                    else:
                        for A, B in ShuatuToTuple(self.transform(), NEED_T=False):
                            print(f"{A}-{B}")
                elif order == "end":
                    return self.transform()
                elif order == "help":
                    self.Help()
                elif order == "file":
                    with open(cmds[1], "r", encoding="utf-8") as f:
                        for line in f:
                            l = line.strip().split(" ")
                            if self.NEED_T:
                                self.add(l[0], l[1], l[2])
                            else:
                                self.add(l[0], l[1], "1")
                else:
                    print("未知的命令")
            except:
                print("命令输入错误，请重新输入")

    def edit(self, obj):
        self.inversetransform(obj)
        return self.create(clear=False)


class ShuatuNNBox(ShuatuBaseBox):

    def add(self, A, B, T):
        A = int(A)
        if A not in NORMAL_COORD:
            print(f"图号 {A} 未录入")
            return
        T = int(T)
        if B == "all":
            for cat in ['left', 'right']:
                for bb in NORMAL_COORD[A][cat].keys():
                    self.tu_dict.setdefault((A, bb), 0)
                    self.tu_dict[(A, bb)] += T
        else:
            B = int(B)
            if B not in NORMAL_COORD[A]["left"] and B not in NORMAL_COORD[A]["right"]:
                print(f"图号 {A} - {B} 未录入")
                return
            self.tu_dict.setdefault((A, B), 0)
            self.tu_dict[(A, B)] += T

    def del_(self, A, B, T):
        A = int(A)
        if A not in NORMAL_COORD:
            print(f"图号 {A} 未录入")
            return
        B = int(B)
        T = int(T)
        if (A, B) in self.tu_dict:
            self.tu_dict[(A, B)] -= T
            if self.tu_dict[(A, B)] <= 0:
                del self.tu_dict[(A, B)]


class ShuatuHHBox(ShuatuBaseBox):
    def Help(self):
        print("输入图号")
        print("帮助（命令用空格隔开）：")
        print("add (A) (B) (Times): 增加刷图：A-B Times次")
        print("del (A) (B) (Times): 减少刷图：A-B Times次")
        print("file (FileAddress): 从文件导入")
        print("   该文件由多行组成，每行三个整数A,B,T，表示刷A-B T次")
        print("clear: 清空记录")
        print("show: 显示当前记录")
        print("end: 保存并退出编辑")

    def add(self, A, B, T):
        A = int(A)
        if A not in HARD_COORD:
            print(f"图号 {A} 未录入")
            return
        B = int(B)
        if B not in HARD_COORD[A]:
            print(f"图号H{A} - {B} 未录入")
            return
        T = int(T)
        self.tu_dict.setdefault((A, B), 0)
        self.tu_dict[(A, B)] += T

    def del_(self, A, B, T):
        A = int(A)
        if A not in HARD_COORD:
            print(f"图号 {A} 未录入")
            return
        B = int(B)
        T = int(T)
        if (A, B) in self.tu_dict:
            self.tu_dict[(A, B)] -= T
            if self.tu_dict[(A, B)] <= 0:
                del self.tu_dict[(A, B)]


class TeamInputer(InputBoxBase):
    def __init__(self):
        self.l = []

    def create(self) -> list:
        print("请输入队号")
        print("输入 A-B 表示使用编组A队伍B，其中A为1~5整数，B为1~3整数")
        print("输入 zhanli 表示按照战力取前五位组队")
        print("输入 end 结束编辑")
        count = 1
        self.l = []
        while True:
            try:
                s = input(f"队伍 {count}:")
                if s == "zhanli":
                    self.l += ["zhanli"]
                    count += 1
                    continue
                if s == "end":
                    return self.l
                ss = s.split("-")
                assert len(ss) == 2
                assert 1 <= int(ss[0]) <= 5
                assert 1 <= int(ss[1]) <= 3
                count += 1
                self.l += [s]
            except:
                print("输入有误，请重新输入")

    def check(self, obj) -> str:
        if not isinstance(obj, list):
            return f"应是list类型，而不是{type(obj)}"
        for i in obj:
            if not isinstance(i, str):
                return f"list的每一项都应是str类型，但检测到{type(i)}"
            if i == "" or i == "zhanli":
                continue
            if '-' not in i:
                return f"list的每一项都应是A-B的格式，或者为zhanli，但{i}不满足要求。"
            ii = i.split('-')
            if len(ii) != 2:
                return f"必须用-分割两个整数，但检测到{i}不符合要求"
            try:
                A = int(ii[0])
                B = int(ii[1])
            except:
                return f"必须用-分割两个整数，但检测到{i}不符合要求"
            if A < 1 or A > 5:
                return f"队号A-B中编组A必须为1~5的整数，但{i}不满足要求"
            if B < 1 or B > 3:
                return f"队号A-B中队伍B必须为1~3的整数，但{i}不满足要求"
        return ""


TeamOrderInputer = StrInputer(desc="none - 不改变队伍，使用上次队伍。\n"
                                   "zhanli   -   按照战力排序取前五。\n"
                                   "dengji   -   按照等级排序取前五。\n"
                                   "xingshu   -   按照星级排序取前五。\n"
                                   "shoucang -   按照收藏排序取前五。\n"
                                   "nobody -  不上任何人（只上支援，没支援就会出错）\n"
                                   "(A)-(B) - 使用队伍编组A-B，且1<=A<=5,1<=B<=3。\n"
                                   "Example:  3-1  # 编组3队伍1.")

"""
class MeiRiHTuInputer(ShuatuBaseBox):
    def __init__(self):
        super().__init__()
        self.NEED_T=False

    def Help(self):
        print("输入图号")
        print("帮助（命令用空格隔开）：")
        print("add (A) (B): 增加刷图：H A-B")
        print("del (A) (B): 减少刷图：H A-B")
        print("file (FileAddress): 从文件导入")
        print("   该文件由多行组成，每行两个整数A,B，表示刷H A-B")
        print("clear: 清空记录")
        print("show: 显示当前记录")
        print("end: 保存并退出编辑")

    def add(self, A, B, T):
        A = int(A)
        if A not in HARD_COORD:
            print(f"图号 {A} 未录入")
            return
        B = int(B)
        if B not in HARD_COORD[A]:
            print(f"图号H{A} - {B} 未录入")
            return
        self.tu_dict.setdefault((A, B), 0)
        self.tu_dict[(A, B)] = 1

    def del_(self, A, B, T):
        A = int(A)
        if A not in HARD_COORD:
            print(f"图号 {A} 未录入")
            return
        B = int(B)
        if (A, B) in self.tu_dict:
            del self.tu_dict[(A, B)]


    def check(self, obj):
        if type(obj) is not list:
            return "参数必须为list类型"
        for s in obj:
            try:
                a, b = tuple(s.split("-"))
                A = int(a)
                B = int(b)
                assert 1 <= B <= 3, "图号不合法"
                assert 1 <= A <= max(HARD_COORD), "图号不合法"
            except Exception as e:
                return str(e)
        return ""

"""


class MeiRiHTuInputer(InputBoxBase):
    def create(self):
        print("输入A-B字符串，表示刷Hard A-B图。")
        print("输入end结束。")
        lst = []
        while True:
            s = input(">")
            if s == "end":
                break
            else:
                lst += [s]
        return lst

    def check(self, obj):
        if type(obj) is not list:
            return "参数必须为list类型"
        for s in obj:
            try:
                a, b = tuple(s.split("-"))
                A = int(a)
                B = int(b)
                assert 1 <= B <= 3, "图号不合法"
                assert 1 <= A <= max(HARD_COORD), "图号不合法"
            except Exception as e:
                return str(e)
        return ""


class ListInputer(InputBoxBase):
    def __init__(self, convert=None, desc=""):
        super().__init__()
        self.desc = desc
        if convert is None:
            self.convert = lambda x: x
        else:
            self.convert = convert

    def create(self):
        print("一行输入一些东西，表示列表中每一行的值。")
        print(self.desc)
        print("啥都不输入直接回车结束。")
        lst = []
        while True:
            s = input(">")
            if s == "":
                break
            else:
                lst += [self.convert(s)]
        return lst

    def check(self, obj):
        if type(obj) is not list:
            return "参数必须为list类型"
        return ""


class StrChooseInputer(InputBoxBase):
    def __init__(self, choose_dict):
        super().__init__()
        self.choose_dict = choose_dict

    def create(self) -> str:
        print("请输入下列字符串之一：")
        for k, v in self.choose_dict.items():
            print(k, "  :  ", v)
        a = input(">")
        return a

    def check(self, obj):
        if not isinstance(obj, str):
            return f"应是str类型，而不是{type(str)}"
        if obj not in self.choose_dict:
            return f"{obj}只能在{list(self.choose_dict)}中选择！"
        return ""


team_order_inputer = StrInputer(desc="none - 不改变队伍，使用上次队伍。\n"
                                     "zhanli - 按照战力排序取前五。\n"
                                     "dengji - 按照等级排序取前五。\n"
                                     "xingshu - 按照星级排序取前五。\n"
                                     "shoucang - 按照收藏排序取前五。\n"
                                     "(A)-(B) - 使用队伍编组A-B，且1<=A<=5,1<=B<=3。\n"
                                     "Example:  3-1  # 编组3队伍1.")

zhiyuan_mode_kwargs = {
    "typ": int,
    "title": "支援模式",
    "desc": "0  - 不使用支援\n"
            "1  - 当有好友助战时使用好友支援+自己队伍，否则直接结束推图。\n"
            "-1 - 当有好友助战时仅使用好友支援一人推图，否则直接结束推图。\n"
            "2  - 当有好友助战时使用好友支援+自己队伍，否则不使用支援自己推图。\n"
            "-2 - 当有好友助战时仅使用好友支援一人推图，否则不使用支援自己推图。\n"
            "3  - 任意选择一个支援+自己队伍推图。\n"
            "-3 - 任意选择一个支援仅支援一人推图。\n",
    "default": 0,
}

huodong_code_kwargs = {
    "key": "code",
    "typ": str,
    "title": "图号代码",
    "desc": """输入"current"表示当前进行的活动，其它代码见scenes/huodong/huodong_manager.py中，
get_huodong_by_code函数里HUODONG_CODE字典。例如，输入"20230115"表示进行活动"狂奔!兰德索尔公会竞速赛复刻"。""",
    "default": "current",
}
huodong_entrance_ind_kwargs = {
    "key": "entrance_ind",
    "typ": str,
    "title": "活动入口位置",
    "desc": """冒险界面的小圆按钮哪个是活动？
    "auto" - 自动寻找位置
    "1"/"2"/"3" - 从右往左数第几个位置（例如有三个按钮：活动/复刻活动/露娜塔，若要刷复刻活动，则输入"2"。
    """,
    "default": "auto",
}

VALID_TASK = ValidTask() \
    .add("h1", "hanghui", "行会捐赠", "小号进行行会自动捐赠装备",
         [TaskParam("once_times", int, "单账号捐赠的次数", "一个账号轮询捐赠多少次，多次可以提高容错率但会增加脚本执行时间", 2)]) \
    .add("h2", "tichuhanghui", "踢出行会", "将战力排名第一人踢出行会") \
    .add("h3", "yaoqinghanghui", "邀请行会", "邀请指定成员进入行会",
         [TaskParam("inviteUID", str, "UID", "被邀请者的UID号")]) \
    .add("h4", "jieshouhanghui", "接受行会", "接受行会的邀请信息") \
    .add("h5", "joinhanghui", "加入行会【不推荐使用】，建议使用h8", "主动搜索并加入行会",
         [TaskParam("clubname", str, "行会名称", "要加入行会的名称")]) \
    .add("h6", "dianzan", "行会点赞", "给指定人点赞",
         [TaskParam("sortflag", int, "给谁点赞", "只能为0或者1的值\n0：给副会长点赞。\n1：给战力最高者点赞。", 0)]) \
    .add("h7", "zhiyuan", "支援设定", "按照战力排行设定支援（最高的）",
         [TaskParam("zhiyuanjieshu", bool, "支援结束", "是否按下支援结束按钮并收取Mana。", False)]) \
    .add("h8", "join_hanghui", "加入行会", "主动搜索并加入行会（全识图版），已在行会会跳过",
         [TaskParam("clubname", str, "行会名称", "要加入行会的名称")]) \
    .add("h9", "faqijuanzeng", "发起捐赠", "自动发起装备捐赠，需要自行截装备图。",
         [TaskParam("equip_img", str, "装备图片相对路径", "装备图片自行截图。\n"
                                                  "截图要求：在行会-发起捐赠请求中截图并保存到本地\n"
                                                  "截图的大小不得超过装备外框，不得包含右下角的数字。\n"
                                                  "截图需要有代表性。\n"),
          TaskParam("wait_time", int, "等待时间", "如果来早了，还有一定宽容时间。\n"
                                              "程序自动记录上一次成功发起的时间.\n"
                                              "如果两次捐赠小于8小时，且相差小于等待时间\n"
                                              "则程序进入什么都不做的等待，否则跳过。", 300)]) \
    .add("h10", "tuanduizhan", "自动摸会战", "自动用完公会战次数",
         [TaskParam("team_order", str, "选择队伍", "选择什么队伍来推图", default="none",
                    inputbox=team_order_inputer),
          TaskParam("get_zhiyuan", bool, "是否借支援", "是否借人推图", False),
          TaskParam("if_full", int, "借人换下的角色位置", "借人换下的角色位置，一般与选队伍配合使用", 0),
          TaskParam("once", bool, "是否只打一次", "摸一下", True)]) \
    .add("d1", "dixiacheng_ocr", "地下城OCR版本", "小号地下城借人换mana",
         [TaskParam("assist_num", int, "支援位置选择", "选支援第一行的第n个（1-8），等级限制会自动选择第n+1个", 1),
          TaskParam("skip", bool, "跳过战斗", "设置为True时，第一层不打直接撤退。\n设置为False时，打完第一层。", False),
          TaskParam("stuck_today", bool, "卡住地下城", "设置为True时，无论如何，进去地下城但是不打。\n设置为False时，为正常借人。", False),
          TaskParam("stuck_notzhandoukaishi", bool, "无法出击但不撤退", "设置为True时，如果发现无法出击，那就不撤退。\n设置为False时，则相反。", False), ]) \
    .add("d2", "dixiacheng", "地下城非OCR版本", "小号地下城借人换mana",
         [TaskParam("skip", bool, "跳过战斗", "设置为True时，第一层不打直接撤退。\n设置为False时，打完第一层。", False)]) \
    .add("d5", "shuatuDD_OCR", "通关地下城OCR", "【适合大号，借人可能有BUG】通用的打通地下城函数",
         [TaskParam("dxc_id", int, "地下城图号", "刷哪个地下城。\n目前支持:1,3,4,5,6,7,8"),
          TaskParam("mode", int, "模式", "mode 0：不打Boss，用队伍1只打小关\n"
                                       "mode 1：打Boss，用队伍1打小关，用队伍[1,2,3,4,5...]打Boss\n"
                                       "mode 2：打Boss，用队伍1打小关，用队伍[2,3,4,5...]打Boss\n"
                                       "mode 3：用队伍1只打第一小关，无论怎样都退出\n"
                                       "mode 4:（攒TP）用队伍[1,2,3,...,N-1]攒TP(无AUTO)，N为总层数；用队伍[N,N+1,...]打Boss （不支持借人）"),
          TaskParam("stop_criteria", int, "终止条件", "设置为0时，只要战斗中出现人员伤亡，直接结束\n"
                                                  "设置为1时，一直战斗到当前队伍无人幸存，才结束\n"
                                                  "注：如果在小关遇到停止条件，则直接结束\n"
                                                  "打Boss时，如果选用mode 2，则当一个队触发停止条件后会更换下一个队伍\n"
                                                  "直到队伍列表全部被遍历完毕才结束。", 0),
          TaskParam("after_stop", int, "停止之后做什么", "设置为0时，直接回到主页\n"
                                                  "设置为1时，撤退并回到主页\n"
                                                  "注：如果mode==1（不打Boss），则打完小关之后是否撤退仍然受到该参数的影响", 0),
          TaskParam("teams", list, "编队列表", "编队列表，参战地下城所使用的编队\n"
                                           "按照列表顺序分别表示编队1号，2号，3号……\n"
                                           "每一个元素为一个字符串\n"
                                           "若为\"zhanli\"，则按照相关排序，选择前五最高为当前队伍\n"
                                           "若为\"a-b\",其中a为1~5的整数，b为1~3的整数，则选择编组a队伍b", inputbox=TeamInputer()),
          TaskParam("safety_stop", int, "安全保护", "防止大号误撤退。\n设置为0时，不管；\n设置为1时，若小关伤亡惨重，直接返回主页不撤退。", 1),
          TaskParam("assist", int, "支援设置", "0表示不用支援，1~16选支援第1/2行的第n个（1-8）(9-16)，等级限制会自动选择第n+1个", 0),
          TaskParam("fight_detail", str, '战斗细节', '（默认推荐）空字符串： 默认全程auto，不过mode=4在攒TP时关闭auto\n'
                                                 '（攒TP时可用）用逗号隔开N个子串（N为队伍总数）：每个队伍对应的战斗细节\n'
                                                 '    对每个隔开的子串：仅应该包含AB12345XYZ这10种字符之一。\n'
                                                 '    auto控制：A - 打开auto   B - 关闭auto  若不设置，默认打开auto（攒TP时默认关闭）\n'
                                                 '    连点控制：12345分别表示从左到右的5个位置是否需要在战斗中连点\n'
                                                 '    速度控制：XYZ分别表示1，2，4倍速 若不设置，默认4倍速。\n'
                                                 '        eg. 若用4队攒TP（连点12位，为了防止打太快设置2倍速），56队打BOSS（全程AUTO），则该参数可以设置为：\n'
                                                 '        B12Y,B12Y,B12Y,B12Y,AZ,AZ', default=""),
          ]) \
    .add("d6", "dixiacheng_skip", "地下城跳过战斗", "一键刷地下城并跳过战斗（要求通关）", 
         [TaskParam("dxc_id", int, "地下城图号", "刷哪个地下城。\n目前支持:1,3,4,5,6,7,8"),]) \
    .add("j1", "doJJC", "竞技场", "竞技场白给脚本") \
    .add("j2", "doPJJC", "公主竞技场", "公主竞技场白给脚本") \
    .add("r1", "gonghuizhijia", "家园领取", "收取公会之家的奖励",
         [TaskParam("auto_update", bool, "自动升级家具", "自动升级家具，家具的位置为游戏默认位置", False), ]) \
    .add("r2", "mianfeiniudan", "免费扭蛋", "抽取免费扭蛋") \
    .add("r3", "mianfeishilian", "免费10连", "抽取免费十连（如果有的话）",
         [TaskParam("select", int, "附奖选择", "选择附奖角色（请输入1或者2）", 1)]) \
    .add("r4", "shouqu", "收取礼物", "收取全部礼物") \
    .add("r5", "shouqurenwu", "收取任务", "收取全部任务奖励。\n如果日常任务和主线任务都存在，需要收取两遍。") \
    .add("r6", "goumaitili", "购买体力", "购买一定次数的体力",
         [TaskParam("times", int, "购买次数", "购买体力的次数"),
          TaskParam("limit_today", bool, "是否用times限制今天脚本购买体力的次数", "True/False", False), ]) \
    .add("r7", "goumaimana", "购买MANA", "购买指定次数的mana",
         [TaskParam("mode", int, "模式", "如果mode为0，则为购买mana的次数；\n如果mode为1，则为购买10连mana的次数。【宝石警告】", 1),
          TaskParam("times", int, "购买mana的次数", "购买mana的次数(第一次单抽不计入)"),
          TaskParam("limit_today", bool, "是否用times限制今天脚本购买mana的次数", "True/False", False), ]) \
    .add("r8", "buyExp", "购买经验", "买空商店里的经验药水",
         [TaskParam("qianghuashi", bool, "是否同时购买强化石", "True/False", False)]) \
    .add("r8-xd", "buyXDShop", "限定商店", "买空限定商店",
         [TaskParam("buy_exp", bool, "购买限定商店经验药水", "True/False", True),
          TaskParam("buy_equip", bool, "购买限定商店装备碎片", "True/False", True)]) \
    .add("r9", "tansuo", "探索【不推荐】", "【非OCR，不推荐使用】进行探索活动",
         [TaskParam("mode", int, "模式", "只能为0~3的整数\n"
                                       "mode 0: 刷最上面的\n"
                                       "mode 1: 刷次上面的\n"
                                       "mode 2: 第一次手动过最上面的，再刷一次次上面的\n"
                                       "mode 3: 第一次手动过最上面的，再刷一次最上面的")]) \
    .add("r9-n", "tansuo_new", "可推图探索【不推荐】", "【非OCR，不推荐使用】进行探索活动",
         [TaskParam("mode", int, "模式", "只能为0~2的整数\n"
                                       "mode 0: 刷最上关卡（适合大号） \n"
                                       "mode 1: 刷最上关卡，若无法点进则刷次上关卡（适合小号推探索图）\n"
                                       "mode 2: 刷次上关卡，若无法点进则刷最上关卡（适合小号日常探索）")]) \
    .add("r9-ocr", "tansuo_new_ocr", "可推图探索OCR【推荐】", "进行探索活动",
         [TaskParam("mode", int, "模式", "只能为0~2的整数\n"
                                       "mode 0: 刷最上关卡（适合大号） \n"
                                       "mode 1: 刷最上关卡，若无法点进则刷次上关卡（适合小号推探索图）\n"
                                       "mode 2: 刷次上关卡，若无法点进则刷最上关卡（适合小号日常探索）"),
          TaskParam("team_order", str, "选择队伍", "选择什么队伍来推图", default="zhanli",
                    inputbox=TeamOrderInputer),
          TaskParam("zhiyuan_mode", **zhiyuan_mode_kwargs),
          ]) \
    .add("r10", "shengjidiaocha", "圣迹调查", "进行圣迹调查",
         [TaskParam("team_order", str, "选择队伍", "选择什么队伍来推图", default="zhanli",
                    inputbox=TeamOrderInputer)]) \
    .add("r10-n", "shengjidiaocha_new", "圣迹调查新版", "进行圣迹调查（可选关）",
         [TaskParam("team_order", str, "选择队伍", "选择什么队伍来推图", default="zhanli",
                    inputbox=TeamOrderInputer),
          TaskParam("tu_order", list, "图号", "只包含1~4的列表，表示圣迹调查图号，每个均刷5次。",
                    inputbox=ListInputer(convert=lambda x: int(x), desc="一行一个1~3的整数"))
          ]) \
    .add("r11", "shouqunvshenji", "收取女神祭", "收取女神祭") \
    .add("r12", "shendiandiaocha", "神殿调查", "进行神殿调查",
         [TaskParam("team_order", str, "选择队伍", "选择什么队伍来推图", default="zhanli",
                    inputbox=TeamOrderInputer)]) \
    .add("r12-n", "shendiandiaocha_new", "神殿调查新版", "进行神殿调查（可选关）",
         [TaskParam("team_order", str, "选择队伍", "选择什么队伍来推图", default="zhanli",
                    inputbox=TeamOrderInputer),
          TaskParam("tu_order", list, "图号", "只包含1~2的列表，表示神殿调查图号，每个均刷5次。",
                    inputbox=ListInputer(convert=lambda x: int(x), desc="一行一个1~2的整数"))
          ]) \
    .add("r13", "kokkoro_schedule", "可可萝日程表", "完成可可萝日程表", 
         [TaskParam("buy_mana", bool, "是否购买mana", "是否根据日程设置购买mana", False)]) \
    .add("r14", "tanxian_oneclick", "探险收取及重新出发", "探险日常及Event处理，请关闭探险进入时的弹窗并编组完成首次三个任务") \
    .add("f1", "tianjiahaoyou", "添加好友", "按照ID添加好友。", [
    TaskParam("friend_id", str, "好友ID", "要添加的好友的数字ID")]) \
    .add("f2", "tongguoshenqing", "通过申请", "处理全部的好友申请，可以指定按前缀过滤。",
         [TaskParam("name_prefix_valid", str, "用户名前缀验证", "[需要OCR]只通过以该项为前缀的用户名。空字符串表示不过滤。", ""),
          TaskParam("gonghui_prefix_valid", str, "行会名前缀验证", "[需要OCR]只通过以该项为前缀的行会名。空字符串表示不过滤。", ""),
          TaskParam("all_reject", bool, "全部拒绝", "不需要OCR，但是把所有申请都拒绝掉。适合于全部拒绝->小号申请->全部通过的思路。", False)
          ]) \
    .add("t1", "rename", "批量重命名", "随机+批量给自己换个名字，建议配合OCR识别信息更佳",
         [TaskParam("name", str, "新名字", "你的量产新名字，以空格为间隔"),
          TaskParam("auto_id", bool, "自动生成随机位数id", "生成一个随机数0-1000在名字后面", False)]) \
    .add("t2", "save_box_screen", "box截图", "按照战力/等级/星数截屏前两行box",
         [TaskParam("dir", str, "box存放位置", "填写box存放文件夹", "box_pic"),
          TaskParam("sort", str, "排序方式", "只能填写下列三个字符串中的一个：\n"
                                         "xingshu：按照星级降序\n"
                                         "zhanli：按照战力降序\n"
                                         "dengji:按照等级降序\n"
                                         "shoucang:按照收藏降序", "xingshu")]) \
    .add("t3", "get_base_info", "OCR获取账号信息【识别精度较低】", "识别会单独消耗时间，大约几分钟\n利用OCR获取等级/名字/行会名/mana/宝石/战力/"
                                                     "扫荡券，并输出成xls表格到xls文件夹\n注意：请不要在生成表格的期间打开表格！",
         [TaskParam("acc_nature", int, "XLS输出格式", "0：小号、农场号\n1：大号"),
          TaskParam("base_info", bool, "账号基础信息", "是否获取账号基本信息（等级/mana/宝石）"),
          TaskParam("introduction_info", bool, "简介基础信息", "是否获取账号简介基本信息（等级/全角色战力/所属行会/玩家ID）"),
          TaskParam("props_info", bool, "道具基础信息", "是否获取账号道具基本信息（扫荡券）"),
          TaskParam("char_info", bool, "持有角色信息", "是否获取持有三星及以上角色信息，较费时", False),
          TaskParam("out_xls", bool, "是否输出为表格", "是否输出为表格"),
          TaskParam("s_sent", bool, "是否用Server酱发送（暂无）", "每个账号识别结果会直接一个个推送到你手机上", False),
          ]) \
    .add("t4", "maizhuangbei", "小号卖装备【别用】", "卖出数量前三的装备（如果数量大于1000)(无需OCR）",
         [TaskParam("day_interval", int, "清理间隔", "请输入清理间隔天数", 30)]) \
    .add("t5", "zanting", "暂停", "暂停脚本，弹出弹窗，直到手动点击弹窗才结束") \
    .add("t6", "kucunshibie", "库存识别", "识别装备库存并输出到outputs文件夹。") \
    .add("t7", "jueseshibie", "角色识别", "识别角色信息并输出到outputs文件夹。") \
    .add("t8", "guozhuxianjuqing", "过主线剧情", "过主线剧情，不包含角色剧情和活动剧情。", ) \
    .add("t9", "buy_all_frag", "碎片购买", "根据角色名称使用代币购买商店碎片",
         [TaskParam("dxc_fraglist", list, "dxc碎片", "需要购买的碎片名称",
                    inputbox=ListInputer(desc="请输入地下城商店角色碎片，一行一个角色名称")),
          TaskParam("jjc_fraglist", list, "jjc碎片", "需要购买的碎片名称",
                    inputbox=ListInputer(desc="请输入JJC商店角色碎片，一行一个角色名称")),
          TaskParam("pjjc_fraglist", list, "pjjc碎片", "需要购买的碎片名称",
                    inputbox=ListInputer(desc="请输入PJJC商店角色碎片，一行一个角色名称")),
          TaskParam("clan_fraglist", list, "行会碎片", "需要购买的碎片名称",
                    inputbox=ListInputer(desc="请输入行会商店角色碎片，一行一个角色名称")),
          ]) \
    .add("t10", "setting", "设置初始化", "初始化设置，例如跳过动画，隐藏外传等，，提升脚本运行效率。", ) \
    .add("t11", "clear_and_save_team", "按角色名称选取角色，并存入编队", "自动编队后存储，支持缺失位置自动补完或指定替补池",
         [TaskParam("cnamelst", list, "角色列表", "请填入标准简中角色名", inputbox=ListInputer(desc="请输入角色名，一行一个")),
          TaskParam("slot", str, "拟存储的队伍位置", "A-B形式，分组1~5，队伍1~3及~10", "1-1"),
          TaskParam("replace", bool, "是否补全5人队", "当找不到指定角色时，是否自动补充同位置的角色", False),
          TaskParam("prefer", list, "替补的角色列表", "当找不到指定角色时，优先选择这些角色。"
                    "如果该列表空白且开启了补全，则自动选同位置最前可用的", inputbox=ListInputer(desc="请输入替补角色名，一行一个"))]) \
    .add("t12", "starup_six", "六星开花", "自选指定4人，进行6星开花",
         [TaskParam("cnamelst", list, "4个角色名字", "请填入标准简中角色名",
                    inputbox=ListInputer(desc="请输入角色名，一行一个")),
          TaskParam("charname", str, "拟开花的角色名", "请填入标准简中角色名")]) \
    .add("t13", "kkr_wallet", "购买可可萝的钱包", "公会之家买mana钱包",) \
    .add("s1", "shuajingyan", "刷经验1-1【别用，除非OCR】", "刷图1-1，经验获取效率最大。",
         [TaskParam("map", int, "废弃参数", "随便输入一个整数")]) \
    .add("s1-3", "shuajingyan3", "刷经验3-1【别用，除非OCR】", "刷图3-1，比较节省刷图卷。",
         [TaskParam("map", int, "废弃参数", "随便输入一个整数")]) \
    .add("s1-s", "shuajingyan_super", "超级刷1-1【别用】", "【可能有BUG】扫荡券用完了就采用手刷，有扫荡券就再用扫荡券\n"
                                                    "一直刷到倾家荡产，体力耗尽！",
         [TaskParam("mode", int, "刷图模式", "0：纯扫荡券\n"
                                         "1：先扫荡券，无法扫荡时手刷\n"
                                         "2：纯手刷\n", 1),
          TaskParam("buytili", int, "体力购买次数", "消耗多少管体力执行超级刷经验", 6)]) \
    .add("s2", "shuatuNN", "刷N图【别用，除非OCR】", "使用扫荡券刷指定普通副本",
         [TaskParam("tu_dict", list, "刷图列表", "要刷的普通图", inputbox=ShuatuNNBox()),
          TaskParam("use_ocr", bool, "使用OCR", "是否使用OCR来优化刷图", False)]) \
    .add("s3", "shuatuHH", "刷H图【别用，除非OCR】", "使用扫荡券刷指定困难副本",
         [TaskParam("tu_dict", list, "刷图列表", "要刷的困难图", inputbox=ShuatuHHBox()),
          TaskParam("use_ocr", bool, "使用OCR", "是否使用OCR来优化刷图", False)]) \
    .add("s5", "chushihua", "初始化【很可能无法使用】", "从1-3自动推到3-1，已经推过的部分不会再推。") \
    .add("s5-2", "chushihua2", "快速初始化【很可能无法使用】", "从1-3自动推到3-1，已经推过的部分不会再推。\n"
                                                 "先刷经验后推图，效率更高，但是会刷很多次1-1.") \
    .add("s6", "zidongtuitu_normal", "自动推Normal图【已经修复】", "使用等级前五的角色自动推Normal图\n"
                                                         "如果某一关没有三星过关，则强化重打。\n"
                                                         "若强化了还是打不过，则退出。\n"
                                                         "若没体力了，也退出。",
         [TaskParam("buy_tili", int, "体力购买次数", "整个推图/强化过程最多购买体力次数（每天）", 3),
          TaskParam("auto_upgrade", int, "自动升级设置", "开启后，如果推图失败，则会进入升级逻辑"
                                                   "如果升级之后仍然推图失败，则放弃推图"
                                                   "0: 关闭自动升级"
                                                   "1: 只自动强化，但是不另外打关拿装备"
                                                   "2: 自动强化并且会补全一切装备", 1),
          TaskParam("max_tu", str, "终点图号", "max表示推到底，A-B表示推到A-B图为止。", "max")]) \
    .add("s6-h", "zidongtuitu_hard", "自动推Hard图【已经修复】", "使用等级前五的角色自动推Hard图\n"
                                                       "如果某一关没有三星过关，则强化重打。\n"
                                                       "若强化了还是打不过，则退出。\n"
                                                       "若没体力了，也退出。",
         [TaskParam("buy_tili", int, "体力购买次数", "整个推图/强化过程最多购买体力次数（每天）", 3),
          TaskParam("auto_upgrade", int, "自动升级设置", "开启后，如果推图失败，则会进入升级逻辑"
                                                   "如果升级之后仍然推图失败，则放弃推图"
                                                   "0: 关闭自动升级"
                                                   "1: 只自动强化，但是不另外打关拿装备"
                                                   "2: 自动强化并且会补全一切装备", 1),
          TaskParam("max_tu", str, "终点图号", "max表示推到底，A-B表示推到A-B图为止。", "max")]) \
    .add("s7", "meiriHtu", "每日H图", "每天按照顺序依次扫荡H图，直到体力耗尽。\n"
                                   "扫过的图当日不会再扫，第二天重置。",
         [TaskParam("H_list", list, "H图列表", "H图图号", inputbox=MeiRiHTuInputer()),
          TaskParam("daily_tili", int, "每日体力", "每天最多用于每日H图的体力购买次数，该记录每日清零。", 0),
          TaskParam("xianding", bool, "买空限定商店", "如果限定商店出现了，是否买空", True),
          TaskParam("do_tuitu", bool, "是否推图", "若关卡能挑战但未三星，是否允许手刷推图。", False)]) \
    .add("s7-ocr", "meiriHtu_ocr", "每日H图OCR", "【使用OCR】每天按照顺序依次扫荡H图，直到体力耗尽。\n"
                                              "扫过的图当日不会再扫，第二天重置。",
         [TaskParam("H_list", list, "H图列表", "H图图号", inputbox=MeiRiHTuInputer()),
          TaskParam("daily_tili", int, "每日体力", "每天最多用于每日H图的体力购买次数，该记录每日清零。", 0),
          TaskParam("xianding", bool, "买空限定商店", "如果限定商店出现了，是否买空", True),
          TaskParam("do_tuitu", bool, "是否推图", "若关卡能挑战但未三星，是否允许手刷推图。", False),
          TaskParam("zhiyuan_mode", **zhiyuan_mode_kwargs)]) \
    .add("s7-a", "xiaohaoHtu", "每日H图全刷", "从H1-1开始一直往后刷直到没法刷为止。",
         [TaskParam("daily_tili", int, "每日体力", "每天最多用于每日H图的体力购买次数，该记录每日清零。", 0),
          TaskParam("do_tuitu", bool, "是否推图", "若关卡能挑战但未三星，是否允许手刷推图。", False)]) \
    .add("s7-a-ocr", "xiaohaoHtu_ocr", "每日H图全刷OCR", "【使用OCR】从H1-1开始一直往后刷直到没法刷为止。",
         [TaskParam("daily_tili", int, "每日体力", "每天最多用于每日H图的体力购买次数，该记录每日清零。", 0),
          TaskParam("xianding", bool, "买空限定商店", "如果限定商店出现了，是否买空", True),
          TaskParam("do_tuitu", bool, "是否推图", "若关卡能挑战但未三星，是否允许手刷推图。", False),
          TaskParam("zhiyuan_mode", **zhiyuan_mode_kwargs)]) \
    .add("nothing", "do_nothing", "啥事不干", "啥事不干，调试用") \
    .add("s8", "zidongqianghua", "自动升级【已重写】", "此功能为自动升级角色功能",
         [TaskParam("do_rank", bool, "是否升rank", "是否进行rank提升", True),
          TaskParam("do_loveplus", bool, "是否升好感", "是否阅读好感剧情,升满好感", False),
          TaskParam("do_shuatu", bool, "是否推图", "是否推图获取装备", True),
          TaskParam("getzhiyuan", bool, "是否借支援", "是否借人推图", False),
          TaskParam("is_full", int, "借人换下的角色位置", "借人换下的角色位置，一般与选队伍推图配合使用", 2),
          TaskParam("team_order", str, "选择队伍", "选择什么队伍来推图", default="1-1",
                    inputbox=team_order_inputer),
          TaskParam("do_kaihua", bool, "是否升星", "是否才能开花", False),
          TaskParam("do_zhuanwu", bool, "是否进行专武任务", "是否进行专武任务，包括佩戴及升级", False),
          TaskParam("sort", str, "角色强化选择排序方式", "角色选择按什么排序，默认使用等级\n"
                                               "level 表示等级\n"
                                               "zhanli 表示战力\n"
                                               "rank 表示品阶\n"
                                               "star 表示*数\n"
                                               "atk 表示物理攻击力\n"
                                               "def 表示物理防御力\n"
                                               "mat 表示魔法攻击力\n"
                                               "mdf 表示魔法防御力\n"
                                               "hp 表示血量\n"
                                               "love 表示亲密度\n"
                                               "zhuanwu 表示专武\n"
                                               "fav 表示我的最爱\n"
                                               "six 表示六星已解放", "level"),
          TaskParam("charlist", list, "角色列表", "需要升级的角色",
                    inputbox=ListInputer(desc="请输入需要升级的角色，一行一个角色名称（如有括号，使用中文括号），例如 凯露（夏日）")),
          TaskParam("torank", int, "rank(品级)上限等级", "品级上限，拉满填写99，默认拉满,", 99),
          TaskParam("tozhuanwulv", int, "专武上限等级", "专武上限等级，拉满填写999", 120)]) \
    .add("s8-a", "auto_upgrade", "自动升级前几个角色", "不能指定角色升级，但能升级前几个角色。",
         [TaskParam("buy_tili", int, "购买体力", "最多购买几次体力来完成升级", 0),
          TaskParam("do_rank", bool, "RANK提升", "是否提升RANK", True),
          TaskParam("do_shuatu", bool, "是否刷图", "缺装备时是否刷图", True),
          TaskParam("count", int, "前几", "对前几个角色进行升级", 5),
          TaskParam("sortby", str, "前几排序", "前几个角色的排序方式(dengji/xingshu/zhanli/shoucang)", "xingshu"),
          TaskParam("do_tuitu", bool, "是否推图", "如果没打过的图，是否要推。", False),
          TaskParam("team_order", str, "选择队伍", "选择什么队伍来推图", default="zhanli",
                    inputbox=team_order_inputer),
          TaskParam("getzhiyuan", bool, "是否支援", "是否需要选择第一个支援位来支援", False)]) \
    .add("s9", "shuatu_daily_ocr", "OCR主线通用刷图推图", "使用OCR辅助的稳定的通用主线刷图/推图",
         [TaskParam("tu_order", list, "刷图顺序", "刷图/推图会依次按照该顺序",
                    inputbox=ListInputer(desc="一行一个字符串(A)-(B)-(T)或者H(A)-(B)-(T)或VH(A)-(B)-(T)\n"
                                              "表示刷/推图A-B或者HA-B T/VHA-B T 次（每日）。\n"
                                              "对H和VH，还可以后加波浪号 ~(TG) \n"
                                              "表示碎片获取量达到TG后跳过刷图，设置为inf则为无限。\n"
                                              "默认H图TG=inf, VH图TG=50。\n"
                                              "Example:\n"
                                              "    3-1-60  # 刷普通图3-1 60次。\n"
                                              "    H10-3-3  # 刷H图10-3 3次。\n"
                                              "    H10-3-3~150  # 若碎片数小于150，则刷H图10-3 3次。\n"
                                              "    VH20-3-3  # 若碎片数小于50，则刷VH图20-3 3次。\n"
                                              "    VH20-3-3~inf  # 刷VH图20-3 3次。\n"
                                              "注：H/VH图最多刷6次，超过3次会尝试购买次数。")),
          TaskParam("daily_tili", int, "每日体力", "每日在刷图上所用的体力购买总数。", 0),
          TaskParam("xianding", bool, "限定商店", "是否买空限定商店", True),
          TaskParam("zero_star_action", str, "从未通关时",
                    desc="对从未通关的图（零星最新图）执行的操作",
                    default="exit",
                    inputbox=StrChooseInputer(dict(do="推图", exit="终止刷图", skip="跳过该图"))),
          TaskParam("not_three_star_action", str, "不可扫荡时",
                    desc="对不可扫荡的图（三星未满但已经过关）执行的操作",
                    default="do",
                    inputbox=StrChooseInputer(dict(do="推图", exit="终止刷图", skip="跳过该图"))),
          TaskParam("lose_action", str, "推图失败时",
                    desc="推图失败后执行的操作",
                    default="skip",
                    inputbox=StrChooseInputer(dict(do="再次推图", exit="终止刷图", skip="跳过该图",
                                                   upgrade="尝试升级，若仍然失败则终止推图。（队伍只能为zhanli/juese/xingshu/shoucang））"))),
          TaskParam("can_not_enter_action", str, "无法进图时",
                    desc="对还无法进入的图（还未解锁）的操作",
                    default="exit",
                    inputbox=StrChooseInputer(dict(exit="终止刷图", skip="跳过该图"))),
          TaskParam("win_without_threestar_is_lose", bool, "不三星就是失败", "如果推图结果未三星，则当作推图失败处理。", True),
          TaskParam("team_order", str, "选择队伍", "选择什么队伍来推图", default="zhanli",
                    inputbox=team_order_inputer),
          TaskParam("zhiyuan_mode", **zhiyuan_mode_kwargs),
          ]) \
    .add("s9-t", "tuitu_ocr", "OCR主线推图", "s9，但是专门用于一个一个图的推",
         [TaskParam("mode", int, "推什么图", "0 - Normal; 1 - Hard, 2 - VH"),
          TaskParam("from_", str, "从哪里推", "请输入(A)-(B) 或者 new表示从最新图开始。", "new"),
          TaskParam("to", str, "推到哪里", "请输入(A)-(B) 或者 max表示推到目前最新进度", "max"),
          TaskParam("buy_tili", int, "推图所用体力", "本任务中最多购买几次体力", 0),

          TaskParam("xianding", bool, "限定商店", "是否买空限定商店", True),
          TaskParam("lose_action", str, "推图失败时",
                    desc="推图失败后执行的操作",
                    default="exit",
                    inputbox=StrChooseInputer(dict(do="再次推图", exit="终止刷图", skip="跳过该图",
                                                   upgrade="尝试升级，若仍然失败则终止推图。（队伍只能为zhanli/juese/xingshu/shoucang））"))),
          TaskParam("win_without_threestar_is_lose", bool, "不三星就是失败", "如果推图结果未三星，则当作推图失败处理。", True),
          TaskParam("team_order", str, "选择队伍", "选择什么队伍来推图", default="zhanli",
                    inputbox=team_order_inputer),
          TaskParam("zhiyuan_mode", **zhiyuan_mode_kwargs),
          ]) \
    .add("s9-auto", "daily_shuatu_auto", "大号自动规划刷N图", "每日刷图，但是基于角色识别和装备识别自动规划要刷的normal图！\n"
                                                        "*你需要在data中事先设定角色的追踪*\n"
                                                        "大号专用，默认所有图均三星可扫荡。",
         [TaskParam("daily_tili", int, "每日体力", "每天最多用于刷N图体力购买次数，该记录每日清零。", 0),
          TaskParam("xianding", bool, "限定商店", "是否买空限定商店", True),
          TaskParam("do_kucunshibie", bool, "前置库存识别", "是否在该任务中前置库存识别任务", True),
          TaskParam("do_jueseshibie", bool, "前置角色识别", "是否在该任务中前置角色识别任务", True),
          TaskParam("n", int, "N几", "当前是N几", 1),
          TaskParam("max_tu", str, "最多考虑图几",
                    f"为整数(A)时，最多考虑到图A为止；设置为max时，自动更新为最高图号（当前为{MAX_MAP}）"),
          ]) \
    .add("s10", "kuaisujieren", "好友快速借人", "借好友随便推一关，点进去什么图就推它的第一关。",
         [TaskParam("max_do", int, "最多借几次", "如果还有好友可以借，最多借几次，默认为2.", 2),
          TaskParam("max_map", int, "最多推图几", "随便推图不会推超过[max_map]-1的图。可以填很大的数，如999来屏蔽该设置。", 999)]) \
    .add("s11-n", "jierentuitu_normal", "借人推普通图", "借好友或别人的进行推普通图。",
         [TaskParam("max_tu", str, "终点图号", "max表示推到底，A-B表示推到A-B图为止。", "max"),
          TaskParam("zhiyuan_mode", **zhiyuan_mode_kwargs),
          TaskParam("max_do", int, "最多借几次", "最多借几次（最多推几关）。", 2)]) \
    .add("s11-h", "jierentuitu_hard", "借人推困难图", "借好友或别人的进行推普通图。",
         [TaskParam("max_tu", str, "终点图号", "max表示推到底，A-B表示推到A-B图为止。", "max"),
          TaskParam("zhiyuan_mode", **zhiyuan_mode_kwargs),
          TaskParam("max_do", int, "最多借几次", "最多借几次（最多推几关）。", 2)]) \
    .add("s12", "tui_wz", "推外传，获取奖励", "简单获取外传的一次性奖励",
         [TaskParam("code", str, "第几个外传", "比如第一个就输入01", "07"),
          TaskParam("team_order", str, "选择队伍", "选择什么队伍来推图", default="zhanli",
                    inputbox=team_order_inputer),
          TaskParam("get_zhiyuan", bool, "是否支援", "是否需要选择第一个支援位来支援"),
          TaskParam("if_full", int, "借人换下的角色位置", "借人换下的角色位置，一般与选队伍推图配合使用")]) \
    .add("s13", "auto_advance", "自动推图", "使用自动推图，推主线", 
         [TaskParam("mode", int, "推什么图", "0 - Normal; 1 - Hard, 2 - VH"),
          TaskParam("team_order", str, "选择队伍", "选择什么队伍来推图", default="zhanli", inputbox=TeamOrderInputer),
          TaskParam("buy_tili", int, "推图所用体力", "本任务中最多购买几次体力", 0),
          TaskParam("lose_action", str, "推图失败时",
                    desc="推图失败后执行的操作",
                    default="exit",
                    inputbox=StrChooseInputer(dict(do="再次推图", exit="终止刷图", skip="跳过该图",
                                                   upgrade="尝试升级，若仍然失败则终止推图。（队伍只能为zhanli/juese/xingshu/shoucang））"))),
         ]) \
    .add("s14", "yijiansaodang", "使用自带的关卡扫荡", "需要预先选定要扫荡的主线图",
         [TaskParam("times", int, "扫荡几次", "扫荡几次，默认3", 3),
          TaskParam("slot", int, "使用哪组预设（1~7）", "预设", 1)]) \
    .add("hd01", "tui_hd_map_normal", "推活动普通图", "用于推N1-15。",
         [TaskParam("team_order", str, "选择队伍", "选择什么队伍来推图", default="zhanli", inputbox=TeamOrderInputer),
          TaskParam("get_zhiyuan", bool, "是否借支援", "是否借人推图", False),
          TaskParam("if_full", int, "借人换下的角色位置", "借人换下的角色位置，一般与选队伍推图配合使用", 0),
          TaskParam("if_auto",bool,"是否开启auto","用满配水星不开auto推图更快",True),
          TaskParam(**huodong_code_kwargs),
          TaskParam(**huodong_entrance_ind_kwargs)]) \
    .add("hd02", "tui_hd_map_hard", "推活动困难图", "用于推H1-5。",
         [TaskParam("team_order", str, "选择队伍", "选择什么队伍来推图", default="zhanli", inputbox=TeamOrderInputer),
          TaskParam("get_zhiyuan", bool, "是否借支援", "是否借人推图", False),
          TaskParam("if_full", int, "借人换下的角色位置", "借人换下的角色位置，一般与选队伍推图配合使用", 0),
          TaskParam("if_auto",bool,"是否开启auto","用满配水星不开auto推图更快",True),
          TaskParam(**huodong_code_kwargs),
          TaskParam(**huodong_entrance_ind_kwargs)]) \
    .add("hd03", "shua_hd_boss", "推/刷活动Boss（N or H or VH），", "刷活动Boss，用完挑战券，一次打不死会直接退出。",
         [TaskParam("boss_type", str, "刷什么难度的Boss", "N表示普通，H表示困难，VH表示极难", "N"),
          TaskParam("once", bool, "是否只打一次", "只打一次解锁地图用", False),
          TaskParam("team_order", str, "选择队伍", "选择什么队伍来推图", default="zhanli", inputbox=TeamOrderInputer),
          TaskParam(**huodong_code_kwargs),
          TaskParam(**huodong_entrance_ind_kwargs)]) \
    .add("hd04", "dahaohuodong_VHBoss", "推/刷活动VHBoss", "刷活动VHBoss图",
         [TaskParam("team_order", str, "选择队伍", "选择什么队伍来推图", default="zhanli", inputbox=TeamOrderInputer),
          TaskParam(**huodong_code_kwargs),
          TaskParam(**huodong_entrance_ind_kwargs)]) \
    .add("hd05", "xiaohaohuodong_11", "推/刷活动1-1", "推/刷活动1-1图，可以借人。",
         [TaskParam("cishu", str, "刷几次", "max表示全刷，或者也可以输入一个整数。", "max"),
          TaskParam("team_order", str, "选择队伍", "选择什么队伍来推图", default="zhanli", inputbox=TeamOrderInputer),
          TaskParam("get_zhiyuan", bool, "是否借支援", "是否借人推图", True),
          TaskParam(**huodong_code_kwargs),
          TaskParam(**huodong_entrance_ind_kwargs)]) \
    .add("hd06", "dahaohuodong_hard", "刷活动Hard图", "刷活动Hard图，要求已经全部三星。",
         [TaskParam("tu_order", list, "图号", "只包含1~5的列表，表示活动困难图图号，每个均刷3次。",
                    inputbox=ListInputer(convert=lambda x: int(x), desc="一行一个1~5的整数")),
          TaskParam(**huodong_code_kwargs),
          TaskParam(**huodong_entrance_ind_kwargs)]) \
    .add("hd07", "shua_hd_map_normal", "刷指定活动普通图（必须打过）", "一般用来刷1-5或者1-15",
         [TaskParam("map_id", int, "活动Normal图号", "1~15的数字", 1),
          TaskParam("cishu", str, "刷几次", "max表示全刷，或者也可以输入一个整数。", "max"),
          TaskParam(**huodong_code_kwargs),
          TaskParam(**huodong_entrance_ind_kwargs)]) \
    .add("hd08", "exchange_tfz", "交换讨伐证（试验性）", "交换讨伐证，不中途重置",
         [TaskParam(**huodong_code_kwargs),
          TaskParam(**huodong_entrance_ind_kwargs)]) \
    .add("hd09", "huodong_getbonus", "获取活动任务奖励", "活动任务奖励",
         [TaskParam(**huodong_code_kwargs),
          TaskParam(**huodong_entrance_ind_kwargs)]) \
    .add("hd10", "huodong_read_juqing", "获取活动剧情奖励", "获取活动剧情奖励",
         [TaskParam(**huodong_code_kwargs),
          TaskParam(**huodong_entrance_ind_kwargs)]) \
    .add("hd11", "huodong_read_xinlai", "获取活动信赖奖励", "获取活动信赖奖励",
         [TaskParam(**huodong_code_kwargs),
          TaskParam(**huodong_entrance_ind_kwargs)])

customtask_addr = "customtask"


def getcustomtask(modulefile) -> list:
    target_name = "%s.%s" % (customtask_addr, modulefile)
    py = importlib.import_module(target_name)
    return py


def list_all_customtasks(verbose=1) -> List[str]:
    import os
    if not os.path.exists(customtask_addr):
        os.makedirs(customtask_addr)
    ld = os.listdir(customtask_addr)
    tasks = []
    count = 0
    for i in ld:
        if not os.path.isdir(i) and i.endswith(".py"):
            try:
                getcustomtask(i[:-3])
                if verbose:
                    print("自定义模块", i, "加载成功！")
                tasks += [i[:-3]]
                count += 1
            except Exception as e:
                if verbose:
                    print("打开模块", i, "失败！", e)
                    import traceback
                    traceback.print_exc()
    if verbose:
        print("加载完成，一共加载成功", count, "个模块。")
    return tasks


for l in list_all_customtasks(verbose=debug):
    VALID_TASK.add_custom(l)
