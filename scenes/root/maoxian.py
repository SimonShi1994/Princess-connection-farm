import time
from typing import TYPE_CHECKING, Union

from core.constant import MAIN_BTN, MAOXIAN_BTN, HUODONG_BTN, JUQING_BTN, p
from core.pcr_checker import LockTimeoutError, PCRRetry, ContinueNow
from scenes.root.seven_btn import SevenBTNMixin
from scenes.huodong.huodong_base import HuodongMapBase, HuodongMenu

if TYPE_CHECKING:
    from scenes.zhuxian.zhuxian_normal import ZhuXianNormal
    from scenes.zhuxian.zhuxian_hard import ZhuXianHard
    from scenes.zhuxian.zhuxian_vh import ZhuXianVH
    from scenes.zhuxian.zhuxian_base import ZhuXianBase
    from scenes.maoxian.tansuo import TanSuoMenu
    from scenes.maoxian.tanxian import AfterGotoTanXian
    from scenes.dxc.dxc_select import DXCSelectA, DXCSelectB
    from scenes.maoxian.diaocha import DiaoChaMenu


class MaoXian(SevenBTNMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "MaoXian"

        def feature(screen):
            return self.is_exists(MAIN_BTN["zhuxian"], screen=screen)

        self.initFC = None
        self.feature = feature
        self.initPC = self.clear_note

    def clear_note(self, screen):
        if self.is_exists(MAOXIAN_BTN["notshow"], screen=screen):
            x, y, _ = self.img_where_all(MAOXIAN_BTN["notshow"], screen=screen)
            self.click(x-100, y)
            time.sleep(1)
            self.click(x, y+70)
        return screen

    def goto_zhuxian(self) -> "ZhuXianBase":
        from scenes.zhuxian.zhuxian_base import ZhuXianBase
        return self.goto(ZhuXianBase, self.fun_click(MAIN_BTN["zhuxian"]), use_in_feature_only=True)

    def goto_normal(self) -> "ZhuXianNormal":
        from scenes.zhuxian.zhuxian_normal import ZhuXianNormal
        def gotofun():
            self.click(MAOXIAN_BTN["normal_off"])

        return self.goto_zhuxian().goto(ZhuXianNormal, gotofun, use_in_feature_only=True)

    def goto_hard(self) -> "ZhuXianHard":
        from scenes.zhuxian.zhuxian_hard import ZhuXianHard
        def gotofun():
            self.click(MAOXIAN_BTN["hard_off"])

        return self.goto_zhuxian().goto(ZhuXianHard, gotofun, use_in_feature_only=True)

    def goto_vh(self) -> "ZhuXianVH":
        from scenes.zhuxian.zhuxian_vh import ZhuXianVH
        def gotofun():
            self.click(MAOXIAN_BTN["vh_off"])

        return self.goto_zhuxian().goto(ZhuXianVH, gotofun, use_in_feature_only=True)

    def goto_tansuo(self) -> "TanSuoMenu":
        from scenes.maoxian.tansuo import TanSuoMenu
        return self.goto(TanSuoMenu, self.fun_click(MAIN_BTN["tansuo"]))

    def goto_dxc(self) -> Union["DXCSelectA", "DXCSelectB"]:
        from scenes.dxc.dxc_select import PossibleDXCMenu, DXCSelectA, DXCSelectB, DXCKKR, DXCJuQing
        PS = self.goto(PossibleDXCMenu, self.fun_click(MAIN_BTN["dxc"]))
        while True:
            if isinstance(PS, (DXCKKR, DXCJuQing)):
                PS.skip()
                PS = self.goto_wodezhuye().goto_maoxian().goto(PossibleDXCMenu, self.fun_click(MAIN_BTN["dxc"]))
                continue
            elif isinstance(PS, DXCSelectA):
                return PS
            elif isinstance(PS, DXCSelectB):
                return PS
            else:
                raise LockTimeoutError("进入地下城失败！")

    def goto_diaocha(self) -> "DiaoChaMenu":
        from scenes.maoxian.diaocha import DiaoChaMenu
        return self.goto(DiaoChaMenu, self.fun_click(MAIN_BTN["diaocha"]))

    def goto_huodong(self, code: str, entrance_ind: Union[str, int] = "auto") -> Union["HuodongMapBase", bool]:
        # 进入活动图，冒险->寻找活动按钮，若发现normal，则结束；否则chulijiaocheng，再进入一次，保证进入Map界面。
        # code: 见scenes/huodong/huodong_manager.py
        # entrance_ind: 设置为"auto"时，自动寻找剧情活动按钮；设置为int时，固定为从右往左数第几个按钮
        # Return:
        # False - 未找到活动图标，lockhome； <MAP> 见scenes/huodong/huodong_base.py
        if entrance_ind != "auto":
            entrance_ind = int(entrance_ind)
        from scenes.huodong.huodong_manager import get_huodong_by_code
        # 点击活动图标
        if entrance_ind == "auto":
            for _ in range(10):
                L = self.img_where_all(HUODONG_BTN["jqhd"].img, threshold=0.8)
                M = self.img_where_all(HUODONG_BTN["fuke"].img, threshold=0.8)
                time.sleep(0.2)
                if len(L) > 0:
                    xx, yy = L[0], L[1]
                    break
                elif len(M) > 0:
                    xx, yy = M[0], M[1]
                    break
            else:
                self.log.write_log("error", "未找到活动图标")
                self._a.lock_home()
                return False
        else:
            xx, yy = MAIN_BTN["round_btn"][entrance_ind]

        MAP = get_huodong_by_code(code)
        MAP(self._a).enter_huodong(xx, yy)

        return self.goto(MAP, gotofun=None)

    def goto_tanxian(self) -> "AfterGotoTanXian":
        self.click_btn(MAOXIAN_BTN["tanxian"])
        from scenes.maoxian.tanxian import AfterGotoTanXian
        return AfterGotoTanXian(self._a)

        pass