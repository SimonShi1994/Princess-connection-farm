import time

from core.constant import DXC_BTN, FIGHT_BTN, MAIN_BTN
from core.cv import UIMatcher
from ._fight_base import FightBaseMixin


class DXCBaseMixin(FightBaseMixin):
    """
    地下城基础插片
    包含地下城脚本的基本操作
    """

    def __init__(self):
        super().__init__()
        self.dxc_switch = 0
        self.is_dixiacheng_end = 0  # 地下城是否结束，0未结束，1结束

    def dxczuobiao(self, x, y, auto, speed, bianzu=0, duiwu=0, min_live=5):
        """
        新的地下城刷图函数
        :param x: 屏幕x坐标
        :param y: 屏幕y坐标
        :param auto: 是否开启自动
        :param speed: 是否开启加速
        :param bianzu: 使用编组号,为0时不切换，为-1时使用前五个角色
        :param duiwu: 使用队伍号，为0时不切换，为-1时使用前五个角色
        :param min_live: 至少该队存活min_live人时才刷图，否则不刷
        :return: 刷图情况
            -1: 出现未知的错误
            0：存活人数不足
            1：战胜
            2：战败
        """
        self.wait_for_stable(at=DXC_BTN["map"].at)  # 等待小人走完
        sc = self.getscreen()
        self.click(x, y, pre_delay=0.5, post_delay=0.5)  # 点人
        self.wait_for_change(at=DXC_BTN["shop"].at, screen=sc)  # 商店被遮住了
        sc = self.getscreen()
        self.click(*DXC_BTN["tiaozhan"], pre_delay=0.5, post_delay=0.5)
        self.wait_for_change(at=DXC_BTN["tiaozhan"].at, screen=sc)  # 挑战没了

        # 换队
        if bianzu == -1 and duiwu == -1:
            self.set_fight_team_order()
        elif bianzu != 0 and duiwu != 0:
            self.set_fight_team(bianzu, duiwu)
        # 换队结束
        # 检查存活人数
        live_count = self.get_fight_current_member_count()
        if live_count < min_live:
            return 0
        self.click(*FIGHT_BTN["zhandoukaishi"], pre_delay=0.5, post_delay=3)
        self.set_fight_auto(auto)
        self.set_fight_speed(speed, max_level=2)
        mode = 0
        while mode == 0:
            # 等待战斗结束
            mode = self.get_fight_state()
        if mode == -1:
            print("奇怪的错误")
            return -1
        elif mode == 1:
            # 点击下一步
            self.click(*DXC_BTN["xiayibu"], pre_delay=0.5, post_delay=4)
            self.wait_for_stable()
            self.click(*DXC_BTN["shouqubaochou_ok"], post_delay=2)
            # 处理跳脸：回到地下城界面
            if self.is_exists(DXC_BTN["dxc_kkr"]):
                self.chulijiaocheng(turnback=None)
                if self.is_exists(DXC_BTN["dxc_in_shop"]):
                    self.click(*DXC_BTN["dxc_in_shop"])
                else:
                    # 应急处理：从主页返回
                    self.lockimg(MAIN_BTN["liwu"], elseclick=MAIN_BTN["zhuye"], elsedelay=1)  # 回首页
                    self.click(480, 505, post_delay=1)
                    self.lockimg('img/dixiacheng.jpg', elseclick=(480, 505), elsedelay=1, alldelay=1)
                    self.click(900, 138, post_delay=3)
                    self.lockimg(DXC_BTN["chetui"])  # 锁定撤退

            return 1
        elif mode == 2:
            # 前往地下城
            self.click(*DXC_BTN["qianwangdixiacheng"], post_delay=3)
            return 2

    def dixiachengzuobiao(self, x, y, auto, team=0):
        # 完整刷完地下城函数
        # 参数：
        # x：目标层数的x轴坐标
        # y：目标层数的y轴坐标
        # auto：取值为0/1,auto=0时不点击auto按钮，auto=1时点击auto按钮
        # team：取值为0/1/2，team=0时不换队，team=1时更换为队伍列表中的1队，team=2时更换为队伍列表中的2队
        if self.is_dixiacheng_end:
            return
        else:
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):
                    break
                self.d.click(1, 1)
                time.sleep(1)
            time.sleep(1)
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):
                    break
                self.d.click(1, 1)
                time.sleep(1)
            self.d.click(1, 1)
            time.sleep(3)

            self.d.click(x, y)  # 层数
            time.sleep(2)
            self.d.click(833, 456)  # 挑战
            time.sleep(2)

            while True:  # 锁定战斗开始
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/zhandoukaishi.jpg'):
                    break

            if team != 0:  # 换队
                self.d.click(866, 91)  # 我的队伍
                time.sleep(2)
                if team == 1:
                    self.d.click(792, 172)  # 1队
                elif team == 2:
                    self.d.click(789, 290)  # 2队
                time.sleep(0.5)
                while True:  # 锁定战斗开始
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot_, 'img/zhandoukaishi.jpg'):
                        break
                    time.sleep(0.5)

            self.d.click(837, 447)  # 战斗开始
            time.sleep(2)

            # while True:  # 战斗中快进
            #     screen_shot_ = self.d.screenshot(format="opencv")
            #     if UIMatcher.img_where(screen_shot_, 'img/caidan.jpg'):
            #         if auto == 1:
            #             time.sleep(0.5)
            #             self.d.click(912, 423)  # 点auto按钮
            #             time.sleep(1)
            #         break
            while True:  # 结束战斗返回
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/shanghaibaogao.jpg'):
                    while True:
                        screen_shot = self.d.screenshot(format="opencv")
                        if UIMatcher.img_where(screen_shot, 'img/xiayibu.jpg'):
                            self.d.click(830, 503)
                            break
                        if UIMatcher.img_where(screen_shot, 'img/gotodixiacheng.jpg'):
                            self.is_dixiacheng_end = 1
                            self.d.click(830, 503)
                            break
                    self.d.click(830, 503)  # 点下一步 避免guochang可能失败
                    break
            time.sleep(3)
            self.d.click(1, 1)  # 取消显示结算动画
            time.sleep(1)
