"""
地下城选大关，小关部分
"""
import time
from typing import Optional

from automator_mixins._base import OCRRecognizeError
from core.constant import DXC_ELEMENT, DXC_ENTRANCE_DRAG, DXC_ENTRANCE, JUQING_BTN, MAIN_BTN
from core.pcr_checker import LockError, LockTimeoutError
from scenes.dxc.dxc_fight import FightInfoDXC
from scenes.scene_base import PossibleSceneList, PCRMsgBoxBase, PCRSceneBase
from scenes.zhuxian.zhuxian_base import SevenBTNMixin


class PossibleDXCMenu(PossibleSceneList):
    def __init__(self, a):
        self.DXCSelectA = DXCSelectA
        self.DXCSelectB = DXCSelectB
        self.DXCKKR = DXCKKR
        self.DXCJuQing = DXCJuQing
        self.ShouQuBaoChou = ShouQuBaoChou
        scene_list = [
            DXCKKR(a),
            ShouQuBaoChou(a),
            DXCJuQing(a),
            DXCSelectA(a),
            DXCSelectB(a),
        ]
        # 使用场景双判，因此MsgBox的DXCKKR,ShouQuBaoChou要往前放，JuQing,A,B作为Scene往后。
        super().__init__(a, scene_list, double_check=1., timeout=90, check_double_scene=True)


class DXCSelectA(SevenBTNMixin):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "DXCSelectA"
        self.feature = self.fun_feature_exist(DXC_ELEMENT["sytzcs"])

    def get_cishu(self):
        cishu = self.check_dict_id({
            0: DXC_ELEMENT["0/1"],
            1: DXC_ELEMENT["1/1"]
        })
        return cishu

    def enter_dxc(self, dxc_id) -> "DXCSelectB":
        drag = DXC_ENTRANCE_DRAG[dxc_id]

        def do_fun():
            if drag == "left":
                self.click(10, 242)
                # self.Drag_Left(origin=True)
                time.sleep(1.5)
            elif drag == "right":
                # self.Drag_Right(origin=True)
                self.click(950, 242)
                time.sleep(1.5)
            self.click(DXC_ENTRANCE[dxc_id])

        PS = self.goto(PossibleDXCMenu, do_fun)
        while True:
            if isinstance(PS, (DXCKKR, DXCJuQing)):
                PS.skip()
                PS = self.goto_maoxian().goto(PossibleDXCMenu, self.fun_click(MAIN_BTN["dxc"]))
                continue
            elif isinstance(PS, DXCSelectB):
                return PS
            else:
                raise LockTimeoutError("进入地下城失败！")


class DXCSelectB(SevenBTNMixin):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "DXCSelectB"
        self.feature = self.fun_feature_exist(DXC_ELEMENT["in_sytzcs"])

    def goto_chetui(self) -> "DXCCheTui":
        return self.goto(DXCCheTui, self.fun_click(DXC_ELEMENT["chetui"]))

    def click_xy_and_open_fightinfo_xy(self, x, y) -> Optional[FightInfoDXC]:
        def gotofun():
            self.click(x, y)

        try:
            return self.goto(FightInfoDXC, gotofun, retry=3, interval=3)
        except LockError:
            return None

    def get_cishu(self, screen=None):
        # OCR获取还可以挑战的次数
        at = (786, 419, 817, 438)
        A, B = self.ocr_A_B(*at, screen_shot=screen)
        return A

    def get_jieshu(self, screen=None):
        # OCR获取当前层数
        at = (582, 422, 614, 437)
        try:
            A, B = self.ocr_A_B(*at, screen_shot=screen)
        except OCRRecognizeError as e:
            self.log.write_log("warning", f"OCR获取层数失败！将从1层开始尝试。{e}")
            return 1
        return A

    def get_next_id(self, screen=None):
        # 寻找“层”字，试图获得下一层的xy
        # 备用，并不准备使用这个。
        LST = self.img_where_all(DXC_ELEMENT["ceng"], threshold=0.8, screen=screen)
        if len(LST) == 0:
            return -1  # 找不到层
        else:
            NLST = []  # Reshape
            now = []
            for L in LST:
                now.append(L)
                if len(now) == 3:
                    NLST.append(now)
                    now = []
            XY = []
            for x, y, _ in NLST:
                x0 = x
                y0 = y - 100
                if y0 < 1:
                    y0 = 1
                XY.append((x0, y0))


class ShouQuBaoChou(PCRMsgBoxBase):
    def __init__(self, a):
        super().__init__(a)
        self.feature = self.fun_feature_exist(DXC_ELEMENT["shouqubaochou_ok"])

    def ok(self):
        self.exit(self.fun_click(475, 481))  # ok


class DXCKKR(PCRMsgBoxBase):
    def __init__(self, a):
        super().__init__(a)
        self.feature = self.fun_feature_exist(DXC_ELEMENT["dxc_kkr"])

    def skip(self):
        self.chulijiaocheng(None)


class DXCJuQing(PCRSceneBase):
    def __init__(self, a):
        super().__init__(a)
        self.feature = self.fun_feature_exist(JUQING_BTN["caidanyuan"])

    def skip(self):
        self.chulijiaocheng(None)


class DXCCheTui(PCRMsgBoxBase):
    def __init__(self, a):
        super().__init__(a)
        self.feature = self.fun_feature_exist(DXC_ELEMENT["chetuiqueren"])

    def ok(self) -> "DXCSelectA":
        return self.goto(DXCSelectA, self.fun_click(DXC_ELEMENT["chetui_ok"]))
