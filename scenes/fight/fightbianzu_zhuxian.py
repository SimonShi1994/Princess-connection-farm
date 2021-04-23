from core.constant import FIGHT_BTN
from scenes.fight.fightbianzu_base import FightBianZuBase
from scenes.fight.fighting_zhuxian import FightingZhuXian


class FightBianZuZhuXian(FightBianZuBase):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name="FightBianZuZhuXian"


    def goto_fight(self) -> FightingZhuXian:
        # 前往战斗开始！
        return self.goto(FightingZhuXian, self.fun_click(FIGHT_BTN["zhandoukaishi"]))
