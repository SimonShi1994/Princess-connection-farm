import time

from core.cv import UIMatcher
from ._base import BaseMixin


class HanghuiMixin(BaseMixin):
    """
    行会插片。
    包含行会相关的脚本。
    """

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
                for _ in range(2):
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

    def tichuhanghui(self):  # 踢出行会
        self.d.click(693, 430)  # 点击行会
        self.lockimg('img/zhiyuansheding.bmp', elseclick=[(1, 1)], alldelay=0.5)  # 锁定行会界面
        self.d.click(241, 350)  # 点击成员
        self.lockimg('img/chengyuanliebiao.bmp', ifclick=[(720, 97)], ifdelay=1)  # 点击排序按钮
        self.lockimg('img/ok.bmp', ifclick=[(289, 303), (587, 372)], ifdelay=1)  # 按战力降序 这里可以加一步调降序
        self.lockimg('img/chengyuanliebiao.bmp', ifclick=[(737, 200)], ifdelay=1)  # 点第一个人
        self.lockimg('img/jiaojie.bmp', ifclick=[(651, 174)], ifdelay=1)  # 踢出行会
        self.lockimg('img/ok.bmp', ifclick=[(590, 369)], ifdelay=1)  # 确认踢出
        self.lockimg('img/chengyuanliebiao.bmp', elseclick=[(1, 1)], alldelay=1)  # 锁定成员列表
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=0.5, at=(891, 413, 930, 452))  # 回首页

    def yaoqinghanghui(self, inviteUID):  # 邀请行会
        self.d.click(693, 430)  # 点击行会
        self.lockimg('img/zhiyuansheding.bmp', elseclick=[(1, 1)], alldelay=0.5)  # 锁定行会界面
        self.d.click(241, 350)  # 点击成员
        self.lockimg('img/chengyuanliebiao.bmp', ifclick=[(717, 33)], ifdelay=1)  # 点击搜索成员
        self.lockimg('img/sousuochengyuan.bmp', ifclick=[(845, 90)], ifdelay=1)  # 点击搜索设定
        self.lockimg('img/ok.bmp', ifclick=[(487, 236)], ifdelay=1)  # 点击输入框
        self.d.send_keys(inviteUID)
        time.sleep(1)
        self.d.click(1, 1)
        self.lockimg('img/ok.bmp', ifclick=[(585, 366)], ifdelay=1)  # 点击ok
        self.lockimg('img/sousuochengyuan.bmp', ifclick=[(844, 181)], ifdelay=1)  # 点击邀请
        self.lockimg('img/ok.bmp', ifclick=[(588, 439)], ifdelay=1)  # 点击ok
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=0.5, at=(891, 413, 930, 452))  # 回首页

    def jieshouhanghui(self):
        self.d.click(693, 430)  # 点击行会
        self.lockimg('img/zujianhanghui.bmp', elseclick=[(1, 1)], alldelay=0.5)  # 锁定行会界面
        self.d.click(687, 35)  # 点击邀请列表
        time.sleep(1)
        self.d.click(704, 170)  # 点击邀请列表
        self.lockimg('img/jiaru.bmp', ifclick=[(839, 443)], ifdelay=1)  # 点击加入
        self.lockimg('img/ok.bmp', ifclick=[(597, 372)], ifdelay=1)  # 点击ok
        time.sleep(1)
        self.lockimg('img/ok.jpg')  # 锁定ok
        screen_shot_ = self.d.screenshot(format="opencv")
        self.guochang(screen_shot_, ['img/ok.jpg'], suiji=0)
        self.lockimg('img/zhiyuansheding.bmp', ifclick=[(85, 350)], alldelay=0.5)  # 点击支援设定
        self.lockimg('img/zhiyuanjiemian.bmp', elseclick=[(1, 1)], alldelay=0.5)  # 锁定支援界面
        self.d.click(109, 234)  # 点击支援
        time.sleep(1)
        self.lockimg('img/quxiao3.bmp', ifclick=[(739, 91)], ifdelay=1)  # 点击排序设定
        self.lockimg('img/ok.bmp', ifclick=[(291, 142), (588, 483)], ifdelay=1)  # 点击战力和ok
        self.lockimg('img/quxiao3.bmp', ifclick=[(109, 175)], ifdelay=1)  # 点击第一个人
        time.sleep(1)
        self.d.click(833, 456)  # 点击设定
        self.lockimg('img/ok.bmp', ifclick=[(591, 440)], ifdelay=1)  # 点击ok

        self.lockimg('img/zhiyuanjiemian.bmp', ifclick=[(105, 356)], ifdelay=1)  # 点击第二个+号
        self.lockimg('img/quxiao3.bmp', ifclick=[(109, 175)], ifdelay=1)  # 点击第一个人
        time.sleep(1)
        self.d.click(833, 456)  # 点击设定
        self.lockimg('img/ok.bmp', ifclick=[(591, 440)], ifdelay=1)  # 点击ok
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=0.5, at=(891, 413, 930, 452))  # 回首页

    def joinhanghui(self, clubname):  # 小号加入行会
        print('>>>>>>>即将加入公会名为：', clubname, '<<<<<<<')
        self.d.click(693, 430)  # 点击行会
        self.lockimg('img/zujianhanghui.bmp', elseclick=[(1, 1)], alldelay=0.5)  # 锁定行会界面
        time.sleep(1)
        self.lockimg('img/zujianhanghui.bmp', elseclick=[(1, 1)], alldelay=0.5)  # 锁定行会界面
        self.d.click(860, 81)  # 点击设定
        self.lockimg('img/quxiao2.jpg', ifclick=[(477, 177)], ifdelay=1)  # 点击输入框
        self.d.send_keys(clubname)
        time.sleep(1)
        self.d.click(1, 1)
        time.sleep(1)
        self.d.click(587, 432)
        time.sleep(5)
        self.d.click(720, 172)
        time.sleep(1)
        self.lockimg('img/jiaru.bmp', ifclick=[(839, 443)], ifdelay=1)  # 点击加入
        self.lockimg('img/ok.jpg', ifclick=[(597, 372)], ifdelay=1)  # 点击ok
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=0.5, at=(891, 413, 930, 452))  # 回首页

    def dianzan(self, sortflag=0):  # 行会点赞
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        # 进入行会
        self.d.click(688, 432)
        time.sleep(3)
        for i in range(2):
            time.sleep(3)
            screen_shot_ = self.d.screenshot(format="opencv")
            self.guochang(screen_shot_, ['img/zhandou_ok.jpg'], suiji=0)
        self.d.click(239, 351)
        time.sleep(3)
        if sortflag == 1:
            self.d.click(720, 97)  # 点击排序
            if not self.lockimg('img/ok.bmp', elsedelay=1, ifclick=[(289, 303), (587, 372)], ifdelay=1,
                                retry=5):  # 按战力降序 这里可以加一步调降序
                # 如果没有加入公会则返回
                print("这个账号看起来并没有加入公会")
                self.lockimg('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=1,
                             at=(891, 413, 930, 452))  # 回首页
                return
            self.d.click(818, 198)  # 点赞 战力降序第一个人
            time.sleep(2)
        else:
            self.d.click(829, 316)  # 点赞 职务降序（默认） 第二个人，副会长
            time.sleep(2)
        self.d.click(479, 381)
        screen_shot_ = self.d.screenshot(format="opencv")
        self.guochang(screen_shot_, ['img/ok.bmp'], suiji=0)
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
