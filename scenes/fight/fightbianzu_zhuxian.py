from core.constant import FIGHT_BTN
from scenes.fight.fightbianzu_base import FightBianZuBase
from scenes.fight.fighting_zhuxian import FightingZhuXian


class FightBianZuZhuXian(FightBianZuBase):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name="FightBianZuZhuXian"
        self.feature = self.fun_feature_exist(FIGHT_BTN["duiwubianzu"])

    def select_by_sort(self,order="zhanli",change=2):
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

    def select_team(self, team_order):
        """
        使用队伍 "A-B" 形式，表示编组A选择B。
        若为 order指令：则按以下order排序后取前5.
            - "zhanli" 按战力排序
            - "dengji" 按等级排序
            - "xingshu" 按星数排序
        若为"none"：不换人
        """
        if team_order in ["zhanli", "dengji", "xingshu"]:
            return self.select_by_sort(team_order)
        elif team_order == "none":
            return None
        else:
            A, B = team_order.split("-")
            A = int(A)
            B = int(B)
            return self.select_by_duiwu(A, B)

    def goto_fight(self) -> FightingZhuXian:
        # 前往战斗开始！
        return self.goto(FightingZhuXian, self.fun_click(FIGHT_BTN["zhandoukaishi"]))
