from typing import TYPE_CHECKING, Union

from core.constant import MAIN_BTN, MAOXIAN_BTN, ZHUCAIDAN_BTN
from core.pcr_checker import LockTimeoutError
from scenes.root.seven_btn import SevenBTNMixin

if TYPE_CHECKING:
    from scenes.zhucaidan.haoyou import HaoYouRoot

class ZhuCaiDan(SevenBTNMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ZhuCaiDan"

        def feature(screen):
            return self.is_exists(ZHUCAIDAN_BTN["bangzhu"], screen=screen)

        self.initFC = None
        self.feature = feature

    def goto_haoyou(self)->"HaoYouRoot":
        from scenes.zhucaidan.haoyou import HaoYouRoot
        return self.goto(HaoYouRoot,self.fun_click(591,232))

