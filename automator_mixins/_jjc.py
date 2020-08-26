import time

from automator_mixins._tools import ToolsMixin


class JJCMixin(ToolsMixin):
    """
    竞技场插片
    包含日常行动相关的脚本
    """

    # 进入jjc
    def enterJJC(self, x, y):
        self.click(480, 505)
        time.sleep(2)
        self.lock_img('img/dixiacheng.jpg')
        self.click(x, y)
        time.sleep(2)
        self.lock_img('img/list.jpg', elseclick=(36, 77), elsedelay=8)

    # 做jjc任务
    def doJJC(self):
        # 以后再改，先用不稳定的苟。
        # 进入jjc
        self.enterJJC(579, 411)

        # 选择第一位进入对战
        self.click(604, 162)
        time.sleep(4)
        # 点击战斗开始
        self.click(822, 456)
        self.lock_img('img/xiayibu.jpg', elsedelay=8, timeout=180)
        self.click(803, 496)
        time.sleep(1)
        self.lock_home()

        # 做pjjc任务

    def doPJJC(self):
        self.enterJJC(821, 410)
        # 选择第一位进入对战
        self.click(604, 162)
        time.sleep(1)
        # 点击队伍2
        self.click(822, 456)
        time.sleep(1)
        # 点击队伍3
        self.click(822, 456)
        time.sleep(1)
        # 点击战斗开始
        self.click(822, 456)
        time.sleep(1)
        # 确保战斗开始
        self.click(822, 456)
        self.lock_img('img/xiayibu.jpg', timeout=180 * 3)
        self.click(803, 506)
        time.sleep(1)
        self.lock_home()
