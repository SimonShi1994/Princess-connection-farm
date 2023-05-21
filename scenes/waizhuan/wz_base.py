import time

from core.constant import JUESE_BTN
from core.constant import p, HUODONG_BTN, MAIN_BTN, JUQING_BTN, WZ_BTN
from scenes.huodong.huodong_fight import BOSS_FightInfoBase
from scenes.scene_base import PCRSceneBase
from scenes.zhuxian.zhuxian_base import ZhuXianBase


class WZ_Gallery(PCRSceneBase):

    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "WZ_Gallery"
        self.feature = self.fun_feature_exist(WZ_BTN["waizhuan_head"])
        self.initPC = self.clear_map

    def clear_map(self, screen):
        if self.is_exists(HUODONG_BTN["shadow_help"], screen=screen):
            self.fclick(1, 1)
        if self.is_exists(WZ_BTN["shadow_waizhuan"], screen=screen):
            self.fclick(1, 1)
        return screen

    def scroll_down(self):
        time.sleep(1)
        obj = self.d.touch.down(934, 250)
        time.sleep(0.1)
        # 目前适配9+6 未来加page
        obj.move(934, 390)
        time.sleep(0.8)
        obj.up(934, 390)
        time.sleep(1)

    def goto_wz_menu(self, code: str) -> "WZ_Menu":
        from scenes.waizhuan.wz_manager import get_wz_by_code
        self.clear_initFC()
        MAP = get_wz_by_code(code)
        BTN_DICT = {
            "01": (380, 155),
            "02": (600, 155),
            "03": (830, 155),
            "04": (380, 342),
            "05": (600, 342),
            "06": (830, 342),
            "07": (380, 440),
            "08": (600, 440),
            "09": (740, 440),
        }
        code_int = int(code)
        time.sleep(2)
        while True:
            if 9 < code_int:
                self.scroll_down()
                code_int = code_int - 6
            else:
                code = "0" + str(code_int)
                break
        T = BTN_DICT[code]
        self.click(T[0], T[1])
        while True:
            out = self.lock_img({
                WZ_BTN["help"]: 1,  # 在menu
                WZ_BTN["saodang_btn"]: 2,  # 在map
                WZ_BTN["enter_wz"]: 3,
                JUQING_BTN["caidanyuan"]: 4,
                WZ_BTN["shujuxiazai"]: 5,
            }, elseclick=(T[0], T[1]), timeout=20, is_raise=False, threshold=0.85)

            if out == 1:
                break
            elif out == 2:
                self.click_btn(HUODONG_BTN["return"], until_appear=WZ_BTN["help"])
                continue
            elif out == 3:
                self.click_btn(WZ_BTN["enter_wz"])
                continue
            elif out == 4:
                self._a.guojuqing(story_type="huodong")
                self.fclick(1, 1)
                continue
            elif out == 5:
                # 选择无语音选项
                # 外传剧情下载弹两种框，一种和剧情框相同，一种只有确认取消
                if self.is_exists(JUQING_BTN["wuyuyin"], at=(410, 277, 553, 452)):
                    self.click_btn(JUQING_BTN["wuyuyin"])
                    time.sleep(2)
                else:
                    self.click_btn(WZ_BTN["shujuxiazai_ok"])
                    time.sleep(2)
                continue
            else:
                self.fclick(1, 1)
                continue

        return self.goto(MAP, gotofun=None)


class WZ_Menu(PCRSceneBase):
    NAME = "UNDEFINED"
    # 坐标
    NXY1 = None
    NXY2 = None
    NXY3 = None
    HXY1 = None
    N1 = 15
    N2 = 15
    N3 = 15
    N_slice = 1

    def __init__(self, a):
        super().__init__(a)
        self.feature = self.fun_feature_exist(WZ_BTN["help"])
        self.initPC = self.clear_map
        self.scene_name = "WZ_Menu"

    def clear_map(self, screen):
        a = self.img_where_all(img="img/ui/quxiao2.bmp", screen=screen, at=(300, 270, 439, 450))
        # 信赖度解锁：如果是推图，则到地图页面跳出。如果是扫荡，则在结算页面跳出。
        b = self.img_where_all(img="img/ui/close_btn_1.bmp", screen=screen, at=(365, 266, 593, 516))
        # 剧情解锁，记录解锁等
        if len(a) > 0:
            self.click(int(a[0]), int(a[1]))
        elif len(b) > 0:
            self.click(int(b[0]), int(b[1]))
        elif self.is_exists(MAIN_BTN["karin_middle"], screen=screen):
            self.chulijiaocheng(None)
            self._a.restart_this_task()
        elif self.is_exists(HUODONG_BTN["shadow_help"], screen=screen):
            self.fclick(1, 1)
            self._a.restart_this_task()
        elif self.is_exists(JUQING_BTN["caidanyuan"], screen=screen):  # 打倒多个boss会出现对话
            self.fclick(1, 1)
        elif self.is_exists(HUODONG_BTN["shadow_return"], screen=screen):
            self.fclick(1, 1)
        elif self.is_exists(HUODONG_BTN["speaker_box"], screen=screen):
            self.fclick(1, 1)
        return screen

    def wz_juqing(self):
        self.clear_initFC()
        self.lock_img(img="img/ui/close_btn_1.bmp", elseclick=(874, 342), elsedelay=3)
        while True:
            time.sleep(1)
            lst = self.img_where_all(img="img/juqing/new_content.bmp", method="sq", at=(245, 98, 320, 442))
            if len(lst) > 0:
                x = lst[0] + 383
                y = lst[1] + 50
                '''
                280, 246
                663, 297
                '''
                self.click(x, y)  # 进入剧情
                time.sleep(1)
                self._a.guojuqing(story_type="huodong")
                continue
            if self.is_exists(JUESE_BTN["lxydjq"]):
                self._a.guojuqing(story_type="huodong")
                continue
            if self.is_exists(JUESE_BTN["lxydjq"].img, at=(394, 73, 564, 100)):
                self._a.guojuqing(story_type="huodong")
                continue
            else:
                self.log.write_log("info", "无可读剧情")
                self.fclick(1, 1)
                break

    def goto_map(self) -> "WZ_MapBase":
        return self.goto(WZ_MapBase, self.fun_click(HUODONG_BTN["huodongguanka"]))

    def goto_nboss(self, timeout=None) -> "BOSS_FightInfoBase":
        while True:
            a1 = self.img_where_all(img=HUODONG_BTN["nboss"].img, at=(682, 152, 826, 358))
            a2 = self.img_where_all(img=HUODONG_BTN["nboss_cn"].img, at=(682, 152, 826, 358))
            a3 = self.img_where_all(img=HUODONG_BTN["nboss_en"].img, at=(682, 152, 826, 358))
            a = a1 + a2 + a3
            if not a:
                time.sleep(2)
                obj = self.d.touch.down(923, 205)
                time.sleep(0.1)
                obj.move(923, 85)
                time.sleep(0.8)
                obj.up(923, 85)
                time.sleep(0.5)
                continue
            else:
                break
        return self.goto(BOSS_FightInfoBase, self.fun_click(a[0], a[1]), timeout=timeout)

    def goto_hboss(self, timeout=None) -> "BOSS_FightInfoBase":
        time.sleep(2)
        while True:
            a1 = self.img_where_all(img=HUODONG_BTN["hboss"].img, at=(682, 152, 826, 358))
            a2 = self.img_where_all(img=HUODONG_BTN["hboss_cn"].img, at=(682, 152, 826, 358))
            a3 = self.img_where_all(img=HUODONG_BTN["hboss_en"].img, at=(682, 152, 826, 358))
            a = a1 + a2 + a3
            if not a:
                time.sleep(2)
                obj = self.d.touch.down(923, 205)
                time.sleep(0.1)
                obj.move(923, 307)
                time.sleep(0.8)
                obj.up(923, 307)
                time.sleep(0.5)
            else:
                break

        return self.goto(BOSS_FightInfoBase, self.fun_click(a[0], a[1]), timeout=timeout)

    def goto_vhboss(self, timeout=None) -> "BOSS_FightInfoBase":
        while True:
            a1 = self.img_where_all(img=HUODONG_BTN["vhboss"].img, at=(682, 152, 826, 358))
            a2 = self.img_where_all(img=HUODONG_BTN["vhboss_cn"].img, at=(682, 152, 826, 358))
            a3 = self.img_where_all(img=HUODONG_BTN["vhboss_en"].img, at=(682, 152, 826, 358))
            a = a1 + a2 + a3
            if not a:
                time.sleep(2)
                obj = self.d.touch.down(923, 205)
                time.sleep(0.1)
                obj.move(923, 307)
                time.sleep(0.8)
                obj.up(923, 307)
                time.sleep(0.5)
            else:
                break
        return self.goto(BOSS_FightInfoBase, self.fun_click(a[0], a[1]), timeout=timeout)

    def get_liwu(self):
        self.lock_img(WZ_BTN["help"], elseclick=(1, 1), elsedelay=1)
        self.click_btn(HUODONG_BTN["liwu"], until_appear=HUODONG_BTN["wanchengqingkuang"])
        time.sleep(0.2)
        self.click(781, 433)  # 收取
        time.sleep(1)
        self.click(478, 468)  # 关闭
        time.sleep(1)

    def goto_menu(self):
        return self.goto(WZ_Menu, self.fun_click(HUODONG_BTN["huodongguanka"]))

    @staticmethod
    def _check_coord(t):
        # t: tuple -> PCRComponent
        # t: None -> raise!
        if t is None:
            raise Exception("该活动图并没有设定该坐标：", t)
        else:
            if isinstance(t, tuple):
                return p(t[0], t[1])
            else:
                return p

    @staticmethod
    def _check_constant(c):
        # t: tuple -> PCRComponent
        # t: None -> raise!
        if c is None:
            raise Exception("该活动图并没有设定该常数：", c)
        else:
            return c


class WZ_MapBase(WZ_Menu, ZhuXianBase):

    def __init__(self, a):
        super().__init__(a)
        self.feature = self.feature_normal_or_hard
        self.initPC = self.clear_map

    def clear_map(self, screen):
        if self.is_exists(JUQING_BTN["caidanyuan"], screen=screen):  # 打倒多个boss会出现对话
            self.fclick(1, 1)
        elif self.is_exists(HUODONG_BTN["shadow_return"], screen=screen):
            self.fclick(1, 1)
        elif self.is_exists(HUODONG_BTN["speaker_box"], screen=screen):
            self.fclick(1, 1)
        return screen

    def feature_normal_or_hard(self, screen):
        normal = self.is_exists(HUODONG_BTN["NORMAL_ON"], screen=screen)
        hard = self.is_exists(HUODONG_BTN["HARD_ON"], screen=screen)
        return normal or hard

    def goto_wz_hard(self):
        self.lock_img(HUODONG_BTN["HARD_ON"], elseclick=HUODONG_BTN["HARD_ON"], method="sq")
        return self

    def goto_wz_normal(self):
        self.lock_img(HUODONG_BTN["NORMAL_ON"], elseclick=HUODONG_BTN["NORMAL_ON"], method="sq")

    def go_left(self, times):
        if times >= 1:
            for _ in range(times):
                time.sleep(1)
                self.click(28, 269)
                time.sleep(2)
        else:
            pass

    def go_right(self, times):
        if times >= 1:
            for _ in range(times):
                time.sleep(1)
                self.click(931, 269)
                time.sleep(2)
        else:
            pass

    def goto_wz_n1(self):
        self.lock_img(HUODONG_BTN["NORMAL_ON"], elseclick=HUODONG_BTN["NORMAL_ON"], method="sq")
        N_slice = self._check_constant(self.N_slice)
        if N_slice == 1:
            self.click(28, 269)
        if N_slice == 2:
            self.click(28, 269)
            time.sleep(2)
            self.click(28, 269)

    def to_leftdown(self):
        time.sleep(4)
        obj = self.d.touch.down(47, 466)
        time.sleep(0.1)
        obj.move(47, 96)
        time.sleep(0.8)
        obj.up(47, 96)
        time.sleep(1)
        obj = self.d.touch.down(84, 80)
        time.sleep(0.1)
        obj.move(600, 80)
        time.sleep(0.8)
        obj.up(600, 80)
        time.sleep(1)

    def goto_menu(self) -> "WZ_Menu":
        return self.goto(WZ_Menu, self.fun_click(HUODONG_BTN["return"]))
