import time
from math import inf

import numpy as np

from automator_mixins._base import DEBUG_RECORD
from core.constant import MAOXIAN_BTN, FIGHT_BTN
from core.pcr_checker import LockMaxRetryError
from core.pcr_config import save_debug_img, ocr_mode
from scenes.fight.fightbianzu_zhuxian import FightBianZuZhuXian
from scenes.scene_base import PCRMsgBoxBase
from scenes.zhuxian.zhuxian_msg import SaoDangQueRen


class FightInfoBase(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightInfo"
        self.initFC = None
        self.feature = self.fun_feature_exist(FIGHT_BTN["baochou"])

    def get_upperright_stars(self, screen=None):
        """
        获取右上角当前关卡的星星数
        :param screen: 设置为None时，不另外截屏
        :return: 0~3
        """
        if screen is None:
            screen = self.getscreen()
        fc = np.array([98, 228, 245])  # G B R:金色
        bc = np.array([212, 171, 139])  # G B R:灰色
        c = []
        us = FIGHT_BTN["upperright_stars"]
        for i in range(1, 4):
            x = us[i].x
            y = us[i].y
            c += [screen[y, x]]
        c = np.array(c)
        tf = np.sqrt(((c - fc) ** 2)).sum(axis=1)
        tb = np.sqrt(((c - bc) ** 2)).sum(axis=1)
        t = tf < tb
        return np.sum(t)

    def get_saodangquan(self, screen=None):
        # OCR获得扫荡券数量
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        at = (841, 272, 887, 291)
        out = self.ocr_int(*at, screen_shot=screen)
        return out

    def get_tili_left(self, screen=None):
        # OCR获得扫荡前体力数量
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        at = (668, 406, 699, 421) if ocr_mode == "网络" or ocr_mode == "智能" else (658, 404, 700, 423)
        out = self.ocr_int(*at, screen_shot=screen)
        return out

    def get_tili_right(self, screen=None):
        # OCR获得扫荡后体力数量
        # TODO: 没体力
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        at = (712, 406, 742, 421) if ocr_mode == "网络" or ocr_mode == "智能" else (711, 405, 748, 422)
        out = self.ocr_int(*at, screen_shot=screen)
        return out

    def get_cishu(self, screen=None, get_B=False):
        # OCR获得剩余次数
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        if self.is_exists(FIGHT_BTN["infinity"]):
            return inf
        at = (860, 403, 920, 424)
        A, B = self.ocr_A_B(*at, screen_shot=screen)
        if get_B:
            return A, B
        else:
            return A

    def is_new_map(self, screen=None):
        # 判断是不是还没打过的图
        return self.get_upperright_stars(screen) == 0

    @DEBUG_RECORD
    def set_saodang_cishu(self, target: int, one_tili=None, left_tili=None, right_tili=None, sc=None, max_retry=6,
                          delay=1):
        # 设定扫荡次数
        if sc is None:
            sc = self.getscreen()
        if left_tili is None:
            left_tili = self.get_tili_left(sc)
        if right_tili is None:
            right_tili = self.get_tili_right(sc)
        if one_tili is None:
            one_tili = left_tili - right_tili
        now_cishu = (left_tili - right_tili) // one_tili  # 使用X张 的识别效果很不好
        retry = 0
        while now_cishu != target:
            if retry >= max_retry:
                raise LockMaxRetryError("设定扫荡次数尝试过多！")
            if now_cishu < target:
                for _ in range(target - now_cishu):
                    self.click(MAOXIAN_BTN["saodang_plus"])
            elif now_cishu > target:
                for _ in range(now_cishu - target):
                    self.click(MAOXIAN_BTN["saodang_minus"])
            time.sleep(delay)
            right_tili = self.get_tili_right()
            now_cishu = (left_tili - right_tili) // one_tili
            if abs(now_cishu - target) > 5:
                self.log.write_log("warning", "可能是OCR出现问题，体力识别失败了！")
                if save_debug_img:
                    self._a.save_last_screen(f"debug_imgs/tili_rec_{time.time()}.bmp")
                return
            retry += 1

    def goto_saodang(self) -> SaoDangQueRen:
        return self.goto(SaoDangQueRen, self.fun_click(MAOXIAN_BTN["saodang_on"]))

    def goto_tiaozhan(self) -> FightBianZuZhuXian:
        return self.goto(FightBianZuZhuXian, self.fun_click(FIGHT_BTN["tiaozhan2"]))
