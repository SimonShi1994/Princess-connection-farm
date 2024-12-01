from core.constant import MAIN_BTN, DXC_ELEMENT, TANXIAN_BTN
from ..root.seven_btn import SevenBTNMixin


class TanXianMenu(SevenBTNMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "TanXianMenu"
        self.feature = self.fun_feature_exist(TANXIAN_BTN["tanxian_logo"])
        self.initFC = lambda FC: FC.getscreen().add_sidecheck(self._a.juqing_kkr)