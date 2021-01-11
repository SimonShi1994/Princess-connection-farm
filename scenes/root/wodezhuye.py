import time

from core.constant import MAIN_BTN
from core.cv import UIMatcher
from core.pcr_checker import Checker
from scenes.root.seven_btn import SevenBTNMixin

class WoDeZhuYe(SevenBTNMixin):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name="WoDeZhuYe"
        def feature(screen):
            return self.is_exists(MAIN_BTN["liwu"],screen=screen)

        def f1(screen):
            sc=screen
            num_of_white, _, x, y = UIMatcher.find_gaoliang(sc)
            if num_of_white < 77000:
                with self.no_initFC():
                    self.chulijiaocheng(None)  # 增加对教程的处理功能
            return False

        def f2():
            def f(screen):
                sc=screen
                if self.is_exists(MAIN_BTN["xiazai"], screen=sc):
                    self.click(MAIN_BTN["xiazai"])
                if self.is_exists(MAIN_BTN["liwu"], screen=sc):
                    return True
                self.click(MAIN_BTN["zhuye"])
                # 防卡公告
                self.click(1, 1)
                return False
            self.getFC(False).getscreen().add(Checker(f),rv=True).lock(1,until=True)
            return True

        self.initFC=self.getFC(False).getscreen().add(Checker(f1,name="教程处理"),clear=True).\
            add(Checker(f2,name="其它处理"))
        self.feature=feature
