from core.constant import MAOXIAN_BTN, FIGHT_BTN
from scenes.scene_base import PCRMsgBoxBase


class FightBianZuBase(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightBianZu"
        self.feature = self.fun_feature_exist(FIGHT_BTN["duiwubianzu"])
        self.initFC = self.getFC(False).exist(MAOXIAN_BTN["bianzusheding"],
                                              self.fun_click(MAOXIAN_BTN["bianzusheding_ok"]))

    def select_by_sort(self, order="zhanli", change=2):
        """
        按order进行选择
        :param order:
            order in ["zhanli","dengji","xingshu"]
        :param change:
            0-不换人 1-人全部换下不上 2-默认：全部换人
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

    def select_team(self, team_order, change=2):
        """
        使用队伍 "A-B" 形式，表示编组A选择B。
        若为 order指令：则按以下order排序后取前5.
            - "zhanli" 按战力排序
            - "dengji" 按等级排序
            - "xingshu" 按星数排序
        若为"none"或者""：不换人
        """
        if team_order in ["zhanli", "dengji", "xingshu"]:
            return self.select_by_sort(team_order, change)
        elif team_order in ["none", ""]:
            return None
        else:
            A, B = team_order.split("-")
            A = int(A)
            B = int(B)
            return self.select_by_duiwu(A, B)
