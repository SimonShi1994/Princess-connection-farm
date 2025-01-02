import time
from math import inf
from typing import Union

import numpy as np

from automator_mixins._base import DEBUG_RECORD
from core.constant import MAOXIAN_BTN, FIGHT_BTN, NORMAL_COORD, HARD_COORD, MAIN_BTN, p
from core.pcr_checker import LockMaxRetryError
from core.pcr_config import save_debug_img, ocr_mode_main
from scenes.fight.fightbianzu_zhuxian import FightBianZuZhuXian
from scenes.scene_base import PCRMsgBoxBase
from scenes.zhuxian.zhuxian_msg import SaoDangQueRen


class FightInfoBase(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightInfo"
        self.initFC = None
        # 检测编组设定
        self.feature = self.fun_feature_exist(FIGHT_BTN["baochou"])

    def next_map(self):
        at1 = (164, 34, 380, 64)  # 标题
        at2 = (150, 228, 481, 317)  # 怪物
        at3 = (144, 399, 399, 482)  # 报酬
        at4 = (857, 17, 922, 68)  # 星
        sc1 = self.getscreen()
        cnt = 0
        while True:
            cnt += 1
            if cnt > 100:
                raise Exception("连续按了100次”下一张图“了，可能出BUG了！")
            self.click(930, 247)
            time.sleep(0.5)
            sc2 = self.getscreen()
            con1 = self.img_equal(sc1, sc2, at=at1)
            con2 = self.img_equal(sc1, sc2, at=at2)
            con3 = self.img_equal(sc1, sc2, at=at3)
            con4 = self.img_equal(sc1, sc2, at=at4)
            con = con1 * con2 * con3 * con4
            if con < 0.96:
                break
            else:
                sc1 = sc2

    def to_last_map(self, max_tu: int = 15):  # 尽量从1-1开始点
        at1 = (164, 34, 380, 64)  # 标题
        at2 = (150, 228, 481, 317)  # 怪物
        at3 = (144, 399, 399, 482)  # 报酬
        at4 = (857, 17, 922, 68)  # 星
        count = 1
        sc1 = self.getscreen()
        while True:
            self.click(930, 247)
            count += 1
            time.sleep(0.5)
            self.log.write_log("info", f"在{count}图")

            if count == max_tu:
                self.log.write_log("info", "推断最后一图")
                return "finish"
            sc2 = self.getscreen()
            con1 = self.img_equal(sc1, sc2, at=at1)
            con2 = self.img_equal(sc1, sc2, at=at2)
            con3 = self.img_equal(sc1, sc2, at=at3)
            con4 = self.img_equal(sc1, sc2, at=at4)
            con = con1 * con2 * con3 * con4
            if con > 0.96:
                self.log.write_log("info", "已到最后一图")
                break
            else:
                sc1 = sc2

    def exit_me(self):
        def exit_fun():
            self.fclick(1, 1)

        self.exit(exit_fun)

    def get_upperright_stars(self, screen=None):
        """
        获取右上角当前关卡的星星数
        :param screen: 设置为None时，不另外截屏
        :return: 0~3
        """
        if screen is None:
            screen = self.getscreen()
        fc = np.array([98, 228, 245])  # G B R:金色
        bc = np.array([212, 171, 139])  # G B R:灰色
        c = []
        us = FIGHT_BTN["upperright_stars"]
        for i in range(1, 4):
            x = us[i].x
            y = us[i].y
            c += [screen[y, x]]
        c = np.array(c)
        tf = np.sqrt(((c - fc) ** 2)).sum(axis=1)
        tb = np.sqrt(((c - bc) ** 2)).sum(axis=1)
        t = tf < tb
        return np.sum(t)

    def get_first_item_count(self):
        # OCR获得第一个item（一般是角色碎片）的当前持有数
        self.check_ocr_running()
        at = (836, 182, 890, 202)
        first_icon = (187, 360)
        handle = self._a.d.touch.down(*first_icon)
        time.sleep(1.5)
        sc = self.getscreen()
        out = self.ocr_int(*at, sc)
        handle.up(*first_icon)
        time.sleep(0.8)  # 防止残留
        return out

    def get_saodangquan(self, screen=None):
        # OCR获得扫荡券数量
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        at = (841, 272, 887, 291)
        out = self.ocr_int(*at, screen_shot=screen)
        return out

    def get_tili_left(self, screen=None):
        # OCR获得扫荡前体力数量
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        at = (668, 406, 700, 421) if ocr_mode_main[:2] == "网络" else (658, 404, 700, 423)
        out = self.ocr_int(*at, screen_shot=screen)
        return out

    def no_tili_for_one_fight(self, screen=None):
        if screen is None:
            screen = self.getscreen()
        return self.is_exists(MAOXIAN_BTN["no_tili_right"], screen=screen)

    def get_tili_right(self, screen=None):
        # OCR获得扫荡后体力数量
        # -1: 没体力，一次都干不了
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        if self.no_tili_for_one_fight(screen):
            return -1
        at = (710, 405, 750, 423) if ocr_mode_main[:2] == "网络" else (711, 405, 748, 422)
        out = self.ocr_int(*at, screen_shot=screen)
        return out

    def get_cishu(self, screen=None, get_B=False):
        # OCR获得剩余次数
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        if self.is_exists(FIGHT_BTN["infinity"]):
            return inf
        at = (860, 403, 920, 424)
        A, B = self.ocr_A_B(*at, screen_shot=screen)
        if get_B:
            return A, B
        else:
            return A

    def is_new_map(self, screen=None):
        # 判断是不是还没打过的图
        return self.get_upperright_stars(screen) == 0

    def is_threestar(self, screen=None):
        # 判断是不是三星
        return self.get_upperright_stars(screen) == 3
    
    def can_auto_advance(self, screen=None):
        return self.is_exists(MAOXIAN_BTN["auto_advance"], screen=screen)
    
    def set_auto_advance(self, auto_on=True):
        out = False
        if not self.can_auto_advance():
            return False
        if auto_on:
            out = self.lock_img(MAOXIAN_BTN["auto_advance_on"], elseclick=(720, 335), retry=3)
        else:
            out = self.lock_img(MAOXIAN_BTN["auto_advance_off"], elseclick=(720, 335), retry=3)
        return out

    def buy_cishu(self):
        # 尝试买次数，必须要求剩余挑战次数=0！！！
        # return True - 成功购买； False - 失败
        out = self.click_btn(MAOXIAN_BTN["saodang_on"], until_appear=MAIN_BTN["querenhuamian_title"],
                             retry=3, is_raise=False, elsedelay=2)
        if out is False:
            return False
        self.lock_img(MAOXIAN_BTN["sytzcshf"], elseclick=(584, 367), elsedelay=8)
        self.click_btn(MAOXIAN_BTN["sytzcshf_queren"], until_appear=MAOXIAN_BTN["jtdhfkncs"])
        self.lock_no_img(MAOXIAN_BTN["jtdhfkncs"], elseclick=(473, 367))
        time.sleep(1)
        return True

    @DEBUG_RECORD
    def set_saodang_to_max(self):
        at = (729, 316, 788, 343)
        sc1 = self.getscreen()
        handle = self._a.d.touch.down(*MAOXIAN_BTN["saodang_plus"])
        time.sleep(1)
        while True:
            time.sleep(1)
            sc2 = self.getscreen()
            p = self.img_equal(sc1, sc2, at=at)
            if p > 0.95:
                break
            sc1 = sc2
        handle.up(*MAOXIAN_BTN["saodang_plus"])

    @DEBUG_RECORD
    def set_saodang_cishu(self, target: int, one_tili=None, left_tili=None, right_tili=None, sc=None, max_retry=6,
                          delay=1):
        # 设定扫荡次数
        if sc is None:
            sc = self.getscreen()
        if left_tili is None:
            left_tili = self.get_tili_left(sc)
        if right_tili is None:
            right_tili = self.get_tili_right(sc)
        if one_tili is None:
            one_tili = left_tili - right_tili
        now_cishu = (left_tili - right_tili) // one_tili  # 使用X张 的识别效果很不好
        if now_cishu < 1:
            now_cishu = 1
        retry = 0
        while now_cishu != target:
            if retry >= max_retry:
                raise LockMaxRetryError("设定扫荡次数尝试过多！")
            if now_cishu < target:
                for _ in range(target - now_cishu):
                    self.click(MAOXIAN_BTN["saodang_plus"])
            elif now_cishu > target:
                for _ in range(now_cishu - target):
                    self.click(MAOXIAN_BTN["saodang_minus"])
            time.sleep(delay)
            right_tili = self.get_tili_right()
            now_cishu = (left_tili - right_tili) // one_tili
            if abs(now_cishu - target) > 5:
                self.log.write_log("warning", "可能是OCR出现问题，体力识别失败了！")
                if save_debug_img:
                    self._a.save_last_screen(f"debug_imgs/tili_rec_{time.time()}.bmp")
                return
            retry += 1

    def goto_saodang(self) -> SaoDangQueRen:
        return self.goto(SaoDangQueRen, self.fun_click(MAOXIAN_BTN["saodang_on"]))

    def goto_tiaozhan(self) -> FightBianZuZhuXian:
        return self.goto(FightBianZuZhuXian, self.fun_click(FIGHT_BTN["tiaozhan2"]))

    def easy_shoushua(self,
                      team_order,
                      one_tili: int = 0,
                      check_cishu=True,
                      max_speed=1,
                      get_zhiyuan=False,
                      if_full=0,
                      if_auto=True
                      ):
        """
        team_order:  见select_team
        one_tili （废弃）:
        check_cishu:
            False - 不进行次数检查
            True - 进行次数检查 （0/N则退出）
        max_speed:
            1 - 两倍速
            2 - 四倍速可用
        get_zhiyuan:
            是否使用支援
        if_full:
            换下的人，详见get_zhiyuan函数
        if_auto:
            是否开启auto

        <return>
            0: 挑战成功
            1: 挑战失败
            2: 没有次数
            3: 体力不足

        <return scene>
            会关闭FightInfo窗口，回到选关页面。
        """
        screen = self.getscreen()
        if check_cishu:
            # 次数检查
            if not self.is_exists(FIGHT_BTN["infinity"], screen=screen):  # 并没有检测到infinity
                cishu_left = self.get_cishu(screen)
                if cishu_left == 0:
                    self.log.write_log("warning", "次数不足，无法挑战！")
                    self.exit_me()
                    return 2

        if self.is_exists(FIGHT_BTN["no_tili"], screen=screen):
            self.log.write_log("warning", "体力不足，无法扫荡！")
            self.exit_me()
            self._a.stop_shuatu()
            return 3

        T = self.goto_tiaozhan()
        T.select_team(team_order)
        if get_zhiyuan:
            T.get_zhiyuan(if_full=if_full)
        F = T.goto_fight()
        D = F.get_during()
        if T.is_auto_advance:
            self.log.write_log("info", f"自动推进中...")
            while True:
                out = D.check()
                if isinstance(out,D.AutoAdvanceStopBox):
                    self.log.write_log("info", f"意外停止！")
                    out.OK()
                    self._a.restart_this_task()
                elif isinstance(out,D.AutoAdvanceEndBox):
                    self.log.write_log("info", f"自动推进完成！")
                    out.OK()
                    out.next()
                    return 0
        else:
            if if_auto:
                F.set_auto(1)
            else:
                F.set_auto(0)
            F.set_speed(max_speed, max_speed, self.last_screen)        
            while True:
                out = D.check()
                if isinstance(out, D.FightingWinZhuXian):
                    self.log.write_log("info", f"战胜了！")
                    out.next()
                    A = out.get_after()
                    while True:
                        out = A.check()
                        if isinstance(out, A.FightingWinZhuXian2):
                            out.next()
                            return 0
                        elif isinstance(out, A.XianDingShangDianBox):
                            out.Cancel()
                        elif isinstance(out, A.LevelUpBox):
                            out.OK()
                            self.start_shuatu()
                        elif isinstance(out, A.LoveUpScene):
                            out.skip()
                        elif isinstance(out, A.TuanDuiZhanBox):
                            out.OK()
                        elif isinstance(out, A.AfterFightKKR):
                            out.skip()
                            self._a.restart_this_task()
                        elif isinstance(out, A.ChaoChuShangXianBox):
                            out.OK()
                        elif isinstance(out, A.HaoYouMsg):
                            out.exit_with_off()
                elif isinstance(out, D.FightingLoseZhuXian):
                    self.log.write_log("info", f"战败了！")
                    out.exit(self.fun_click(814, 493))
                    return 1
                elif isinstance(out, D.FightingDialog):
                    out.skip()
                elif isinstance(out, D.LoveUpScene):
                    out.skip()
                elif isinstance(out, D.HaoYouMsg):
                    out.exit_with_off()
                elif isinstance(out, D.TuanDuiZhanBox):
                    out.OK()
                elif isinstance(out, D.LevelUpBox):
                    out.OK()
                    self.start_shuatu()

    def easy_saodang(self,
                     target_cishu: Union[int, str] = "max",
                     one_tili: int = 0,
                     check_cishu=True,
                     additional_info=None,
                     ):
        """
        target_cishu: 目标次数， max则满。
        one_tili:
            0 - 不进行体力检查
            (int) - 一次消耗的体力次数，会进行体力检查。 （一次刷不了则退出）
            -1 - 假设消耗10体，进去后进一步计算one_tili
        check_cishu:
            False - 不进行次数检查
            True - 进行次数检查 （0/N则退出）
        additional_info:
            Optional[dict] 从内部传出一些其它信息。
        <return>
            0: 正常扫荡结束
            1: 体力不足
            2：次数不足
            3: 未三星
            4: 扫荡券不足
        <return scene>
            会关闭FightInfo窗口，回到选关页面。
        """
        if additional_info is None:
            additional_info = {}
        screen = self.getscreen()
        exitflag = 0
        stars = self.get_upperright_stars(screen)
        if stars < 3:
            self.log.write_log("warning", "未三星，无法扫荡！")
            self.exit_me()
            return 3

        quan = self.get_saodangquan(screen)
        if quan == 0:
            self.log.write_log("warning", "无扫荡券，无法扫荡！")
            self.exit_me()
            return 4
        elif isinstance(target_cishu, int) and quan < target_cishu:
            self.log.write_log("warning", f"扫荡券只能扫荡{quan}次！")
            exitflag = 4

        if check_cishu:
            # 次数检查
            if not self.is_exists(FIGHT_BTN["infinity"], screen=screen):  # 并没有检测到infinity
                cishu_left = self.get_cishu(screen)
                if cishu_left == 0:
                    self.log.write_log("warning", "次数不足，无法扫荡！")
                    self.exit_me()
                    return 2
                elif isinstance(target_cishu, int) and cishu_left < target_cishu:
                    self.log.write_log("warning", f"次数不足，只能扫荡{cishu_left}次！")
                    exitflag = 2

        if one_tili > 0 or one_tili == -1:
            # 体力检查
            tili_left = self.get_tili_left(screen)
            if self.is_exists(FIGHT_BTN["no_tili"], screen=screen):
                self.log.write_log("warning", "体力不足，无法扫荡！")
                self.exit_me()
                self._a.stop_shuatu()
                return 1
            if one_tili == -1:
                one_tili = tili_left - self.get_tili_right(screen)
            if isinstance(target_cishu, int):
                all_tili = one_tili * target_cishu
                if tili_left < all_tili:
                    self.log.write_log("warning", f"体力不足，只能扫荡{all_tili // tili_left}次！")
                    exitflag = 1

        if isinstance(target_cishu, int) and exitflag == 0:
            self.set_saodang_cishu(target_cishu)
        else:
            self.set_saodang_to_max()
        tili_left = self.get_tili_left()
        tili_right = self.get_tili_right()
        saodang_cishu = (tili_left - tili_right) // one_tili
        additional_info["cishu"] = saodang_cishu
        S = self.goto_saodang()
        J = S.OK()
        ML = J.OK()
        ML.exit_all(False)
        self.fclick(1, 1)
        if exitflag == 1:
            self._a.stop_shuatu()
        return exitflag
