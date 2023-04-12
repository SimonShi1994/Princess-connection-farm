from core.constant import SHOP_BTN
from scenes.shop.shop_base import ShopBase


class XianDingShangDian(ShopBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def buy_all(self):
        self.clear_initFC()
        self.click(911, 64, post_delay=0.5)
        self.click(694, 124, post_delay=0.5)
        self.click(856, 126, post_delay=0.5)

        # 点击购买
        self.click(794, 438)
        # 购买确认
        self.click_btn(SHOP_BTN["xianding_ok"], wait_self_before=True)
        for _ in range(5):
            self.click(24, 84)
        # # 立即关闭
        # self.click_btn(SHOP_BTN["lijiguanbi"], until_appear=SHOP_BTN["querenchongzhi"])
        # # 确认重制
        # self.click_btn(SHOP_BTN["querenchongzhi"])
        # # 返回
        # for _ in range(5):
        #     self.click(24, 84)

    def back(self):
        self.click_btn(SHOP_BTN["fanhui"])
        self.wait_for_loading()