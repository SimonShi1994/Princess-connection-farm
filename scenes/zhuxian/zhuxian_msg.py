from typing import TYPE_CHECKING

from core.constant import FIGHT_BTN, MAOXIAN_BTN
from scenes.scene_base import PCRMsgBoxBase

if TYPE_CHECKING:
    from scenes.shop.xianding import XianDingShangDian



class SaoDangQueRen(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "SaoDangQueRen"

        def feature(screen):
            return self.is_exists(MAOXIAN_BTN["saodang_query"], screen=screen)

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

        def feature(screen):
            a1 = self.is_exists(MAOXIAN_BTN["saodang_tiaoguo"], screen=screen)
            a2 = self.is_exists(MAOXIAN_BTN["saodang_ok2"], screen=screen)
            a3 = self.is_exists(MAOXIAN_BTN["saodang_tiaoguo"], is_black=True, screen=screen)
            return a1 or a2 or a3

        self.initFC = None
        self.feature = feature

    def OK(self):
        def gotofun():
            self.click(473, 475)


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
