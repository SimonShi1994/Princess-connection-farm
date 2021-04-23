import time

from core.constant import MAIN_BTN, JUESE_BTN, DXC_ELEMENT, MAOXIAN_BTN, FIGHT_BTN, JIAYUAN_BTN
from core.cv import UIMatcher
from core.pcr_checker import Checker
from scenes.root.seven_btn import SevenBTNMixin

class GongHuiZhiJia(SevenBTNMixin):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name="GongHuiZhiJia"
        def feature(screen):
            return self.is_exists(JIAYUAN_BTN["quanbushouqu"],screen=screen)

        def f1():
            with self.no_initFC():
                self.chulijiaocheng(turnback=None)
            self.enter()

        self.initFC=self.getFC(False).exist(DXC_ELEMENT["dxc_kkr"],f1,clear=True)
        self.feature=feature

    def gonghuizhijia(self,auto_update=False):
        # 2020-07-31 TheAutumnOfRice: 检查完毕
        # 2020-09-09 CyiceK: 添加升级
        jiaju_list = ["saodangquan", "mana", "jingyan", "tili"]
        self.clear_initFC()
        if auto_update:
            screen_shot = self.getscreen()
            if self.click_img(img="img/jiayuan/jiayuan_shengji.bmp", screen=screen_shot):
                time.sleep(10)

        self.lock_img(JIAYUAN_BTN["guanbi"], elseclick=JIAYUAN_BTN["quanbushouqu"], elsedelay=0.5,
                      side_check=self._a.juqing_kkr, retry=5)

        if auto_update:
            i = 0
            while i <= 3:
                screen_shot = self.getscreen()
                if self.click_img(img="img/jiayuan/jiayuan_shengji.bmp", screen=screen_shot):
                    time.sleep(10)
                # 家具坐标
                self.lock_img(JIAYUAN_BTN["xinxi"], elseclick=JIAYUAN_BTN["jiaju"][jiaju_list[i]], elsedelay=2, retry=3)
                time.sleep(2)
                if self.is_exists(JIAYUAN_BTN["jy_dengjitisheng2"], is_black=True):
                    break
                elif not self.is_exists(JIAYUAN_BTN["zhuye"]):
                    self.click_btn(JIAYUAN_BTN["jy_dengjitisheng"],
                                   until_appear=JIAYUAN_BTN["quxiao"], elsedelay=2, retry=2)
                    time.sleep(3)
                    if self.is_exists(JIAYUAN_BTN["dengjitisheng"], is_black=True, black_threshold=1300):
                        self.lock_img(JIAYUAN_BTN["zhuye"], elseclick=[(1, 1)], retry=3)
                        i = i + 1
                        continue
                    elif self.is_exists(JIAYUAN_BTN["dengjitisheng"]):
                        self.click_btn(JIAYUAN_BTN["dengjitisheng"], until_disappear=JIAYUAN_BTN["dengjitisheng"],
                                       retry=2)
                i = i + 1
                continue

        return self.goto_wodezhuye()


