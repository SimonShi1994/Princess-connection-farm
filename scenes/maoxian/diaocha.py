from core.MoveRecord import MoveRestartException
from core.constant import MAIN_BTN, DXC_ELEMENT
from core.pcr_checker import LockMaxRetryError, ContinueNow
from ..fight.fightinfo_base import FightInfoBase
from ..root.seven_btn import SevenBTNMixin


class DiaoChaMenu(SevenBTNMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "DiaoChaMenu"
        self.feature = self.fun_feature_exist(MAIN_BTN["shengjidiaocha"])
        self.initFC = lambda FC: FC.getscreen().add_sidecheck(self._a.juqing_kkr)

    def goto_shengji(self) -> "ShengJiDiaoCha":
        return self.goto(ShengJiDiaoCha, gotofun=self.fun_click(MAIN_BTN["jingyanzhiguanqia"]),
                         use_in_feature_only=False)

    def goto_shendian(self) -> "ShenDianDiaoCha":
        return self.goto(ShenDianDiaoCha, gotofun=self.fun_click(MAIN_BTN["shendiandiaocha"]), use_in_feature_only=False)


class DiaoChaInfoBox(FightInfoBase):

    def shua(self, team_order):
        screen = self.getscreen()
        stars = self.get_upperright_stars(screen)
        if stars == 3:
            # 扫荡
            quan = self.get_saodangquan(screen)
            if quan == 0:
                self.log.write_log("info", f"扫荡券不足，使用手动！")
                return self.easy_shoushua(team_order, one_tili=15, check_cishu=True)
            else:
                return self.easy_saodang("max", one_tili=15, check_cishu=True)
        else:
            # 战斗
            self.log.write_log("info", "还未过关，进行战斗！")
            return self.easy_shoushua(team_order, one_tili=15, check_cishu=True)


class DiaoChaXuanGuanBase(SevenBTNMixin):

    def doit(self, team_order="zhanli"):
        ec = [(539, 146), (541, 255)]
        for xx, yy in ec:
            if not self._a.check_shuatu():
                break
            try:
                DC: DiaoChaInfoBox = self.goto(DiaoChaInfoBox, gotofun=self.fun_click(xx, yy), use_in_feature_only=True,
                                               retry=2, interval=2, before_clear=False)
                DC.shua(team_order)
                self.fclick(1, 1)
            except LockMaxRetryError:
                self.fclick(1, 1)

    def doit_new(self, team_order="zhanli", tu_order=[], shengji=True):
        # 自上到下，未来圣迹调查追加到LV5需要滑动
        ec = [(539, 146), (541, 255), (540, 355)]
        # 圣迹3关，神殿两关(日服至今未追加)
        N_SHENGJI = 3
        N_SHENDIAN = 2
        # 检查输入
        valid_range = range(1, N_SHENGJI+1 if shengji else N_SHENDIAN + 1)
        for i in tu_order:
            assert i in valid_range, f'输入了错误的{"圣迹" if shengji else "神殿"}调查图号-{tu_order}！'
        # 第i关坐标为ec[n-i]
        if shengji:
            ec_l = [ ec[N_SHENGJI-i] for i in tu_order]
        else:
            ec_l = [ ec[2-i] for i in tu_order]
        for xx, yy in ec_l:
            if not self._a.check_shuatu():
                break
            try:
                DC: DiaoChaInfoBox = self.goto(DiaoChaInfoBox, gotofun=self.fun_click(xx, yy), use_in_feature_only=True,
                                               retry=2, interval=2, before_clear=False)
                DC.shua(team_order)
                self.fclick(1, 1)
            except LockMaxRetryError:
                self.fclick(1, 1)

class ShengJiDiaoCha(DiaoChaXuanGuanBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ShengJiDiaoCha"
        self.feature = self.fun_feature_exist(MAIN_BTN["shengji_title"])
        self.initPC = self.shenji_precheck


    def shenji_precheck(self, screen):
        if self.is_exists(MAIN_BTN["karin_middle"], screen=screen) or self.is_exists(MAIN_BTN["kailu_middle"],
                                                                                     screen=screen):
            self.chulijiaocheng(turnback=None)
            self.clear_initFC()
            self._a.restart_this_task()
        return screen


class ShenDianDiaoCha(DiaoChaXuanGuanBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ShenDianDiaoCha"
        self.feature = self.fun_feature_exist(MAIN_BTN["shendian_title"])
        self.initPC = self.shendian_sidecheck

    def shendian_sidecheck(self, screen):
        if self.is_exists(DXC_ELEMENT["dxc_kkr"], screen=screen):
            self.chulijiaocheng(turnback=None)
            self.clear_initFC()
            self._a.restart_this_task()
        return screen
