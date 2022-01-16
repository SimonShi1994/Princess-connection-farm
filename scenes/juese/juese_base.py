import os
import pathlib
import time

import cv2
import numpy as np

from DataCenter import LoadPCRData
from core.constant import JUESE_BTN, RANKS_DICT
from core.cv import UIMatcher
from core.pcr_config import debug
from core.utils import make_it_as_juese_as_possible, checkNameValid
from scenes.scene_base import PCRMsgBoxBase


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
        at = (24, 67, 919, 384)
        r_list = UIMatcher.img_where(screen, imgpath, threshold=0.8, at=at,
                                     method=cv2.TM_CCOEFF_NORMED, is_black=False, black_threshold=1500)
        if r_list is not False:
            if len(r_list) == 2:
                x_arg = int(r_list[0])
                y_arg = int(r_list[1])
                self.goto(CharBase, self.fun_click(x_arg, y_arg), use_in_feature_only=True)
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

class CharBase(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "CharBase"
        self.initFC = None
        # 检测角色强化装备页
        self.feature = self.fun_feature_exist(JUESE_BTN["equip_selected"])

    def goto_menu(self) -> "CharMenu":
        return self.goto(CharMenu, self.fun_click(JUESE_BTN["return_menu"]))

    def get_char_lv_status(self, screen=None):
        if screen is None:
            screen = self.getscreen()
        fc = [69, 123, 247]  # G B R:红点
        bc = [243, 247, 239]  # G B R:面板白
        xcor = 645
        ycor = 64
        self.check_color(fc, bc, xcor, ycor, color_type="gbr", screen=screen)

    def get_auto_upgrade_status(self, screen=None):
        if screen is None:
            screen = self.getscreen()
        fc = [73, 132, 247]  # G B R:红点
        bc = [182, 247, 90]  # G B R:面板蓝
        xcor = 425
        ycor = 415
        a = self.check_color(fc, bc, xcor, ycor, color_type="gbr", screen=screen)
        return a

    def get_equip_status(self, screen=None):
        if screen is None:
            screen = self.getscreen()
        if self.is_exists(JUESE_BTN["yjzb_off"], method="sq", threshold=0.95):
            # 已经穿满
            return 0
        if self.is_exists(JUESE_BTN["yjzb"]):
            # 有装备可穿
            return 1
        if self.is_exists(JUESE_BTN["rank_on"]):
            # 可升rank
            return 2

    def get_enhance_status(self, screen=None):
        if screen is None:
            screen = self.getscreen()
        # return: 0-穿满强化满 1-穿满强化没满 2-没穿满且等级没满； 3-等级没满 4-没穿满
        if self.get_auto_upgrade_status():
            # 没穿满/等级没满，自动强化带红点
            if self.get_char_lv_status():
                if self.get_equip_status() == 0:
                    # 装备及等级都没满，导致自动强化带红点
                    return 2
                else:
                    # 只是等级没满
                    return 3
            else:
                # 没穿满
                return 4
        else:
            # 自动强化不亮/自动强化暗
            if self.is_exists(JUESE_BTN["zdqh_0"]):
                # 自动强化亮，需要刷装备或装备强化
                return 1
            if self.is_exists(JUESE_BTN["zdqh_2"], method="sq", threshold=0.95):
                # 自动强化是暗的,已经穿满强化满
                return 0

    def get_rank(self, screen=None):
        if screen is None:
            screen = self.getscreen()
        out = self.check_dict_id(RANKS_DICT, screen, diff_threshold=0.001)
        for _ in range(3):
            if out is None:
                self.click(525, 71, post_delay=1)
                out = self.check_dict_id(RANKS_DICT, screen, diff_threshold=0.001)
        if out is None:
            self.log.write_log("warning", "获取Rank失败！")
            return None
        return int(out)

    def goto_kaihua(self) -> "CharKaihua":
        return self.goto(CharKaihua, self.fun_click(JUESE_BTN["kaihua_unselected"]))

    def goto_zhuanwu(self) -> "CharZhuanwu":
        return self.goto(CharZhuanwu, self.fun_click(JUESE_BTN["zhuanwu_unselected"]))

    def next_char(self):
        at = (201, 77, 298, 98)
        sc1 = self.getscreen()
        while True:
            self.click(940, 268)
            time.sleep(2)
            sc2 = self.getscreen()
            p = self.img_equal(sc1, sc2, at=at)
            if p < 0.95:
                while True:
                    time.sleep(2)
                    if self.is_exists(JUESE_BTN["equip_unselected"], threshold=0.9):
                        break
                    else:
                        self.fclick(784, 76)
                        time.sleep(2)
                        self.fclick(784, 76)
                        continue
                break
            else:
                sc1 = sc2


class CharKaihua(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "CharKaihua"
        self.initFC = None
        # 检测角色开花页
        self.feature = self.fun_feature_exist(JUESE_BTN["kaihua_selected"])

    def next_char(self):
        at = (483, 119, 760, 141)
        sc1 = self.getscreen()
        while True:
            self.click(940, 268)
            time.sleep(2)
            sc2 = self.getscreen()
            p = self.img_equal(sc1, sc2, at=at)
            if p < 0.95:
                while True:
                    time.sleep(2)
                    if self.is_exists(JUESE_BTN["equip_unselected"], threshold=0.9):
                        break
                    else:
                        self.fclick(784, 76)
                        time.sleep(2)
                        self.fclick(784, 76)
                        continue
                break
            else:
                sc1 = sc2

    def goto_base(self) -> "CharBase":
        return self.goto(CharBase, self.fun_click(JUESE_BTN["equip_unselected"]))

    def get_starup_status(self, screen=None):
        if screen is None:
            screen = self.getscreen()
        if self.is_exists(JUESE_BTN["kaihua_enough"], screen=screen):
            return True
        else:
            return False

    def cainengkaihua(self):
        self.click_btn(JUESE_BTN["do_kaihua"], until_appear=JUESE_BTN["kaihua_confirm"])
        self.click_btn(JUESE_BTN["kaihua_confirm"], until_appear=JUESE_BTN["kaihua_complete"])
        self.fclick(1, 1)

    def get_name(self, screen=None):
        if screen is None:
            screen = self.getscreen()
        at = (483, 119, 760, 141)
        ori_out = self.ocr_center(*at, screen)
        out = make_it_as_juese_as_possible(ori_out)
        if out == "公主宝珠":
            for _ in range(5):
                self.click(121, 172)
            time.sleep(1)
            return self.get_name()
        out = self._check_img_in_list_or_dir(out, (482, 114, 750, 261), "ocrfix/juese", "C_ID", screen)
        return out

    def _check_img_in_list_or_dir(self, target_txt, target_pic_at, target_dir, target_list_name, screen):
        if screen is None:
            screen = self.getscreen()
        data = self._load_data_cache()
        if data is None:
            return target_txt  # No Dataset, Do Nothing.
        target_list = getattr(data, target_list_name)
        if target_txt in target_list:
            return target_txt  # Good
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)
        P = pathlib.Path(target_dir)
        if target_pic_at is not None:
            screen = UIMatcher.img_cut(screen, target_pic_at)
        for p in P.iterdir():
            if p.suffix == ".bmp":
                bmp2 = cv2.imdecode(np.fromfile(str(p), dtype=np.uint8), -1)
                if self.img_equal(screen, bmp2, similarity=0.1) > 0.98:
                    if debug:
                        print("找到相似图片：", p)
                    if p.stem in target_list:
                        return p.stem

        # 失败
        target_name = checkNameValid(target_txt)
        save_target = os.path.join(target_dir, target_name + ".bmp")
        save_target = str(pathlib.Path(save_target))
        cv2.imencode('.bmp', screen)[1].tofile(save_target)
        self.log.write_log("warning", f"文字{target_txt}可能识别有误！请修改{save_target}的文件名为正确的值！")
        return target_txt

    def _load_data_cache(self):
        if hasattr(self, "data_cache"):
            data = getattr(self, "data_cache")
        else:
            from DataCenter import LoadPCRData
            data = LoadPCRData()
            if data is not None:
                setattr(self, "data_cache", data)
        return data


class CharZhuanwu(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "CharZhuanwu"
        self.initFC = None
        # 检测角色开花页
        self.feature = self.fun_feature_exist(JUESE_BTN["zhuanwu_selected"])

    def get_zhuanwu_status(self, screen=None):
        # return: 0-未开放 1-资源不足 2-可穿戴 3-可解锁上限 4-可升级 5-可解锁可升级
        if screen is None:
            screen = self.getscreen()
        if self.is_exists(JUESE_BTN["zhuanwu_lock"], screen=screen):
            return 0
        else:
            if self.is_exists(JUESE_BTN["zhuanwu_equipable"], method="sq", threshold=0.95, screen=screen):
                return 2
            else:
                if self.is_exists(img="img/juese/red_mid.bmp", at=(660, 409, 668, 418), screen=screen):
                    # 解放红点亮
                    if self.is_exists(img="img/juese/red_mid.bmp", at=(879, 409, 887, 418), screen=screen):
                        # 强化红点亮
                        return 5
                    else:
                        return 3
                else:
                    if self.is_exists(img="img/juese/red_mid.bmp", at=(879, 409, 887, 418), screen=screen):
                        # 强化红点亮
                        return 4
                    else:
                        return 1

    def wear_zhuanwu(self):
        self.click_btn(JUESE_BTN["wear"], until_appear=JUESE_BTN["wear_confirm"])
        self.click_btn(JUESE_BTN["wear_confirm"])
        time.sleep(2)

    def unlock_ceiling(self, tozhuanwulv=100):
        self.click_btn(JUESE_BTN["unlock_ceiling"], until_appear=JUESE_BTN["unlock_ceiling_confirm"])
        while True:
            a = self.get_zhuanwu_uplimit_during_unlock()
            if self.is_exists(JUESE_BTN["sucaibuzu"]):
                if debug:
                    print("素材不足")
                self.fclick(1, 1)
                break

            if a <= tozhuanwulv:
                if self.is_exists(JUESE_BTN["unlock_ceiling_need_lv"]):
                    self.fclick(1, 1)
                    break
                if debug:
                    print("解锁上限")
                self.click(585, 476)
                # 点击解锁上限
                time.sleep(5)
                if self.is_exists(JUESE_BTN["unlock_ceiling_off"], method="sq"):
                    self.fclick(1, 1)
                    break
                continue
            else:
                self.fclick(1, 1)
                print("已达到目标专武等级")
                return 2

    def levelup_zhuanwu(self):
        while True:
            if self.is_exists(img="img/juese/red_mid.bmp", at=(879, 409, 887, 418)):
                self.click_btn(JUESE_BTN["levelup_zhuanwu"], until_appear=JUESE_BTN["qhscxz"])
                at = (615, 389, 694, 412)
                sc1 = self.getscreen()
                handle = self._a.d.touch.down(200, 200)
                time.sleep(1)
                while True:
                    time.sleep(1)
                    sc2 = self.getscreen()
                    p = self.img_equal(sc1, sc2, at=at)
                    if p > 0.95:
                        break
                    sc1 = sc2
                handle.up(200, 200)
                # 由于按钮点击认为没点到，只能workround
                self.fclick(810, 470)
                time.sleep(2)
                self.fclick(1, 1)
                continue
            else:
                break

    def get_zhuanwu_uplimit_during_unlock(self, screen=None):
        # OCR获得专武上限目标等级，可靠
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        at = (569, 80, 601, 99)
        out = self.ocr_int(*at, screen_shot=screen)
        return out

    def get_zhuanwu_uplimit_at_panel(self, screen=None):
        # OCR获得专武等级上限，结果不可靠
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        at = (711, 235, 744, 255)
        out = self.ocr_int(*at, screen_shot=screen)
        return out

    def goto_base(self) -> "CharBase":
        return self.goto(CharBase, self.fun_click(JUESE_BTN["equip_unselected"]))

    def goto_menu(self) -> "CharMenu":
        return self.goto(CharMenu, self.fun_click(JUESE_BTN["return_menu"]))