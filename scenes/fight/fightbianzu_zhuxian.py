from core.constant import FIGHT_BTN, MAOXIAN_BTN, DXC_ELEMENT
from scenes.fight.fightbianzu_base import FightBianZuBase
from scenes.fight.fighting_zhuxian import FightingZhuXian
from scenes.fight.auto_advance_settings import AutoAdvanceSettings
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
        self.is_auto_advance = False

    def goto_fight(self, buy_ap=False) -> "FightingZhuXian":
        # 前往战斗开始！ (自动编组需要买体力)

        if self.is_exists(FIGHT_BTN["zhandoukaishi"]):
            out = self.goto(AfterEnterTiaoZhan, self.fun_click(FIGHT_BTN["zhandoukaishi"]))
            if isinstance(out, ZhiYuanQueRen):
                return out.ok()
            elif isinstance(out, AutoAdvanceSettings):
                self.is_auto_advance = True
                return out.goto_fight(buy_ap)
            else:
                return out
        elif self.is_exists(MAOXIAN_BTN["auto_advance_next"]):
            # 自动编组 借不了支援
            AAS = self.goto(AutoAdvanceSettings, self.fun_click(MAOXIAN_BTN["auto_advance_next"]))
            if isinstance(AAS, AutoAdvanceSettings):
                self.is_auto_advance = True
                return AAS.goto_fight(buy_ap)
            else:
                return False
        
