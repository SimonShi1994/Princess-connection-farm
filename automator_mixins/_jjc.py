import time

from automator_mixins._tools import ToolsMixin
from core.cv import UIMatcher


class JJCMixin(ToolsMixin):
    """
    竞技场插片
    包含日常行动相关的脚本
    """

    # 进入jjc
    def enterJJC(self, x, y):
        self.click(480, 505)
        time.sleep(2)
        while True:
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
        self.click(x, y)
        time.sleep(2)
        while True:
            screen_shot_ = self.getscreen()
            self.click(36, 77)
            if UIMatcher.img_where(screen_shot_, 'img/list.jpg'):
                break

    # 做jjc任务
    def doJJC(self):
        # 进入jjc
        self.enterJJC(579, 411)

        # 选择第一位进入对战
        self.click(604, 162)
        time.sleep(1)
        # 点击战斗开始
        self.click(822, 456)

        while True:
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/xiayibu.jpg'):
                self.click(803, 496)
                break
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

        while True:
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/xiayibu.jpg'):
                self.click(803, 506)
                break
        time.sleep(1)
        self.lock_home()
