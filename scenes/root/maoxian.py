import time

from core.constant import MAIN_BTN, JUESE_BTN, DXC_ELEMENT, MAOXIAN_BTN, FIGHT_BTN
from core.cv import UIMatcher
from core.pcr_checker import Checker
from scenes.root.seven_btn import SevenBTNMixin

class MaoXian(SevenBTNMixin):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name="MaoXian"
        def feature(screen):
            return self.is_exists(MAIN_BTN["zhuxian"],screen=screen)

        self.initFC=None
        self.feature=feature
