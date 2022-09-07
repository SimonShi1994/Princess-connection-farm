from core.constant import FIGHT_BTN, DXC_ELEMENT
from scenes.fight.fightbianzu_base import FightBianZuBase
from scenes.fight.fighting_zhuxian import FightingZhuXian
from scenes.scene_base import PCRMsgBoxBase, PossibleSceneList


class ZhiYuanQueRen(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ZhiYuanQueRen"
        self.feature = self.fun_feature_exist(DXC_ELEMENT["zyjsqr"])

    def ok(self):
        return self.goto(FightingZhuXian, self.fun_click(DXC_ELEMENT["zyjsqr_ok"]))


class AfterEnterTiaoZhan(PossibleSceneList):
    def __init__(self, a):
        self.ZhiYuanQueRen = ZhiYuanQueRen
        self.next_scene = FightingZhuXian
        scene_list = [
            ZhiYuanQueRen(a),
            FightingZhuXian(a),
        ]
        super().__init__(a, scene_list, double_check=1.)


class FightBianZuZhuXian(FightBianZuBase):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name="FightBianZuZhuXian"

    def goto_fight(self) -> "FightingZhuXian":
        # 前往战斗开始！
        out=self.goto(AfterEnterTiaoZhan, self.fun_click(FIGHT_BTN["zhandoukaishi"]))
        if isinstance(out,ZhiYuanQueRen):
            return out.ok()
        else:
            return out
