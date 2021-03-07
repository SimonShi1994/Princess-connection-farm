from core.constant import FIGHT_BTN
from scenes.fight.fightbianzu_base import FightBianZuBase
from scenes.scene_base import PCRMsgBoxBase


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
        return self._a.set_fight_team_order(order,change)

    def select_by_duiwu(self, bianzu, duiwu):
        """
        :param bianzu: 编组编号1~5
        :param duiwu: 队伍编号1~3
        :return: False - 选取编组失败
        """
        return self._a.set_fight_team(bianzu, duiwu)

    def goto_fight(self):
        # 前往战斗开始！
        pass
        # FIGHT_BTN["zhandoukaishi"]


