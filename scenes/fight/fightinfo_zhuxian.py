from math import inf

from core.constant import FIGHT_BTN
from scenes.fight.fightinfo_base import FightInfoBase
import numpy as np

class FightInfoZhuXian(FightInfoBase):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name="FightInfoZhuXian"
        def feature(screen):
            return self.is_exists(FIGHT_BTN["tgdw"],screen=screen)

        self.initFC=None
        self.feature=feature

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

    def get_saodangquan(self,screen=None):
        # OCR获得扫荡券数量
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        at=(836,271,888,291)
        out = self.ocr_int(*at,screen_shot=screen)
        return out

    def get_tili_left(self, screen=None):
        # OCR获得扫荡前体力数量
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        at=(658,404,700,423)
        out = self.ocr_int(*at, screen_shot=screen)
        return out

    def get_tili_right(self, screen=None):
        # OCR获得扫荡后体力数量
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        at = (711, 405, 748, 422)
        out = self.ocr_int(*at, screen_shot=screen)
        return out

    def get_cishu(self, screen=None, get_B=False):
        # OCR获得剩余次数
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        if self.is_exists(FIGHT_BTN["infinity"]):
            return inf
        at=(860,403,920,424)
        A,B = self.ocr_A_B(*at, screen_shot=screen)
        if get_B:
            return A,B
        else:
            return A