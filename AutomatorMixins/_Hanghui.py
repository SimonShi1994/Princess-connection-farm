import time
from cv import UIMatcher
from ._Base import BaseMixin

class HanghuiMixin(BaseMixin):
    def hanghui(self):
        """
        行会自动捐赠装备
        """
        self.find_img('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        time.sleep(1)
        # self.d.click(693, 436)
        self.find_img('img/hanghui.bmp', elseclick=[(693, 436)], elsedelay=1)  # 锁定进入行会
        time.sleep(1)
        while True:  # 6-17修改：减少opencv使用量提高稳定性
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/zhiyuansheding.bmp'):
                time.sleep(3)  # 加载行会聊天界面会有延迟
                for _ in range(5):
                    time.sleep(2)
                    screen_shot = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot, 'img/juanzengqingqiu.jpg'):
                        self.click(367, 39, post_delay=2)  # 点击定位捐赠按钮
                        screen_shot = self.d.screenshot(format="opencv")
                        self.guochang(screen_shot, ['img/juanzeng.jpg'], suiji=0)
                        self.click(644, 385, pre_delay=1, post_delay=3)  # 点击max
                        screen_shot = self.d.screenshot(format="opencv")
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                        self.click(560, 369, pre_delay=2, post_delay=1)
                while True:
                    self.click(1, 1, post_delay=1)
                    screen_shot = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot, 'img/zhiyuansheding.bmp'):
                        break
                break
            time.sleep(2)
            # 处理多开捐赠失败的情况
            screen_shot = self.d.screenshot(format="opencv")
            self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
            self.click(1, 1, post_delay=1)  # 处理被点赞的情况

        self.click(100, 505, post_delay=1)  # 回到首页
        self.find_img('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页