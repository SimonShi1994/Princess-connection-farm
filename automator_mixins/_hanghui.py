import time

from core.constant import MAIN_BTN, HANGHUI_BTN

from core.cv import UIMatcher
from core.log_handler import pcr_log
from ._tools import ToolsMixin


class HanghuiMixin(ToolsMixin):
    """
    行会插片。
    包含行会相关的脚本。
    """

    def hanghui(self):
        """
        行会自动捐赠装备
        2020/8/6 By:CyiceK 检查完毕
        """
        self.find_img('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        # self.d.click(693, 436)
        self.find_img('img/hanghui.bmp', elseclick=[(693, 436)], elsedelay=2)  # 锁定进入行会
        while True:  # 6-17修改：减少opencv使用量提高稳定性
            if self.is_exists('img/zhiyuansheding.bmp'):
                time.sleep(3)  # 加载行会聊天界面会有延迟
                self.lock_no_img('img/juanzengqingqiu.jpg', elseclick=[(367, 39)], retry=1)
                for _ in range(5):
                    time.sleep(0.8)
                    if self.is_exists('img/juanzeng.jpg', threshold=0.90):
                        screen_shot = self.getscreen()
                        self.click_img(screen_shot, 'img/juanzeng.jpg')
                        # 点击max 后 ok
                        time.sleep(2)
                        self.lock_no_img('img/max.jpg', elseclick=[(644, 385), (552, 470)], elsedelay=1, retry=20)
                        if self.is_exists('img/ok.bmp', threshold=0.90):
                            self.lock_no_img('img/ok.bmp', elseclick=[(494, 368)], retry=4)
                        self.lock_no_img('img/zhandou_ok.jpg', elseclick=[(536, 361)], retry=3)
                        self.lock_no_img('img/juanzengqingqiu.jpg', elseclick=[(367, 39)], retry=1)
                    else:
                        self.lock_no_img('img/juanzengqingqiu.jpg', elseclick=[(367, 39)], elsedelay=1, retry=1)
                    # self.lock_img('img/juanzengqingqiu.jpg', ifclick=[(367, 39)], retry=2)
                    # screen_shot = self.getscreen()
                    # if UIMatcher.img_where(screen_shot, 'img/juanzengqingqiu.jpg'):
                    #    self.click(367, 39, post_delay=2)  # 点击定位捐赠按钮
                    #    screen_shot = self.getscreen()
                    #    self.guochang(screen_shot, ['img/juanzeng.jpg'], suiji=0)
                    #    self.click(644, 385, pre_delay=1, post_delay=3)  # 点击max
                    #    screen_shot = self.getscreen()
                    #    self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    #    self.click(560, 369, pre_delay=2, post_delay=1)
                while True:
                    self.click(1, 1, post_delay=1)
                    if self.is_exists('img/zhiyuansheding.bmp'):
                        break
                break
            time.sleep(2)
            # 处理多开捐赠失败的情况
            screen_shot = self.getscreen()
            self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
            self.click(1, 1, post_delay=1)  # 处理被点赞的情况

        self.click(100, 505, post_delay=1)  # 回到首页
        self.find_img('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    def tichuhanghui(self):  # 踢出行会
        self.lock_home()
        # 进入
        self.click_btn(MAIN_BTN["hanghui"], elsedelay=1, until_appear=HANGHUI_BTN["hanghui_title"])
        # 管理界面
        self.click_btn(HANGHUI_BTN["chengyuanxinxi"], elsedelay=1, until_appear=HANGHUI_BTN["shaixuantiaojian"])
        # 筛选全角色战力
        self.click_btn(HANGHUI_BTN["shaixuantiaojian"],elsedelay=1,until_appear=HANGHUI_BTN["fenlei"])
        self.click_btn(HANGHUI_BTN["quanjuesezhanli"],elsedelay=1,until_appear=HANGHUI_BTN["quanjuesezhanli"])
        self.click_btn(HANGHUI_BTN["hanghui_ok"],elsedelay=1)
        # 降序排列
        self.lock_img(HANGHUI_BTN["jiangxu"],elseclick=HANGHUI_BTN["jiangxu"])
        # 踢出第一
        self.click_btn(HANGHUI_BTN["chengyuanguanli_first"],elsedelay=1,until_appear=HANGHUI_BTN["kaichu"])
        self.click_btn(HANGHUI_BTN["kaichu"],elsedelay=1,until_appear=HANGHUI_BTN["hanghui_ok"])
        self.click_btn(HANGHUI_BTN["hanghui_ok"])
        # 返回
        self.lock_home()

    def yaoqinghanghui(self, inviteUID):  # 邀请行会
        self.click(693, 430)  # 点击行会
        self.lock_img('img/zhiyuansheding.bmp', elseclick=[(1, 1)], alldelay=0.5)  # 锁定行会界面
        self.click(241, 350)  # 点击成员
        self.lock_img('img/chengyuanliebiao.bmp', ifclick=[(717, 33)], ifdelay=1)  # 点击搜索成员
        self.lock_img('img/sousuochengyuan.bmp', ifclick=[(845, 90)], ifdelay=1)  # 点击搜索设定
        self.lock_img('img/ok.bmp', ifclick=[(487, 236)], ifdelay=1)  # 点击输入框
        self.d.send_keys(inviteUID)
        time.sleep(1)
        self.click(1, 1)
        self.lock_img('img/ok.bmp', ifclick=[(585, 366)], ifdelay=1)  # 点击ok
        self.lock_img('img/sousuochengyuan.bmp', ifclick=[(844, 181)], ifdelay=1)  # 点击邀请
        self.lock_img('img/ok.bmp', ifclick=[(588, 439)], ifdelay=1)  # 点击ok
        self.lock_img('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=0.5, at=(891, 413, 930, 452))  # 回首页

    def jieshouhanghui(self):
        self.click(693, 430)  # 点击行会
        self.lock_img('img/zujianhanghui.bmp', elseclick=[(1, 1)], alldelay=0.5)  # 锁定行会界面
        self.click(687, 35)  # 点击邀请列表
        time.sleep(1)
        self.click(704, 170)  # 点击邀请列表
        self.lock_img('img/jiaru.bmp', ifclick=[(839, 443)], ifdelay=1)  # 点击加入
        self.lock_img('img/ok.bmp', ifclick=[(597, 372)], ifdelay=1)  # 点击ok
        time.sleep(1)
        self.lock_img('img/ok.jpg')  # 锁定ok
        screen_shot_ = self.getscreen()
        self.guochang(screen_shot_, ['img/ok.jpg'], suiji=0)
        self.lock_img('img/zhiyuansheding.bmp', ifclick=[(85, 350)], alldelay=0.5)  # 点击支援设定
        self.lock_img('img/zhiyuanjiemian.bmp', elseclick=[(1, 1)], alldelay=0.5)  # 锁定支援界面
        self.click(109, 234)  # 点击支援
        time.sleep(1)
        self.lock_img('img/quxiao3.bmp', ifclick=[(739, 91)], ifdelay=1)  # 点击排序设定
        self.lock_img('img/ok.bmp', ifclick=[(291, 142), (588, 483)], ifdelay=1)  # 点击战力和ok
        self.lock_img('img/quxiao3.bmp', ifclick=[(109, 175)], ifdelay=1)  # 点击第一个人
        time.sleep(1)
        self.click(833, 456)  # 点击设定
        self.lock_img('img/ok.bmp', ifclick=[(591, 440)], ifdelay=1)  # 点击ok

        self.lock_img('img/zhiyuanjiemian.bmp', ifclick=[(105, 356)], ifdelay=1)  # 点击第二个+号
        self.lock_img('img/quxiao3.bmp', ifclick=[(109, 175)], ifdelay=1)  # 点击第一个人
        time.sleep(1)
        self.click(833, 456)  # 点击设定
        self.lock_img('img/ok.bmp', ifclick=[(591, 440)], ifdelay=1)  # 点击ok
        self.lock_img('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=0.5, at=(891, 413, 930, 452))  # 回首页

    def joinhanghui(self, clubname):  # 小号加入行会
        print('>>>>>>>即将加入公会名为：', clubname, '<<<<<<<')
        self.click(693, 430)  # 点击行会
        self.lock_img('img/zujianhanghui.bmp', elseclick=[(1, 1)], alldelay=0.5)  # 锁定行会界面
        time.sleep(1)
        self.lock_img('img/zujianhanghui.bmp', elseclick=[(1, 1)], alldelay=0.5)  # 锁定行会界面
        self.click(860, 81)  # 点击设定
        self.lock_img('img/quxiao2.jpg', ifclick=[(477, 177)], ifdelay=1)  # 点击输入框
        self.d.send_keys(clubname)
        time.sleep(1)
        self.click(1, 1)
        time.sleep(1)
        self.click(587, 432)
        time.sleep(5)
        self.click(720, 172)
        time.sleep(1)
        self.lock_img('img/jiaru.bmp', ifclick=[(839, 443)], ifdelay=1)  # 点击加入
        self.lock_img('img/ok.jpg', ifclick=[(597, 372)], ifdelay=1)  # 点击ok
        self.lock_img('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=0.5, at=(891, 413, 930, 452))  # 回首页

    def dianzan(self, sortflag=0):
        """
        2020/8/6 By:CyiceK 检查完毕
        :param sortflag:
        :return:
        """
        # 行会点赞
        self.lock_home()
        # 进入行会
        self.lock_img('img/zhiyuansheding.bmp', ifclick=[(230, 351)], elseclick=[(688, 432)], elsedelay=3, retry=10)
        self.lock_no_img('img/zhandou_ok.jpg', elseclick=[(239, 351)], retry=5)
        if sortflag == 1:
            self.lock_img('img/ok.bmp', elseclick=[(720, 97)], retry=3)  # 点击排序
            self.lock_no_img('img/ok.bmp', elseclick=[(289, 303), (587, 372)], elsedelay=1, retry=3)  # 按战力降序 这里可以加一步调降序
            self.lock_img('img/dianzan.bmp', ifclick=[(818, 198), (480, 374), (826, 316), (480, 374), (826, 428)]
                          , elseclick=[(1, 1)], elsedelay=3, ifdelay=1, retry=10)
            # 点赞 战力降序第一/第二/第三个人
            # (480, 374) 是ok的坐标
        else:
            self.lock_img('img/dianzan.bmp', ifclick=[(829, 316), (480, 374), (826, 428)], elseclick=[(1, 1)],
                          elsedelay=3, ifdelay=1, retry=10)
            # 点赞 职务降序（默认） 第二/第三个人，副会长
        self.click(479, 381)
        screen_shot_ = self.getscreen()
        self.click_img(screen_shot_, 'img/ok.bmp')
        self.lock_img('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
