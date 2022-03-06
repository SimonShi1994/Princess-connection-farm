import time

from core.constant import MAOXIAN_BTN, FIGHT_BTN, DXC_ELEMENT, HAOYOU_BTN, JUESE_BTN
from scenes.scene_base import PCRMsgBoxBase
import random


class FightBianZuBase(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightBianZu"
        self.feature = self.fun_feature_exist(FIGHT_BTN["duiwubianzu"])
        self.initFC = self.getFC(False).exist(MAOXIAN_BTN["bianzusheding"],
                                              self.fun_click(476, 437))

    def select_by_sort(self, order="zhanli", change=2):
        """
        按order进行选择
        :param order:
            order in ["zhanli","dengji","xingshu","shoucang","none"]
        :param change:
            0-不换人 1-人全部换下不上 2-默认：全部换人 3 - 不下人直接上
        """
        return self._a.set_fight_team_order(order, change)

    def select_by_duiwu(self, bianzu, duiwu):
        """
        :param bianzu: 编组编号1~5
        :param duiwu: 队伍编号1~3
        :return: False - 选取编组失败
        """
        return self._a.set_fight_team(bianzu, duiwu)

    def click_juese_by_rc(self, r, c):
        # 通过行列来选中角色，没什么用。而且仅限前两排
        r1 = [
            (107, 170),
            (214, 168),
            (318, 170),
            (423, 173),
            (531, 175),
            (636, 171),
            (742, 171),
            (849, 170),
        ]
        r2 = [
            (102, 305),
            (214, 303),
            (320, 301),
            (421, 299),
            (529, 299),
            (640, 295),
            (746, 297),
            (851, 291),
        ]
        if 1 <= c <= 8:
            if r == 1:
                self.click(*r1[c - 1])
                return
            elif r == 2:
                self.click(*r2[c - 1])
                return
        raise ValueError("只能1~2行，1~8列！而不是", r, '-', c)

    @staticmethod
    def check_team_AB(team_order):
        return '-' in team_order

    def clear_team(self):
        self.select_by_sort("zhanli", change=1)

    def select_team(self, team_order="zhanli", change=2):
        """
        使用队伍 "A-B" 形式，表示编组A选择B。
        若为 order指令：则按以下order排序后取前5.
            - "none" 不变化
            - "nobody" 不上人（只上支援）
            - "zhanli" 按战力排序
            - "dengji" 按等级排序
            - "xingshu" 按星数排序
            - "shoucang" 按收藏排序
        若为"none"或者""：不换人
        """
        if team_order in ["zhanli", "dengji", "xingshu", "shoucang"]:
            return self.select_by_sort(team_order, change)
        elif team_order in ["none", ""]:
            return None
        elif team_order == "nobody":
            self.select_by_sort("none", 1)
        else:
            A, B = team_order.split("-")
            A = int(A)
            B = int(B)
            return self.select_by_duiwu(A, B)

    def get_fight_current_member_count(self):
        return self._a.get_fight_current_member_count()

    def sort_down(self):
        if self.is_exists(FIGHT_BTN["sort_down"]):
            return
        else:
            self.click_btn(FIGHT_BTN["sort_up"], until_appear=FIGHT_BTN["sort_down"])
        time.sleep(1)

    def sort_by(self, cat=None):
        cor_dict = {
            'level': (69, 137),
            'zhanli': (287, 137),
            'rank': (508, 137),
            'star': (727, 137),
            'atk': (69, 193),
            'mat': (287, 193),
            'def': (508, 193),
            'mdf': (727, 193),
            'hp': (69, 251),
            'zhuanwu': (287, 251),
            'six': (510, 252)
        }
        # 兼容
        name_dict = {
            "dengji": "level",
            "xingshu": "star",
            "shoucang": "fav",
        }
        if cat in name_dict:
            cat = name_dict[cat]
        if cat is None:
            return
        else:
            self.click_btn(FIGHT_BTN["sort_by"], until_appear=JUESE_BTN["fenlei"])
            time.sleep(1)
            self.click(cor_dict.get(cat)[0], cor_dict.get(cat)[1])
            # 点击分类类型
            time.sleep(1)
            self.click(597, 477)
            # 点击确认
            time.sleep(1)

    def get_zhiyuan(self, assist_num=1, force_haoyou=False, if_full=0, zhiyuan_sort="zhanli"):
        # 从左到右获取一个可能的支援
        # out: 0- Success 1- 人满 2- 等级不够 3- 无支援人物 4- 无好友
        # force_haoyou: 只借好友，不然不借
        # if full: 人满时？ -1： 返回人满；  0： 随机下一个人  1~5： 下第n个人
        # zhiyuan_sort: 排序方式，方便确认想借的角色
        out = 0
        if self.click_btn(DXC_ELEMENT["zhiyuan_white"], until_appear=DXC_ELEMENT["zhiyuan_blue"],
                          retry=3, wait_self_before=True):
            if zhiyuan_sort is not None:
                self.sort_down()
                self.sort_by(cat=zhiyuan_sort)
                self.log.write_log("info", f"已经按{zhiyuan_sort}排序！")

            if force_haoyou and not self.is_exists(HAOYOU_BTN["haoyou_sup"]):
                out = 4
                self.log.write_log("info", "没有好友了，不借了！")
            else:
                now_count = self.get_fight_current_member_count()
                if now_count == 5:
                    if if_full == -1:
                        self.log.write_log("warning", "已经人满，无法借人！")
                        out = 1
                    else:
                        if if_full == 0:
                            choose = 2
                        else:
                            choose = if_full
                        self.click(FIGHT_BTN["empty"][choose], pre_delay=1, post_delay=0.5)
                        if if_full == 0:
                            self.log.write_log("info", f"已经人满，随机换下第{choose}人！")
                        else:
                            self.log.write_log("info", f"已经人满，换下第{choose}人！")
                        now_count -= 1
                for c in range(assist_num, assist_num + 2):
                    if c <= 8:
                        self.click_juese_by_rc(1, c)
                    else:
                        self.click_juese_by_rc(2, c - 8)
                time.sleep(0.5)
                new_count = self._a.get_fight_current_member_count()
                if new_count == now_count + 1:
                    self.log.write_log(level='info', message="借人成功！")
                else:
                    self.log.write_log(level='warning', message="借人失败，可能因为等级不够！")
                    out = 2
            # if self.lock_no_img(DXC_ELEMENT["zhiyuan_blue"], retry=1):
        else:
            self.log.write_log(level='info', message="无支援人物!")
            out = 3
        self.click_btn(DXC_ELEMENT["quanbu_white"], until_appear=DXC_ELEMENT["quanbu_blue"], elsedelay=0.1)
        return out
