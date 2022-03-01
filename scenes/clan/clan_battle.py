import time

import random
from core.constant import HANGHUI_BTN, FIGHT_BTN, DXC_ELEMENT, HAOYOU_BTN
from scenes.root.seven_btn import SevenBTNMixin
from core.cv import UIMatcher
from core.pcr_checker import LockTimeoutError


class ClanBattleMAP(SevenBTNMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ClanBattleMAP"
        self.feature = self.fun_feature_exist(HANGHUI_BTN["rank_info"])
        self.initPC = self.gonghuizhan_precheck

    def gonghuizhan_precheck(self, screen):
        if self.is_exists(HANGHUI_BTN["queren"], screen=screen):  # 报酬确认
            self.click_btn(HANGHUI_BTN["queren"])
        if self.is_exists(HANGHUI_BTN["guanbi"], screen=screen):  # 公会战开始、排名公布
            self.click_btn(HANGHUI_BTN["guanbi"])
        if self.is_exists(HANGHUI_BTN["kkr_dialog"], screen=screen):
            self.click(160, 100)
            self.click(160, 100)
        if self.is_exists(HANGHUI_BTN["kkr_dialog2"], screen=screen):
            self.click(160, 100)
            self.click(160, 100)
        if self.is_exists(HANGHUI_BTN["sudu"]):  # 战斗速度上限设定（关闭）
            self.click(349, 282)
            time.sleep(1)
            self.click(479, 365)
        return screen

    def goto_battlepre(self):   # 点击进入BOSS
        time.sleep(5)
        screen = self.getscreen()
        r = self.img_where_all(img="img/hanghui/battle/boss_lp.bmp", threshold=0.5, at=(13, 133, 916, 379), )
        if not r:
            self.log.write_log("info", "未识别到BOSS，可能不在公会战期间")
            return False
        else:
            x = r[0]
            y = r[1]
            x1 = int(x) + 77
            y1 = int(y) - 43
            return self.goto(ClanBattleBianzu, self.fun_click(x1, y1))

    def get_cishu(self):
        a = self.ocr_int(549, 395, 569, 415)
        if a == 0:
            if self.is_exists(HANGHUI_BTN["fanhuanshijian"]):
                return 1
            else:
                return 0
        else:
            return a


class ClanBattlePre(ClanBattleMAP):
    # 公会战准备
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ClanBattlePre"
        self.feature = self.fun_feature_exist(HANGHUI_BTN["shbg"])
        self.initPC = self.zhandouzhunbei_precheck

    def zhandouzhunbei_precheck(self, screen):
        if self.is_exists(HANGHUI_BTN["kkr_dialog"], screen=screen):
            self.click(160, 100)
            self.click(160, 100)
        if self.is_exists(HANGHUI_BTN["kkr_dialog2"], screen=screen):
            self.click(160, 100)
            self.click(160, 100)

    def make_formal(self):
        self.lock_img(HANGHUI_BTN["monizhan_unselected"], elseclick=(862, 104))

    def goto_battle(self) -> "ClanBattleBianzu":  # 点击挑战，进入队伍编组
        return self.goto(ClanBattleBianzu, self.fun_click(HANGHUI_BTN["tiaozhan"]))


class ClanBattleBianzu(ClanBattleMAP):  # 公会战编组
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ClanBattlePre"
        self.feature = self.fun_feature_exist(FIGHT_BTN["duiwubianzu"])
        self.initPC = self.duiwubianji_precheck

    def duiwubianji_precheck(self, screen):
        if self.is_exists(HANGHUI_BTN["kkr_dialog"], screen=screen):
            self.click(160, 100)
            self.click(160, 100)

    def select_by_sort(self, order="zhanli", change=2):
        """
        按order进行选择
        :param order:
            order in ["zhanli","dengji","xingshu","shoucang"]
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
        self.select_by_sort("zhanli",change=1)

    def select_team(self, team_order="zhanli", change=2):
        """
        使用队伍 "A-B" 形式，表示编组A选择B。
        若为 order指令：则按以下order排序后取前5.
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
        else:
            A, B = team_order.split("-")
            A = int(A)
            B = int(B)
            return self.select_by_duiwu(A, B)

    def get_fight_current_member_count(self):
        return self._a.get_fight_current_member_count()

    def get_zhiyuan(self, assist_num=1,force_haoyou=False,if_full=2):
        # 从左到右获取一个可能的支援
        # out: 0- Success 1- 人满 2- 等级不够 3- 无支援人物 4- 无好友
        # force_haoyou: 只借好友，不然不借
        # if full: 人满时？ -1： 返回人满；  0： 随机下一个人  1~5： 下第n个人
        out = 0
        if self.click_btn(DXC_ELEMENT["zhiyuan_white"], until_appear=DXC_ELEMENT["zhiyuan_blue"],
                            retry=3, wait_self_before=True):
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
                            choose = random.choice([1, 2, 3, 4, 5])
                        else:
                            choose = if_full
                        self.click(FIGHT_BTN["empty"][choose], pre_delay=1,post_delay=0.5)
                        if if_full == 0:
                            self.log.write_log("info", f"已经人满，随机换下第{choose}人！")
                        else:
                            self.log.write_log("info", f"已经人满，换下第{choose}人！")
                        now_count-=1
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

