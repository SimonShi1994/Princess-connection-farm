import time

from core.constant import DXC_ELEMENT, FIGHT_BTN
from core.pcr_checker import LockTimeoutError
from scenes.fight.fightbianzu_base import FightBianZuBase
from scenes.fight.fightinfo_base import FightInfoBase
from scenes.fight.fighting_base import FightingBase, FightingLoseBase, FightingWinBase
from scenes.scene_base import PCRMsgBoxBase, PossibleSceneList


class FightInfoDXC(FightInfoBase):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "FightInfoDXC"
        self.feature = self.fun_feature_exist(DXC_ELEMENT["kyzdjs"])

    def goto_tiaozhan(self) -> "FightBianzuDXC":
        return self.goto(FightBianzuDXC, self.fun_click(FIGHT_BTN["tiaozhan2"]))


class FightBianzuDXC(FightBianZuBase):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "FightBianzuDXC"


    def goto_zhandou(self) -> "FightingDXC":
        out = self.goto(AfterEnterTiaoZhan, self.fun_click(FIGHT_BTN["zhandoukaishi"]))
        if isinstance(out, ZhiYuanQueRen):
            return out.ok()
        else:  # FightingDXC
            return out


class ZhiYuanQueRen(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ZhiYuanQueRen"
        self.feature = self.fun_feature_exist(DXC_ELEMENT["zyjsqr"])

    def ok(self) -> "FightingDXC":
        return self.goto(FightingDXC, self.fun_click(DXC_ELEMENT["zyjsqr_ok"]))


class AfterEnterTiaoZhan(PossibleSceneList):
    def __init__(self, a):
        self.ZhiYuanQueRen = ZhiYuanQueRen
        self.FightingDXC = FightingDXC
        scene_list = [
            ZhiYuanQueRen(a),
            FightingDXC(a),
        ]
        super().__init__(a, scene_list, double_check=1.)


class FightingDXC(FightingBase):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "FightingDXC"

    def wait_for_end(self, timeout=300):
        # 1 - Win
        # 2 - Loss
        # raise: LockTimeoutError
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise LockTimeoutError("地下城战斗超时！")
            During = DuringFightingDXC(self._a)
            out = During.check()
            if isinstance(out, During.FightingWinDXC):
                out.ok()
                return 1
            elif isinstance(out, During.FightingLossDXC):
                out.ok()
                return 2


class DuringFightingDXC(PossibleSceneList):
    def __init__(self, a):
        self.FightingWinDXC = FightingWinDXC
        self.FightingLossDXC = FightingLossDXC
        scene_list = [
            FightingWinDXC(a),
            FightingLossDXC(a),
        ]
        super().__init__(a, scene_list, double_check=0.)


class FightingWinDXC(FightingWinBase):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "FightingWinDXC"

    def ok(self):
        self.exit(self.fun_click(836, 491))


class FightingLossDXC(FightingLoseBase):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "FightingLossDXC"
        self.feature = self.lose_feature

    def lose_feature(self, screen):
        from core.constant import p
        duiwu_icon_1 = p(910, 35, img="img/fight/duiwu_icon.bmp", at=(896, 25, 924, 44))
        shbg_1 = p(790, 37, img="img/fight/shbg.bmp", at=(754, 26, 826, 48))
        duiwu_icon_2 = p(850, 35, img="img/fight/duiwu_icon.bmp", at=(836, 25, 864, 44))
        shbg_2 = p(730, 37, img="img/fight/shbg.bmp", at=(694, 26, 766, 48))

        return (self.is_exists(duiwu_icon_1, screen=screen) and self.is_exists(shbg_1, screen=screen)) or \
               (self.is_exists(duiwu_icon_2, screen=screen) and self.is_exists(shbg_2, screen=screen))

    def ok(self):
        self.exit(self.fun_click(814, 493))
