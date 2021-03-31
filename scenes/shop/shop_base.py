from core.constant import SHOP_BTN
from scenes.root.seven_btn import SevenBTNMixin


class ShopBase(SevenBTNMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ShopBase"
        self.feature = self.fun_feature_exist(SHOP_BTN["shop_left_kkr"])
        self.initFC = self.getFC(False) \
            .getscreen() \
            .exist(SHOP_BTN["middle_kkr"], self.fun_click(1, 1))
