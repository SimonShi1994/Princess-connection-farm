import time

from core.constant import MAIN_BTN, JUESE_BTN, DXC_ELEMENT, MAOXIAN_BTN, FIGHT_BTN
from core.cv import UIMatcher
from core.pcr_checker import Checker
from scenes.root.seven_btn import SevenBTNMixin

class JueSe(SevenBTNMixin):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name="JueSe"
        def feature(screen):
            return self.is_exists(JUESE_BTN["duiwu"],screen=screen)

        def f1():
            with self.no_initFC():
                self.chulijiaocheng(turnback=None)
            self.enter()

        self.initFC=self.getFC(False).exist(DXC_ELEMENT["dxc_kkr"],f1,clear=True)
        self.feature=feature

    def check_level_sort(self):
        # 等级降序
        sc = self.getscreen()
        p0 = self.img_prob(JUESE_BTN["sort_up"], screen=sc)
        p1 = self.img_prob(JUESE_BTN["sort_down"], screen=sc)
        if p0 > p1:
            self.click_btn(JUESE_BTN["sort_up"])
        if not self.is_exists(JUESE_BTN["sort_level"]):
            self.click_btn(JUESE_BTN["sort_level"], until_appear=FIGHT_BTN["cat_ok"])
            self.click(FIGHT_BTN["cat_dengji"], pre_delay=0.5, post_delay=1)
            self.click_btn(FIGHT_BTN["cat_ok"])
        self.clear_initFC()
        return self
