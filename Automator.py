# coding=utf-8
import time
from utils import *
import uiautomator2 as u2
import asyncio
from cv import *
import tkinter
import threading
from tkinter import ttk
from log_handler import *


# import matplotlib.pylab as plt


class Automator:
    def __init__(self, address, account, auto_task=False, auto_policy=True,
                 auto_goods=False, speedup=True):
        """
        device: 如果是 USB 连接，则为 adb devices 的返回结果；如果是模拟器，则为模拟器的控制 URL 。
        """
        self.d = u2.connect(address)
        self.dWidth, self.dHeight = self.d.window_size()
        self.appRunning = False
        self.account = account
        self.switch = 0
        self.dxc_switch = 0
        self.times = 3  # 总刷图次数
        self.is_dixiacheng_end = 0 # 地下城是否结束，0未结束，1结束

    def start(self):
        """
        启动脚本，请确保已进入游戏页面。
        """
        while True:
            # 判断jgm进程是否在前台, 最多等待20秒，否则唤醒到前台
            if self.d.app_wait("com.bilibili.priconne", front=True, timeout=1):
                if not self.appRunning:
                    # 从后台换到前台，留一点反应时间
                    time.sleep(1)
                self.appRunning = True
                break
            else:
                self.app = self.d.session("com.bilibili.priconne")
                self.appRunning = False
                continue
        self.dWidth, self.dHeight = self.d.window_size()

    def login(self, ac, pwd):
        while True:
            if self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_id_welcome_change").exists():
                self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_id_welcome_change").click()
            if self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_username_login").exists():
                self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_username_login").click()
                break
            else:
                self.d.click(self.dWidth * 0.965, self.dHeight * 0.029)
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_username_login").click()
        self.d.clear_text()
        self.d.send_keys(str(ac))
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_password_login").click()
        self.d.clear_text()
        self.d.send_keys(str(pwd))
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_buttonLogin").click()
        time.sleep(5)
        if self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_authentication_name").exists(timeout=0.1):
            return 1  # 说明要进行认证
        else:
            return 0  # 正常

    def auth(self, auth_name, auth_id):
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_authentication_name").click()
        self.d.clear_text()
        self.d.send_keys(str(auth_name))
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_authentication_id_number").click()
        self.d.clear_text()
        self.d.send_keys(str(auth_id))
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_authentication_submit").click()
        self.d(resourceId="com.bilibili.priconne:id/bagamesdk_auth_success_comfirm").click()

    def guochang(self, screen_shot, template_paths, suiji=1):
        # suji标号置1, 表示未找到时将点击左上角, 置0则不点击
        # 输入截图, 模板list, 得到下一次操作

        self.dWidth, self.dHeight = self.d.window_size()
        screen_shot = screen_shot
        template_paths = template_paths
        active_path = UIMatcher.imgs_where(screen_shot, template_paths)
        if active_path:
            print(active_path)
            if 'img/caidan_tiaoguo.jpg' in active_path:
                x, y = active_path['img/caidan_tiaoguo.jpg']
                self.d.click(x, y)
            else:
                for name, (x, y) in active_path.items():
                    print(name)
                    self.d.click(x, y)
            time.sleep(0.5)
        else:
            if suiji:
                print('未找到所需的按钮,将点击左上角')
                self.d.click(0.1 * self.dWidth, 0.1 * self.dHeight)
            else:
                print('未找到所需的按钮,无动作')

    def click(self, screen, img, threshold=0.84, at=None):
        """
        try to click the img
        :param screen:
        :param threshold:
        :param img:
        :return: success
        """
        position = UIMatcher.img_where(screen, img, threshold, at)
        if position:
            self.d.click(*position)
            return True
        else:
            return False

    def lockimg(self, img, ifclick=[], ifbefore=0.5, ifdelay=1, elseclick=[], elsedelay=0.5, alldelay=0.5, retry=0,
                at=None):
        """
        @args:
            img:要匹配的图片目录
            ifbefore:识别成功后延迟点击时间
            ifclick:在识别到图片时要点击的坐标，列表，列表元素为坐标如(1,1)
            ifdelay:上述点击后延迟的时间
            elseclick:在找不到图片时要点击的坐标，列表，列表元素为坐标如(1,1)
            elsedelay:上述点击后延迟的时间
            retry:elseclick最多点击次数，0为无限次
        @return:是否在retry次内点击成功
        """
        # 2020-07-12 Add: 增加了ifclick,elseclick参数对Tuple的兼容性
        # 2020-07-14 Add: added retry
        if type(ifclick) is tuple:
            ifclick = [ifclick]
        if type(elseclick) is tuple:
            elseclick = [elseclick]

        attempt = 0
        while True:
            screen_shot = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot, img, at=at):
                if ifclick != []:
                    for clicks in ifclick:
                        time.sleep(ifbefore)
                        self.d.click(clicks[0], clicks[1])
                        time.sleep(ifdelay)
                break
            if elseclick != []:
                for clicks in elseclick:
                    self.d.click(clicks[0], clicks[1])
                    time.sleep(elsedelay)
            time.sleep(alldelay)
            attempt += 1
            if retry != 0 and attempt >= retry:
                return False
        return True

    def lock_no_img(self, img, ifclick=[], ifbefore=0.5, ifdelay=1, elseclick=[], elsedelay=0.5, alldelay=0.5,
                    retry=0, at=None):  # 锁定指定图像
        """
        @args:
            img:要匹配的图片目录
            ifbefore:识别成功后延迟点击时间
            ifclick:在识别不到图片时要点击的坐标，列表，列表元素为坐标如(1,1)
            ifdelay:上述点击后延迟的时间
            elseclick:在找到图片时要点击的坐标，列表，列表元素为坐标如(1,1)
            retry:elseclick最多点击次数，0为无限次
        @return:是否在retry次内点击成功
        """
        # 2020-07-13 Added By Dr-Blueomnd
        if type(ifclick) is tuple:
            ifclick = [ifclick]
        if type(elseclick) is tuple:
            elseclick = [elseclick]

        attempt = 0
        while True:
            screen_shot = self.d.screenshot(format="opencv")
            if not UIMatcher.img_where(screen_shot, img, at=at):
                if ifclick != []:
                    for clicks in ifclick:
                        time.sleep(ifbefore)
                        self.d.click(clicks[0], clicks[1])
                        time.sleep(ifdelay)
                break
            if elseclick != []:
                for clicks in elseclick:
                    self.d.click(clicks[0], clicks[1])
                    time.sleep(elsedelay)
            time.sleep(alldelay)
            attempt += 1
            if retry != 0 and attempt >= retry:
                return False
        return True

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

    def login_auth(self, ac, pwd):
        need_auth = self.login(ac=ac, pwd=pwd)
        if need_auth:
            auth_name, auth_id = random_name(), CreatIDnum()
            self.auth(auth_name=auth_name, auth_id=auth_id)

    def init_home(self):
        while True:
            screen = self.d.screenshot(format='opencv')
            if UIMatcher.img_where(screen, 'img/liwu.bmp', at=(891, 413, 930, 452)):
                break
            if UIMatcher.img_where(screen, 'img/niudan_jiasu.jpg', at=(700, 0, 960, 100)):
                self.d.click(893, 39)  # 跳过
                time.sleep(0.5)
                continue
            if UIMatcher.img_where(screen, 'img/jingsaikaishi.bmp', at=(755, 471, 922, 512)):
                self.d.click(786, 308)  # 选角色
                time.sleep(0.2)
                self.d.click(842, 491)  # 开始
                time.sleep(0.5)
                continue
            self.d.click(1, 1)
            time.sleep(0.3)

        self.lockimg('img/liwu.bmp', elseclick=[(1, 1)], elsedelay=0.2, at=(891, 413, 930, 452))  # 首页锁定
        time.sleep(0.5)
        # 这里防一波第二天可可萝跳脸教程
        screen_shot_ = self.d.screenshot(format='opencv')
        num_of_white, _, _ = UIMatcher.find_gaoliang(screen_shot_)
        if num_of_white < 50000:
            self.lockimg('img/renwu_1.bmp', elseclick=[(837, 433)], elsedelay=1)
            self.lockimg('img/liwu.bmp', elseclick=[(90, 514)], elsedelay=0.2, at=(891, 413, 930, 452))
            return
        if UIMatcher.img_where(screen_shot_, 'img/kekeluo.bmp'):
            self.lockimg('img/renwu_1.bmp', elseclick=[(837, 433)], elsedelay=1)
            self.lockimg('img/liwu.bmp', elseclick=[(90, 514)], elsedelay=0.2, at=(891, 413, 930, 452))

    def sw_init(self):
        self.switch = 0

    def gonghuizhijia(self):  # 家园领取
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        self.lockimg('img/jyquanbushouqu.jpg', elseclick=[(622, 509)], elsedelay=1)
        self.lockimg('img/guanbi.jpg', elseclick=[(899, 429)], elsedelay=0.5, retry=3)
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=0.5, at=(891, 413, 930, 452))  # 回首页

    def mianfeiniudan(self):
        # 免费扭蛋
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        self.lockimg('img/liwu.bmp', ifclick=[(750, 510)], ifdelay=1, at=(891, 413, 930, 452))  # 点进扭蛋界面
        while True:
            # 跳过抽奖提示
            time.sleep(4)
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/niudan_sheding.jpg'):
                self.guochang(screen_shot_, ['img/niudan_sheding.jpg'], suiji=0)
                break
            else:
                time.sleep(1)
                self.d.click(473, 436)  # 手动点击
                time.sleep(2)
                break

        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/niudanputong.jpg'):
                self.guochang(screen_shot_, ['img/niudanputong.jpg'], suiji=0)
                time.sleep(1)
                self.d.click(722, 351)  # 点进扭蛋
                time.sleep(1)
                self.d.click(584, 384)
                break
            else:
                time.sleep(1)
                self.d.click(876, 75)  # 手动点击
                time.sleep(1)
                self.d.click(722, 351)  # 点进扭蛋
                time.sleep(1)
                self.d.click(584, 384)
                break
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    def mianfeishilian(self):
        # 免费十连
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        self.lockimg('img/liwu.bmp', ifclick=[(750, 510)], ifdelay=1, at=(891, 413, 930, 452))  # 点进扭蛋界面

        time.sleep(1)
        screen_shot_ = self.d.screenshot(format="opencv")
        if UIMatcher.img_where(screen_shot_, 'img/mianfeishilian.jpg'):  # 仅当有免费十连时抽取免费十连
            self.d.click(872, 355)  # 点击十连
            time.sleep(1)
            self.d.click(592, 369)  # 确认

        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/liwu.bmp', at=(891, 413, 930, 452)):
                break
            self.d.click(900, 40)
            time.sleep(0.5)
            self.d.click(100, 505)
            time.sleep(0.5)
            self.d.click(100, 505)
            time.sleep(1)  # 首页锁定，保证回到首页

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

    def shouqu(self):  # 收取全部礼物
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        self.lockimg('img/shouqulvli.jpg', elseclick=[(910, 434)], at=(98, 458, 199, 496))
        self.lockimg('img/shouquliwu.bmp', elseclick=[(712, 477)], elsedelay=0.5, ifclick=[(588, 479)], ifbefore=0.5,
                     retry=3, at=(435, 30, 527, 58))
        self.lockimg('img/liwu.bmp', elseclick=[(1, 1)], elsedelay=0.3, at=(891, 413, 930, 452))  # 回首页

    def shouqurenwu(self):  # 收取任务报酬
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/renwu.jpg'):
                self.guochang(screen_shot_, ['img/renwu.jpg'], suiji=0)
                break
            self.d.click(1, 1)
            time.sleep(1)
        time.sleep(3.5)
        self.d.click(846, 437)  # 全部收取
        time.sleep(1)
        self.d.click(100, 505)
        time.sleep(0.5)
        self.d.click(100, 505)
        time.sleep(1.5)
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    def change_acc(self):  # 切换账号
        self.d.click(871, 513)  # 主菜单
        while True:  # 锁定帮助
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/bangzhu.bmp'):
                break
        self.d.click(165, 411)  # 退出账号
        while True:  # 锁定帮助
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                break
        self.d.click(591, 369)  # ok
        time.sleep(1)
        print('-----------------------------')
        print('完成该任务')
        print('-----------------------------\r\n')

    def goumaitili(self, times):  # 购买体力，注意此函数参数默认在首页执行，其他地方执行要调整参数
        for i in range(times):
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
            self.d.click(320, 31)
            time.sleep(1)
            screen_shot = self.d.screenshot(format="opencv")
            self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
            time.sleep(1)
            screen_shot = self.d.screenshot(format="opencv")
            self.guochang(screen_shot, ['img/zhandou_ok.jpg'], suiji=1)
            self.d.click(100, 505)  # 点击一下首页比较保险

    def goumaimana(self, times, mode=1):
        # mode 1: 购买times次10连
        # mode 0：购买times次1连
        if mode == 0:
            time.sleep(2)
            self.d.click(189, 62)
            for i in range(times):
                while True:  # 锁定取消2
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot_, 'img/quxiao2.jpg'):
                        break
                    self.d.click(189, 62)
                    time.sleep(2)
                self.d.click(596, 471)  # 第一次购买的位置
                while True:  # 锁定ok
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                        self.guochang(screen_shot_, ['img/ok.bmp'], suiji=0)
                        break
        else:
            time.sleep(2)
            self.d.click(189, 62)
            while True:  # 锁定取消2
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/quxiao2.jpg'):
                    break
                self.d.click(189, 62)
                time.sleep(2)
            self.d.click(596, 471)  # 第一次购买的位置
            while True:  # 锁定ok
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                    self.guochang(screen_shot_, ['img/ok.bmp'], suiji=0)
                    break
            for i in range(times):  # 购买剩下的times次
                while True:  # 锁定取消2
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot_, 'img/quxiao2.jpg'):
                        break
                time.sleep(3)
                self.d.click(816, 478)  # 购买10次
                while True:  # 锁定ok
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                        self.guochang(screen_shot_, ['img/ok.bmp'], suiji=0)
                        break

        self.lockimg('img/liwu.bmp', elseclick=[(1, 1)], elsedelay=0.5, at=(891, 413, 930, 452))  # 回首页

    def goumaijingyan(self):
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        self.d.click(617, 435)
        time.sleep(2)
        self.lockimg('img/tongchang.jpg', elseclick=[(1, 100)], elsedelay=0.5, alldelay=1)
        self.d.click(387, 151)
        time.sleep(0.3)
        self.d.click(557, 151)
        time.sleep(0.3)
        self.d.click(729, 151)
        time.sleep(0.3)
        self.d.click(900, 151)
        time.sleep(0.3)
        self.d.click(785, 438)
        time.sleep(1.5)
        self.d.click(590, 476)
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    def hanghui(self):  # 自动行会捐赠
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        time.sleep(1)
        # self.d.click(693, 436)
        self.lockimg('img/hanghui.bmp', elseclick=[(693, 436)], elsedelay=1)  # 锁定进入行会
        time.sleep(1)
        while True:  # 6-17修改：减少opencv使用量提高稳定性
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/zhiyuansheding.bmp'):
                time.sleep(3)  # 加载行会聊天界面会有延迟
                for _ in range(3):
                    time.sleep(2)
                    screen_shot = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot, 'img/juanzengqingqiu.jpg'):
                        self.d.click(367, 39)  # 点击定位捐赠按钮
                        time.sleep(2)
                        screen_shot = self.d.screenshot(format="opencv")
                        self.guochang(screen_shot, ['img/juanzeng.jpg'], suiji=0)
                        time.sleep(1)
                        self.d.click(644, 385)  # 点击max
                        time.sleep(3)
                        screen_shot = self.d.screenshot(format="opencv")
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                        time.sleep(2)
                        self.d.click(560, 369)
                        time.sleep(1)
                while True:
                    self.d.click(1, 1)
                    time.sleep(1)
                    screen_shot = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot, 'img/zhiyuansheding.bmp'):
                        break
                break
            time.sleep(2)
            # 处理多开捐赠失败的情况
            screen_shot = self.d.screenshot(format="opencv")
            self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
            self.d.click(1, 1)  # 处理被点赞的情况
            time.sleep(1)

        self.d.click(100, 505)  # 回到首页
        time.sleep(1)
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    def shuatuzuobiao(self, x, y, times):  # 刷图函数，xy为该图的坐标，times为刷图次数
        if self.switch == 0:
            tmp_cout = 0
            self.d.click(x, y)
            time.sleep(0.5)
        else:
            print('>>>无扫荡券或者无体力！', '结束 全部 刷图任务！<<<\r\n')
            return
        if self.switch == 0:
            while True:  # 锁定加号
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/jiahao.bmp'):
                    # screen_shot = a.d.screenshot(format="opencv")
                    for i in range(times - 1):  # 基础1次
                        # 扫荡券不必使用opencv来识别，降低效率
                        self.d.click(876, 334)
                    time.sleep(0.3)
                    self.d.click(758, 330)  # 使用扫荡券的位置 也可以用OpenCV但是效率不够而且不能自由设定次数
                    time.sleep(0.3)
                    screen_shot = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot, 'img/ok.bmp'):
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    else:
                        time.sleep(0.5)
                        self.d.click(588, 370)
                    # screen_shot = a.d.screenshot(format="opencv")
                    # a.guochang(screen_shot,['img/shiyongsanzhang.jpg'])
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot_, 'img/tilibuzu.jpg'):
                        print('>>>无扫荡券或者无体力！结束此次刷图任务！<<<\r\n')
                        self.switch = 1
                        self.d.click(677, 458)  # 取消
                        break
                    screen_shot = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot, 'img/tiaoguo.jpg'):
                        self.guochang(screen_shot, ['img/tiaoguo.jpg'], suiji=0)
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    else:
                        time.sleep(1)
                        self.d.click(475, 481)  # 手动点击跳过
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    break
                else:
                    if tmp_cout < 3:
                        # 计时3次就失败
                        self.d.click(x, y)
                        time.sleep(0.5)
                        tmp_cout = tmp_cout + 1
                    else:
                        print('>>>无扫荡券或者无体力！结束此次刷图任务！<<<\r\n')
                        self.switch = 1
                        self.d.click(677, 458)  # 取消
                        break
        else:
            print('>>>无扫荡券或者无体力！结束刷图任务！<<<\r\n')
        while True:
            self.d.click(1, 1)
            time.sleep(0.3)
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/normal.jpg', at=(660, 72, 743, 94)):
                break
            if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                break

    def shuajingyan(self, map):
        """
        刷图刷1-1
        map为主图
        """
        # 进入冒险
        time.sleep(2)
        self.d.click(480, 505)
        time.sleep(2)

        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
        self.d.click(562, 253)
        time.sleep(2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/normal.jpg', at=(660, 72, 743, 94)):
                break
        for i in range(map):
            time.sleep(3)
            self.d.click(27, 272)
        self.shuatuzuobiao(106, 279, 160)  # 1-1 刷7次体力为佳

        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
    
    # 买药
    def buyExp(self):
        # 进入商店
        count = 0
        self.d.click(616, 434)
        while True:
            self.d.click(82, 84)
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/exp.jpg'):
                break
            count += 1
            time.sleep(1)
            if count > 4:
                break
        if count <= 4:
            self.d.click(386, 148)
            self.d.click(556, 148)
            self.d.click(729, 148)
            self.d.click(897, 148)
            self.d.click(795, 437)
            time.sleep(1)
            self.d.click(596, 478)
            time.sleep(1)
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    # 做jjc任务
    def doJJC(self):
        # 进入jjc
        self.enterJJC(579, 411)

        # 选择第一位进入对战
        self.d.click(604, 162)
        time.sleep(1)
        # 点击战斗开始
        self.d.click(822, 456)

        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/xiayibu.jpg'):
                self.d.click(803, 496)
                break
        time.sleep(1)
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    # 做pjjc任务
    def doPJJC(self):
        self.enterJJC(821, 410)
        # 选择第一位进入对战
        self.d.click(604, 162)
        time.sleep(1)
        # 点击队伍2
        self.d.click(822, 456)
        time.sleep(1)
        # 点击队伍3
        self.d.click(822, 456)
        time.sleep(1)
        # 点击战斗开始
        self.d.click(822, 456)
        time.sleep(1)
        # 确保战斗开始
        self.d.click(822, 456)
        
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/xiayibu.jpg'):
                self.d.click(803, 506)
                break
        time.sleep(1)
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
    
    # 进入jjc
    def enterJJC(self, x, y):
        self.d.click(480, 505)
        time.sleep(2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
        self.d.click(x, y)
        time.sleep(2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            self.d.click(36, 77)
            if UIMatcher.img_where(screen_shot_, 'img/list.jpg'):
                break

    # 进入hard图
    def enterHardMap(self):
        # 进入冒险
        time.sleep(2)
        self.d.click(480, 505)
        time.sleep(2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
        # 点击进入主线关卡
        self.d.click(562, 253)
        time.sleep(2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/normal.jpg'):
                self.d.click(880, 80)
            if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                break

    # 刷11-3 hard图
    def do11to3Hard(self):
        # 进入冒险
        self.enterHardMap()
        self.continueDo9(767, 327) # 11-3
        self.continueDo9(479, 241) # 11-2
        self.continueDo9(217, 360) # 11-1
        self.goLeft()
        self.continueDo9(764, 334) # 10-3
        self.goLeft()
        self.goLeft()
        self.continueDo9(218, 386) # 8-1
        self.goLeft()
        self.continueDo9(749, 285) # 7-3
        self.continueDo9(476, 335) # 7-2
        self.goLeft()
        self.goLeft()
        self.continueDo9(696, 270) # 5-3
        self.goLeft()
        self.continueDo9(247, 270) # 4-1

        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
    
    # 左移动
    def goLeft(self):
        self.d.click(35, 275)
        time.sleep(2)

    # 刷1-3 hard图
    def do1to3Hard(self):
        # 进入冒险
        self.enterHardMap()
        self.shuatuzuobiao(250, 280, self.times)  # 4-1
        self.goLeft()
        self.continueDo9(715, 280) # 3-3
        self.continueDo9(470, 365) # 3-2
        self.continueDo9(255, 260) # 3-1
        self.goLeft()
        self.continueDo9(729, 340) # 2-3
        self.continueDo9(473, 368) # 2-2
        self.continueDo9(280, 275) # 2-1
        self.goLeft()
        self.continueDo9(251, 340) # 1-1
        self.continueDo9(465, 266) # 1-2
        self.continueDo9(695, 318) # 1-3
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
    
    # 继续执行函数
    def continueDo9(self, x, y):
        self.switch = 0
        self.shuatuzuobiao(x, y, self.times)  # 3-3

    # 刷活动hard图
    def doActivityHard(self):
        # 进入冒险
        time.sleep(2)
        self.d.click(480, 505)
        time.sleep(2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
        # 点击进入活动
        self.d.click(415, 430)
        time.sleep(3)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            self.d.click(480, 380)
            time.sleep(0.5)
            self.d.click(480, 380)
            if UIMatcher.img_where(screen_shot_, 'img/normal.jpg'):
                self.d.click(880, 80)
            if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                break
        self.shuatuzuobiao(689, 263, self.times)  # 1-5
        self.continueDo9(570, 354) # 1-4
        self.continueDo9(440, 255) # 1-3
        self.continueDo9(300, 339) # 1-2
        self.continueDo9(142, 267) # 1-1
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    def shuatu8(self):
        # 进入冒险
        time.sleep(2)
        self.d.click(480, 505)
        time.sleep(2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
        self.d.click(562, 253)
        time.sleep(2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/normal.jpg', at=(660, 72, 743, 94)):
                break
            if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                self.d.click(701, 83)
        self.switch = 0
        self.shuatuzuobiao(584, 260, self.times)  # 8-14
        self.shuatuzuobiao(715, 319, self.times)  # 8-13
        self.shuatuzuobiao(605, 398, self.times)  # 8-12
        self.shuatuzuobiao(478, 374, self.times)  # 8-11
        self.shuatuzuobiao(357, 405, self.times)  # 8-10
        self.shuatuzuobiao(263, 324, self.times)  # 8-9
        self.shuatuzuobiao(130, 352, self.times)  # 8-8
        self.d.drag(200, 270, 600, 270, 0.1)  # 拖拽到最左
        time.sleep(2)
        self.shuatuzuobiao(580, 401, self.times)  # 8-7
        self.shuatuzuobiao(546, 263, self.times)  # 8-6
        self.shuatuzuobiao(457, 334, self.times)  # 8-5
        self.shuatuzuobiao(388, 240, self.times)  # 8-4
        self.shuatuzuobiao(336, 314, self.times)  # 8-3
        self.shuatuzuobiao(230, 371, self.times)  # 8-2
        self.shuatuzuobiao(193, 255, self.times)  # 8-1
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    def shuatu10(self):
        # 进入冒险
        time.sleep(2)
        self.d.click(480, 505)
        time.sleep(2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
        self.d.click(562, 253)
        time.sleep(5)
        for _ in range(1):
            # 左移到10图
            time.sleep(3)
            self.d.click(27, 272)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/normal.jpg', at=(660, 72, 743, 94)):
                break
            if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                self.d.click(701, 83)
        self.switch = 0
        self.d.drag(600, 270, 200, 270, 0.1)
        time.sleep(2)
        self.shuatuzuobiao(821, 299, self.times)  # 10-17
        self.shuatuzuobiao(703, 328, self.times)  # 10-16
        self.shuatuzuobiao(608, 391, self.times)  # 10-15
        self.shuatuzuobiao(485, 373, self.times)  # 10-14
        self.shuatuzuobiao(372, 281, self.times)  # 10-13
        self.shuatuzuobiao(320, 421, self.times)  # 10-12
        self.shuatuzuobiao(172, 378, self.times)  # 10-11
        self.shuatuzuobiao(251, 235, self.times)  # 10-10
        self.shuatuzuobiao(111, 274, self.times)  # 10-9
        self.d.drag(200, 270, 600, 270, 0.1)  # 拖拽到最左
        time.sleep(2)
        self.shuatuzuobiao(690, 362, self.times)  # 10-8
        self.shuatuzuobiao(594, 429, self.times)  # 10-7
        self.shuatuzuobiao(411, 408, self.times)  # 10-6
        self.shuatuzuobiao(518, 332, self.times)  # 10-5
        self.shuatuzuobiao(603, 238, self.times)  # 10-4
        self.shuatuzuobiao(430, 239, self.times)  # 10-3
        self.shuatuzuobiao(287, 206, self.times)  # 10-2
        self.shuatuzuobiao(146, 197, self.times)  # 10-1
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    def shuatu11(self):
        # 进入冒险
        time.sleep(2)
        self.d.click(480, 505)
        time.sleep(2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
        self.d.click(562, 253)
        time.sleep(2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/normal.jpg', at=(660, 72, 743, 94)):
                break
            if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                self.d.click(701, 83)
        self.switch = 0
        self.shuatuzuobiao(663, 408, self.times)  # 11-17
        self.shuatuzuobiao(542, 338, self.times)  # 11-16
        self.shuatuzuobiao(468, 429, self.times)  # 11-15
        self.shuatuzuobiao(398, 312, self.times)  # 11-14
        self.shuatuzuobiao(302, 428, self.times)  # 11-13
        self.shuatuzuobiao(182, 362, self.times)  # 11-12
        self.shuatuzuobiao(253, 237, self.times)  # 11-11
        self.shuatuzuobiao(107, 247, self.times)  # 11-10
        self.d.drag(200, 270, 600, 270, 0.1)  # 拖拽到最左
        time.sleep(2)
        self.shuatuzuobiao(648, 316, self.times)  # 11-9
        self.shuatuzuobiao(594, 420, self.times)  # 11-8
        self.shuatuzuobiao(400, 432, self.times)  # 11-7
        self.shuatuzuobiao(497, 337, self.times)  # 11-6
        self.shuatuzuobiao(558, 240, self.times)  # 11-5
        self.shuatuzuobiao(424, 242, self.times)  # 11-4
        self.shuatuzuobiao(290, 285, self.times)  # 11-3
        self.shuatuzuobiao(244, 412, self.times)  # 11-2
        self.shuatuzuobiao(161, 326, self.times)  # 11-1
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    async def juqingtiaoguo(self):
        # 异步跳过教程 By：CyiceK
        # 测试
        f = 0
        while f == 0:
            await asyncio.sleep(10)
            # 过快可能会卡
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/caidan_yuan.jpg', at=(860, 0, 960, 100), debug=False):
                self.d.click(917, 39)  # 菜单
                await asyncio.sleep(1)
                self.d.click(807, 44)  # 跳过
                await asyncio.sleep(3)
                self.d.click(589, 367)  # 跳过ok
                await asyncio.sleep(5)

    async def bad_connecting(self):
        # 异步判断异常 By：CyiceK
        # 测试
        f = 0
        _time = 0
        while f == 0:
            try:
                await asyncio.sleep(30)
                # 过快可能会卡
                time_start = time.time()
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/connecting.bmp', at=(748, 20, 931, 53), debug=False):
                    time_end = time.time()
                    _time = time_end - time_start
                    _time = _time + _time
                    if _time > 15:
                        LOG().Account_bad_connecting(self.account)
                        self.d.session("com.bilibili.priconne")
                        await asyncio.sleep(8)
                        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1,
                                     at=(891, 413, 930, 452))  # 回首页
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/loading.bmp', threshold=0.8, debug=False):
                    # 不知道为什么，at 无法在这里使用
                    time_end = time.time()
                    _time = time_end - time_start
                    _time = _time + _time
                    if _time > 15:
                        LOG().Account_bad_connecting(self.account)
                        self.d.session("com.bilibili.priconne")
                        await asyncio.sleep(8)
                        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1,
                                     at=(891, 413, 930, 452))  # 回首页
                if UIMatcher.img_where(screen_shot_, 'img/fanhuibiaoti.bmp', debug=False):
                    self.guochang(screen_shot_, ['img/fanhuibiaoti.bmp'], suiji=0)
                    await asyncio.sleep(8)
                    self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
            except Exception as e:
                print('异步线程终止并检测出异常{}'.format(e))
                break

    def dixiacheng_to_fix(self, skip):
        """
        地下城函数已于2020/7/11日重写
        By:Cyice
        有任何问题 bug请反馈
        :param skip:
        :return:
        """
        while True:
            time.sleep(3)
            self.d.click(480, 505)
            time.sleep(1)
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                self.d.click(900, 138)
                time.sleep(15)
                # 我太怕妈妈了QAQ,这上面是防可可萝骑脸，按需求调配
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/kekeluo.bmp'):
                    time.sleep(10)
                    # 跳过可可萝
                    self.d.click(1, 1)
                    time.sleep(1)
                    break
                else:
                    break
        while True:
            try:
                time.sleep(5)
                dixiacheng_floor = self.baidu_ocr(200, 410, 263, 458)
                dixiacheng_floor = int(dixiacheng_floor['words_result'][0]['words'].split('/')[0])
                if dixiacheng_floor > 1:
                    print('%s 已经打过地下城，执行撤退' % self.account)
                    time.sleep(3)
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):
                        self.d.click(808, 435)
                        time.sleep(1)
                        self.d.click(588, 371)
                        time.sleep(3)
                        break
                else:
                    break
            except Exception as result:
                print('检测出异常{}'.format(result))
            break
        try:
            time.sleep(5)
            dixiacheng_times = self.baidu_ocr(868, 419, 928, 459)
            dixiacheng_times = int(dixiacheng_times['words_result'][0]['words'].split('/')[0])
        except Exception as result:
            print('检测出异常{}'.format(result))
        # 下面这段因为调试而注释了，实际使用时要加上
        while True:
            try:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/yunhai.bmp') and dixiacheng_times == 1:
                    self.d.click(233, 311)
                    time.sleep(1)
                elif UIMatcher.img_where(screen_shot_, 'img/yunhai.bmp') and dixiacheng_times == 0:
                    self.dxc_switch = 1
                    LOG().Account_undergroundcity(self.account)
                if self.dxc_switch == 0:
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                        self.d.click(592, 369)
                    # self.lockimg('img/ok.bmp', ifclick=[(592, 369)], elseclick=[(592, 369)])
                    # 锁定OK
                else:
                    print('>>>今天无次数\r\n')
                    # LOG().Account_undergroundcity(self.account)
                    break
            except Exception as error:
                print('检测出异常{}'.format(error))
                print('OCR无法识别！\r\n')
                break
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):
                break
        while self.dxc_switch == 0:
            while True:
                time.sleep(2)
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):
                    self.lockimg('img/tiaozhan.bmp', ifclick=[(833, 456)], elseclick=[(667, 360)])
                    # 锁定挑战和第一层
                    break
            while True:
                time.sleep(2)
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/zhiyuan.jpg'):
                    time.sleep(1)
                    # self.d.click(100, 173)  # 第一个人
                    screen_shot = self.d.screenshot(format="opencv")
                    self.guochang(screen_shot, ['img/zhiyuan.jpg'], suiji=0)
                    break

            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dengjixianzhi.jpg'):
                self.d.click(213, 208)  # 如果等级不足，就支援的第二个人
                time.sleep(1)
            else:
                self.d.click(100, 173)  # 支援的第一个人
                time.sleep(1)
                self.d.click(213, 208)  # 以防万一
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/notzhandoukaishi.bmp', threshold=1.0):
                # 逻辑顺序改变
                # 当无法选支援一二位时，将会退出地下城
                print("无法出击!")
                break
            else:
                self.d.click(98, 88)  # 全部
                time.sleep(1)
                self.d.click(100, 173)  # 第一个人
                time.sleep(1)
                self.d.click(833, 470)  # 战斗开始
            while True:
                time.sleep(2)
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                    self.guochang(screen_shot_, ['img/ok.bmp'], suiji=0)
                    break
                if UIMatcher.img_where(screen_shot_, 'img/zhandoukaishi.jpg'):
                    time.sleep(1.5)
                    self.d.click(833, 470)  # 战斗开始
                    break

            if skip:  # 直接放弃战斗
                self.lockimg('img/caidan.jpg', ifclick=[(902, 33)], ifbefore=2, ifdelay=1)
                self.lockimg('img/fangqi.jpg', ifclick=[(625, 376)], ifbefore=2, ifdelay=3)
                self.lockimg('img/fangqi_2.bmp', ifclick=[(625, 376)], ifbefore=2, ifdelay=1)
            else:
                self.lockimg('img/kuaijin_1.jpg', ifclick=[(913, 494)], elseclick=[(913, 494)], ifbefore=2, ifdelay=1)
            while skip is False:  # 结束战斗返回
                time.sleep(2)
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/shanghaibaogao.jpg'):
                    time.sleep(3)
                    self.guochang(screen_shot_, ['img/xiayibu.jpg', 'img/qianwangdixiacheng.jpg'], suiji=0)
                    if UIMatcher.img_where(screen_shot_, 'img/duiwu.jpg'):
                        self.guochang(screen_shot_, ['img/xiayibu.jpg', 'img/qianwangdixiacheng.jpg'], suiji=0)
                        break
                    else:
                        print('>>>无法识别到图像，坐标点击\r\n')
                        time.sleep(3)
                        self.d.click(828, 502)
                        break
                elif UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):
                    time.sleep(3)
                    # 撤退
                    self.d.click(808, 435)
                    time.sleep(1)
                    self.d.click(588, 371)
                    break

            time.sleep(1)
            self.d.click(1, 1)  # 取消显示结算动画
            while True:  # 撤退地下城
                time.sleep(2)
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):
                    # for i in range(3):
                    # 保险措施
                    # self.d.click(808, 435)
                    # time.sleep(1)
                    # self.d.click(588, 371)
                    self.guochang(screen_shot_, ['img/chetui.jpg'], suiji=0)
                    time.sleep(1)
                    screen_shot = self.d.screenshot(format="opencv")
                    self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    LOG().Account_undergroundcity(self.account)
                    break
                self.d.click(1, 1)  #
                time.sleep(1)
            break
        while True:  # 首页锁定
            if UIMatcher.img_where(screen_shot_, 'img/liwu.bmp', at=(891, 413, 930, 452)):
                break
            self.d.click(131, 533)
            time.sleep(1)  # 保证回到首页
            # 防卡死
            screen_shot_ = self.d.screenshot(format="opencv")
            self.guochang(screen_shot_, ['img/xiayibu.jpg', 'img/qianwangdixiacheng.jpg'], suiji=0)
            screen_shot = self.d.screenshot(format="opencv")
            self.guochang(screen_shot, ['img/chetui.jpg'], suiji=0)
            screen_shot = self.d.screenshot(format="opencv")
            self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)

    def dixiacheng(self, skip):
        """
        地下城函数于2020/7/14日修改
        By:Dr-Bluemond
        有任何问题 bug请反馈
        :param skip:
        :return:
        """
        # 首页 -> 地下城选章/（新号）地下城章内
        self.lockimg('img/dixiacheng.jpg', elseclick=[(480, 505)], elsedelay=0.5, at=(837, 92, 915, 140))  # 进入地下城
        self.lock_no_img('img/dixiacheng.jpg', elseclick=[(900, 138)], elsedelay=0.5, alldelay=5,
                         at=(837, 92, 915, 140))

        # 撤退 如果 已经进入
        while True:
            screen = self.d.screenshot(format='opencv')
            if UIMatcher.img_where(screen, 'img/yunhai.bmp'):
                break
            if UIMatcher.img_where(screen, 'img/chetui.jpg', at=(738, 420, 872, 442)):
                self.lockimg('img/ok.bmp', elseclick=[(810, 433)], elsedelay=1, ifclick=[(592, 370)], ifbefore=0.5,
                             at=(495, 353, 687, 388))
                continue
            self.d.click(1, 100)
            time.sleep(0.3)

        ok = self.lockimg('img/ok.bmp', elseclick=[(298, 213)], elsedelay=0.5, ifclick=[(596, 371)], ifbefore=1,
                          ifdelay=0, retry=3)
        if not ok:
            print("未能成功进入云海的山脉，跳过刷地下城")
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], at=(891, 413, 930, 452))
            return

        while True:
            # 锁定挑战和第一层
            self.lockimg('img/tiaozhan.bmp', elseclick=[(667, 360)], ifclick=[(833, 456)], at=(759, 428, 921, 483))
            time.sleep(2)
            self.d.click(480, 88)
            time.sleep(0.5)
            poses = [(106, 172), (216, 172), (323, 172), (425, 172)]
            for pos in poses:
                self.d.click(*pos)
                time.sleep(0.2)
            self.d.click(98, 92)
            time.sleep(0.5)
            for pos in poses:
                self.d.click(*pos)
                time.sleep(0.2)
            screen = self.d.screenshot(format='opencv')
            if UIMatcher.img_where(screen, 'img/notzhandoukaishi.bmp', threshold=0.98):
                # 当无法出击时将会退出地下城
                time.sleep(0.5)
                self.d.click(1, 100)
                print("无法出击!")
                break
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/zhandoukaishi.jpg', at=(758, 427, 917, 479)):
                    time.sleep(1)
                    self.d.click(833, 470)  # 战斗开始
                    self.lockimg('img/ok.bmp', ifclick=[(588, 479)], ifdelay=0.5, retry=5)
                    break
                time.sleep(1)

            time.sleep(4)  # 这里填写你预估的进入战斗加载所花费的时间
            if skip:  # 直接放弃战斗
                ok = self.lockimg('img/fangqi.jpg', elseclick=[(902, 33)], elsedelay=0.5, ifclick=[(625, 376)],
                                  ifbefore=0, ifdelay=0, retry=7, at=(567, 351, 686, 392))
                if ok:
                    ok2 = self.lockimg('img/fangqi_2.bmp', ifclick=[(625, 376)], ifbefore=0.5, ifdelay=0, retry=3,
                                       at=(486, 344, 693, 396))
                    if not ok2:
                        skip = False
                else:
                    skip = False
            else:
                self.lockimg('img/kuaijin_2.bmp', elseclick=[(913, 494)], ifbefore=0, ifdelay=0.5, retry=10)
                screen = self.d.screenshot(format='opencv')
                if UIMatcher.img_where(screen, 'img/auto.jpg'):
                    time.sleep(0.2)
                    self.d.click(914, 425)

            if skip is False:
                self.lockimg('img/shanghaibaogao.jpg', elseclick=[(1, 100)], ifclick=[(820, 492)], ifdelay=3)
                self.lock_no_img('img/shanghaibaogao.jpg', elseclick=[(820, 492)], elsedelay=3)

            self.d.click(1, 1)  # 取消显示结算动画
            self.lockimg('img/chetui.jpg', elseclick=[(1, 1)], at=(738, 420, 872, 442))
            self.lockimg('img/ok.bmp', elseclick=[(809, 433)], elsedelay=1, at=(495, 353, 687, 388))
            self.lock_no_img('img/ok.bmp', elseclick=[(592, 373)], elsedelay=0.5, at=(495, 353, 687, 388))
            break

        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], at=(891, 413, 930, 452))

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

    def tansuo(self, mode=0):  # 探索函数
        """
        mode 0: 刷最上面的
        mode 1: 刷次上面的
        mode 2: 第一次手动过最上面的，再刷一次次上面的
        mode 3: 第一次手动过最上面的，再刷一次最上面的
        """
        is_used = 0
        self.d.click(480, 505)
        time.sleep(1)
        while True:  # 锁定地下城
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
            self.d.click(480, 505)
            time.sleep(1)
        self.d.click(734, 142)  # 探索
        time.sleep(3.5)
        while True:  # 锁定凯留头（划掉）返回按钮
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/fanhui.bmp', at=(16, 12, 54, 48)):
                break
            self.d.click(1, 1)
            time.sleep(0.5)
        # 经验
        self.d.click(592, 255)  # 经验
        time.sleep(3)
        screen_shot_ = self.d.screenshot(format="opencv")
        if UIMatcher.img_where(screen_shot_, 'img/tansuo_used.jpg'):
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页
        else:
            if mode >= 2:
                self.shoushuazuobiao(704, 152, lockpic='img/fanhui.bmp', screencut=(16, 12, 54, 48))
            if mode == 0 or mode == 3:
                self.d.click(704, 152)  # 5级
            else:
                self.d.click(707, 265)  # 倒数第二
            time.sleep(1)
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/tansuo_used2.jpg'):
                    is_used = 1
                    self.d.click(668, 452)  # 取消
                    break
                if UIMatcher.img_where(screen_shot_, 'img/tiaozhan.jpg'):
                    break
                time.sleep(0.5)
            if is_used == 0:
                self.d.drag(876, 329, 876, 329, 0.5)  # +号
                time.sleep(0.5)
                self.d.click(752, 327)  # 扫荡
                time.sleep(0.5)
                while True:
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                        self.d.click(590, 363)  # ok
                        time.sleep(0.5)
                        break
            if is_used == 1:
                self.d.click(36, 32)  # back
                time.sleep(1)
            is_used = 0
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/home.jpg'):
                    break
                self.d.click(1, 1)
                time.sleep(1)
            # mana
            self.d.click(802, 267)  # mana
            time.sleep(3)
            if mode >= 2:
                self.shoushuazuobiao(704, 152, lockpic='img/fanhui.bmp', screencut=(16, 12, 54, 48))
            if mode == 0 or mode == 3:
                self.d.click(704, 152)  # 5级
            else:
                self.d.click(707, 265)  # 倒数第二
            time.sleep(1.5)
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/tansuo_used2.jpg'):
                    is_used = 1
                    self.d.click(668, 452)  # 取消
                    break
                if UIMatcher.img_where(screen_shot_, 'img/tiaozhan.jpg'):
                    break
                time.sleep(0.5)
            if is_used == 0:
                self.d.drag(876, 329, 876, 329, 0.5)  # +号
                time.sleep(0.5)
                self.d.click(752, 327)  # 扫荡
                time.sleep(0.5)
                while True:
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                        self.d.click(590, 363)  # ok
                        time.sleep(0.5)
                        break
            if is_used == 1:
                self.d.click(36, 32)  # back
                time.sleep(1)
            is_used = 0
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/home.jpg'):
                    break
                self.d.click(1, 1)
                time.sleep(1)
        # 完成战斗后
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    def dixiachengYunhai(self): # 地下城 云海 （第一个）
        self.d.click(480, 505)
        time.sleep(1)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
            self.d.click(480, 505)
            time.sleep(1)
        self.d.click(900, 138)
        time.sleep(3)

        screen_shot_ = self.d.screenshot(format="opencv")
        if UIMatcher.img_where(screen_shot_, 'img/dixiacheng_used.jpg'):  # 避免某些农场号刚买回来已经进了地下城
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页
        else:
            # 下面这段因为调试而注释了，实际使用时要加上
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):  # 避免某些农场号刚买回来已经进了地下城
                    break
                if UIMatcher.img_where(screen_shot_, 'img/yunhai.bmp'):
                    self.d.click(250, 250)  # 云海
                    time.sleep(1)
                    while True:
                        screen_shot_ = self.d.screenshot(format="opencv")
                        if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                            break
                    self.d.click(592, 369)  # 点击ok
                    time.sleep(1)
                    break
            # 刷地下城
            self.dixiachengzuobiao(666, 340, 0, 1)  # 1层
            self.dixiachengzuobiao(477, 296, 0)  # 2层
            self.dixiachengzuobiao(311, 306, 0)  # 3层
            self.dixiachengzuobiao(532, 301, 0)  # 4层
            self.dixiachengzuobiao(428, 315, 0)  # 5层
            self.dixiachengzuobiao(600, 313, 0)  # 6层
            self.dixiachengzuobiao(447, 275, 0)  # 7层

            # 完成战斗后
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页

    def dixiachengDuanya(self):  # 地下城 断崖（第三个）
        self.d.click(480, 505)
        time.sleep(1)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
            self.d.click(480, 505)
            time.sleep(1)
        self.d.click(900, 138)
        time.sleep(3)
        screen_shot_ = self.d.screenshot(format="opencv")
        if UIMatcher.img_where(screen_shot_, 'img/dixiacheng_used.jpg'):  # 避免某些农场号刚买回来已经进了地下城
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页
        else:
            # 下面这段因为调试而注释了，实际使用时要加上
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):  # 避免某些农场号刚买回来已经进了地下城
                    break
                if UIMatcher.img_where(screen_shot_, 'img/yunhai.bmp'):
                    self.d.click(712, 267)  # 断崖
                    time.sleep(1)
                    while True:
                        screen_shot_ = self.d.screenshot(format="opencv")
                        if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                            break
                    self.d.click(592, 369)  # 点击ok
                    time.sleep(1)
                    break
            # 刷地下城
            self.dixiachengzuobiao(642, 371, 0, 1)  # 1层
            self.dixiachengzuobiao(368, 276, 0, 2)  # 2层
            self.dixiachengzuobiao(627, 263, 0)  # 3层
            self.dixiachengzuobiao(427, 274, 0)  # 4层
            self.dixiachengzuobiao(199, 275, 0)  # 5层
            self.dixiachengzuobiao(495, 288, 0)  # 6层
            self.dixiachengzuobiao(736, 291, 0)  # 7层
            self.dixiachengzuobiao(460, 269, 0)  # 8层
            self.dixiachengzuobiao(243, 274, 0)  # 9层
            self.dixiachengzuobiao(654, 321, 0, 1)  # 10层

            # 点击撤退
            if self.is_dixiacheng_end == 1:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/10.jpg'):  # 地下城10层失败重试1次，使低练度号能2刀通关boss
                    self.is_dixiacheng_end = 0
                    self.dixiachengzuobiao(654, 321, 0)  # 10层
                self.d.click(780, 430)
                time.sleep(1)
                self.d.click(576, 364)

        # 完成战斗后
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    def shoushuazuobiao(self, x, y, jiaocheng=0, lockpic='img/normal.jpg', screencut=None):
        """
        不使用挑战券挑战，xy为该图坐标
        jiaocheng=0 只处理简单的下一步和解锁内容
        jiaocheng=1 要处理复杂的教程
        lockpic: 返回时锁定的图
        screencut: 返回时锁定的图的搜索范围
        :return:
        """
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, lockpic, at=screencut):
                break
            self.d.click(1, 138)
            time.sleep(1)
        self.lockimg('img/tiaozhan.jpg', elseclick=[(x, y)], elsedelay=2)
        self.d.click(840, 454)
        time.sleep(0.7)

        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.imgs_where(screen_shot_, ['img/kuaijin.jpg', 'img/kuaijin_1.jpg']) != {}:
                break
            self.d.click(840, 454)  # 点到进入战斗画面
            time.sleep(0.7)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.click(screen_shot_, 'img/kuaijin.jpg', at=(891, 478, 936, 517)):
                time.sleep(1)
            if self.click(screen_shot_, 'img/auto.jpg', at=(891, 410, 936, 438)):
                time.sleep(1)
            if UIMatcher.img_where(screen_shot_, 'img/wanjiadengji.jpg', at=(233, 168, 340, 194)):
                break
            self.d.click(1, 138)
            time.sleep(0.5)
        if jiaocheng == 1:  # 有复杂的教程，交给教程函数处理
            self.chulijiaocheng()
        else:  # 无复杂的教程，自己处理掉“下一步”
            for _ in range(7):
                self.d.click(832, 506)
                time.sleep(0.2)
            while True:
                time.sleep(2)
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, lockpic, at=screencut):
                    break
                elif UIMatcher.img_where(screen_shot_, 'img/xiayibu.jpg'):
                    self.d.click(832, 506)
                else:
                    self.d.click(1, 100)
            while True:  # 两次确认回到挑战界面
                self.d.click(1, 100)
                time.sleep(0.5)
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, lockpic, at=screencut):
                    break

    def chulijiaocheng(self):  # 处理教程, 最终返回刷图页面
        """
        有引导点引导
        有下一步点下一步
        有主页点主页
        有圆menu就点跳过，跳过
        有跳过点跳过
        都没有就点边界点
        # 有取消点取消
        :return:
        """
        count = 0  # 出现主页的次数
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            num_of_white, x, y = UIMatcher.find_gaoliang(screen_shot_)
            if num_of_white < 77000:
                try:
                    self.d.click(x * self.dWidth, y * self.dHeight + 20)
                except:
                    pass
                time.sleep(1)
                continue

            if UIMatcher.img_where(screen_shot_, 'img/liwu.bmp', at=(891, 413, 930, 452)):
                count += 1
                if count > 2:
                    break
                time.sleep(1)
                continue
            elif UIMatcher.img_where(screen_shot_, 'img/jiaruhanghui.jpg'):
                break
            elif self.click(screen_shot_, 'img/xiayibu.jpg'):
                time.sleep(2)
            elif self.click(screen_shot_, 'img/niudan_jiasu.jpg', at=(700, 0, 960, 100)):
                pass
            elif self.click(screen_shot_, 'img/wuyuyin.jpg', at=(450, 355, 512, 374)):
                time.sleep(3)
            elif self.click(screen_shot_, 'img/tiaoguo.jpg'):
                time.sleep(3)
            elif self.click(screen_shot_, 'img/zhuye.jpg', at=(46, 496, 123, 537)):
                pass
            elif self.click(screen_shot_, 'img/caidan_yuan.jpg', at=(898, 23, 939, 62)):
                time.sleep(0.7)
                self.d.click(804, 45)
                time.sleep(0.7)
                self.d.click(593, 372)
                time.sleep(2)
            elif UIMatcher.img_where(screen_shot_, 'img/qianwanghuodong.bmp'):
                for _ in range(3):
                    self.d.click(390, 369)
                    time.sleep(1)
            else:
                self.d.click(1, 100)
            count = 0
            time.sleep(1)
        # 返回冒险
        self.d.click(480, 505)
        time.sleep(2)
        self.lockimg('img/zhuxianguanqia.jpg', elseclick=[(480, 513), (390, 369)], elsedelay=0.5)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/zhuxianguanqia.jpg', at=(511, 286, 614, 314)):
                self.d.click(562, 253)
                time.sleep(0.5)
            else:
                break
        time.sleep(3)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/normal.jpg', at=(660, 72, 743, 94)):
                break
            self.d.click(704, 84)
            time.sleep(0.5)

    def qianghua(self):
        # 此处逻辑极为复杂，代码不好理解
        time.sleep(3)
        self.d.click(215, 513)  # 角色
        time.sleep(3)
        self.d.click(177, 145)  # First
        time.sleep(3)
        for i in range(5):
            print("Now: ", i)
            while True:
                screen_shot_ = self.d.screenshot(format='opencv')
                if UIMatcher.img_where(screen_shot_, 'img/keyihuode.jpg'):
                    # 存在可以获得，则一直获得到没有可以获得，或者没有三星
                    self.d.click(374, 435)
                    time.sleep(1)
                    screen_shot_ = self.d.screenshot(format='opencv')
                    if UIMatcher.img_where(screen_shot_, 'img/tuijianguanqia.jpg', at=(258, 87, 354, 107)):
                        # 已经强化到最大等级，开始获取装备
                        if not UIMatcher.img_where(screen_shot_, 'img/sanxingtongguan.jpg'):
                            # 装备不可刷，换人
                            self.d.click(501, 468)  # important
                            time.sleep(1)
                            break
                        while UIMatcher.img_where(screen_shot_, 'img/sanxingtongguan.jpg'):
                            # 一直刷到没有有推荐关卡但没有三星或者返回到角色列表
                            self.guochang(screen_shot_, ['img/sanxingtongguan.jpg'], suiji=0)
                            time.sleep(1)
                            # 使用扫荡券的数量：
                            for _ in range(4 - 1):
                                self.d.click(877, 333)
                                time.sleep(0.3)
                            self.d.click(752, 333)
                            time.sleep(0.7)
                            self.d.click(589, 371)
                            while True:
                                screen_shot_ = self.d.screenshot(format='opencv')
                                active_paths = UIMatcher.imgs_where(screen_shot_,
                                                                    ['img/tuijianguanqia.jpg', 'img/zidongqianghua.jpg',
                                                                     'img/tiaoguo.jpg'])
                                if 'img/tiaoguo.jpg' in active_paths:
                                    x, y = active_paths['img/tiaoguo.jpg']
                                    self.d.click(x, y)
                                if 'img/tuijianguanqia.jpg' in active_paths:
                                    flag = 'img/tuijianguanqia.jpg'
                                    break
                                elif 'img/zidongqianghua.jpg' in active_paths:
                                    flag = 'img/zidongqianghua.jpg'
                                    break
                                else:
                                    self.d.click(1, 100)
                                    time.sleep(1.3)
                            if flag == 'img/zidongqianghua.jpg':
                                # 装备获取完成，跳出小循环，重进大循环
                                self.d.click(371, 437)
                                time.sleep(0.7)
                                break
                            else:
                                # 装备未获取完毕，继续尝试获取
                                continue
                        self.d.click(501, 468)  # important
                        time.sleep(2)
                        continue
                    else:
                        # 未强化到最大等级，强化到最大登记
                        self.d.click(501, 468)  # important
                        time.sleep(3)
                        continue
                else:
                    # 没有可以获得
                    if UIMatcher.img_where(screen_shot_, 'img/ranktisheng.jpg', at=(206, 325, 292, 346)):
                        self.d.click(250, 338)
                        time.sleep(2)
                        screen_shot_ = self.d.screenshot(format='opencv')
                        active_list = UIMatcher.imgs_where(screen_shot_, ['img/queren.jpg', 'img/ok.bmp'])
                        if 'img/queren.jpg' in active_list:
                            x, y = active_list['img/queren.jpg']
                            self.d.click(x, y)
                        if 'img/ok.bmp' in active_list:
                            x, y = active_list['img/ok.bmp']
                            self.d.click(x, y)
                        time.sleep(8)
                        self.d.click(481, 369)
                        time.sleep(1)
                        continue
                    else:
                        self.d.click(371, 437)
                        time.sleep(0.7)
                        self.d.click(501, 468)  # important
                        time.sleep(2)
                        break
            self.d.click(933, 267)  # 下一位
            time.sleep(2)

        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        self.lockimg('img/zhuxianguanqia.jpg', elseclick=[(480, 513)], elsedelay=3)
        self.d.click(562, 253)
        time.sleep(3)
        self.lockimg('img/normal.jpg', elseclick=[(704, 84)], elsedelay=0.5, alldelay=1, at=(660, 72, 743, 94))
        self.d.click(923, 272)
        time.sleep(3)

    def setting(self):
        self.d.click(875, 517)
        time.sleep(2)
        self.d.click(149, 269)
        time.sleep(2)
        self.d.click(769, 87)
        time.sleep(1)
        self.d.click(735, 238)
        time.sleep(0.5)
        self.d.click(735, 375)
        time.sleep(0.5)
        self.d.click(479, 479)
        time.sleep(1)
        self.d.click(95, 516)

    # 对当前界面(x1,y1)->(x2,y2)的矩形内容进行OCR识别
    # 使用Baidu OCR接口
    # 离线接口还没写
    def baidu_ocr(self, x1, y1, x2, y2, size=1.0):
        # size表示相对原图的放大/缩小倍率，1.0为原图大小，2.0表示放大两倍，0.5表示缩小两倍
        # 默认原图大小（1.0）
        from aip import AipOcr
        print('初始化百度OCR识别')
        with open('baiduocr.txt', 'r') as faip:
            fconfig = faip.read()
        apiKey, secretKey = fconfig.split('\t')
        if len(apiKey) == 0 or len(secretKey) == 0:
            print('读取SecretKey或apiKey失败！')
            return -1
        config = {
            'appId': 'PCR',
            'apiKey': apiKey,
            'secretKey': secretKey
        }
        client = AipOcr(**config)

        screen_shot_ = self.d.screenshot(format="opencv")
        from numpy import rot90
        screen_shot_ = rot90(screen_shot_)  # 旋转90°
        part = screen_shot_[y1:y2, x1:x2]  # 对角线点坐标
        # cv2.imwrite('test.bmp', part)
        part = cv2.resize(part, None, fx=size, fy=size, interpolation=cv2.INTER_LINEAR)  # 利用resize调整图片大小
        # cv2.imshow('part',part)
        # cv2.waitKey(0)
        partbin = cv2.imencode('.jpg', part)[1]  # 转成base64编码（误）
        try:
            print('识别成功！')
            result = client.basicGeneral(partbin)
            return result
        except:
            print('百度云识别失败！请检查apikey和secretkey是否有误！')
            return -1

    def get_tili(self):
        # 利用baiduOCR获取当前体力值（要保证当前界面有‘主菜单’选项）
        # API key存放在baiduocr.txt中
        # 格式：apiKey secretKey（中间以一个\t作为分隔符）
        # 返回值：一个int类型整数；如果读取失败返回-1

        self.d.click(871, 513)  # 主菜单
        while True:  # 锁定帮助
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/bangzhu.jpg'):
                break
        # cv2.imwrite('all.png',screen_shot_)
        # part = screen_shot_[526:649, 494:524]
        ret = self.baidu_ocr(494, 526, 524, 649, 1)  # 获取体力区域的ocr结果
        if ret == -1:
            print('体力识别失败！')
            return -1
        else:
            return int(ret['words_result'][1]['words'].split('/')[0])

    def rename(self,name):  # 重命名
        self.d.click(871, 513)  # 主菜单
        self.lockimg('img/bangzhu.bmp', ifclick=[(370, 270)])# 锁定帮助 点击简介
        self.lockimg('img/bianji.bmp', ifclick=[(900, 140)])# 锁定 点击铅笔修改按钮
        self.lockimg('img/biangeng.bmp', ifclick=[(480, 270)])# 锁定 玩家名 点击游戏渲染编辑框
        time.sleep(1)
        self.d.click(290, 425)  # 点击编辑框
        self.d.clear_text()
        self.d.send_keys(name)
        self.d.click(880, 425)  # 点击确定
        time.sleep(0.5)
        self.d.click(590, 370)  # 变更按钮
        time.sleep(1)
        self.lockimg('img/bangzhu.bmp', elseclick=[(32, 32)])# 锁定帮助
        print('账号：', name, '已修改名字')
