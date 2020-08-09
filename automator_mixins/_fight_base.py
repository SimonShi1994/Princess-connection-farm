import time

import numpy as np

from core.constant import FIGHT_BTN, MAIN_BTN
from core.cv import UIMatcher
from pcr_config import debug
from ._tools import ToolsMixin


class FightBaseMixin(ToolsMixin):
    """
    战斗基础插片
    包括与战斗相关的基本操作
    """

    def get_fight_state(self, screen=None, max_retry=3, delay=1) -> int:
        """
        获取战斗状态
        注：不适用竞技场的战斗！
        :param: screen 第一次检测用的截图
        :param max_retry: 最大重试次数
        :return:
            -1：未知状态
            0： 战斗进行中
            1： 战斗胜利
            2： 战斗失败
        """
        for retry in range(max_retry):
            if screen is None:
                sc = self.getscreen()
            else:
                sc = screen
                screen = None
            if self.is_exists(FIGHT_BTN["shbg"], screen=sc):
                # 出现伤害报告，战斗结束 （地下城）
                if self.is_exists(FIGHT_BTN["qwjsyl"], screen=sc):
                    # 前往角色一览：失败
                    return 2
                elif self.is_exists(FIGHT_BTN["win"], screen=sc):
                    # 找到帽子：成功
                    return 1
                elif self.is_exists(FIGHT_BTN["xiayibu"], screen=sc):
                    # 右下角有长的下一步，但是没找到帽子：点掉它
                    self.click_btn(FIGHT_BTN["xiayibu"])
                    return 1
                else:
                    time.sleep(1)
                    continue
            elif self.is_exists(FIGHT_BTN["menu"], screen=sc, threshold=0.95):
                # 右上角有菜单，说明战斗还未结束
                return 0
            elif self.is_exists(FIGHT_BTN["xiayibu2"], screen=sc):
                # 右下角短的下一步：说明战斗胜利
                return 1
            elif self.is_exists(MAIN_BTN["tiaoguo"], screen=sc):
                # 检测到右上角跳过：点击 （羁绊剧情）
                self.click(MAIN_BTN["tiaoguo"])
            else:
                self.click(471, 5)  # 避免奇怪的对话框
                time.sleep(delay)
                continue
        return -1

    def get_fight_speed(self, screen=None, max_retry=3) -> int:
        """
        获取速度等级
        :param: screen 第一次检测用的截图
        :param max_retry: 最大重试次数
        :return:
            -1：检测失败
            0，1，2：原速、两倍速、三倍速
        """
        retry = 0
        while retry <= max_retry:
            retry += 1
            if screen is None:
                sc = self.getscreen()
            else:
                sc = screen
                screen = None
            state = self.get_fight_state(sc, max_retry=1)
            if state == -1:
                continue
            elif state in [1, 2]:
                return -1

            p0 = self.img_prob(FIGHT_BTN["speed_0"], screen=sc)
            p1 = self.img_prob(FIGHT_BTN["speed_1"], screen=sc)
            p2 = self.img_prob(FIGHT_BTN["speed_2"], screen=sc)
            probs = np.array([p0, p1, p2])
            if probs.max() < 0.84:
                continue
            else:
                return probs.argmax()
        return -1

    def set_fight_speed(self, level, max_level=1, screen=None, max_retry=3) -> bool:
        """
        调节速度等级
        :param level: 0,1,2。0：正常速，1：两倍速，2：三倍速
        :param max_level: 最大可以调节的速度,默认1（两倍速）
        :param: screen 第一次检测用的截图
        :param max_retry: 最大重试次数
        :return:
            True 设置成功
            False 可能未设置成功
        """
        retry = 0
        while retry <= max_retry:
            retry += 1
            if screen is None:
                sc = self.getscreen()
            else:
                sc = screen
                screen = None
            speed = self.get_fight_speed(sc)
            if speed == -1:
                return False
            else:
                # 获取速度成功
                if speed != level:
                    while speed != level:
                        speed = (speed + 1) % (max_level + 1)
                        self.click(FIGHT_BTN["speed_0"])
                    # 检查设置情况
                    time.sleep(0.2)
                    speed = self.get_fight_speed()
                    if speed == -1:
                        return False
                    elif speed == level:
                        # 设置成功
                        return True
                    else:
                        continue
                else:
                    return True
        # 超过最大尝试次数
        return False

    def get_fight_auto(self, screen=None, max_retry=3) -> int:
        """
        获取当前是否开着自动
        :param: screen 第一次检测用的截图
        :param max_retry: 最大重试次数
        :return:
            -1：识别失败
            0：未开
            1：开了
        """
        retry = 0
        while retry <= max_retry:
            retry += 1
            if screen is None:
                sc = self.getscreen()
            else:
                sc = screen
                screen = None
            state = self.get_fight_state(sc, max_retry=1)
            if state == -1:
                continue
            elif state in [1, 2]:
                return -1
            p0 = self.img_prob(FIGHT_BTN["auto_off"], screen=sc)
            p1 = self.img_prob(FIGHT_BTN["auto_on"], screen=sc)
            probs = np.array([p0, p1])
            if probs.max() < 0.84:
                continue
            else:
                return probs.argmax()
        return -1

    def set_fight_auto(self, auto, screen=None, max_retry=3) -> bool:
        """
        调节auto开关
        :param auto: 0：关闭 1：开启
        :param: screen 第一次检测用的截图
        :param max_retry: 最大重试次数
        :return:
            True 设置成功
            False 可能未设置成功
        """
        retry = 0
        while retry <= max_retry:
            retry += 1
            if screen is None:
                sc = self.getscreen()
            else:
                sc = screen
                screen = None
            cur = self.get_fight_auto(sc)
            if cur == -1:
                return False
            else:
                if cur != auto:
                    self.click(FIGHT_BTN["auto_off"])
                    # 检查设置情况
                    time.sleep(0.2)
                    cur = self.get_fight_auto()
                    if cur == -1:
                        return False
                    elif cur == auto:
                        # 设置成功
                        return True
                    else:
                        continue
                else:
                    return True
        # 超过最大尝试次数
        return False

    def set_fight_team(self, bianzu, duiwu):
        """
        设置战斗队伍
        要求场景：处于”队伍编组“情况下。
        :param bianzu: 编组编号1~5
        :param duiwu: 队伍编号1~3
        """
        assert bianzu in [1, 2, 3, 4, 5]
        assert duiwu in [1, 2, 3]
        self.click_btn(FIGHT_BTN["my_team"], until_disappear=FIGHT_BTN["zhandoukaishi"])
        self.click(FIGHT_BTN["team_h"][bianzu], pre_delay=1, post_delay=1)
        self.click(FIGHT_BTN["team_v"][duiwu], pre_delay=1, post_delay=1)

    def get_fight_current_member_count(self, screen=None):
        """
        获取”当前的成员"的数量
        要求场景：处于”队伍编组“情况下。
        :return: int 0~5
        """
        count_live = 5
        if screen is None:
            sc = self.getscreen()
        else:
            sc = screen
        for i in range(1, 6):
            cur = UIMatcher.img_cut(sc, FIGHT_BTN["empty"][i].at)
            if debug:
                print("std: ", i, cur.std())
            if cur.std() <= 15:
                count_live -= 1
        return count_live

    def set_fight_team_order(self):
        """
        按照战力顺序设置战斗队伍
        要求场景：处于”队伍编组“情况下。
        """
        sc = self.getscreen()
        p0 = self.img_prob(FIGHT_BTN["sort_up"], screen=sc)
        p1 = self.img_prob(FIGHT_BTN["sort_down"], screen=sc)
        if p0 > p1:
            # 升序改降序
            self.click(FIGHT_BTN["sort_up"], pre_delay=0.5, post_delay=1)
        if not self.is_exists(FIGHT_BTN["sort_power"], screen=sc):
            self.click(FIGHT_BTN["sort_power"], pre_delay=0.5, post_delay=1)
            self.click(FIGHT_BTN["cat_zhanli"], pre_delay=0.5, post_delay=1)
            self.click(FIGHT_BTN["cat_ok"], pre_delay=0.5, post_delay=1)
        # 换人
        for _ in range(5):
            self.click(FIGHT_BTN["empty"][1], post_delay=0.5)
        for i in range(5):
            self.click(FIGHT_BTN["first_five"][i + 1], post_delay=0.5)

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
