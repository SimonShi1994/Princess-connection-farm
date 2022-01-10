import time

from core.constant import MAIN_BTN, MAOXIAN_BTN
from ..fight.fightinfo_base import FightInfoBase
from ..root.seven_btn import SevenBTNMixin
from ..scene_base import PossibleSceneList


class TanSuoMenu(SevenBTNMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "TanSuoMenu"
        self.feature = self.fun_feature_exist(MAIN_BTN["jingyanzhiguanqia"])
        self.initFC = self.getFC(False).getscreen().add_sidecheck(self._a.right_kkr)

    def goto_jingyan(self) -> "TanSuoJingYan":
        return self.goto(TanSuoJingYan, gotofun=self.fun_click(MAIN_BTN["jingyanzhiguanqia"]), use_in_feature_only=True)

    def goto_mana(self) -> "TanSuoMaNa":
        return self.goto(TanSuoMaNa, gotofun=self.fun_click(MAIN_BTN["managuanqia"]), use_in_feature_only=True)


class TanSuoXuanGuanBase(SevenBTNMixin):
    NAME = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "TanSuoXuanGuanBase"
        self.feature = self.fun_feature_exist(MAIN_BTN["tansuo_sytzcs"])

    def back(self) -> "TanSuoMenu":
        return self.goto(TanSuoMenu, self.fun_click(MAIN_BTN["tansuo_back"]))

    def get_cishu_left(self, screen=None):
        if screen is None:
            screen = self.getscreen()
        left_at = (659, 433, 676, 450)
        lc = self.ocr_int(*left_at, screen_shot=screen)
        return lc

    def get_cishu_right(self, screen=None):
        if screen is None:
            screen = self.getscreen()
        right_at = (682, 435, 692, 448)

        rc = self.ocr_int(*right_at, screen_shot=screen)
        return rc

    def try_click(self, mode) -> "TanSuoInfoBox":
        """
        mode=0 刷最上关卡（适合大号）
        mode=1 刷最上关卡，若无法点进则刷次上关卡（适合小号推探索图）
        mode=2 刷次上关卡，若无法点进则刷最上关卡（适合小号日常探索）
        """
        if mode == 0:
            ec = [(539, 146)]
        elif mode == 1:
            ec = [(539, 146), (541, 255)]
        else:
            ec = [(541, 255), (539, 146)]

        def gotofun():
            for p in ec:
                self.click(*p)

        IB = self.goto(TanSuoInfoBox, gotofun, retry=3)
        IB.NAME = self.NAME
        return IB


class PossibleTansuoScene(PossibleSceneList):
    def __init__(self, a, *args, **kwargs):
        self.TanSuoMenu = TanSuoMenu
        self.TanSuoXuanGuanBase = TanSuoXuanGuanBase
        super().__init__(a, scene_list=[
            TanSuoMenu(a),
            TanSuoXuanGuanBase(a),
        ])


class TanSuoInfoBox(FightInfoBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = None
        self.NAME = ""

    def shua(self, team_order):
        screen = self.getscreen()
        stars = self.get_upperright_stars(screen)
        if stars == 3:
            # 扫荡
            quan = self.get_saodangquan(screen)
            if quan == 0:
                self.log.write_log("info", f"扫荡券不足，使用手动！")
                return self.tiaozhan(team_order)
            else:
                return self.saodang_all()
        else:
            # 战斗
            self.log.write_log("info", "还未过关，进行战斗！")
            return self.tiaozhan(team_order)

    def saodang_all(self):
        for _ in range(10):
            self.click(MAOXIAN_BTN["saodang_plus"])
        S = self.goto_saodang()
        J = S.OK()
        J.OK()
        for _ in range(6):
            self.click(1, 1)
        self.state = True
        return PossibleTansuoScene(self._a)

    def tiaozhan(self, team_order):
        T = self.goto_tiaozhan()
        T.select_team(team_order)
        F = T.goto_fight()
        F.set_auto(1)
        F.set_speed(1)
        D = F.get_during()
        while True:
            time.sleep(1)
            out = D.check()
            if isinstance(out, D.FightingWinZhuXian):
                self.log.write_log("info", f"战胜于：{self.NAME}！")
                self.state = True
                out.next()
                A = out.get_after()
                while True:
                    out = A.check()
                    if isinstance(out, A.FightingWinZhuXian2):
                        out.next()
                        return PossibleTansuoScene(self._a)

            elif isinstance(out, D.FightingLoseZhuXian):
                self.log.write_log("info", f"战败于：{self.NAME}！")
                self.state = False
                out.exit(self.fun_click(814, 493))
                return PossibleTansuoScene(self._a)


class TanSuoJingYan(TanSuoXuanGuanBase):
    NAME = "经验值关卡"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "TanSuoJingYan"


class TanSuoMaNa(TanSuoXuanGuanBase):
    NAME = "玛娜关卡"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "TanSuoMana"
