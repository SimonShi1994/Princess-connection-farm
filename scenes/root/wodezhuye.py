from core.constant import MAIN_BTN
from scenes.root.seven_btn import SevenBTNMixin
from scenes.scene_base import PossibleSceneList


class WoDeZhuYe(SevenBTNMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "WoDeZhuYe"

        def feature(screen):
            return self.is_exists(MAIN_BTN["liwu"], screen=screen)

        self.initFC = None
        self.feature = feature


class ZhuYePossibleMsgBox(PossibleSceneList):
    pass  # 暂时好像用不到
