from typing import TYPE_CHECKING, Union

from core.constant import FIGHT_BTN, MAOXIAN_BTN, MAIN_BTN, SHOP_BTN
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
            # For Tansuo:
            a4 = self.is_exists(MAIN_BTN["tansuo_saodangok2"], screen=screen)
            return a1 or a2 or a3 or a4

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
        self.feature = self.fun_feature_exist(MAOXIAN_BTN["suoxumana"])

    def buy_all(self):
        self.click(659, 122, post_delay=0.5)
        self.click(858, 120, post_delay=0.5)
        self.lock_img(SHOP_BTN["xianding_ok"], elseclick=(822, 469))
        self.click_btn(SHOP_BTN["xianding_ok"])
        self.fclick(1, 1, times=10, post_delay=1.0)
        self.fclick(1, 1)

    def Cancel(self):
        self.fclick(1, 1)


class KKRQianBao(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "KKRQianBao"
        self.feature = self.fun_feature_exist(MAOXIAN_BTN["kkr_qianbao"])

    def set_and_ok(self):
        self.click(388, 302, post_delay=0.5)
        self.click(475, 366)


class AfterSaoDangScene(PossibleSceneList):
    def __init__(self, a):
        msgbox_list = [
            KKRQianBao(a),
            ChaoChuShangXianBox(a),
            LevelUpBox(a),
            TuanDuiZhanBox(a),
            XianDingShangDianBox(a),
        ]
        self.ChaoChuShangXianBox = ChaoChuShangXianBox
        self.LevelUpBox = LevelUpBox
        self.TuanDuiZhanBox = TuanDuiZhanBox
        self.XianDingShangDianBox = XianDingShangDianBox
        self.KKRQianBao = KKRQianBao
        super().__init__(a,msgbox_list)

    def exit_all(self,xianding=False):
        """
        扫荡后关闭所有对话框
        xianding：是否进入限定商店。
        """
        while True:
            out = self.check()
            if out is None:  # 无msgbox
                break
            if isinstance(out, self.XianDingShangDianBox):
                # 限定商店
                if xianding:
                    out.buy_all()
                else:
                    out.Cancel()
            if isinstance(out, self.TuanDuiZhanBox):
                out.OK()
            if isinstance(out, self.LevelUpBox):
                out.OK()
                self._a.start_shuatu()  # 体力又有了！
            if isinstance(out, self.ChaoChuShangXianBox):
                out.OK()
            if isinstance(out, self.KKRQianBao):
                out.set_and_ok()


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