import time

from core.pcr_checker import PCRRetry
from scenes.fight.fightinfo_base import FightInfoBase
from scenes.fight.fightbianzu_base import FightBianZuBase
from scenes.fight.fighting_base import FightingBase
from scenes.fight.fighting_zhuxian import LoveUpScene, HaoYouMsg, FightingDialog, FightingWinZhuXian
from scenes.huodong.huodong_fight import BOSS_FightInfoBase
from scenes.zhuxian.zhuxian_base import ZhuXianBase
from scenes.scene_base import PCRSceneBase, PossibleSceneList, PCRMsgBoxBase
from core.constant import p, FIGHT_BTN, HUODONG_BTN, MAIN_BTN, JUQING_BTN, JUESE_BTN
from typing import Union


class FightingWinHuodong(FightingWinZhuXian):
    def __init__(self, a):
        super().__init__(a)
        self.feature = self.fun_feature_exist(HUODONG_BTN["long_next"])


class FightingLoseHuodong(FightingWinZhuXian):
    def __init__(self, a):
        super().__init__(a)
        self.feature = self.fun_feature_exist(HUODONG_BTN["short_next"])

    def exit_me(self):
        self.click_btn(HUODONG_BTN["short_next"])


class DuringFightingHuodong(PossibleSceneList):
    def __init__(self, a, *args, **kwargs):
        self.LoveUpScene = LoveUpScene
        self.FightingWin = FightingWinHuodong
        self.FightingLose = FightingLoseHuodong
        self.FightingDialog = FightingDialog
        self.HaoYouMsg = HaoYouMsg

        scene_list = [
            LoveUpScene(a),
            FightingWinHuodong(a),
            FightingLoseHuodong(a),
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
    # 坐标
    XY11 = None  # Normal(1,1)的坐标，用于刷1-1
    XY21 = None
    XY31 = None
    HARD_COORD = None  # 大号刷Hard用坐标
    XY_HARD_BOSS = None
    XY_VH_BOSS = None
    # 常数
    N_slice = 1
    N1 = 15
    N2 = 15
    N3 = 15

    def __init__(self, a):
        super().__init__(a)
        self.feature = self.feature_normal_or_hard
        self.initPC = self.clear_map

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
        elif self.is_exists(HUODONG_BTN["shadow_return"], screen=screen):
            self.fclick(1, 1)
        elif self.is_exists(JUQING_BTN["caidanyuan"], screen=screen):  # 打倒多个boss会出现对话
            self.fclick(1, 1)
        return screen

    def feature_normal_or_hard(self, screen):
        normal = self.is_exists(HUODONG_BTN["NORMAL_ON"], screen=screen)
        hard = self.is_exists(HUODONG_BTN["HARD_ON"], screen=screen)
        return normal or hard

    def goto_hd_hard(self):
        self.lock_img(HUODONG_BTN["HARD_ON"], elseclick=HUODONG_BTN["HARD_ON"], method="sq")
        return self

    def goto_hd_normal(self):
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

    def goto_hd_n1(self):
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
        obj.move(416, 80)
        time.sleep(0.8)
        obj.up(416, 80)
        time.sleep(1)

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

    def goto_hd_menu(self) -> "HuodongMenu":
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
        self.goto_hd_n1()
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
            self.goto_hd_hard()
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
        self.goto_hd_hard()
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
                self.log.write_log("info", "打不过难度为VH活动Boss")
                out.exit_me()
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
        self.feature = self.fun_feature_exist(HUODONG_BTN["taofazheng_btn"])
        self.initPC = self.clear_map

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
        return screen

    def hd_juqing(self):
        self.clear_initFC()
        self.lock_img(img="img/ui/close_btn_1.bmp", elseclick=(874, 342), elsedelay=1.5)
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

    def hd_xinlaidu(self):
        self.clear_initFC()
        self.click(498, 270)
        # 角色循环
        counter = 0  # 下拉次数计数器
        while True:
            self.lock_img(HUODONG_BTN["xinlaiduliwu"])
            time.sleep(1)
            lst = self.img_where_all(img="img/juqing/new_content.bmp", method="sq", at=(468, 60, 545, 466))
            if len(lst) > 0:
                x = lst[0] + 250
                y = lst[1] + 20
                self.click(x, y)  # 进入角色信赖度
                self.lock_no_img(HUODONG_BTN["wanfa"])
                self.lock_img(HUODONG_BTN["xinlaiduliwu2"])
                time.sleep(1)
                # 进入到角色界面了
                # 点击气泡
                while True:
                    time.sleep(1)
                    lst = self.img_where_all(img="img/juqing/rong.bmp", at=(3, 43, 863, 427))
                    if len(lst) > 0:
                        a = lst[0] + 50
                        b = lst[1] + 30
                        self.click(a, b)  # 进入剧情
                        time.sleep(1)
                        self._a.guojuqing(story_type="xinlai")
                        continue
                    else:
                        self.log.write_log("info", "无未读剧情")
                        self.click_btn(HUODONG_BTN["return"])
                        break
                continue
            else:
                if counter > 1:
                    self.log.write_log("info", "无未读角色")
                    break
                time.sleep(2)
                obj = self.d.touch.down(920, 165)
                time.sleep(0.1)
                obj.move(920, 282)
                time.sleep(0.8)
                obj.up(923, 282)
                time.sleep(1)
                counter += 1
                continue

    def goto_map(self, map_id) -> "HuodongMapBase":
        return self.goto(map_id, self.fun_click(HUODONG_BTN["huodongguanka"]))

    def goto_jiaohuan(self) -> "Jiaohuan":
        return self.goto(Jiaohuan, self.fun_click(HUODONG_BTN["taofazheng_btn"]))

    def goto_nboss(self) -> "BOSS_FightInfoBase":
        while True:
            a1 = self.img_where_all(img=HUODONG_BTN["nboss"].img, at=(681, 130, 789, 302))
            a2 = self.img_where_all(img=HUODONG_BTN["nboss_en"].img, at=(681, 130, 789, 302))
            a = a1 + a2
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
        return self.goto(BOSS_FightInfoBase, self.fun_click(a[0], a[1]))

    def goto_hboss(self) -> "BOSS_FightInfoBase":
        time.sleep(2)
        while True:
            a1 = self.img_where_all(img=HUODONG_BTN["hboss"].img, at=(681, 130, 789, 302))
            a2 = self.img_where_all(img=HUODONG_BTN["hboss_en"].img, at=(681, 130, 789, 302))
            a = a1 + a2
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
        return self.goto(BOSS_FightInfoBase, self.fun_click(a[0], a[1]))

    def goto_vhboss(self) -> "BOSS_FightInfoBase":
        while True:
            a1 = self.img_where_all(img=HUODONG_BTN["vhboss"].img, at=(681, 130, 789, 302))
            a2 = self.img_where_all(img=HUODONG_BTN["vhboss_en"].img, at=(681, 130, 789, 302))
            a = a1 + a2
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
        return self.goto(BOSS_FightInfoBase, self.fun_click(a[0], a[1]))

    def get_bonus(self):
        if self.check_color(fc=[222, 89, 123], bc=[255, 255, 255], xcor=896, ycor=400, color_type="rgb"):
            self.click_btn(HUODONG_BTN["liwu"], until_appear=HUODONG_BTN["wanchengqingkuang"])
            self.click(344, 22)  # 每日
            time.sleep(0.2)
            self.click(781, 433)  # 收取
            time.sleep(1)
            self.click(478, 468)  # 关闭
            time.sleep(1)

            self.click(547, 22)  # 普通
            time.sleep(0.2)
            self.click(781, 433)  # 收取
            time.sleep(1)
            self.click(478, 468)  # 关闭
            time.sleep(1)

            self.click(710, 22)  # 特别
            time.sleep(0.2)
            self.click(781, 433)  # 收取
            time.sleep(1)
            self.click(478, 468)  # 关闭
            time.sleep(1)

            self.click(860, 22)  # 称号
            time.sleep(0.2)
            self.click(781, 433)  # 收取
            time.sleep(1)
            self.click(478, 468)  # 关闭
            time.sleep(1)


class Jiaohuan(PCRSceneBase):
    def __init__(self, a):
        super().__init__(a)
        self.feature = self.fun_feature_exist(HUODONG_BTN["tfz_bottom"])

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
        obj = self.d.touch.down(868, 270)
        time.sleep(0.1)
        obj.move(868, 120)
        time.sleep(0.8)
        obj.up(868, 120)
        self.click(502, 233)  # 5次后一键
        self.click(724, 352)  # 交换不确认
        time.sleep(0.5)
        self.click(483, 475)  # 关闭

    def exchange_all(self, reset=False):
        time.sleep(0.5)
        a = self.get_taofazheng()
        if a > 1:
            self.click(825, 371)
            time.sleep(2)
            while True:
                out = self.lock_img({
                    HUODONG_BTN["zaicijiaohuan_blue"]: 1,  # 再次交换（没有到碎片）
                    HUODONG_BTN["zaicijiaohuan_white"]: 2,  # 再次交换（到碎片了，在中间）
                    HUODONG_BTN["tfz_bottom"]: 3,  # 换完了，回到交换页了
                    HUODONG_BTN["reset"]: 4,  # 抽干了，重置
                    HUODONG_BTN["reset2"]: 5,  # 两分栏，是讨伐证空了
                    HUODONG_BTN["queren_white"]: 6,  # 换完了，白色确认中间
                    HUODONG_BTN["chakanyihuode"]: 7,  # 换完了，白色确认中间
                    HUODONG_BTN["reset_confirm1"]: 8,  # 选择中途重置的确认

                }, elseclick=(1, 1), timeout=20, is_raise=False)

                if out == 1:
                    self.click(HUODONG_BTN["zaicijiaohuan_blue"])
                    continue
                elif out == 2:
                    if reset is True:
                        self.click(HUODONG_BTN["reset3"])
                        time.sleep(1)
                    else:
                        self.click(HUODONG_BTN["zaicijiaohuan_white"])
                    continue
                elif out == 3:
                    a = self.get_taofazheng()
                    if a > 1:
                        self.click(825, 371)
                        time.sleep(2)
                    else:
                        break
                    continue
                elif out == 4:
                    self.click(HUODONG_BTN["reset"])
                    continue
                elif out == 5:
                    break
                elif out == 6:
                    self.click(HUODONG_BTN["queren_white"])
                    continue
                elif out == 7:
                    self.click(HUODONG_BTN["chakanyihuode"])
                    continue
                elif out == 8:
                    self.click(HUODONG_BTN["reset_confirm1"])
                    time.sleep(1.5)
                    self.click(HUODONG_BTN["reset_confirm2"])
                    time.sleep(1.5)
                    self.fclick(1, 1)
                    continue
                else:
                    self.fclick(1, 1)
                    continue
        else:
            pass

    def goto_menu(self):
        return self.goto(HuodongMenu, self.fun_click(HUODONG_BTN["huodongguanka"]))
