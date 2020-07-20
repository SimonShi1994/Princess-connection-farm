import time

from core.cv import UIMatcher
from ._base import BaseMixin


class DXCBaseMixin(BaseMixin):
    """
    地下城基础插片
    包含地下城脚本的基本操作
    """

    def __init__(self):
        super().__init__()
        self.dxc_switch = 0
        self.is_dixiacheng_end = 0  # 地下城是否结束，0未结束，1结束

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
