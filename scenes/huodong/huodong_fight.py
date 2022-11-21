import time
from math import inf
from typing import Union

import numpy as np

from automator_mixins._base import DEBUG_RECORD
from core.constant import MAOXIAN_BTN, FIGHT_BTN, NORMAL_COORD, HARD_COORD, MAIN_BTN, p, HUODONG_BTN
from core.pcr_checker import LockMaxRetryError
from core.pcr_config import save_debug_img, ocr_mode_main
from scenes.fight.fightbianzu_zhuxian import FightBianZuZhuXian
from scenes.scene_base import PCRMsgBoxBase
from scenes.zhuxian.zhuxian_msg import SaoDangQueRen


class BOSS_FightInfoBase(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "BOSS_FightInfo"
        self.initFC = None
        # 检测编组设定
        self.feature = self.fun_feature_exist(HUODONG_BTN["baochou"])

    def exit_me(self):
        def exit_fun():
            self.fclick(1, 1)

        self.exit(exit_fun)

    def get_bsq_left(self, screen=None):
        # OCR获得扫荡前BOSS券BOSS券数量
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        at = (836, 416, 876, 432)
        out = self.ocr_int(*at, screen_shot=screen)
        return out

    def no_bsq_for_one_fight(self, screen=None):
        if screen is None:
            screen = self.getscreen()
        return self.is_exists(HUODONG_BTN["no_quan_right"], screen=screen)

    def get_bsq_right(self, screen=None):
        # OCR获得扫荡后BOSS券数量
        # -1: 没BOSS券，一次都干不了
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        if self.no_bsq_for_one_fight(screen):
            return -1
        at = (886, 416, 915, 431)
        out = self.ocr_int(*at, screen_shot=screen)
        return out

    def get_saodangquan(self, screen=None):
        # OCR获得扫荡券数量
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        at = (799, 322, 849, 340)
        out = self.ocr_int(*at, screen_shot=screen)
        return out

    def get_taofashu(self, screen=None):
        # 讨伐数
        if screen is None:
            screen = self.getscreen()
        at = (886, 32, 922, 49)
        out = self.ocr_int(*at, screen_shot=screen)
        return out

    def check_taofa(self, screen=None):
        # 是否可扫荡
        if screen is None:
            screen = self.getscreen()
        if self.get_taofashu() >= 3:
            return True
        else:
            return False

    @DEBUG_RECORD
    def set_saodang_to_max(self):
        at = (839, 415, 922, 439)
        sc1 = self.getscreen()
        handle = self._a.d.touch.down(879, 359)
        time.sleep(1)
        while True:
            time.sleep(1)
            sc2 = self.getscreen()
            p = self.img_equal(sc1, sc2, at=at)
            if p > 0.95:
                break
            sc1 = sc2
        handle.up(879, 359)

    def set_saodang_cishu(self, target: int, one_quan=None, left_bsq=None, right_bsq=None, sc=None, max_retry=6,
                          delay=1):
        # 设定扫荡次数
        if sc is None:
            sc = self.getscreen()
        if left_bsq is None:
            left_bsq = self.get_bsq_left(sc)
        if right_bsq is None:
            right_bsq = self.get_bsq_right(sc)
        if one_quan is None:
            one_quan = left_bsq - right_bsq
        now_cishu = (left_bsq - right_bsq) // one_quan  # 使用X张 的识别效果很不好
        if now_cishu < 1:
            now_cishu = 1
        retry = 0
        while now_cishu != target:
            if retry >= max_retry:
                raise LockMaxRetryError("设定扫荡次数尝试过多！")
            if now_cishu < target:
                for _ in range(target - now_cishu):
                    self.click(879, 359)
            elif now_cishu > target:
                for _ in range(now_cishu - target):
                    self.click(628, 317)
            time.sleep(delay)
            right_bsq = self.get_bsq_right()
            now_cishu = (left_bsq - right_bsq) // one_quan
            if abs(now_cishu - target) > 5:
                self.log.write_log("warning", "可能是OCR出现问题，BOSS券识别失败了！")
                if save_debug_img:
                    self._a.save_last_screen(f"debug_imgs/bsq_rec_{time.time()}.bmp")
                return
            retry += 1

    def goto_saodang(self) -> SaoDangQueRen:
        return self.goto(SaoDangQueRen, self.fun_click(HUODONG_BTN["saodang2_on"]))

    def goto_tiaozhan(self) -> FightBianZuZhuXian:
        return self.goto(FightBianZuZhuXian, self.fun_click(HUODONG_BTN["tiaozhan2_on"]))

    def easy_shoushua(self,
                      team_order,
                      max_speed=1
                      ):
        """
        team_order:  见select_team
        max_speed:
            1 - 两倍速(B0SS不得四倍速)

        <return>
            0: 挑战成功
            1: 挑战失败
            3: BOSS券不足

        <return scene>
            会关闭FightInfo窗口，回到选关页面。
        """

        T = self.goto_tiaozhan()
        T.select_team(team_order)
        F = T.goto_fight()
        F.set_auto(1)
        F.set_speed(max_speed, max_speed, self.last_screen)
        D = F.get_during()
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
                    elif isinstance(out, A.AfterFightKKR):
                        out.skip()
                        self._a.restart_this_task()
                    elif isinstance(out, A.ChaoChuShangXianBox):
                        out.OK()

            elif isinstance(out, D.FightingLoseZhuXian):
                self.log.write_log("info", f"战败了！")
                out.exit(self.fun_click(814, 493))
                return 1
            elif isinstance(out, D.FightingDialog):
                out.skip()
            elif isinstance(out, D.LoveUpScene):
                out.skip()

    def easy_saodang(self,
                     target_cishu: Union[int, str] = "max",
                     one_quan: int = 0,
                     additional_info=None,
                     ):
        """
        target_cishu: 目标次数， max则满。
        one_quan:
            0 - 不进行BOSS券检查
            (int) - 一次消耗的BOSS券，会进行BOSS券检查。 （一次刷不了则退出）
            -1 - 假设消耗10体，进去后进一步计算one_quan
        additional_info:
            Optional[dict] 从内部传出一些其它信息。
        <return>
            0: 正常扫荡结束
            1: BOSS券不足
            3: 未打满次数解锁扫荡
            4: 扫荡券不足
        <return scene>
            会关闭FightInfo窗口，回到选关页面。
        """
        if additional_info is None:
            additional_info = {}
        screen = self.getscreen()
        exitflag = 0
        taofashu = self.get_taofashu(screen)
        if taofashu < 3:
            self.log.write_log("warning", "未打满三次，无法扫荡！")
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

        if one_quan > 0 or one_quan == -1:
            # BOSS券检查
            bsq_left = self.get_bsq_left(screen)
            if self.is_exists(HUODONG_BTN["no_quan_right"], screen=screen):
                self.log.write_log("warning", "BOSS券不足，无法扫荡！")
                self.exit_me()
                return 1
            if one_quan == -1:
                one_quan = bsq_left - self.get_bsq_right(screen)
            if isinstance(target_cishu, int):
                all_bsq = one_quan * target_cishu
                if bsq_left < all_bsq:
                    self.log.write_log("warning", f"BOSS券不足，只能扫荡{all_bsq // bsq_left}次！")
                    exitflag = 1

        if isinstance(target_cishu, int) and exitflag == 0:
            self.set_saodang_cishu(target_cishu)
        else:
            self.set_saodang_to_max()
        bsq_left = self.get_bsq_left()
        bsq_right = self.get_bsq_right()
        saodang_cishu = (bsq_left - bsq_right) // one_quan
        additional_info["cishu"] = saodang_cishu
        S = self.goto_saodang()
        J = S.OK()
        ML = J.OK()
        ML.exit_all(False)
        self.fclick(1, 1)
        return exitflag
