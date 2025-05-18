from core.constant import MAIN_BTN
from scenes.caravan.caravan import AfterGoToCaravan, CaravanMenu, FirstEnterCaravan
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
    
    def goto_caravan(self) -> "CaravanMenu":
        out = self.goto(AfterGoToCaravan, gotofun=self.fun_click(MAIN_BTN["caravan"]))
        if isinstance(out, FirstEnterCaravan):
            return out.skip()
        if isinstance(out, CaravanMenu):
            return out


class ZhuYePossibleMsgBox(PossibleSceneList):
    pass  # 暂时好像用不到
