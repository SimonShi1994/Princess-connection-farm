import time
from core.constant import JUESE_BTN, RANKS_DICT
from scenes.scene_base import PCRMsgBoxBase


class CharMenu(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "CharMenu"
        self.initFC = None
        self.feature = self.fun_feature_exist(JUESE_BTN["duiwu"])
        # 我的队伍

    def click_first(self):
        self.fclick(169, 135)
        time.sleep(1)

    def click_second(self):
        self.click(469, 148)
        time.sleep(1)

    def sort_down(self):
        if self.is_exists(JUESE_BTN["sort_down"]):
            return
        else:
            self.click_btn(JUESE_BTN["sort_up"], until_appear=JUESE_BTN["sort_down"])

    def sort_up(self):
        if self.is_exists(JUESE_BTN["sort_up"]):
            return
        else:
            self.click_btn(JUESE_BTN["sort_down"], until_appear=JUESE_BTN["sort_up"])

    def sort_by(self, cat=None):
        cor_dict = {
            'level': (69, 137),
            'zhanli': (287, 137),
            'rank': (508, 137),
            'star': (727, 137),
            'atk': (69, 193),
            'mat': (287, 193),
            'def': (508, 193),
            'mdf': (727, 193),
            'hp': (69, 251),
            'love': (287, 251),
            'zhuanwu': (508, 251),
            'fav': (727, 251),
            'six': (69, 309)
        }
        if cat is None:
            return
        else:
            self.click_btn(JUESE_BTN["sort_by"], until_appear=JUESE_BTN["fenlei"])
            time.sleep(1)
            self.click(cor_dict.get(cat)[0], cor_dict.get(cat)[1])
            # 点击分类类型
            time.sleep(2)
            self.click(597, 477)
            # 点击确认

