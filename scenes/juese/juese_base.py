import time
import os
from core.constant import JUESE_BTN, RANKS_DICT
from scenes.scene_base import PCRMsgBoxBase
import time
from core.pcr_config import debug
from core.constant import SHOP_BTN
from DataCenter import LoadPCRData
from core.cv import UIMatcher
import cv2


def get_plate_img_path(charname):
    data = LoadPCRData()
    a = str(data.get_id(name=charname))
    '''
    example: 
    望返回值 102901
    三星前 102911
    三星后 102931
    六星后 102961
    '''
    b = str(a[0:4] + "11")
    c = str(a[0:4] + "31")
    d = str(a[0:4] + "61")
    imgpath_1 = "img/juese/plate/" + b + ".bmp"
    imgpath_2 = "img/juese/plate/" + c + ".bmp"
    imgpath_3 = "img/juese/plate/" + d + ".bmp"
    imgpath = [imgpath_1, imgpath_2]
    if os.path.exists(imgpath_3):
        imgpath.append(imgpath_3)

    return imgpath


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

    def click_plate(self, imgpath, screen=None):
        # 寻找角色，确认碎片图片中心点并点击
        if screen is None:
            screen = self.getscreen()
        at=(24, 67, 919, 384)
        r_list = UIMatcher.img_where(screen, imgpath, threshold=0.8, at=at,
                                     method=cv2.TM_CCOEFF_NORMED, is_black=False, black_threshold=1500)
        if r_list is not False:
            if len(r_list) == 2:
                x_arg = int(r_list[0])
                y_arg = int(r_list[1])
                self.click(x_arg, y_arg)
                return True
            else:
                return False
        else:
            return False

    def dragdown(self):
        obj = self.d.touch.down(621, 364)
        time.sleep(0.1)
        obj.move(620, 70)
        time.sleep(0.8)
        obj.up(620, 70)

    def check_buttom(self):
        fc = [92, 156, 244]
        bc = [158, 164, 176]
        xcor = 922
        ycor = 448
        return self.check_color(fc, bc, xcor, ycor, color_type="rgb")