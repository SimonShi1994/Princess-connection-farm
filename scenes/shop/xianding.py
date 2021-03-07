from core.constant import SHOP_BTN
from scenes.scene_base import PCRSceneBase


class XianDingShangDian(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def buy_all(self):
        self.click(388, 148, post_delay=0.8)
        self.clear_initFC()
        self.click(558, 149, post_delay=0.8)
        self.click(729, 149, post_delay=0.8)
        self.click(900, 148, post_delay=0.8)
        self._a.d.drag(613, 392, 613, 140, duration=0.1)
        self.click(388, 176, post_delay=0.8)
        self.click(559, 175, post_delay=0.8)
        self.click(729, 177, post_delay=0.8)
        self.click(899, 176, post_delay=0.8)
        # 点击购买
        self.click(794, 438)
        # 购买确认
        self.click_btn(SHOP_BTN["xianding_ok"], wait_self_before=True)
        for _ in range(5):
            self.click(24, 84)
        # 立即关闭
        self.click_btn(SHOP_BTN["lijiguanbi"], until_appear=SHOP_BTN["querenchongzhi"])
        # 确认重制
        self.click_btn(SHOP_BTN["querenchongzhi"])
        # 返回
        for _ in range(5):
            self.click(24, 84)
