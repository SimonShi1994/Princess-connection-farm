from typing import TYPE_CHECKING, Union

from core.constant import FIGHT_BTN, MAOXIAN_BTN
from core.pcr_checker import LockError
from scenes.scene_base import PCRMsgBoxBase, PossibleSceneList

if TYPE_CHECKING:
    from scenes.shop.xianding import XianDingShangDian



class SaoDangQueRen(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "SaoDangQueRen"

        def feature(screen):
            return self.is_exists(MAOXIAN_BTN["sdqqr"], screen=screen)

        self.initFC = None
        self.feature = feature

    def OK(self) -> "SaoDangJieGuo":
        def gotofun():
            self.click(591, 369)

        return self.goto(SaoDangJieGuo, gotofun)


class SaoDangJieGuo(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "SaoDangJieGuo"
        self._last_see_ok2 = False

        def feature(screen):
            a1 = self.is_exists(MAOXIAN_BTN["saodang_tiaoguo"], screen=screen)
            a2 = self.is_exists(MAOXIAN_BTN["saodang_ok2"], screen=screen)
            self._last_see_ok2 = a2
            a3 = self.is_exists(MAOXIAN_BTN["saodang_tiaoguo"], is_black=True, screen=screen)
            return a1 or a2 or a3

        self.initFC = None
        self.feature = feature

    def OK(self) -> "AfterSaoDangScene":
        def _click():
            self.click(473, 475, post_delay=1 if self._last_see_ok2 else 2)

        self.exit(_click, interval=4)
        return AfterSaoDangScene(self._a)


class ChaoChuShangXianBox(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ChaoChuShangXianBox"
        self.feature = self.fun_feature_exist(MAOXIAN_BTN["chaochushangxian"])

    def OK(self):
        self.exit(self.fun_click(38, 24))  # Outside


class LevelUpBox(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "LevelUpBox"
        self.feature = self.fun_feature_exist(FIGHT_BTN["dengjitisheng"])

    def OK(self):
        self.exit(self.fun_click(38, 24))  # Outside


class TuanDuiZhanBox(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "TuanDuiZhanBox"
        self.feature = self.fun_feature_exist(MAOXIAN_BTN["tuanduizhan"])

    def OK(self):
        self.click_btn(MAOXIAN_BTN["tuanduizhan_quxiao"])  # 跳过团队站


class XianDingShangDianBox(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "XianDingShangDianBox"
        self.feature = self.fun_feature_exist(MAOXIAN_BTN["xianding"])

    def Go(self) -> "XianDingShangDian":
        from scenes.shop.xianding import XianDingShangDian
        return self.goto(XianDingShangDian, self.fun_click(MAOXIAN_BTN["xianding"]))

    def Cancel(self):
        self.exit(self.fun_click(1, 1))  # OutSide


class AfterSaoDangScene(PossibleSceneList):
    def __init__(self, a, *args, **kwargs):
        msgbox_list = [
            ChaoChuShangXianBox(a),
            LevelUpBox(a),
            TuanDuiZhanBox(a),
            XianDingShangDianBox(a),
        ]
        self.ChaoChuShangXianBox = ChaoChuShangXianBox
        self.LevelUpBox = LevelUpBox
        self.TuanDuiZhanBox = TuanDuiZhanBox
        self.XianDingShangDianBox = XianDingShangDianBox
        super().__init__(a,msgbox_list)

class BuyTiliBox(PCRMsgBoxBase):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name = "BuyTiliBox"
        self.feature = self.fun_feature_exist(MAOXIAN_BTN["tlhf"])

    def OK(self)->Union["BuyTiliSuccessBox","EmptyOK"]:
        try:
            return self.goto(BuyTiliSuccessBox,self.fun_click(MAOXIAN_BTN["buytili_ok"]))
        except LockError:
            # 这个框不检测也没问题。直接左上角跳过。
            return self.goto(EmptyOK,self.fun_click(1,1))

class EmptyOK(PCRMsgBoxBase):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name = "无能狂怒"

    def OK(self):
        for _ in range(6):
            self.click(1,1)


class BuyTiliSuccessBox(PCRMsgBoxBase):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name = "BuyTiliSuccessBox"
        self.feature = self.fun_feature_exist(MAOXIAN_BTN["tili_success"])
    def OK(self):
        for _ in range(6):
            self.click(1,1)