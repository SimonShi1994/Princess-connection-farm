import time

from core.pcr_checker import PCRRetry
from scenes.fight.fightinfo_base import FightInfoBase
from scenes.fight.fightbianzu_base import FightBianZuBase
from scenes.fight.fighting_base import FightingBase
from scenes.fight.fighting_zhuxian import LoveUpScene, HaoYouMsg, FightingDialog, FightingWinZhuXian, \
    FightingLoseZhuXian
from scenes.huodong.huodong_fight import BOSS_FightInfoBase
from scenes.zhuxian.zhuxian_base import ZhuXianBase
from scenes.scene_base import PCRSceneBase, PossibleSceneList, PCRMsgBoxBase
from core.constant import p, FIGHT_BTN, HUODONG_BTN, MAIN_BTN
from typing import Union


class FightingWinHuodong(FightingWinZhuXian):
    def __init__(self, a):
        super().__init__(a)
        self.feature = self.fun_feature_exist(HUODONG_BTN["long_next"])


class DuringFightingHuodong(PossibleSceneList):
    def __init__(self, a, *args, **kwargs):
        self.LoveUpScene = LoveUpScene
        self.FightingWin = FightingWinHuodong
        self.FightingLose = FightingLoseZhuXian
        self.FightingDialog = FightingDialog
        self.HaoYouMsg = HaoYouMsg

        scene_list = [
            LoveUpScene(a),
            FightingWinHuodong(a),
            FightingLoseZhuXian(a),
            FightingDialog(a),
            HaoYouMsg(a),
        ]
        super().__init__(a, scene_list, double_check=0)


class FightingHuodong(FightingBase):
    def get_during(self):
        return DuringFightingHuodong(self._a)


class FightBianZuHuoDong(FightBianZuBase):
    def goto_zhandou(self) -> FightingHuodong:
        return self.goto(FightingHuodong, self.fun_click(839, 452))


class HuodongMapBase(ZhuXianBase):
    NAME = "UNDEFINED"
    NORMAL_ON = p(764, 83, img="img/maoxian/normal_on.bmp", at=(739, 72, 788, 93))
    HARD_ON = p(886, 82, img="img/maoxian/hard_on.bmp", at=(856, 70, 916, 93))
    XY11 = None  # Normal(1,1)的坐标，用于刷1-1
    HARD_COORD = None  # 大号刷Hard用坐标
    XY_HARD_BOSS = None
    XY_VH_BOSS = None

    def __init__(self, a):
        super().__init__(a)
        self.feature = self.feature_normal_or_hard
        self.initPC = self.karin_restart

    def karin_restart(self, screen):
        if self.is_exists(MAIN_BTN["karin_middle"], screen=screen):
            self.chulijiaocheng(None)
            self._a.restart_this_task()
        return screen

    def feature_normal_or_hard(self, screen):
        normal = self.is_exists(self.NORMAL_ON, screen=screen)
        hard = self.is_exists(self.HARD_ON, screen=screen)
        return normal or hard

    def goto_hard(self):
        self.lock_img(self.HARD_ON, elseclick=self.HARD_ON, method="sq")
        return self

    def goto_normal(self):
        self.lock_img(self.NORMAL_ON, elseclick=self.NORMAL_ON, method="sq")
        return self

    def to_leftdown(self):
        time.sleep(1)
        obj = self.d.touch.down(47, 466)
        time.sleep(0.1)
        obj.move(47, 96)
        time.sleep(0.8)
        obj.up(47, 96)
        time.sleep(1)
        obj = self.d.touch.down(84, 80)
        time.sleep(0.1)
        obj.move(416, 80)
        time.sleep(0.8)
        obj.up(416, 80)
        time.sleep(1)


    def _check_coord(self, t):
        # t: tuple -> PCRComponent
        # t: None -> raise!
        if t is None:
            raise Exception("该活动图并没有设定该坐标：", t)
        else:
            if isinstance(t, tuple):
                return p(t[0], t[1])
            else:
                return p

    def goto_menu(self) -> "HuodongMenu":
        return self.goto(HuodongMenu, self.fun_click(HUODONG_BTN["return"]))

    def shua_11(self, cishu: Union[str, int] = "max", team_order="nobody", get_zhiyuan=True, ):
        """
        小号刷1-1，必须没有推过Normal图的号才能用。
        返回场景： 主页！！！！
        cishu: 刷几次，设置为"max"时，tomax.

        Return: (Code, LeftCishu)
            Code - 返回代码
                0 - 成功
                1 - 体力不足
            LeftCishu - 剩余几次
                cishu设置为"max"时，永远返回 0
                cishu设置为整数时，返回剩余未刷的次数
        """
        self.set_initFC()
        XY11 = self._check_coord(self.XY11)
        self.goto_normal()
        self.to_leftdown()
        fi = self.click_xy_and_open_fightinfo(*XY11, typ=FightInfoBase)
        if fi is None:
            self.chulijiaocheng(None)
            self._a.restart_this_task()
        ADDD = {}
        if fi.is_threestar():
            out = fi.easy_saodang(cishu, 8, False, additional_info=ADDD)
            left_cishu = 0 if cishu == "max" else cishu - ADDD["cishu"]
            if out == 1:
                self.chulijiaocheng(None)
                return 1, left_cishu
            else:
                self.chulijiaocheng(None)
                return 0, left_cishu
        else:
            self.log.write_log("info", "尚未通关1-1，尝试手刷。")
            out = fi.easy_shoushua(team_order=team_order,
                                   one_tili=8,
                                   check_cishu=False,
                                   max_speed=2,
                                   get_zhiyuan=get_zhiyuan)
            # 强制处理教程
            self.chulijiaocheng(None)
            if out == 1:
                self.log.write_log("warning", "你甚至打不过活动1-1……跳过任务。")
                self._a.skip_this_task()
            elif out == 3:
                return 1, 0 if cishu == "max" else cishu - 1
            else:
                return 0, "max" if cishu == "max" else cishu - 1

    def shua_hard(self, tu_order=[]):
        """
        tu_order: List of [1,2,3,4,5]
        return:
            0 : Success
            1 : 体力不足
            2 : 扫荡券不足
        """
        assert self.HARD_COORD is not None
        for t in tu_order:
            assert t in self.HARD_COORD

        for tu in tu_order:
            self.set_initFC()
            self.goto_hard()
            XY = self._check_coord(self.HARD_COORD[tu])
            fi = self.click_xy_and_open_fightinfo(*XY, typ=FightInfoBase)
            self.clear_initFC()
            out = fi.easy_saodang(target_cishu="max", one_tili=-1, check_cishu=True)
            if out == 1:
                return 1
            elif out == 4:
                return 4
            self.fclick(1, 1)

        return 0

    def shua_VHBoss(self, team_order="none"):
        """
        大号刷VHBoss。最好已经打过一遍了。
        之后可能有剧情，因此默认跳过剧情。
        这个函数的结束位置在home，无论如何都会返回主页
        return
            0 - 挑战成功
            1 - 挑战失败
            2 - 券不足
            -1 - 无法进入
        """
        XY = self._check_coord(self.XY_VH_BOSS)
        self.goto_hard()
        out = self.lock_img(HUODONG_BTN["bossqsl"], elseclick=XY, elsedelay=2, retry=3, is_raise=False)
        if out is False:
            self.log.write_log("info", "无法进入VHBoss，今天可能已经打过了。")
            self._a.lock_home()
            return -1
        quan = self.ocr_int(800, 416, 856, 434)
        if quan < 30:
            self.log.write_log("warning", f"券不够，只有{quan}<30，打不了。")
            self._a.lock_home()
            return 2
        self.clear_initFC()
        fb: FightBianZuHuoDong = self.goto(FightBianZuHuoDong, self.fun_click(FIGHT_BTN["tiaozhan2"]))
        fb.select_team(team_order)
        zd = fb.goto_zhandou()
        zd.auto_and_fast(1)
        during = zd.get_during()
        after = None
        while True:
            out = during.check(timeout=300, double_check=3)
            if isinstance(out, during.FightingWin):
                self.log.write_log("info", "你胜利了。")
                out.next()
                after = out.get_after()
                break
            elif isinstance(out, during.FightingLose):
                self.log.write_log("info", "你失败了.")
                out.goto_zhuxian(type(self))
                self._a.lock_home()
                return 1
            elif isinstance(out, during.FightingDialog):
                out.skip()
            else:
                continue
        if after is not None:
            while True:
                out = after.check()
                if isinstance(out, after.FightingWinZhuXian2):
                    out.next()
                    self.chulijiaocheng(turnback=None)
                    return 0


class HuodongMenu(PCRSceneBase):
    def __init__(self, a):
        super().__init__(a)
        self.feature = self.fun_feature_exist(HUODONG_BTN["huodongguanka"])

    def goto_map(self) -> "HuodongMapBase":
        return self.goto(HuodongMapBase, self.fun_click(HUODONG_BTN["huodongguanka"]))

    def goto_jiaohuan(self) -> "Jiaohuan":
        return self.goto(Jiaohuan, self.fun_click(HUODONG_BTN["taofazheng_btn"]))

    def goto_nboss(self) -> "BOSS_FightInfoBase":
        screen = self.getscreen()
        self.click_img(img=HUODONG_BTN["nboss"].img, screen=screen, at=(681, 130, 789, 302))
        return self.goto(BOSS_FightInfoBase, gotofun=None)

    def goto_hboss(self) -> "BOSS_FightInfoBase":
        screen = self.getscreen()
        self.click_img(img=HUODONG_BTN["hboss"].img, screen=screen, at=(681, 130, 789, 302))
        return self.goto(BOSS_FightInfoBase, gotofun=None)

    def goto_vhboss(self) -> "BOSS_FightInfoBase":
        screen = self.getscreen()
        self.click_img(img=HUODONG_BTN["vhboss"].img, screen=screen, at=(681, 130, 789, 302))
        return self.goto(BOSS_FightInfoBase, gotofun=None)

    def shua_Boss(self, team_order="none", boss_type=None):
        """
        刷活动Boss。最好已经打过一遍了。
        之后可能有剧情，因此默认跳过剧情。
        这个函数的结束位置在home，无论如何都会返回主页
        return
            0 - 挑战成功
            1 - 挑战失败
            -1 - 无法进入
        """
        if boss_type == "N" or boss_type == "n":
            fi = self.goto_nboss()
        elif boss_type == "H" or boss_type == "h":
            fi = self.goto_hboss()
        elif boss_type == "VH" or boss_type == "vh":
            fi = self.goto_vhboss()
        else:
            self.log.write_log("warning", "错误的boss类型，跳过该任务")
            return

        while True:
            screen = self.getscreen()
            if fi.get_bsq_right(screen) == -1:
                break
            if fi.check_taofa(screen):
                # 检查是否打满3次，可以扫荡
                fi.easy_saodang(target_cishu="max", one_quan=20)
                break
            else:
                fb: FightBianZuHuoDong = self.goto(FightBianZuHuoDong, self.fun_click(HUODONG_BTN["tiaozhan2_on"]))
                fb.select_team(team_order)
                zd = fb.goto_zhandou()
                zd.auto_and_fast(1)
                during = zd.get_during()
                after = None
                while True:
                    out = during.check(timeout=300, double_check=3)
                    if isinstance(out, during.FightingWin):
                        self.log.write_log("info", "你胜利了。")
                        out.next()
                        after = out.get_after()
                        break
                    elif isinstance(out, during.FightingLose):
                        self.log.write_log("info", "你失败了.")
                        out.goto_zhuxian(type(self))
                        self._a.lock_home()
                        return 1
                    elif isinstance(out, during.FightingDialog):
                        out.skip()
                    else:
                        continue
                if after is not None:
                    while True:
                        out = after.check()
                        if isinstance(out, after.FightingWinZhuXian2):
                            out.next()
                            self.chulijiaocheng(turnback=None)
                            return 0


class Jiaohuan(PCRSceneBase):
    def __init__(self, a):
        super().__init__(a)
        self.feature = self.fun_feature_exist(HUODONG_BTN["dangqianliebiao"])

    def get_taofazheng(self, screen=None):
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        at = (880, 431, 928, 448)
        return self.ocr_int(*at, screen)

    def setting(self):
        self.lock_img(HUODONG_BTN["blsd"], elseclick=(785, 38))
        self.click(721, 156)  # 100次
        self.click(500, 272)  # 跳过
        self.click(500, 379)  # 5次后一键
        self.fclick(1, 1)

    def exchange_all(self, reset=False):
        while True:
            a = self.get_taofazheng()
            if a > 10:
                self.click(825, 371)
                time.sleep(2)

                # 这轮换完/不足一轮
                if self.is_exists(HUODONG_BTN["exchange_queren"]):
                    self.click_btn(HUODONG_BTN["return"], until_appear=HUODONG_BTN["dangqianliebiao"])
                # TODO:多周目扩充
                # self.lock_img(HUODONG_BTN["return"])
                pass
            elif a <= 10:
                self.lock_img(HUODONG_BTN["return"])
                self.click_btn(HUODONG_BTN["return"], until_appear=HUODONG_BTN["dangqianliebiao"])
                return
            else:
                return

    def goto_menu(self):
        return self.goto(HuodongMapBase, self.fun_click(HUODONG_BTN["huodongguanka"]))
