from typing import TYPE_CHECKING

from core.constant import MAIN_BTN, MAOXIAN_BTN
from scenes.root.seven_btn import SevenBTNMixin

if TYPE_CHECKING:
    from scenes.zhuxian.zhuxian_normal import ZhuXianNormal
    from scenes.zhuxian.zhuxian_hard import ZhuXianHard
    from scenes.zhuxian.zhuxian_base import ZhuXianBase


class MaoXian(SevenBTNMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "MaoXian"

        def feature(screen):
            return self.is_exists(MAIN_BTN["zhuxian"], screen=screen)

        self.initFC = None
        self.feature = feature

    def goto_zhuxian(self) -> "ZhuXianBase":
        from scenes.zhuxian.zhuxian_base import ZhuXianBase
        return self.goto(ZhuXianBase, self.fun_click(MAIN_BTN["zhuxian"]), use_in_feature_only=True)

    def goto_normal(self) -> "ZhuXianNormal":
        from scenes.zhuxian.zhuxian_normal import ZhuXianNormal
        def gotofun():
            self.click(MAOXIAN_BTN["normal_off"])

        return self.goto_zhuxian().goto(ZhuXianNormal, gotofun, use_in_feature_only=True)

    def goto_hard(self)->"ZhuXianHard":
        from scenes.zhuxian.zhuxian_hard import ZhuXianHard
        def gotofun():
            self.click(MAOXIAN_BTN["hard_off"])

        return self.goto_zhuxian().goto(ZhuXianHard, gotofun, use_in_feature_only=True)
