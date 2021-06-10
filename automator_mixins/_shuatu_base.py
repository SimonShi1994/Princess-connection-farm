import time
from typing import Union, Optional, Tuple

import numpy as np

from automator_mixins._base import DEBUG_RECORD
from automator_mixins._fight_base import FightBaseMixin
from core.MoveRecord import movevar
from core.constant import MAOXIAN_BTN, MAIN_BTN, PCRelement, FIGHT_BTN, DXC_ELEMENT, SHOP_BTN, \
    ZHUXIAN_ID, JUESE_BTN, NORMAL_COORD, HARD_COORD, ZHUXIAN_SECOND_ID
from core.cv import UIMatcher
from core.log_handler import pcr_log
from core.pcr_config import debug, disable_timeout_raise


class XiandingPopupException(Exception):
    def __init__(self, *args):
        super().__init__(args)


class FightStepsBase:
    """
    Fight步骤，拆解之前无人能懂的zhandouzuobiao函数
    强制使用OCR，旨在提高稳定性和效率。
    """

    def __init__(self, obj):
        self.obj: FightBaseMixin = obj
        self.data = {}
        self.info = {}

    def _xiadian(self, x, y):
        for _ in range(6):
            self.obj.click(x, y)

    def enter_map(self, x, y, drag=None, **kwargs):
        """
        点击(x,y)进入某一关卡，此后可能会弹出Info界面
        @params
        drag
            left - 事先左拖动
            right - 事先右拖动
            None - 不拖动
        通过检测选关取消来判断是否成功
        @return
        False 进入失败
        True 进入成功
        """
        kwargs.setdefault("lock_obj", FIGHT_BTN["xuanguan_quxiao"])  # 目标检测对象
        kwargs.setdefault("try_times", 3)  # 尝试点击次数
        kwargs.setdefault("elsedelay", 8)  # 点击检测间隔
        btn = PCRelement(x, y)
        if drag == "left":
            self.obj.Drag_Left()
        elif drag == "right":
            self.obj.Drag_Right()
        return self.obj.lock_img(kwargs["lock_obj"], is_raise=False, elseclick=btn, retry=kwargs["try_times"],
                                 elsedelay=kwargs["elsedelay"])

    def show_info(self, **kwargs):
        """
        跳过关卡显示信息，
        该步骤会搜集一些必要的关卡信息,并存储至self.data
        @params
        kwargs:
            use_ocr 是否使用ocr，总控制，为后面所有ocr_XXX参数的默认值
            ocr_quan 是否获取券的数量
                -> data["quan"] ，整数，剩余券的数量
            ocr_times 是否获取剩余挑战次数
                -> data["times"]，整数，剩余挑战次数的数量
                    若挑战次数为无限，则设置为99999999
            ocr_tili 是否获取体力
                -> data["tili"]，整数，当前体力
            check_tili_once 是否获取单次挑战的体力耗费
                -> data["tili_once"]，整数，打一次所消耗的体力
                -> info["not_enough_tili"]：若检测到 -- ，则一次都没法打，此项设置为True
            ocr_tili_next 是否获取挑战后体力剩余，若check_tili_once打开，则此项打开。
                -> data["tili_next"]，整数，变化后的体力，若检测到--，则为-1
            check_saodang_button 是否检测扫荡按钮是否亮
                -> data["saodang_button"] True or False
            check_tiaozhan_button 是否检测挑战按钮是否亮
                -> data["tiaozhan_button"] True or False
            check_stars 是否检测右上角星数
                -> data["stars"] 0,1,2,3

            XXX_at OCR的位置
        """
        kwargs.setdefault("use_ocr", True)

        kwargs.setdefault("ocr_quan", kwargs["use_ocr"])
        kwargs.setdefault("ocr_tili", kwargs["use_ocr"])
        kwargs.setdefault("ocr_times", kwargs["use_ocr"])
        kwargs.setdefault("check_tili_once", kwargs["use_ocr"])
        kwargs.setdefault("ocr_tili_next", kwargs["check_tili_once"])

        kwargs.setdefault("check_saodang_button", True)
        kwargs.setdefault("check_tiaozhan_button", True)
        kwargs.setdefault("check_stars", True)

        kwargs.setdefault("quan_at", (836, 271, 888, 291))
        kwargs.setdefault("tili_at", (662, 404, 699, 424))
        kwargs.setdefault("tili_next_at", (712, 404, 744, 421))
        kwargs.setdefault("times_at", (861, 402, 919, 424))

        sc = self.obj.getscreen()

        if kwargs["check_stars"]:
            self.data["stars"] = self.obj.get_upperright_stars(sc)

        if kwargs["ocr_quan"]:
            out = self.obj.ocr_center(*kwargs["quan_at"])
            if out.isnumeric():
                self.data["quan"] = int(out)

        if kwargs["ocr_tili"]:
            out = self.obj.ocr_center(*kwargs["tili_at"])
            if out.isnumeric():
                self.data["tili"] = int(out)
            if kwargs["ocr_tili_next"]:
                out = self.obj.ocr_center(*kwargs["tili_next_at"])
                if out == "--":
                    self.data["tili_next"] = -1  # 无体力
                    self.data["not_enough_tili"] = True
                if out.isnumeric():
                    self.data["tili_next"] = int(out)
            if "not_enough_tili" not in self.data and kwargs["check_tili_once"]:
                if "tili" in self.data and "tili_next" in self.data:
                    self.data["tili_once"] = self.data["tili"] - self.data["tili_next"]

        if kwargs["ocr_times"]:
            out = self.obj.ocr_center(*kwargs["times_at"])
            if out == "oo":
                self.data["times"] = 99999999
            elif "/" in out:
                outs = out[:out.find('/')]
                if outs.isnumeric():
                    self.data["times"] = int(outs)

        if kwargs["check_saodang_button"]:
            p0 = self.obj.img_prob(MAOXIAN_BTN["saodang_off"], screen=sc, method="sq")
            p1 = self.obj.img_prob(MAOXIAN_BTN["saodang_on"], screen=sc, method="sq")
            self.data["saodadefng_button"] = p1 > p0

        if kwargs["check_tiaozhan_button"]:
            p0 = self.obj.img_prob(MAOXIAN_BTN["tiaozhan_off"], method="sq", screen=sc)
            p1 = self.obj.img_prob(MAOXIAN_BTN["tiaozhan_on"], method="sq", screen=sc)
            self.data["tiaozhan_button"] = p1 > p0

    def before_fight(self, mode=0, **kwargs):
        """
        战斗（手刷，扫荡）前的判断，是否有足够次数，能否战斗，能否扫荡等
        @params
        mode:
            0 - 判断是否可以扫荡，若可以扫荡，返回True，否则返回False
            1 - 判断是否可以手刷，若可以手刷，返回True，否则返回False
        buy_tili: 整数，本次最多购买体力数量
        kwargs:
        @return
            False 不可执行
            True 可以执行
        @info
            error_code:
                这两个错误优先级低
                    1 - 不可挑战/扫荡，挑战按钮为灰色，可能是挑战次数不足或者需要先打上一关卡
                    2 - 不可扫荡，扫荡按钮为灰色，可能是未三星通关或者体力、扫荡券不足
                优先以下错误：
                    3 - 不可挑战/扫荡，因为体力不足
                    4 - 不可挑战/扫荡，因为次数不足
                        若次数不足，但可以购买次数，此时扫荡按钮仍然亮；
                        若不可购买次数，则扫荡按钮灭。
                    5 - 不可扫荡，因为扫荡券不足
                    6 - 不可扫荡，因为没有三星通关

        """
        if mode == 0 and "stars" in self.data:
            if self.data["stars"] < 3:
                self.info["error_code"] = 6
                return False
        if mode == 0 and "quan" in self.data:
            if self.data["quan"] == 0:
                self.info["error_code"] = 5
                return False
        if "not_enough_tili" in self.info and self.info["not_enough_tili"]:
            self.info["error_code"] = 3
            return False
        if "cishu" in self.data:
            if self.data["cishu"] == 0:
                self.info["error_code"] = 4
                return False
        if "tiaozhan_button" in self.data:
            if not self.data["tiaozhan_button"]:
                self.info["error_code"] = 1
                return False
        if mode == 0 and "saodang_button" in self.data:
            if not self.data["saodang_button"]:
                self.info["error_code"] = 2
                return False
        return True

    def buy_tili(self, click: Optional[Tuple[int, int]], **kwargs):
        """
        购买一次体力
        若click不为None，则首先点击click，并锁定“体力不足，要回复吗”
        主体部分从出现界面"体力不足，要恢复吗"开始，
        点击OK，此界面显示剩余次数、消耗宝石、体力回复量等，可以选择性OCR。
        再次点击OK，则成功
        @param
            click : Tuple(x,y) or None - 事先是否按下(x,y)触发事件
            kwargs
                ocr_gem - 是否ocr消耗宝石和总宝石数
                xd_xy - 瞎点的坐标，用于退出买体力窗口


        @return
            False 购买体力失败
            True 购买体力成功
        @info
            error_code
                1 - 没有找到体力恢复窗口，可能无需购买
                2 - 宝石不足，无法购买
        """
        kwargs.setdefault("ocr_gem", False)
        kwargs.setdefault("xd_xy", (33, 25))
        consume_gem_at = (418, 246, 476, 264)
        gem_at = (611, 249, 694, 262)
        if not self.obj.lock_img(MAOXIAN_BTN["no_tili"], elseclick=click, timeout=20, is_raise=False):
            self.info["error_code"] = 1
            return False
        self.obj.click_btn(MAOXIAN_BTN["buytili_ok"], until_appear=MAOXIAN_BTN["tlhf"])

        if kwargs["ocr_gem"]:
            out = self.obj.ocr_center(*consume_gem_at)
            if out.isnumeric():
                self.data["tili_consume_gems"] = int(out)
            out = self.obj.ocr_center(*gem_at)
            if out.isnumeric():
                self.data["gems"] = int(out)

            if self.data["tili_consume_gems"] > self.data["gems"]:
                self._xiadian(*kwargs["xd_xy"])
                self.info["error_code"] = 2
                return False
        self.obj.click_btn(MAOXIAN_BTN["buytili_ok"])
        self._xiadian(*kwargs["xd_xy"])
        return True

    def before_saodang(self, times, **kwargs):
        """
        扫荡关卡之前的信息获取
        @params
            times - 扫荡次数，设置为"max"时全部扫荡
        @return
            0 - 无法扫荡，原因保存在self.info["saodang_error"]中
            扫荡次数 - 开启OCR时，实际扫荡成功的次数
            times - 未开启OCR时，默认，times全部扫荡过
        """
        kwargs.setdefault("ocr_checktimes", False)  # 检测实际真正扫荡的次数

        if "tili_once" in self.data:
            kwargs.setdefault("one_tili", self.data["tili_once"])
        else:
            kwargs.setdefault("one_tili", 10)  # 一次体力多少

        if times == "max":
            # 长按加号，直到图片保持不动
            at = (729, 316, 788, 343)
            sc1 = self.obj.getscreen()
            handle = self.obj.d.touch.down(*MAOXIAN_BTN["saodang_plus"])
            time.sleep(1)
            while True:
                time.sleep(1)
                sc2 = self.obj.getscreen()
                p = self.obj.img_equal(sc1, sc2, at=at)
                if p > 0.95:
                    break
                sc1 = sc2
            handle.up(*MAOXIAN_BTN["saodang_plus"])
        else:
            # 按times-1次加号
            for i in range(times - 1):
                self.obj.click(MAOXIAN_BTN["saodang_plus"])

        # 检测真正扫荡的次数
        if kwargs["ocr_checktimes"] and "tili" not in self.data:
            self.show_info(ocr_tili=True)
        if "tili" in self.data and kwargs["ocr_checktimes"]:
            out = self.obj.ocr_center(*(712, 404, 744, 421))
            if out.isnumeric():
                self.data["tili_next"] = int(out)
        if "tili" in self.data and "tili_next" in self.data:
            self.info["saodang_true_times"] = (self.data["tili"] - self.data["tili_next"]) // kwargs["one_tili"]

    def end(self, **kwargs):
        """
        瞎点(1,1)退出界面
        """
        self._xiadian(1, 1)

    def saodang(self, **kwargs):
        """
        点击“扫荡”扫荡关卡的过程
        @return
            False 扫荡失败 - 强点(1,1)退回到选关界面
            True 扫荡成功
        """
        # 点击按钮，检测屏幕变化
        kwargs.setdefault("xd_xy", (33, 25))
        kwargs.setdefault("saodang_ok2", MAOXIAN_BTN["saodang_ok2"])
        at = (263, 193, 698, 315)
        sc1 = self.obj.getscreen()

        def PopQuery():
            sc2 = self.obj.getscreen()
            p = self.obj.img_equal(sc1, sc2, at=at)
            if p < 0.85:
                return True
            else:
                return False

        click_ok = self.obj.lock_fun(PopQuery, elseclick=MAOXIAN_BTN["saodang_on"], elsedelay=5, is_raise=False,
                                     retry=3)
        if not click_ok:
            # 可能无法扫荡
            self.obj.log.write_log("warning", "点击扫荡失败，可能无法扫荡")
            self._xiadian(*kwargs["xd_xy"])
            return False
        # 屏幕出现变化，但不一定出现saodang_query提示是否扫荡
        # 如果出现 saodang_query，则说明可以扫荡，继续点即可
        # 否则，则说明体力不足/次数不足/未三星通关等等，无法扫荡
        if self.obj.is_exists(MAOXIAN_BTN["saodang_query"], screen=self.obj.last_screen):
            # 可以扫荡
            self.obj.click_btn(MAOXIAN_BTN["saodang_ok"])
            # 无脑快进到扫荡结束，啥都不管
            while self.obj.is_exists(MAOXIAN_BTN["saodang_jieguo"]):
                self.obj.click(471, 481, pre_delay=0.5)  # 点“跳过”或者“OK”
                self._xiadian(*kwargs["xd_xy"])
            self._xiadian(*kwargs["xd_xy"])
            return True
        elif self.obj.is_exists(MAOXIAN_BTN["no_cishu"], screen=self.obj.last_screen):
            self.obj.log.write_log("warning", "次数不足，无法扫荡")
            self.info["error_code"] = 4
            self._xiadian(*kwargs["xd_xy"])
            return False
        elif self.obj.is_exists(MAOXIAN_BTN["no_tili"], screen=self.obj.last_screen):
            self.obj.log.write_log("warning", "体力不足，无法扫荡")
            self.info["error_code"] = 3
            self._xiadian(*kwargs["xd_xy"])
            return False
        else:
            self.obj.log.write_log("warning", "可能因为体力不足/次数不足/未三星通关而无法扫荡")
            self.info["error_code"] = 1
            self._xiadian(*kwargs["xd_xy"])
            return False

    def before_shoushua(self, **kwargs):
        """
        点击“挑战”后，到选人界面
        @return
            True - 点击成功
            False - 点击失败
        """
        # 点击按钮，检测屏幕变化
        kwargs.setdefault("xd_xy", (33, 25))
        at = (263, 193, 698, 315)
        sc1 = self.obj.getscreen()

        def PopQuery():
            sc2 = self.obj.getscreen()
            p = self.obj.img_equal(sc1, sc2, at=at)
            if p < 0.85:
                return True
            else:
                return False

        click_ok = self.obj.lock_fun(PopQuery, elseclick=FIGHT_BTN["tiaozhan2"], elsedelay=5, is_raise=False, retry=3)
        if not click_ok:
            # 可能无法挑战
            self.obj.log.write_log("warning", "点击挑战失败，可能无法挑战")
            self._xiadian(*kwargs["xd_xy"])
            return False
        if self.obj.is_exists(MAOXIAN_BTN["no_cishu"], screen=self.obj.last_screen):
            self.obj.log.write_log("warning", "次数不足，无法扫荡")
            self.info["error_code"] = 4
            self._xiadian(*kwargs["xd_xy"])
            return False
        elif self.obj.is_exists(MAOXIAN_BTN["no_tili"], screen=self.obj.last_screen):
            self.obj.log.write_log("warning", "体力不足，无法扫荡")
            self.info["error_code"] = 3
            self._xiadian(*kwargs["xd_xy"])
            return False
        elif self.obj.is_exists(FIGHT_BTN["zhandoukaishi"], screen=self.obj.last_screen):
            return True
        else:
            self.obj.log.write_log("warning", "可能因为体力不足/次数不足/未三星通关而无法扫荡")
            self.info["error_code"] = 1
            self._xiadian(*kwargs["xd_xy"])
            return False

    def select_by_sort(self, order, **kwargs):
        # 按照排序选择队伍
        self.obj.set_fight_team_order(order)

    def select_by_duiwu(self, bianzu, duiwu, **kwargs):
        # 按照某特定编组选择队伍
        self.obj.set_fight_team(bianzu, duiwu)

    def start_shoushua(self, **kwargs):
        # 点击战斗开始按钮，开始手刷
        self.obj.click_btn(FIGHT_BTN["zhandoukaishi"])
        self.obj.wait_for_loading(delay=2)

    def set_fight_auto_speed(self, auto=None, speed=None, **kwargs):
        # 设置战斗是否自动，及速度
        if auto is not None:
            self.obj.set_fight_auto(auto)
        if speed is not None:
            self.obj.set_fight_speed(speed)

    def shuatu_end_sidecheck(self, screen=None, **kwargs):
        if screen is None:
            screen = self.obj.getscreen()
        kwargs.setdefault("check_tdz", True)
        kwargs.setdefault("check_xd", True)
        kwargs.setdefault("check_sx", True)
        kwargs.setdefault("check_lv", True)

        if kwargs["check_tdz"] and self.obj.is_exists(MAOXIAN_BTN["tuanduizhan"], screen=screen):
            self.obj.click(1, 1, pre_delay=0.5)
            self.info["tdz_popup"] = True
            return True
        if kwargs["check_xd"] and self.obj.is_exists(MAOXIAN_BTN["xianding"], screen=screen):
            self.obj.click(1, 1, pre_delay=0.5)
            self.info["xd_popup"] = True
            return True
        if kwargs["check_sx"] and self.obj.is_exists(MAOXIAN_BTN["chaochushangxian"], screen=screen):
            self.obj.click(1, 1, pre_delay=0.5)
            self.info["sx_popup"] = True
            return True
        if kwargs["check_lv"] and self.obj.is_exists(FIGHT_BTN["dengjitisheng"], screen=screen):
            self.obj.click(1, 1, pre_delay=0.5)
            self.info["lv_popup"] = True
            return True
        return False

    def zhuxian_kkr(self, screen=None, **kwargs):
        cnt = 0
        kwargs.setdefault("check_xd", True)
        kwargs.setdefault("check_close", True)
        kwargs.setdefault("check_kkr", True)
        kwargs.setdefault("kkr_return", self.obj.__getattribute__("enter_zhuxian"))
        while cnt <= 2:
            if screen is not None:
                sc = screen
                screen = None
            else:
                sc = self.obj.getscreen()
            if kwargs["check_xd"] and self.obj.is_exists(MAOXIAN_BTN["xianding"], screen=sc):
                self.info["xd_popup"] = True
                self.obj.click(1, 1)
                continue
            if kwargs["check_close"] and self.obj.click_img(img="img/ui/close_btn_1.bmp", screen=sc):
                self.info["other_popup"] = True
                self.obj.save_last_screen(f"F:/op/{self.obj.account}_{int(time.time())}.bmp")
                continue
            if kwargs["check_kkr"] and self.obj.is_exists(DXC_ELEMENT["dxc_kkr"], screen=sc):
                self.info["kkr_popup"] = True
                self.obj.chulijiaocheng(turnback=None)
                kwargs["kkr_return"]()
            if self.obj.is_exists(MAOXIAN_BTN["ditu"], screen=sc):
                cnt += 1
                time.sleep(0.8)
                continue

    def wait_for_finish(self, **kwargs):
        """
        等待战斗结束，但不会主动退出战斗。
        @return
            True - 战斗胜利
            False - 战斗失败
        """
        # 等待战斗结束
        kwargs.setdefault("timeout", 500)  # 等待战斗结束最长时间
        kwargs.setdefault("delay", 1)

        kwargs.setdefault("check_jiban", False)  # 检测右上角跳过剧情
        kwargs.setdefault("check_jq", False)  # 检测是否出现剧情对话的粉色框，但误判可能性大

        kwargs.setdefault("win_target", MAOXIAN_BTN["duiwu_win"])
        kwargs.setdefault("loss_target", MAOXIAN_BTN["duiwu_loss"])

        tm = time.time()
        while True:
            if time.time() - tm > kwargs["timeout"]:
                if not disable_timeout_raise:
                    raise Exception("战斗超时")
            time.sleep(kwargs["delay"])
            self.shuatu_end_sidecheck(screen=sc)
            self._xiadian(1, 1)
            sc = self.obj.getscreen()
            if kwargs["check_jiban"] and self.obj.is_exists(MAIN_BTN["tiaoguo"], screen=sc):
                # 右上角有 》》》 按钮，跳过羁绊剧情
                self.obj.click(MAIN_BTN["tiaoguo"])
                continue
            if self.obj.is_exists(FIGHT_BTN["menu"], screen=sc, threshold=0.95):
                # 右上角有圆形菜单，说明战斗还在进行中
                continue
            if kwargs["check_jq"] and self.obj.is_exists(MAIN_BTN["speaker_box"], screen=sc, method="sq"):
                self._xiadian(1, 1)
                continue
            if self.obj.is_exists(kwargs["win_target"], screen=sc):
                return True
            if self.obj.is_exists(kwargs["loss_target"], screen=sc):
                return False

    def end_loss(self, **kwargs):
        # 输了，返回。
        kwargs.setdefault("lockimg", FIGHT_BTN["qwzxgq"])  # 返回点击的按钮
        self.obj.click_btn(kwargs["lockimg"], wait_self_before=True)
        self.obj.wait_for_loading(delay=1)

    def again_win(self, **kwargs):
        """
        赢了，点击再次挑战
        @return
            True - 点击成功
            False - 点击失败
        """
        kwargs.setdefault("xd_xy", (1, 1))
        at = (263, 193, 698, 315)
        sc1 = self.obj.getscreen()

        def PopQuery():
            sc2 = self.obj.getscreen()
            p = self.obj.img_equal(sc1, sc2, at=at)
            if p < 0.85:
                return True
            else:
                return False

        click_ok = self.obj.lock_fun(PopQuery, elseclick=FIGHT_BTN["zaicitiaozhan"], elsedelay=5,
                                     is_raise=False, retry=3)
        if not click_ok:
            # 可能无法挑战
            self.obj.log.write_log("warning", "点击挑战失败，可能无法挑战")
            self._xiadian(*kwargs["xd_xy"])
            return False
        if self.obj.is_exists(MAOXIAN_BTN["no_cishu"], screen=self.obj.last_screen):
            self.obj.log.write_log("warning", "次数不足，无法挑战")
            self.info["error_code"] = 4
            self._xiadian(*kwargs["xd_xy"])
            return False
        elif self.obj.is_exists(MAOXIAN_BTN["no_tili"], screen=self.obj.last_screen):
            self.obj.log.write_log("warning", "体力不足，无法挑战")
            self.info["error_code"] = 3
            self._xiadian(*kwargs["xd_xy"])
            return False
        return True

    def end_win_firstscreen(self, **kwargs):
        """
        胜利后的第一个界面，在normal/hard关卡时回遇到
        此界面中间显示星数，右上角有”队伍“符号（偏右中),右下角有长的”下一步“
        该界面下，读取中间星数，存入info，并点击右下角下一步。
        限定商店、升级等popups也会在此界面处理，包括羁绊跳过等。
        全部处理完毕后，右下角长的”下一步“出现。
        @info
            current_stars - 本次几星通关
        """
        # 赢了，返回
        self.obj.lock_img(FIGHT_BTN["xiayibu"], is_raise=False, timeout=30, side_check=self.shuatu_end_sidecheck)
        self.info["current_stars"] = self.obj.get_fight_middle_stars(self.obj.last_screen)
        if self.info["current_stars"] == 0:
            self.obj.log.write_log("error", "星数检测失败，默认三星过关。")

    def end_win(self, **kwargs):
        """
        胜利并返回。
        """
        kwargs.setdefault("ok_btn", FIGHT_BTN["xiayibu2"])
        self.obj.click_btn(kwargs["ok_btn"], wait_self_before=True)
        self.obj.wait_for_loading(delay=1)


class ShuatuBaseMixin(FightBaseMixin):
    """
    刷图基础插片
    包含刷图基本操作和基本变量存储
    """

    def __init__(self):
        super().__init__()
        self.switch = 0
        self._zdzb_info = ""  # 为什么zhandouzuobiao失败了：原因
        self.times = 3  # 总刷图次数

    def GetFightSteps(self):
        return FightStepsBase(self)

    def sw_init(self):
        self.switch = 0
    @DEBUG_RECORD
    def zhuxian_kkr(self, screen=None):
        """
        处理跳脸
        :return:
        """
        cnt = 0
        while cnt <= 2:
            if screen is not None:
                sc = screen
                screen = None
            else:
                sc = self.getscreen()
            if self.is_exists(MAOXIAN_BTN["xianding"], screen=sc):
                raise XiandingPopupException("限定商店出现！")
            if self.click_img(img="img/ui/close_btn_1.bmp", screen=sc):
                continue
            if self.is_exists(DXC_ELEMENT["dxc_kkr"], screen=sc):
                self.chulijiaocheng(turnback=None)
                self.enter_zhuxian()
            if self.is_exists(MAOXIAN_BTN["ditu"], screen=sc):
                cnt += 1
                time.sleep(0.8)
                continue
            # self.click(80,16,post_delay=1)

    @staticmethod
    def clear_tili_info(var):
        mv = movevar(var)
        if "cur_tili" in var:
            del var["cur_tili"]
        mv.save()

    def stop_shuatu(self):
        self.switch = 1

    def start_shuatu(self):
        self.switch = 0

    def check_shuatu(self):
        return self.switch == 0

    @DEBUG_RECORD
    def zhandouzuobiao(self, x, y, times, drag=None, use_saodang: Union[bool, str] = "auto", buy_tili=0, buy_cishu=0,
                       xianding=False,
                       bianzu=0, duiwu=0, auto=1, speed=1, fastmode=True, fail_retry=False,
                       juqing_in_fight=False, end_mode=0, saodang_ok2=MAOXIAN_BTN["saodang_ok2"], var={}):
        """
        战斗坐标，新刷图函数（手刷+扫荡结合）
        内置剧情跳过、奇怪对话框跳过功能
        BUG：当手刷模式时，困难图会自动买次数，不管是否同意。
        :param var:
            注意！zhandouzuobiao共会生成3个断点变量：
                cur_tili：当前已经购买体力的次数
                cur_times：当前已经战斗的次数
                cur_win:当前已经胜利的次数
            其中，cur_times和cur_win都会在退出后自动清理，但是！
            ！！！cur_tili不会自行清除！！！！
            ！！！使用后一定要在外部self.clear_tili_info(var) 清除体力！！！

        :param x: 点击图的x坐标
        :param y: 点击图的y坐标
        :param times: 刷图/手刷次数，设置为"all"时，用光全部体力（包括升级所得）[仅用于主线！]
        :param drag: 是否进行拖动校准
            设置为None时，点击坐标前不另外拖动给。
            "left"：进行左移动校准
            "right"：进行右移动校准
        :param use_saodang: 是否使用扫荡券
            True: 使用扫荡券，扫荡不成功则跳过
            False: 手打
            "auto“ (默认) 如果扫荡失败，则手打
        :param buy_tili: 是否自动购买体力。0不买，n表示最多买n次体力
        :param buy_cishu: 是否自动购买挑战次数（困难副本），0不买，1表示买1次。
        :param xianding: 是否买空限定商店
        :param auto: 是否开启自动
        :param speed: 是否开启加速
        :param bianzu: 使用编组号,为0时不切换，为-1时使用战力前五个角色，为-2时使用等级前五的角色
        :param duiwu: 使用队伍号，为0时不切换，为-1时使用战力前五个角色，为-2时使用等级前五的角色
        :param fastmode: 快速手刷模式：不退出重进而是通过“使用同一队伍再次挑战”来加速流程
        :param fail_retry: 失败是否重试。设置为True时手刷关卡，即使打败了也会重新再打。
                    重打的次数仍然算进总次数中。
        :param juqing_in_fight: 战斗中是否可能出现剧情。
            开启后，在get_fight_state中增加剧情检测能力，
            但是xianding很可能无法启用（点击剧情不小心把限定点掉）
        :param end_mode: 战斗结束做的事情
            mode=0：退出战斗后，什么都不做，不进行场景检测
            mode=1：退出战斗后，执行zhuxian_kkr，可以一定程度点击出现的对话框和跳过剧情
            mode=2：退出战斗后，必定lock_home后重enter_zhuxian
        :param saodang_ok2: 扫荡结束click的按钮
            默认的MAOXIAN_BTN["saodang_ok2"]适用于NORMAL和HARD图推图
            如果对于探索，需要设置为MAIN_BTN["tansuo_saodangok2"]
        :return:
            raise Error：场景判断错误
            -2: 无法挑战
            -3: 无法点进关卡
            >=0 整数：成功战胜的次数（非扫荡时）
            times：扫荡成功至少一次（扫荡时）
        --By TheAutumnOfRice
        """
        if not self.check_shuatu():
            return 0
        mv = movevar(var)
        var.setdefault("cur_tili", 0)  # 已经购买体力的次数
        var.setdefault("cur_times", 0)  # 已经战斗的次数
        var.setdefault("cur_win", 0)  # 已经胜利的次数

        def clear():
            # del var["cur_tili"]  # ！ 必须在外部进行！
            del var["cur_times"]
            del var["cur_win"]

        def end(screen=None):
            if end_mode == 0:
                pass
            elif end_mode == 1:
                try:
                    self.zhuxian_kkr(screen)
                except XiandingPopupException:
                    if buy():
                        self.zhuxian_kkr()
                    else:
                        for _ in range(3):
                            # 超级瞎点，此代码实在惨不忍睹
                            for _ in range(2):
                                self.click(76, 15)
                                self.click(843, 491)  # 本不应该有这行代码，但是查不出漏洞了，只能用这个解
                            time.sleep(0.2)
                        self.lock_home()
                        self.enter_zhuxian()

            elif end_mode == 2:
                self.lock_home()
                self.enter_zhuxian()

        def tili():
            # 0: 无需购买体力
            # 1：购买体力成功
            # 2：购买体力失败或次数用尽
            if self.is_exists(MAOXIAN_BTN["no_tili"]):
                if var["cur_tili"] < buy_tili:
                    var["cur_tili"] += 1
                    self.log.write_log("info", f"体力不足，购买体力：{var['cur_tili']}/{buy_tili}！")
                    self.click_btn(MAOXIAN_BTN["buytili_ok"], until_appear=MAOXIAN_BTN["tlhf"])
                    self.click_btn(MAOXIAN_BTN["buytili_ok"])
                    click_ok = self.click_btn(MAOXIAN_BTN["buytili_ok2"], is_raise=False, wait_self_before=True)
                    if not click_ok:
                        self.log.write_log("warning", "购买体力可能失败。")
                        self._zdzb_info = "notili"
                        self.stop_shuatu()
                    mv.save()
                    return 1 if click_ok else 2
                else:
                    self.click_btn(MAOXIAN_BTN["buytili_quxiao"])
                    self.stop_shuatu()
                    self._zdzb_info = "notili"
                    return 2
            else:
                return 0

        def cishu():
            # 0：无需购买次数
            # 1：购买次数成功
            # 2：购买次数失败
            if self.is_exists(MAOXIAN_BTN["no_cishu"]):
                if buy_cishu:
                    self.click_btn(MAOXIAN_BTN["buytili_ok"], until_appear=MAOXIAN_BTN["sytzcshf"])
                    self.click_btn(MAOXIAN_BTN["buytili_ok"])
                    click_ok = self.click_btn(MAOXIAN_BTN["buytili_ok2"], is_raise=False, wait_self_before=True)
                    if not click_ok:
                        self._zdzb_info = "nocishu"
                        self.log.write_log("warning", "购买次数可能失败。")
                    return 1 if click_ok else 2
                else:
                    self._zdzb_info = "nocishu"
                    return 2
            else:
                return 0

        def buy(entered=False):
            # entered: 是否已经进入了商店，设置为True，则跳过“限定”的检测
            if not xianding:
                return False
            time.sleep(1.5)  # 等出现
            if entered or self.is_exists(MAOXIAN_BTN["xianding"]):
                if not entered:
                    self.click_btn(MAOXIAN_BTN["xianding"])
                self.wait_for_loading(delay=2)
                self.click(388, 148, post_delay=0.8)
                self.click(558, 149, post_delay=0.8)
                self.click(729, 149, post_delay=0.8)
                self.click(900, 148, post_delay=0.8)
                self.d.drag(613, 392, 613, 140, duration=0.1)
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
                self.click_btn(SHOP_BTN["fanhui"])
                self.wait_for_loading(delay=2)
                return True
            return False

        def tdz_sidecheck(screen):
            if self.is_exists(MAOXIAN_BTN["tuanduizhan"], screen=screen):
                self.click_btn(MAOXIAN_BTN["tuanduizhan_quxiao"])
                return True
            return False

        def shoushua(times):
            # return:
            # 0: 无法挑战
            # 1： 打赢了
            # 2： 打输了
            win_cnt = 0
            if not self.is_exists(FIGHT_BTN["tiaozhan2"], method="sq"):  # 不能挑战
                self._zdzb_info = "nocishu"
                return 0
            out = 0
            while out != 3:
                out = self.click_btn(FIGHT_BTN["tiaozhan2"], until_appear={
                    MAOXIAN_BTN["no_cishu"]: 1,
                    MAOXIAN_BTN["no_tili"]: 2,
                    FIGHT_BTN["zhandoukaishi"]: 3
                })
                if out == 1 and cishu() == 2:
                    return 0
                if out == 2 and tili() == 2:
                    return 0

            # 换队

            if bianzu == -2 and duiwu == -2:
                self.set_fight_team_order("dengji")
            elif bianzu == -1 and duiwu == -1:
                self.set_fight_team_order()
            elif bianzu != 0 and duiwu != 0:
                self.set_fight_team(bianzu, duiwu)
            self.click_btn(FIGHT_BTN["zhandoukaishi"])
            while True:
                # 刷满times次
                self.wait_for_loading(delay=2)
                self.set_fight_auto(auto, screen=self.last_screen)
                self.set_fight_speed(speed, max_level=1, screen=self.last_screen)
                mode = 0
                while mode == 0:
                    # 等待战斗结束
                    mode = self.get_fight_state(delay=3, check_hat=False,
                                                check_xd=True, go_xd=xianding,
                                                check_jq=juqing_in_fight, check_star=True)
                    if debug:
                        print("上次星数：", self.last_star)
                    time.sleep(3)
                if mode == -1:
                    raise Exception("战斗场景识别失败")
                elif mode == 1:
                    # 点击下一步：
                    var["cur_win"] += 1
                    var["cur_times"] += 1
                    win_cnt += 1
                    mv.save()
                    if win_cnt < times:
                        # 点击”再次挑战“
                        if not self.click_btn(MAOXIAN_BTN["zaicitiaozhan"], is_raise=False, side_check=tdz_sidecheck):
                            break
                        cishu()
                        if tili() < 2:
                            self.click_btn(MAOXIAN_BTN["chongshi_ok"])
                            # 点击了重试，继续刷！
                            if self.check_shuatu():
                                continue
                        else:
                            # 不刷了，退出
                            pass
                    # 结束挑战
                    state = self.lock_img({FIGHT_BTN["xiayibu2"]: 1, MAOXIAN_BTN["xianding"]: 2},
                                          side_check=tdz_sidecheck)
                    if state == 1:
                        self.click_btn(FIGHT_BTN["xiayibu2"], wait_self_before=True, side_check=tdz_sidecheck)
                        self.wait_for_loading(delay=1)
                        end()
                        return 1
                    else:
                        mv.save()
                        buy(True)
                        return 1

                elif mode == 2:
                    # 前往主线关卡
                    var["cur_times"] += 1
                    mv.save()
                    self.click_btn(FIGHT_BTN["qwzxgq"], wait_self_before=True)
                    self.wait_for_loading(delay=1)
                    end()
                    return 2
                elif mode == 3:
                    # 买东西
                    var["cur_times"] += 1
                    mv.save()
                    buy(True)
                    return 1

        def saodang(times):
            # 使用扫荡券
            # return:
            # -1: 失败，且不可转手刷（无次数）
            # 0：失败，可以转手刷（无券）
            # >0：成功
            def alllll():
                # 最快速点光扫荡
                at = (729, 316, 788, 343)
                sc1 = self.getscreen()
                handle = self.d.touch.down(*MAOXIAN_BTN["saodang_plus"])
                time.sleep(1)
                while True:
                    time.sleep(1)
                    sc2 = self.getscreen()
                    p = self.img_equal(sc1, sc2, at=at)
                    if p > 0.95:
                        break
                    sc1 = sc2
                handle.up(*MAOXIAN_BTN["saodang_plus"])

            sc = self.getscreen()
            p0 = self.img_prob(MAOXIAN_BTN["tiaozhan_off"], method="sq", screen=sc)
            p1 = self.img_prob(MAOXIAN_BTN["tiaozhan_on"], method="sq", screen=sc)
            if p0 > p1:
                self._zdzb_info = "nocishu"
                return -1  # 无法挑战，甚至无法手刷。
            p0 = self.img_prob(MAOXIAN_BTN["saodang_off"], screen=sc, method="sq")
            p1 = self.img_prob(MAOXIAN_BTN["saodang_on"], screen=sc, method="sq")
            if p1 < p0:
                # 即使是黑色，点了还能买体力。
                # 除非没有扫荡券
                while True:
                    out = self.click_btn(MAOXIAN_BTN["saodang_off"],
                                         until_appear=[MAOXIAN_BTN["no_tili"], MAOXIAN_BTN["no_cishu"]]
                                         , is_raise=False, timeout=6)
                    if out:
                        if cishu() == 2:
                            return -2
                        if tili() == 2:
                            for _ in range(5):
                                self.click(45, 32)  # 瞎点点空一切对话框
                            return -2
                        # 购买了体力，重制p0,p1
                        sc = self.getscreen()
                        p0 = self.img_prob(MAOXIAN_BTN["saodang_off"], screen=sc, method="sq")
                        p1 = self.img_prob(MAOXIAN_BTN["saodang_on"], screen=sc, method="sq")
                        break
                    else:
                        return 0  # 没扫荡券了
            if p1 > p0:
                # 可以扫荡
                while True:
                    # 这个while True为"all"服务，用光所有体力后等级提升了，此时只需要再点即可(all2)
                    if times == "all":
                        alllll()
                        times = "all2"
                    elif times == "all2":
                        pass
                    else:
                        for t in range(times - 1):  # 减一，本来就有一个了
                            self.click(MAOXIAN_BTN["saodang_plus"])
                    click_ok = self.lock_img(MAOXIAN_BTN["saodang_ok"], elseclick=MAOXIAN_BTN["saodang_on"],
                                             elsedelay=5,
                                             is_raise=False, retry=2)
                    if not click_ok or self.is_exists(MAOXIAN_BTN["no_cishu"], screen=self.last_screen):
                        # 可能不可扫荡
                        c = cishu()
                        if c == 2:
                            for _ in range(5):
                                self.click(45, 32)  # 瞎点点空一切对话框
                            self.click_btn(MAOXIAN_BTN["quxiao"])
                            return -1
                        elif c == 1:
                            for _ in range(5):
                                self.click(45, 32)  # 瞎点点空一切对话框
                            continue
                        for _ in range(5):
                            self.click(45, 32)  # 瞎点点空一切对话框
                        self.click_btn(MAOXIAN_BTN["quxiao"])
                        return 0
                    if not self.lock_img(MAOXIAN_BTN["sdqqr"], timeout=10, is_raise=False):
                        for _ in range(5):
                            self.click(45, 32)  # 瞎点点空一切对话框
                        continue
                    self.click_btn(MAOXIAN_BTN["saodang_ok"], wait_self_before=True)
                    self.lock_img([MAOXIAN_BTN["saodang_tiaoguo"], saodang_ok2])
                    out = self.click_btn(MAOXIAN_BTN["saodang_tiaoguo"], until_appear={
                        MAOXIAN_BTN["saodang_ok"]: 1,
                        MAOXIAN_BTN["chaochushangxian"]: 2,
                        saodang_ok2: 3
                    })
                    if out == 2:
                        if times == "all2":
                            self.lock_home()
                            self.__getattribute__("shouqu")()
                            self.enter_zhuxian()
                            enter()
                            times = "all"
                            continue
                    self.click_btn(saodang_ok2, wait_self_before=True, elsedelay=2)
                    # 此处会有升级提示
                    while True:
                        time.sleep(0.5)
                        sc = self.getscreen()
                        if times == "all2" and self.is_exists(MAOXIAN_BTN["chaochushangxian"], screen=sc):
                            # 超出上限，对all模式，领了礼物回来继续刷好哇
                            self.lock_home()
                            enter()
                            times = "all"
                            break
                        if self.is_exists(FIGHT_BTN["dengjitisheng"], screen=sc):
                            self.click(38, 24)
                            continue
                        if buy():
                            return 1
                        if self.is_exists(MAOXIAN_BTN["tuanduizhan"], screen=sc):
                            self.click_btn(MAOXIAN_BTN["tuanduizhan_quxiao"])  # 跳过团队站
                            continue
                        break
                    if times == "all2" and self.is_exists(MAOXIAN_BTN["tiaozhan_off"], method="sq", threshold=0.92):
                        # 挑战还是暗的，还能继续刷
                        continue
                    self.click_btn(MAOXIAN_BTN["quxiao"], elsedelay=2)
                    return 1
            else:
                # 不可扫荡
                self.click_btn(MAOXIAN_BTN["quxiao"], elsedelay=2)
                self._zdzb_info = "notili"
                return -1

        def enter(mode=True):
            # mode=True时，如果点不进关卡会报错，否则只会返回false
            btn = PCRelement(x, y)
            if drag == "left":
                self.Drag_Left()
            elif drag == "right":
                self.Drag_Right()
            return self.lock_img(FIGHT_BTN["xuanguan_quxiao"], is_raise=mode, elseclick=btn, timeout=30,
                                 elsedelay=8)

        if not enter(False):
            return -3
        stars = self.get_upperright_stars()
        if use_saodang in ["auto", True] and stars < 3:
            if use_saodang == "auto":
                use_saodang = False
            else:
                self.click_btn(MAOXIAN_BTN["quxiao"])
                self._zdzb_info = "nosaodang"
                return -2
        if use_saodang in ["auto", True]:
            state = saodang(times)

            if state == 1:
                # 扫荡成功
                clear()
                return 1 if type(times) is str else times
            elif use_saodang == "auto" and state == 0:
                # 改手刷,state = -1
                use_saodang = False
            else:
                if state == 0:
                    self._zdzb_info = "noquan"
                clear()
                self.click_btn(MAOXIAN_BTN["quxiao"])
                return -2
        if use_saodang is False:
            if times == "all":
                times = 99999999
            while var["cur_times"] < times:
                # 手刷
                enter()
                if fastmode:
                    s = shoushua(times - var["cur_times"])
                else:
                    s = shoushua(1)
                if s == 2:
                    if not fail_retry:
                        # 失败了不重试，结束
                        r = var["cur_win"]
                        clear()
                        return r
                elif s == 0:
                    return -2
                if var["cur_times"] < times - 1:
                    if not self.check_shuatu():
                        self.click_btn(MAOXIAN_BTN["quxiao"])
                        self._zdzb_info = "notili"
                        return -2
                    enter()  # 再次进入
            r = var["cur_win"]
            clear()
            return r
        else:
            # 扫荡失败，还不是auto
            clear()
            self.click_btn(MAOXIAN_BTN["quxiao"])
            self._zdzb_info = "nosaodang"
            return -2

    @DEBUG_RECORD
    def shuatuzuobiao(self, x, y, times):  # 刷图函数，xy为该图的坐标，times为刷图次数
        if self.switch == 0:
            tmp_cout = 0
            self.click(x, y, pre_delay=2, post_delay=2)
        else:
            # pcr_log(self.account).write_log(level='info', message='>>>无扫荡券或者无体力，结束 全部 刷图任务！<<<')
            return
        if self.switch == 0:
            while True:  # 锁定加号
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/jiahao.bmp', at=(850, 305, 907, 358)):
                    # screen_shot = a.d.screenshot(format="opencv")
                    for i in range(times - 1):  # 基础1次
                        # 扫荡券不必使用opencv来识别，降低效率
                        self.click(876, 334)
                    self.click(758, 330, pre_delay=1, post_delay=1)  # 使用扫荡券的位置 也可以用OpenCV但是效率不够而且不能自由设定次数
                    screen_shot = self.getscreen()
                    if UIMatcher.img_where(screen_shot, 'img/ok.bmp'):
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    else:
                        time.sleep(0.5)
                        self.click(588, 370)
                    # screen_shot = a.d.screenshot(format="opencv")
                    # a.guochang(screen_shot,['img/shiyongsanzhang.jpg'])
                    screen_shot_ = self.getscreen()
                    if UIMatcher.img_where(screen_shot_, 'img/tilibuzu.jpg'):
                        pcr_log(self.account).write_log(level='info', message='>>>无扫荡券或者无体力！结束此次刷图任务！<<<')
                        self.switch = 1
                        self.click(677, 458)  # 取消
                        break
                    screen_shot = self.getscreen()
                    if UIMatcher.img_where(screen_shot, 'img/juqing/tiaoguo_2.bmp'):
                        self.guochang(screen_shot, ['img/juqing/tiaoguo_2.bmp'], suiji=0)
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    else:
                        time.sleep(1)
                        self.click(475, 481)  # 手动点击跳过
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    break
                else:
                    if tmp_cout < 3:
                        # 计时3次就失败
                        self.click(x, y)
                        time.sleep(0.5)
                        tmp_cout = tmp_cout + 1
                    else:
                        pcr_log(self.account).write_log(level='info', message='>>>无扫荡券或者无体力！结束此次刷图任务！<<<')
                        self.switch = 1
                        self.click(677, 458)  # 取消
                        break
        else:
            pcr_log(self.account).write_log(level='info', message='>>>无扫荡券或者无体力！结束刷图任务！<<<')
        while True:
            self.click(1, 1)
            time.sleep(0.3)
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/normal.jpg', at=(660, 72, 743, 94)):
                break
            if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                break

    @DEBUG_RECORD
    def enter_zhuxian(self):
        # Fix: 2020-08-09 By TheAutumnOfRice: 未解锁地下城也可以使用了。
        # 进入主线
        self.lock_home()
        self.click_btn(MAIN_BTN["maoxian"], until_appear=MAIN_BTN["zhuxian"])
        # 进入地图
        self.click_btn(MAIN_BTN["zhuxian"], wait_self_before=True, until_appear=MAOXIAN_BTN["ditu"])

    @DEBUG_RECORD
    def enter_hard(self, max_retry=3):
        for retry in range(max_retry):
            self.enter_zhuxian()
            for retry_2 in range(3):
                time.sleep(1)
                self.wait_for_loading()
                state = self.check_maoxian_screen()
                if state == 1:
                    self.click(MAOXIAN_BTN["hard_on"])
                elif state == 2:
                    return
        raise Exception("进入困难图超过最大尝试次数！")

    # 左移动
    @DEBUG_RECORD
    def goLeft(self):
        self.click(35, 275, post_delay=3)

    # 右移动
    @DEBUG_RECORD
    def goRight(self):
        self.click(925, 275, post_delay=3)

    @DEBUG_RECORD
    def check_maoxian_screen(self, screen=None):
        """
        获得冒险界面屏幕状态
        :return:
        -1: 未知状态
        0： 找到了“冒险”，但不清楚是Normal还是Hard
        1:  Normal图
        2： Hard图
        """
        sc = screen if screen is not None else self.getscreen()
        pn1 = self.img_prob(MAOXIAN_BTN["normal_on"], screen=sc)
        ph1 = self.img_prob(MAOXIAN_BTN["hard_on"], screen=sc)
        if pn1 > 0.9:
            return 1
        elif ph1 > 0.9:
            return 2
        elif self.is_exists(MAOXIAN_BTN["ditu"], screen=sc):
            return 0
        else:
            return -1

    @DEBUG_RECORD
    def hard_shuatuzuobiao(self, x, y, times):  # 刷图函数，xy为该图的坐标，times为刷图次数,防止占用shuatuzuobiao用的
        if self.switch == 0:
            tmp_cout = 0
            self.click(x, y)
            time.sleep(0.5)
        else:
            # pcr_log(self.account).write_log(level='info', message='>>>无扫荡券,无体力,无次数！结束 全部 刷图任务！<<<')
            return
        if self.switch == 0:
            while True:  # 锁定加号
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/jiahao.bmp'):
                    # screen_shot = a.d.screenshot(format="opencv")
                    for i in range(times - 1):  # 基础1次
                        # 扫荡券不必使用opencv来识别，降低效率
                        self.click(876, 334)
                    time.sleep(0.3)
                    self.click(758, 330)  # 使用扫荡券的位置 也可以用OpenCV但是效率不够而且不能自由设定次数
                    time.sleep(0.3)
                    screen_shot = self.getscreen()
                    if UIMatcher.img_where(screen_shot, 'img/ok.bmp'):
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    else:
                        time.sleep(0.5)
                        self.click(588, 370)
                    # screen_shot = a.d.screenshot(format="opencv")
                    # a.guochang(screen_shot,['img/shiyongsanzhang.jpg'])
                    screen_shot_ = self.getscreen()
                    if UIMatcher.img_where(screen_shot_, 'img/tilibuzu.jpg'):
                        pcr_log(self.account).write_log(level='info', message='>>>无扫荡券,无体力,无次数！结束此次刷图任务！<<<')
                        self.switch = 1
                        self.click(677, 458)  # 取消
                        break
                    screen_shot = self.getscreen()
                    if UIMatcher.img_where(screen_shot, 'img/juqing/tiaoguo_2.bmp'):
                        self.guochang(screen_shot, ['img/juqing/tiaoguo_2.bmp'], suiji=0)
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    else:
                        time.sleep(1)
                        self.click(475, 481)  # 手动点击跳过
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    break
                else:
                    if tmp_cout < 3:
                        # 计时3次就失败
                        self.click(x, y)
                        time.sleep(0.5)
                        tmp_cout = tmp_cout + 1
                    else:
                        pcr_log(self.account).write_log(level='info', message='>>>无扫荡券,无体力,无次数！结束此次刷图任务！<<<')
                        self.switch = 1
                        self.click(677, 458)  # 取消
                        break
        else:
            pcr_log(self.account).write_log(level='info', message='>>>无扫荡券,无体力,无次数！结束刷图任务！<<<')
        while True:
            self.click(1, 1)
            time.sleep(0.3)
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/zhuxian.jpg', at=(660, 72, 743, 94)):
                break
            if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                break

    # 继续执行函数
    @DEBUG_RECORD
    def continueDo9(self, x, y):
        self.switch = 0
        self.shuatuzuobiao(x, y, self.times)  # 3-3

    # 识别7村断崖
    @DEBUG_RECORD
    def duanyazuobiao(self):
        """
        识别断崖的坐标
        """
        from core.constant import MAX_MAP
        tag = 0
        time.sleep(2)
        while True:
            if tag > MAX_MAP:  # 超过MAX_MAP次点击则不刷图
                for _ in range(6):
                    self.click(925, 275)
                    time.sleep(1.5)  # 这是高延迟识别时间,模拟器卡顿请加时
                break
            else:
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/duanyazuobiao.jpg'):
                    pcr_log(self.account).write_log(level='info', message='>>>成功识别标记,开始刷图.<<<\r\n')
                    break
                self.click(27, 272)
                tag += 1
                time.sleep(1.5)

    @DEBUG_RECORD
    def check_zhuxian_id(self, screen=None, max_retry=2):
        """
        识别主线图的图号
        2020-08-14 Add: By TheAutumnOfRice :
            只要截图截的小，普通困难都打倒！
        :param: screen:设置为None时，第一次重新截图
        :param max_retry: 找图失败最多尝试次数
        :return:
        -1：识别失败
        1~ ：图号
        """
        # self.Drag_Left()  # 保证截图区域一致
        for retry in range(max_retry):
            if screen is None:
                screen = self.getscreen()
            id = self.check_dict_id(ZHUXIAN_ID, screen, diff_threshold=0)
            for second in ZHUXIAN_SECOND_ID:
                if id in second:
                    id = self.check_dict_id(ZHUXIAN_SECOND_ID[second], screen, diff_threshold=0.1)
                    break
            if id is None:
                time.sleep(1)
            else:
                return id
        return -1

    def check_normal_id(self, screen=None):
        return self.check_zhuxian_id(screen)

    def check_hard_id(self, screen=None):
        return self.check_zhuxian_id(screen)

    @DEBUG_RECORD
    def shoushuazuobiao(self, x, y, jiaocheng=0, lockpic='img/zhuxian.jpg', screencut=None):
        """
        不使用挑战券挑战，xy为该图坐标
        jiaocheng=0 只处理简单的下一步和解锁内容
        jiaocheng=1 要处理复杂的教程
        lockpic: 返回时锁定的图
        screencut: 返回时锁定的图的搜索范围
        :return:
        """
        while True:
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, lockpic, at=screencut):
                break
            self.click(1, 138)
            time.sleep(1)
        self.lock_img('img/tiaozhan.jpg', elseclick=[(x, y)], elsedelay=2)
        self.click(840, 454)
        time.sleep(0.7)

        while True:
            screen_shot_ = self.getscreen()
            if UIMatcher.imgs_where(screen_shot_, ['img/kuaijin.jpg', 'img/kuaijin_1.jpg']) != {}:
                break
            self.click(840, 454)  # 点到进入战斗画面
            time.sleep(0.7)
        while True:
            screen_shot_ = self.getscreen()
            if self.click_img(screen_shot_, 'img/kuaijin.jpg', at=(891, 478, 936, 517)):
                time.sleep(1)
            if self.click_img(screen_shot_, 'img/auto.jpg', at=(891, 410, 936, 438)):
                time.sleep(1)
            if UIMatcher.img_where(screen_shot_, 'img/wanjiadengji.jpg', at=(233, 168, 340, 194)):
                break
            self.click(1, 138)
            time.sleep(0.5)
        if jiaocheng == 1:  # 有复杂的教程，交给教程函数处理
            self.chulijiaocheng()
        else:  # 无复杂的教程，自己处理掉“下一步”
            for _ in range(7):
                self.click(832, 506)
                time.sleep(0.2)
            while True:
                time.sleep(2)
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, lockpic, at=screencut):
                    break
                elif UIMatcher.img_where(screen_shot_, 'img/xiayibu.jpg'):
                    self.click(832, 506)
                else:
                    self.click(1, 100)
            while True:  # 两次确认回到挑战界面
                self.click(1, 100)
                time.sleep(0.5)
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, lockpic, at=screencut):
                    break

    @DEBUG_RECORD
    def upgrade_kkr(self, screen_shot=None):
        if screen_shot is None:
            screen_shot = self.getscreen()
        if self.is_exists(DXC_ELEMENT["dxc_kkr"], screen=screen_shot):
            self.chulijiaocheng(turnback=None)
            self.enter_upgrade()
            return True
        if self.is_exists(MAOXIAN_BTN["jsjsqr"], screen=screen_shot):
            self.click(369, 485)
            for _ in range(5):
                self.click(5, 117)
            return True
        return False

    @DEBUG_RECORD
    def enter_upgrade(self):
        self.click_btn(MAIN_BTN["juese"], until_appear=JUESE_BTN["duiwu"])

        def _check_level_sort():
            sc = self.getscreen()
            p0 = self.img_prob(JUESE_BTN["sort_up"], screen=sc)
            p1 = self.img_prob(JUESE_BTN["sort_down"], screen=sc)
            if p0 > p1:
                self.click_btn(JUESE_BTN["sort_up"])
            if not self.is_exists(JUESE_BTN["sort_level"]):
                self.click_btn(JUESE_BTN["sort_level"], until_appear=FIGHT_BTN["cat_ok"])
                self.click(FIGHT_BTN["cat_dengji"], pre_delay=0.5, post_delay=1)
                self.click_btn(FIGHT_BTN["cat_ok"])

        _check_level_sort()
        juese = 1
        while juese <= 9:
            mode = self.click_btn(JUESE_BTN["nine_juese"][juese], until_appear={
                JUESE_BTN["mana_ball"]: 1,
                DXC_ELEMENT["dxc_kkr"]: 2,
                MAOXIAN_BTN["jsjsqr"]: 3,
            })
            if mode == 2:
                self.chulijiaocheng(turnback=None)
                self.click_btn(MAIN_BTN["juese"], until_appear=JUESE_BTN["duiwu"])
                continue
            if mode == 3:
                self.click(369, 485)
                for _ in range(5):
                    self.click(5, 117)
                juese += 1
            if mode == 1:
                break

    @DEBUG_RECORD
    def get_tuijian_stars(self, screen=None):
        """
        获取推荐强化菜单中第一个关卡的星星数
        :param screen: 设置为None时，不另外截屏
        :return: 0~3
        """
        if screen is None:
            screen = self.getscreen()
        fc = np.array([98, 228, 245])  # G B R:金色
        bc = np.array([212, 171, 139])  # G B R:灰色
        c = []
        us = JUESE_BTN["firstqianghua_stars"]
        for i in range(1, 4):
            x = us[i].x
            y = us[i].y
            c += [screen[y, x]]
        c = np.array(c)
        tf = np.sqrt(((c - fc) ** 2)).sum(axis=1)
        tb = np.sqrt(((c - bc) ** 2)).sum(axis=1)
        t = tf < tb
        return np.sum(t)

    @DEBUG_RECORD
    def auto_upgrade(self, buy_tili=0, do_rank=True, do_shuatu=True, var={}):
        """
        :param buy_tili: 如果要通过刷图来获取装备，最多买体力次数
        :param do_rank: 是否升rank
        :param do_shuatu: 是否在装备可以获得但不够时，通过刷图来获取装备
        ！注：auto_upgrade不会调用self.clear_tili_info()！
        ！注：目前不会进行装备强化
        新的自动强化函数
        """

        # TODO 装备强化问题
        def _next():
            sc = self.getscreen()
            name_at = (40, 393, 104, 441)
            self.click(929, 269)
            # TODO 这里会卡，原因不明
            for _ in range(10):
                m = self.wait_for_change(screen=sc, at=name_at, delay=1, threshold=0.84, max_retry=1)
                if self.is_exists(JUESE_BTN["fhqhdj_ok"], screen=self.last_screen):
                    self.click_btn(JUESE_BTN["fhqhdj_ok"])
                    time.sleep(0.5)
                    sc = self.getscreen()
                elif m:
                    break
                if self.upgrade_kkr(sc):
                    break
            else:
                raise Exception("原因不明的wait_for_change错误！")

        def _rank_up():
            # rank提升步骤
            if do_rank and self.is_exists(JUESE_BTN["rank_tisheng"]):
                out = self.click_btn(JUESE_BTN["rank_tisheng"], until_appear={
                    JUESE_BTN["rank_tisheng_ok"]: 1,
                    JUESE_BTN["rank_tisheng_ok_noequ"]: 2}, side_check=self.upgrade_kkr)
                if out == 1:
                    self.click_btn(JUESE_BTN["rank_tisheng_ok"])
                else:
                    self.click_btn(JUESE_BTN["rank_tisheng_ok_noequ"])
                self.click_btn(JUESE_BTN["rank_tisheng_ok2"], wait_self_before=True)
                return True

            return False

        def _auto():
            # 自动强化
            def _xiadian():
                for _ in range(5):  # 瞎点结束
                    self.click(9, 73)

            while True:
                if self.is_exists(JUESE_BTN["zdqh"], method="sq"):
                    self.click_btn(JUESE_BTN["zdqh"], side_check=self.upgrade_kkr)
                    mode = self.lock_img(
                        {JUESE_BTN["rank_tisheng_ok"]: 1, JUESE_BTN["tjqhcd"]: 2, JUESE_BTN["zdqh"]: 99})
                    if mode == 99:
                        continue  # 报错修补
                    if mode == 1:
                        # 存在正常的强化
                        self.click_btn(JUESE_BTN["rank_tisheng_ok"])
                        while True:
                            out = self.lock_img({
                                JUESE_BTN["yjzb_off"]: 1,
                                JUESE_BTN["rank_tisheng"]: 2,
                                JUESE_BTN["fhqhdj_ok"]: 3,
                            }, is_raise=False, timeout=15)
                            if out == 3:
                                self.click_btn(JUESE_BTN["fhqhdj_ok"])
                                continue
                            if out == 2 and do_rank:
                                _rank_up()
                            else:
                                break

                        continue
                    else:
                        # 推荐强化菜单：必须刷装备，或者进行装备升级
                        if self.is_exists(JUESE_BTN["tuijianguanqia"], screen=self.last_screen):
                            if not do_shuatu:
                                _xiadian()
                                break
                            if not self.check_shuatu():
                                _xiadian()
                                break
                            stars = self.get_tuijian_stars(screen=self.last_screen)
                            if stars == 3:
                                self.zhandouzuobiao(485, 232, 3, None, use_saodang=True, speed=1, auto=1,
                                                    buy_tili=buy_tili, var=var)
                            elif stars > 0:
                                self.zhandouzuobiao(485, 232, 1, None, speed=1, auto=1, buy_tili=buy_tili, var=var)
                            else:
                                _xiadian()
                                break
                            _xiadian()
                            if self._zdzb_info == "nocishu":
                                break
                        else:
                            # 直接结束
                            _xiadian()
                            break
                else:
                    return False

        # 进入强化
        if buy_tili > 0:
            self.start_shuatu()
        self.lock_home()
        self.enter_upgrade()
        for _ in range(5):
            while _rank_up():
                pass
            _auto()
            _next()
        self.lock_home()

    @DEBUG_RECORD
    def select_most_right(self):
        """
        移动到最右关卡
        :return: 最右关卡图号
        """
        last = None
        now = self.check_zhuxian_id()
        while now != last:
            last = now
            if now == 13:
                self.Drag_Right()  # 防止误触
            self.goRight()
            now = self.check_zhuxian_id()
        return now

    def _exist_lock(self, x, y, size=100, screen=None):
        at = (x - size, y - size, x + size, y + size)
        if self.is_exists(MAOXIAN_BTN["lock"], screen=screen, at=at):
            return True

    @DEBUG_RECORD
    def get_next_normal_id(self):
        tu = self.select_most_right()
        D = NORMAL_COORD[tu]
        DR = D["right"]
        DL = D["left"]
        Max = max(max(DR), max(DL))
        last_dict = {"last": None}

        def get_try(i, last_dict):
            if i in DR:
                if last_dict["last"] != "right":
                    self.Drag_Right()
                    last_dict["last"] = "right"
                s = self.click_btn(DR[i], until_appear=FIGHT_BTN["xuanguan_quxiao"], is_raise=False, elsedelay=2,
                                   timeout=3)
                if s:
                    self.click_btn(MAOXIAN_BTN["quxiao"])
                    return (tu, i)
                else:
                    return None
            else:
                if last_dict["last"] != "left":
                    self.Drag_Left()
                    last_dict["last"] = "left"
                s = self.click_btn(DL[i], until_appear=FIGHT_BTN["xuanguan_quxiao"], is_raise=False, elsedelay=2,
                                   timeout=3)
                if s:
                    self.click_btn(MAOXIAN_BTN["quxiao"])
                    return (tu, i)
                else:
                    return None

        # 二分查找
        left = 1
        right = Max
        mid = (left + right) // 2
        s = None
        while left + 1 < right:
            s = get_try(mid, last_dict)
            if s is None:
                right = mid
            else:
                left = mid
            mid = (left + right) // 2
        if left == Max - 1:
            s = get_try(right, last_dict)
            if s is not None:
                left = right
        return (tu, left)

    @DEBUG_RECORD
    def get_next_hard_id(self):
        def count_lock(tu):
            sc = self.getscreen()
            cnt = 0
            for i in range(1, 4):
                x, y = HARD_COORD[tu][i]
                if self._exist_lock(x, y, screen=sc):
                    cnt += 1
            return cnt

        last_tu = None
        last_cnt = None
        while True:
            tu = self.check_zhuxian_id(max_retry=5)  # 此处老是图号识别失败，很诡异
            cnt = count_lock(tu)
            if tu == last_tu:
                return tu, 3 - cnt
            if last_cnt is not None:
                if last_cnt == 3 and cnt < 3:
                    return tu, 3 - cnt
                if last_cnt == 0 and cnt == 3:
                    return last_tu, 3
            if cnt == 3:
                self.goLeft()
            elif cnt == 0:
                self.goRight()
            else:
                return tu, 3 - cnt
            last_tu = tu
            last_cnt = cnt

    @DEBUG_RECORD
    def qianghua(self):
        # 此处逻辑极为复杂，代码不好理解
        time.sleep(3)
        self.click(215, 513)  # 角色
        time.sleep(3)
        self.click(177, 145)  # First
        time.sleep(3)
        for i in range(5):
            print("Now: ", i)
            time.sleep(5)
            while True:
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/keyihuode.jpg'):
                    # 存在可以获得，则一直获得到没有可以获得，或者没有三星
                    self.click(374, 435)
                    time.sleep(1)
                    screen_shot_ = self.getscreen()
                    if UIMatcher.img_where(screen_shot_, 'img/tuijianguanqia.jpg', at=(258, 87, 354, 107)):
                        # 已经强化到最大等级，开始获取装备
                        if not UIMatcher.img_where(screen_shot_, 'img/sanxingtongguan.jpg'):
                            # 装备不可刷，换人
                            self.click(501, 468)  # important
                            time.sleep(1)
                            break
                        while UIMatcher.img_where(screen_shot_, 'img/sanxingtongguan.jpg'):
                            # 一直刷到没有有推荐关卡但没有三星或者返回到角色列表
                            self.guochang(screen_shot_, ['img/sanxingtongguan.jpg'], suiji=0)
                            time.sleep(1)
                            # 使用扫荡券的数量：
                            for _ in range(4 - 1):
                                self.click(877, 333)
                                time.sleep(0.3)
                            self.click(752, 333)
                            time.sleep(0.7)
                            self.click(589, 371)
                            while True:
                                screen_shot_ = self.getscreen()
                                active_paths = UIMatcher.imgs_where(screen_shot_,
                                                                    ['img/tuijianguanqia.jpg', 'img/zidongqianghua.jpg',
                                                                     'img/juqing/tiaoguo_2.bmp'])
                                if 'img/juqing/tiaoguo_2.bmp' in active_paths:
                                    x, y = active_paths['img/juqing/tiaoguo_2.bmp']
                                    self.click(x, y)
                                if 'img/tuijianguanqia.jpg' in active_paths:
                                    flag = 'img/tuijianguanqia.jpg'
                                    break
                                elif 'img/zidongqianghua.jpg' in active_paths:
                                    flag = 'img/zidongqianghua.jpg'
                                    break
                                else:
                                    self.click(1, 100)
                                    time.sleep(1.3)
                            if flag == 'img/zidongqianghua.jpg':
                                # 装备获取完成，跳出小循环，重进大循环
                                self.click(371, 437)
                                time.sleep(0.7)
                                break
                            else:
                                # 装备未获取完毕，继续尝试获取
                                continue
                        self.click(501, 468)  # important
                        time.sleep(2)
                        continue
                    else:
                        # 未强化到最大等级，强化到最大登记
                        self.click(501, 468)  # important
                        time.sleep(3)
                        continue
                else:
                    # 没有可以获得
                    if UIMatcher.img_where(screen_shot_, 'img/ranktisheng.jpg', at=(206, 325, 292, 346)):
                        self.click(250, 338)
                        time.sleep(2)
                        screen_shot_ = self.getscreen()
                        active_list = UIMatcher.imgs_where(screen_shot_, ['img/queren.jpg', 'img/ok.bmp'])
                        if 'img/queren.jpg' in active_list:
                            x, y = active_list['img/queren.jpg']
                            self.click(x, y)
                        if 'img/ok.bmp' in active_list:
                            x, y = active_list['img/ok.bmp']
                            self.click(x, y)
                        time.sleep(8)
                        self.click(481, 369)
                        time.sleep(1)
                        continue
                    else:
                        self.click(371, 437)
                        time.sleep(0.7)
                        self.click(501, 468)  # important
                        time.sleep(2)
                        break
            self.click(933, 267)  # 下一位
            time.sleep(2)

        self.lock_home()
        self.lock_img('img/zhuxianguanqia.jpg', elseclick=[(480, 513)], elsedelay=3)
        self.click(562, 253)
        time.sleep(3)
        self.lock_img('img/zhuxian.jpg', elseclick=[(704, 84)], elsedelay=0.5, alldelay=1, at=(660, 72, 743, 94))
        self.click(923, 272)
        time.sleep(3)

    @DEBUG_RECORD
    def enter_normal(self, max_retry=3):
        """
        进入normal图
        """
        for retry in range(max_retry):
            self.enter_zhuxian()
            for retry_2 in range(3):
                time.sleep(1)
                self.wait_for_loading()
                state = self.check_maoxian_screen()
                if state == 2:
                    self.click(MAOXIAN_BTN["normal_on"])
                elif state == 1:
                    return
        raise Exception("进入普通图超过最大尝试次数！")

    @DEBUG_RECORD
    def select_normal_id(self, id):
        """
        走到normal的几图
        要求场景：已经在normal内
        :param id: 图号
        """
        retry_cnt = 0
        all_cnt = 0
        while all_cnt < 3:
            sc = self.getscreen()
            while self.check_maoxian_screen(sc) == 2:
                self.click(MAOXIAN_BTN["normal_on"], post_delay=1)
                sc = self.getscreen()
            cur_id = self.check_normal_id(sc)
            if cur_id == -1:
                self.wait_for_loading(sc)
                if self.is_exists(MAOXIAN_BTN["ditu"], screen=self.last_screen):
                    if self.check_maoxian_screen() == 2:
                        self.click(MAOXIAN_BTN["normal_on"], post_delay=1)
                    # 重试一次
                    continue
                else:
                    retry_cnt += 1
                    if retry_cnt == 1:
                        for _ in range(6):
                            self.click(76, 15)  # 防止奇怪对话框
                            self.click(843, 491)  # 本不应该有这行代码，但是查不出漏洞了，只能用这个解
                            # 决推图，Win后出现限定商店后直接暴毙的问题
                        continue
                    elif retry_cnt == 2:
                        for _ in range(3):
                            self.goLeft()  # 可能没更新新图？
                        continue
                    elif retry_cnt == 3:
                        self.lock_home()  # 发大招
                        self.enter_normal()
                        for _ in range(3):
                            self.goLeft()  # 可能没更新新图？
                        continue
                    else:
                        raise Exception("Normal 图号识别失败！")

            if cur_id == id:
                return
            elif cur_id < id:
                for i in range(id - cur_id):
                    self.goRight()
            elif cur_id > id:
                for i in range(cur_id - id):
                    self.goLeft()
            all_cnt += 1
        raise Exception("可能不存在的图号！")

    @DEBUG_RECORD
    def select_hard_id(self, id):
        """
        走到hard的几图
        要求场景：已经在hard内
        :param id: 图号
        """
        retry_cnt = 0
        all_cnt = 0
        while all_cnt < 3:
            sc = self.getscreen()
            while self.check_maoxian_screen(sc) == 1:
                self.click(MAOXIAN_BTN["hard_on"], post_delay=1)
                sc = self.getscreen()
            cur_id = self.check_hard_id(sc)
            if cur_id == -1:
                self.wait_for_loading(sc)
                if self.is_exists(MAOXIAN_BTN["ditu"], screen=self.last_screen):
                    # 重试一次
                    if self.check_maoxian_screen() == 1:
                        self.click(MAOXIAN_BTN["hard_on"], post_delay=1)
                    continue
                else:
                    retry_cnt += 1
                    if retry_cnt == 1:
                        for _ in range(6):
                            self.click(76, 15)  # 防止奇怪对话框
                        continue
                    elif retry_cnt == 2:
                        for _ in range(3):
                            self.goLeft()  # 可能没更新新图？
                        continue
                    elif retry_cnt == 3:
                        self.lock_home()  # 发大招
                        self.enter_hard()
                        for _ in range(3):
                            self.goLeft()  # 可能没更新新图？
                        continue
                    else:
                        raise Exception("Hard 图号识别失败！")
            if cur_id == id:
                return
            elif cur_id < id:
                for i in range(id - cur_id):
                    self.goRight()
            elif cur_id > id:
                for i in range(cur_id - id):
                    self.goLeft()
            all_cnt += 1
        raise Exception("可能不存在的图号！")

