from typing import List, Type, Any, Optional


# 合法Task参数
class TaskParam:
    def __init__(self, key: str, typ: Optional[Type] = None, title: Optional[str] = None,
                 desc: Optional[str] = None,
                 default: Optional[Any] = None):
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


class ValidTask:
    def __init__(self):
        self.T = {}  # 存放合法Task记录

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
        self.T[abbr] = {
            "funname": funname,
            "title": title,
            "desc": desc,
            "params": params
        }
        return self


VALID_TASK = ValidTask() \
    .add("h1", "hanghui", "行会捐赠", "小号进行行会自动捐赠装备") \
    .add("h2", "tichuhanghui", "踢出行会", "将战力排名第一人踢出行会") \
    .add("h3", "yaoqinghanghui", "邀请行会", "邀请指定成员进入行会",
         [TaskParam("inviteUID", str, "UID", "被邀请者的UID号")]) \
    .add("h4", "jieshouhanghui", "接受行会", "接受行会的邀请信息") \
    .add("h5", "joinhanghui", "加入行会", "小号主动搜索并加入行会",
         [TaskParam("clubname", str, "行会名称", "要加入行会的名称")]) \
    .add("h6", "dianzan", "行会点赞", "给指定人点赞",
         [TaskParam("sortflag", int, "给谁点赞", "只能为0或者1的值\n0：给副会长点赞。\n1：给战力最高者点赞。", 0)]) \
    .add("d1", "dixiacheng_ocr", "地下城(使用OCR)", "小号地下城借人换mana",
         [TaskParam("skip", bool, "跳过战斗", "设置为True时，第一层不打直接撤退。\n设置为False时，打完第一层。")]) \
    .add("d2", "dixiacheng", "地下城", "小号地下城借人换mana",
         [TaskParam("skip", bool, "跳过战斗", "设置为True时，第一层不打直接撤退。\n设置为False时，打完第一层。")]) \
    .add("d3", "dixiachengYunhai", "打云海关", "打通云海关【细节待补充】") \
    .add("d4", "dixiachengDuanya", "打断崖关", "打通断崖关【细节待补充】") \
    .add("j1", "doJJC", "竞技场", "竞技场白给脚本") \
    .add("j2", "doPJJC", "公主竞技场", "公主竞技场白给脚本") \
    .add('r1', "gonghuizhijia", "家园领取", "收取公会之家的奖励") \
    .add("r2", "mianfeiniudan", "免费扭蛋", "抽取免费扭蛋") \
    .add("r3", "mianfeishilian", "免费10连", "抽取免费十连（如果有的话）") \
    .add("r4", "shouqu", "收取礼物", "收取全部礼物") \
    .add("r5", "shouqurenwu", "收取任务", "收取全部任务奖励。\n如果日常任务和主线任务都存在，需要收取两遍。") \
    .add("r6", "goumaitili", "购买体力", "购买一定次数的体力",
         [TaskParam("times", int, "购买次数", "购买体力的次数")]) \
    .add("r7", "goumaimana", "购买MANA", "购买指定次数的mana",
         [TaskParam("times", int, "购买mana的次数", "如果mode为0，则为购买mana的次数；\n如果mode为1，则为购买10连mana的次数。【宝石警告】"),
          TaskParam("mode", int, "模式", "只能为0或1的值。\n0：一连模式。\n1：十连模式", 1)]) \
    .add("r8", "buyExp", "购买经验", "买空商店里的经验药水") \
    .add("r9", "tansuo", "探索", "进行探索活动",
         [TaskParam("mode", int, "模式", "只能为0~3的整数\n"
                                       "mode 0: 刷最上面的\n"
                                       "mode 1: 刷次上面的\n"
                                       "mode 2: 第一次手动过最上面的，再刷一次次上面的\n"
                                       "mode 3: 第一次手动过最上面的，再刷一次最上面的")]) \
    .add("t1", "rename", "重命名", "给自己换个名字",
         [TaskParam("name", str, "新名字", "你的新名字")]) \
    .add("s1", "shuajingyan", "刷经验1-1", "刷图1-1，经验获取效率最大。",
         [TaskParam("map", int, "主图", "如果你的号最远推到A-B,则主图为A。")]) \
    .add("s2", "shuatuNN", "刷N图", "使用扫荡券刷指定普通副本",
         [TaskParam("tu_list", list, "刷图列表",
                    "一个包含了若干个List的List\n"
                    "每一个List的格式如下：\n"
                    "[大图号,小图号,刷图次数]\n"
                    "例如[12,3,3]表示刷12-3图3次\n"
                    "该List不必在意顺序，因为该函数内自动会调整顺序。")]) \
    .add("s3", "shuatuHH", "刷H图", "使用扫荡券刷指定困难副本",
         [TaskParam("tu_list", list, "刷图列表",
                    "一个包含了若干个List的List\n"
                    "每一个List的格式如下：\n"
                    "[大图号,小图号,刷图次数]\n"
                    "例如[12,3,3]表示刷H12-3图3次\n"
                    "该List不必在意顺序，因为该函数内自动会调整顺序。")]) \
    .add("s4", "doActivityHard", "刷活动图", "使用扫荡券刷活动副本（慎用，因为每次活动坐标都不同）")
