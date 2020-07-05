# coding=utf-8
import time
from utils import *
import uiautomator2 as u2
from cv import *


# import matplotlib.pylab as plt


class Automator:
    def __init__(self, address, auto_task=False, auto_policy=True,
                 auto_goods=False, speedup=True):
        """
        device: 如果是 USB 连接，则为 adb devices 的返回结果；如果是模拟器，则为模拟器的控制 URL 。
        """
        self.d = u2.connect(address)
        self.dWidth, self.dHeight = self.d.window_size()
        self.appRunning = False
        self.switch = 0
        self.times = 3  # 总刷图次数

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

    def get_butt_stat(self, screen_shot, template_paths, threshold=0.84):
        # 此函数输入要判断的图片path,屏幕截图,阈值,返回大于阈值的path坐标字典
        self.dWidth, self.dHeight = self.d.window_size()
        return_dic = {}
        zhongxings, max_vals = UIMatcher.findpic(screen_shot, template_paths=template_paths)
        for i, name in enumerate(template_paths):
            print(name + '--' + str(round(max_vals[i], 3)), end=' ')
            if max_vals[i] > threshold:
                return_dic[name] = (zhongxings[i][0] * self.dWidth, zhongxings[i][1] * self.dHeight)
        print('')
        return return_dic

    def is_there_img(self, screen, img, threshold=0.84, cut=None):
        # 输入要判断的图片path，屏幕截图，返回是否存在大于阈值的图片的布尔值
        # cut: (x1,y1,x2,y2)
        if cut is not None:
            screen = screen[cut[1]:cut[3] + 1, cut[0]:cut[2] + 1]
        active_path = self.get_butt_stat(screen, [img], threshold)
        if img in active_path:
            return True
        else:
            return False

    def guochang(self, screen_shot, template_paths, suiji=1):
        # suji标号置1, 表示未找到时将点击左上角, 置0则不点击
        # 输入截图, 模板list, 得到下一次操作

        self.dWidth, self.dHeight = self.d.window_size()
        screen_shot = screen_shot
        template_paths = template_paths
        active_path = self.get_butt_stat(screen_shot, template_paths)
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

    def lockimg(self, img, ifclick=[], ifdelay=1, elseclick=[], elsedelay=0.5, alldelay=0.5):  # 锁定指定图像
        """
        @args:
            img:要匹配的图片目录
            ifclick:在识别到图片时要点击的坐标，列表，列表元素为坐标如(1,1)
            ifdelay:上述点击后延迟的时间
            ifclick:在找不到图片时要点击的坐标，列表，列表元素为坐标如(1,1)
            ifdelay:上述点击后延迟的时间
        @return:无
        """
        while True:  #
            screen_shot = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot, img):
                if ifclick != []:
                    for clicks in ifclick:
                        self.d.click(clicks[0], clicks[1])
                        time.sleep(ifdelay)
                break
            if elseclick != []:
                for clicks in elseclick:
                    self.d.click(clicks[0], clicks[1])
                    time.sleep(elsedelay)
            time.sleep(alldelay)

    def tichuhanghui(self):  # 踢出行会
        self.d.click(693, 430)  # 点击行会
        self.lockimg('img/zhiyuansheding.jpg', elseclick=[(1, 1)], alldelay=0.5)  # 锁定行会界面
        self.d.click(241, 350)  # 点击成员
        self.lockimg('img/chengyuanliebiao.bmp', ifclick=[(720, 97)], ifdelay=1)  # 点击排序按钮
        self.lockimg('img/ok.bmp', ifclick=[(289, 303), (587, 372)], ifdelay=1)  # 按战力降序 这里可以加一步调降序
        self.lockimg('img/chengyuanliebiao.bmp', ifclick=[(737, 200)], ifdelay=1)  # 点第一个人
        self.lockimg('img/jiaojie.bmp', ifclick=[(651, 174)], ifdelay=1)  # 踢出行会
        self.lockimg('img/ok.bmp', ifclick=[(590, 369)], ifdelay=1)  # 确认踢出
        self.lockimg('img/chengyuanliebiao.bmp', elseclick=[(1, 1)], alldelay=1)  # 锁定成员列表
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=0.5)  # 回首页

    def yaoqinghanghui(self, inviteUID):  # 邀请行会
        self.d.click(693, 430)  # 点击行会
        self.lockimg('img/zhiyuansheding.jpg', elseclick=[(1, 1)], alldelay=0.5)  # 锁定行会界面
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
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=0.5)  # 回首页

    def jieshouhanghui(self):
        self.d.click(693, 430)  # 点击行会
        self.lockimg('img/zujianhanghui.bmp', elseclick=[(1, 1)], alldelay=0.5)  # 锁定行会界面
        self.d.click(687, 35)  # 点击邀请列表
        time.sleep(1)
        self.d.click(704, 170)  # 点击邀请列表
        self.lockimg('img/jiaru.bmp', ifclick=[(839, 443)], ifdelay=1)  # 点击加入
        self.lockimg('img/ok.bmp', ifclick=[(597, 372)], ifdelay=1)  # 点击ok
        time.sleep(1)
        self.lockimg('img/zhiyuansheding.jpg', ifclick=[(85, 350)], alldelay=0.5)  # 点击支援设定
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
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=0.5)  # 回首页

    def login_auth(self, ac, pwd):
        need_auth = self.login(ac=ac, pwd=pwd)
        if need_auth:
            auth_name, auth_id = random_name(), CreatIDnum()
            self.auth(auth_name=auth_name, auth_id=auth_id)

    def init_home(self):
        self.lockimg('img/liwu.bmp', elseclick=[(1, 1)], elsedelay=0.5)  # 首页锁定
        time.sleep(0.5)
        self.lockimg('img/liwu.bmp', elseclick=[(1, 1)], elsedelay=0.2)  # 首页锁定
        time.sleep(0.5)
        # 这里防一波第二天可可萝跳脸教程
        screen_shot_ = self.d.screenshot(format='opencv')
        num_of_white, _, _ = UIMatcher.find_gaoliang(screen_shot_)
        if num_of_white < 50000:
            self.lockimg('img/renwu_1.bmp', elseclick=[(837, 433)], elsedelay=1)
            self.lockimg('img/liwu.bmp', elseclick=[(90, 514)], elsedelay=0.2)  # 首页锁定
            return
        if self.is_there_img(screen_shot_, 'img/kekeluo.bmp'):
            self.lockimg('img/renwu_1.bmp', elseclick=[(837, 433)], elsedelay=1)
            self.lockimg('img/liwu.bmp', elseclick=[(90, 514)], elsedelay=0.2)  # 首页锁定

    def sw_init(self):
        self.switch = 0

    def gonghuizhijia(self):  # 家园领取
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页
        self.d.click(622, 509)
        time.sleep(8)
        for _ in range(2):
            self.d.click(899, 429)  # 一键领取
            time.sleep(3)
            screen_shot_ = self.d.screenshot(format="opencv")
            self.guochang(screen_shot_, ['img/jyquanbushouqu.jpg'], suiji=0)
            screen_shot_ = self.d.screenshot(format="opencv")
            self.guochang(screen_shot_, ['img/guanbi.jpg'], suiji=0)
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页

    def mianfeiniudan(self):
        # 免费扭蛋
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页
        self.lockimg('img/liwu.bmp', ifclick=[(750, 510)], ifdelay=1)  # 点进扭蛋界面
        while True:
            # 跳过抽奖提示
            time.sleep(4)
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/niudan_sheding.jpg'):
                self.guochang(screen_shot_, ['img/niudan_sheding.jpg'], suiji=0)
                break
            else:
                time.sleep(1)
                self.d.click(473, 436)  # 手动点击
                time.sleep(2)
                break

        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/niudanputong.jpg'):
                self.guochang(screen_shot_, ['img/niudanputong.jpg'], suiji=0)
                self.d.click(722, 351)  # 点进扭蛋
                time.sleep(0.5)
                self.d.click(584, 384)
                break
            else:
                self.d.click(876, 75)  # 手动点击
                time.sleep(0.5)
                self.d.click(722, 351)  # 点进扭蛋
                time.sleep(0.5)
                self.d.click(584, 384)
                break
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页

    def mianfeishilian(self):
        # 免费十连
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页
        self.lockimg('img/liwu.bmp', ifclick=[(750, 510)], ifdelay=1)  # 点进扭蛋界面

        time.sleep(1)
        screen_shot_ = self.d.screenshot(format="opencv")
        if self.is_there_img(screen_shot_, 'img/mianfeishilian.jpg'):  # 仅当有免费十连时抽取免费十连
            self.d.click(872, 355)  # 点击十连
            time.sleep(1)
            self.d.click(592, 369)  # 确认

        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/liwu.bmp'):
                break
            self.d.click(900, 40)
            time.sleep(0.5)
            self.d.click(100, 505)
            time.sleep(0.5)
            self.d.click(100, 505)
            time.sleep(1)  # 首页锁定，保证回到首页

    def dianzan(self, sortflag=0):  # 行会点赞
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页
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
            self.lockimg('img/chengyuanliebiao.bmp', ifclick=[(720, 97)], ifdelay=1)  # 点击排序按钮
            self.lockimg('img/ok.bmp', ifclick=[(289, 303), (587, 372)], ifdelay=1)  # 按战力降序 这里可以加一步调降序
            self.d.click(818, 198)  # 点赞 战力降序第一个人
            time.sleep(2)
        else:
            self.d.click(829, 316)  # 点赞 职务降序（默认） 第二个人，副会长
            time.sleep(2)
        self.d.click(479, 381)
        screen_shot_ = self.d.screenshot(format="opencv")
        self.guochang(screen_shot_, ['img/ok.bmp'], suiji=0)
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=1)  # 回首页

    def shouqu(self):  # 收取全部礼物
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=1)  # 回首页
        screen_shot_ = self.d.screenshot(format="opencv")
        self.guochang(screen_shot_, ['img/liwu.bmp'], suiji=0)
        while True:  # 锁定收取履历（礼品盒）
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/shouqulvli.jpg'):
                self.d.click(809, 471)  # 点击全部收取
                time.sleep(1)
                self.d.click(589, 472)  # 2020-5-29 19:41 bug fixed
                break
        self.lockimg('img/liwu.bmp', elseclick=[(1, 1)], elsedelay=0.3)  # 回首页

    def shouqurenwu(self):  # 收取任务报酬
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/renwu.jpg'):
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
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页

    def change_acc(self):  # 切换账号
        self.d.click(871, 513)  # 主菜单
        while True:  # 锁定帮助
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/bangzhu.bmp'):
                break
        self.d.click(165, 411)  # 退出账号
        while True:  # 锁定帮助
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/ok.bmp'):
                break
        self.d.click(591, 369)  # ok
        time.sleep(1)
        print('-----------------------------')
        print('完成该任务')
        print('-----------------------------\r\n')

    def goumaitili(self, times):  # 购买体力，注意此函数参数默认在首页执行，其他地方执行要调整参数
        for i in range(times):
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页
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
                    if self.is_there_img(screen_shot_, 'img/quxiao2.jpg'):
                        break
                    self.d.click(189, 62)
                    time.sleep(2)
                self.d.click(596, 471)  # 第一次购买的位置
                while True:  # 锁定ok
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if self.is_there_img(screen_shot_, 'img/ok.bmp'):
                        self.guochang(screen_shot_, ['img/ok.bmp'], suiji=0)
                        break
        else:
            time.sleep(2)
            self.d.click(189, 62)
            while True:  # 锁定取消2
                screen_shot_ = self.d.screenshot(format="opencv")
                if self.is_there_img(screen_shot_, 'img/quxiao2.jpg'):
                    break
                self.d.click(189, 62)
                time.sleep(2)
            self.d.click(596, 471)  # 第一次购买的位置
            while True:  # 锁定ok
                screen_shot_ = self.d.screenshot(format="opencv")
                if self.is_there_img(screen_shot_, 'img/ok.bmp'):
                    self.guochang(screen_shot_, ['img/ok.bmp'], suiji=0)
                    break
            for i in range(times):  # 购买剩下的times次
                while True:  # 锁定取消2
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if self.is_there_img(screen_shot_, 'img/quxiao2.jpg'):
                        break
                time.sleep(3)
                self.d.click(816, 478)  # 购买10次
                while True:  # 锁定ok
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if self.is_there_img(screen_shot_, 'img/ok.bmp'):
                        self.guochang(screen_shot_, ['img/ok.bmp'], suiji=0)
                        break

        self.lockimg('img/liwu.bmp', elseclick=[(1, 1)], elsedelay=0.5)  # 回首页

    def goumaijingyan(self):
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页
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
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页

    def hanghui(self):  # 自动行会捐赠
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页
        time.sleep(1)
        self.d.click(693, 436)
        time.sleep(1)
        while True:  # 6-17修改：减少opencv使用量提高稳定性
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/zhiyuansheding.jpg'):
                time.sleep(3)  # 加载行会聊天界面会有延迟
                for _ in range(3):
                    time.sleep(2)
                    screen_shot = self.d.screenshot(format="opencv")
                    if self.is_there_img(screen_shot, 'img/juanzengqingqiu.jpg'):
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
                        screen_shot = self.d.screenshot(format="opencv")
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                        time.sleep(1)
                while True:
                    self.d.click(1, 1)
                    time.sleep(1)
                    screen_shot = self.d.screenshot(format="opencv")
                    if self.is_there_img(screen_shot, 'img/zhiyuansheding.jpg'):
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
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=1)  # 回首页

    def shuatuzuobiao(self, x, y, times):  # 刷图函数，xy为该图的坐标，times为刷图次数
        if self.switch == 0:
            tmp_cout = 0
            self.d.click(x, y)
            time.sleep(0.5)
        else:
            print('>>>无扫荡券或者无体力！', '结束 全部 刷图任务！<<<\r\n')
        if self.switch == 0:
            while True:  # 锁定加号
                screen_shot_ = self.d.screenshot(format="opencv")
                if self.is_there_img(screen_shot_, 'img/jiahao.bmp'):
                    # screen_shot = a.d.screenshot(format="opencv")
                    for i in range(times - 1):  # 基础1次
                        # a.guochang(screen_shot,['img/jiahao.bmp'])
                        # 扫荡券不必使用opencv来识别，降低效率
                        self.d.click(876, 334)
                        # time.sleep(0.2)
                    time.sleep(0.3)
                    self.d.click(758, 330)  # 使用扫荡券的位置 也可以用OpenCV但是效率不够而且不能自由设定次数
                    time.sleep(0.3)
                    screen_shot = self.d.screenshot(format="opencv")
                    if self.is_there_img(screen_shot, 'img/ok.bmp'):
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    else:
                        time.sleep(0.5)
                        self.d.click(588, 370)
                    # screen_shot = a.d.screenshot(format="opencv")
                    # a.guochang(screen_shot,['img/shiyongsanzhang.jpg'])
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if self.is_there_img(screen_shot_, 'img/tilibuzu.jpg'):
                        print('>>>无扫荡券或者无体力！结束此次刷图任务！<<<\r\n')
                        self.switch = 1
                        self.d.click(677, 458)  # 取消
                        break
                    screen_shot = self.d.screenshot(format="opencv")
                    if self.is_there_img(screen_shot, 'img/tiaoguo.jpg'):
                        self.guochang(screen_shot, ['img/tiaoguo.jpg'], suiji=0)
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    else:
                        time.sleep(1)
                        self.d.click(475, 481)  # 手动点击跳过
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    break
                else:
                    if tmp_cout < 5:
                        # 计时5次就失败
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
            if self.is_there_img(screen_shot_, 'img/normal.jpg'):
                break

    def shuajingyan(self, map):
        """
        刷图刷1-1
        map为主图
        """
        # 体力单独设置
        for i in range(7):
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if self.is_there_img(screen_shot_, 'img/liwu.bmp'):
                    break
                self.d.click(100, 505)
                time.sleep(1)  # 首页锁定，保证回到首页
            self.d.click(320, 31)
            time.sleep(0.5)
            screen_shot = self.d.screenshot(format="opencv")
            self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
            time.sleep(0.5)
            screen_shot = self.d.screenshot(format="opencv")
            self.guochang(screen_shot, ['img/zhandou_ok.jpg'], suiji=1)
            self.d.click(100, 505)  # 点击一下首页比较保险
        # 进入冒险
        time.sleep(2)
        self.d.click(480, 505)
        time.sleep(2)

        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/dixiacheng.jpg'):
                break
        self.d.click(562, 253)
        time.sleep(2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/normal.jpg'):
                break
        for i in range(map):
            self.d.click(27, 272)
            time.sleep(3)
        self.shuatuzuobiao(106, 279, 160)  # 1-1 刷7次体力为佳

        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页

    def shuatu8(self):
        # 进入冒险
        time.sleep(2)
        self.d.click(480, 505)
        time.sleep(2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/dixiacheng.jpg'):
                break
        self.d.click(562, 253)
        time.sleep(2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/normal.jpg'):
                break
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
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页

    def shuatu10(self):
        # 进入冒险
        time.sleep(2)
        self.d.click(480, 505)
        time.sleep(2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/dixiacheng.jpg'):
                break
        self.d.click(562, 253)
        time.sleep(2)
        for _ in range(1):
            # 左移到10图
            self.d.click(27, 272)
            time.sleep(3)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/normal.jpg'):
                break
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
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页

    def shuatu11(self):
        # 进入冒险
        time.sleep(2)
        self.d.click(480, 505)
        time.sleep(2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/dixiacheng.jpg'):
                break
        self.d.click(562, 253)
        time.sleep(2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/normal.jpg'):
                break
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
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页

    def dixiacheng(self):  # 地下城
        time.sleep(2)
        self.d.click(1, 1)  # 可可萝教程跳过
        time.sleep(0.5)
        tmp_cout = 0
        tmp_cout2 = 0
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/dixiacheng.jpg'):
                break
            self.d.click(480, 505)
            time.sleep(1)
        self.d.click(900, 138)
        time.sleep(3)
        while True:
            time.sleep(4)
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/chetui.jpg'):  # 避免某些农场号刚买回来已经进了地下城
                # 撤退
                self.d.click(808, 435)
                time.sleep(1)
                self.d.click(588, 371)
                break
            else:
                time.sleep(3)
                # 撤退
                self.d.click(808, 435)
                time.sleep(1)
                self.d.click(588, 371)
                break
        screen_shot_ = self.d.screenshot(format="opencv")
        if self.is_there_img(screen_shot_, 'img/caidan_yuan.jpg'):
            self.d.click(917, 39)  # 菜单
            time.sleep(1)
            self.d.click(807, 44)  # 跳过
            time.sleep(1)
            self.d.click(589, 367)  # 跳过ok
            time.sleep(1)
        # 下面这段因为调试而注释了，实际使用时要加上
        while True:
            time.sleep(2)
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/caidan_yuan.jpg'):
                self.d.click(917, 39)  # 菜单
                time.sleep(1)
                self.d.click(807, 44)  # 跳过
                time.sleep(1)
                self.d.click(589, 367)  # 跳过ok
                time.sleep(1)
            if tmp_cout < 3:  # 预防卡死，3次错误失败后直接进行下一步
                tmp_cout = tmp_cout + 1
                # print(tmp_cout)
                if self.is_there_img(screen_shot_, 'img/yunhai.bmp'):
                    self.d.click(233, 311)
                    time.sleep(1)
                    while True:
                        screen_shot_ = self.d.screenshot(format="opencv")
                        if tmp_cout2 < 3:  # 预防卡死，10次错误失败后直接进行下一步
                            tmp_cout2 = tmp_cout2 + 1
                            if self.is_there_img(screen_shot_, 'img/ok.bmp'):
                                self.guochang(screen_shot_, ['img/ok.bmp'], suiji=0)
                                time.sleep(1)
                                break
                            else:
                                self.d.click(592, 369)  # 点击ok
                                break
                        else:
                            tmp_cout2 = 0
                            print('>>>识别卡死跳过\r\n')
                            break
            else:
                tmp_cout = 0
                print('>>>识别卡死跳过\r\n')
                break

        while True:
            time.sleep(2)
            screen_shot_ = self.d.screenshot(format="opencv")
            if tmp_cout < 5:  # 预防卡死，10次错误失败后直接进行下一步
                tmp_cout = tmp_cout + 1
                if self.is_there_img(screen_shot_, 'img/chetui.jpg'):
                    self.d.click(667, 360)  # 1层
                    time.sleep(1)
                    self.d.click(833, 456)  # 挑战
                    time.sleep(1)
                    break
            else:
                tmp_cout = 0
                print('>>>识别卡死跳过\r\n')
                break
        while True:
            time.sleep(2)
            screen_shot_ = self.d.screenshot(format="opencv")
            if tmp_cout < 5:  # 预防卡死，10次错误失败后直接进行下一步
                tmp_cout = tmp_cout + 1
                if self.is_there_img(screen_shot_, 'img/zhiyuan.jpg'):
                    self.d.click(100, 173)  # 第一个人
                    time.sleep(1)
                    screen_shot = self.d.screenshot(format="opencv")
                    self.guochang(screen_shot, ['img/zhiyuan.jpg'], suiji=0)
                    break
            else:
                tmp_cout = 0
                print('>>>识别卡死跳过\r\n')
                break

        screen_shot_ = self.d.screenshot(format="opencv")
        if self.is_there_img(screen_shot_, 'img/dengjixianzhi.jpg'):
            self.d.click(213, 208)  # 如果等级不足，就支援的第二个人
            time.sleep(1)
        else:
            self.d.click(100, 173)  # 支援的第一个人
            time.sleep(1)
            self.d.click(213, 208)  # 以防万一

        self.d.click(833, 470)  # 战斗开始
        time.sleep(1)
        while True:
            time.sleep(2)
            screen_shot_ = self.d.screenshot(format="opencv")
            if tmp_cout < 5:  # 预防卡死，10次错误失败后直接进行下一步
                tmp_cout = tmp_cout + 1
                if self.is_there_img(screen_shot_, 'img/ok.bmp'):
                    self.guochang(screen_shot_, ['img/ok.bmp'], suiji=0)
                    break
            else:
                tmp_cout = 0
                print('>>>识别卡死跳过\r\n')
                break

        while True:  # 战斗中快进
            time.sleep(2)
            screen_shot_ = self.d.screenshot(format="opencv")
            if tmp_cout < 5:  # 预防卡死，10次错误失败后直接进行下一步
                tmp_cout = tmp_cout + 1
                if self.is_there_img(screen_shot_, 'img/kuaijin.jpg'):
                    self.d.click(913, 494)  # 点击快进
                    time.sleep(1)
                if self.is_there_img(screen_shot_, 'img/kuaijin_1.jpg'):
                    self.d.click(913, 494)  # 点击快进
                    time.sleep(1)
            else:
                tmp_cout = 0
                print('>>>识别卡死跳过\r\n')
                break
        while True:  # 结束战斗返回
            time.sleep(2)
            screen_shot_ = self.d.screenshot(format="opencv")
            if tmp_cout < 5:  # 预防卡死，10次错误失败后直接进行下一步
                if self.is_there_img(screen_shot_, 'img/yunhai.bmp', threshold=0.8):
                    print('>>>今天次数用完!\r\n')
                    break
                if self.is_there_img(screen_shot_, 'img/shanghaibaogao.jpg'):
                    time.sleep(3)
                    self.guochang(screen_shot_, ['img/xiayibu.jpg', 'img/qianwangdixiacheng.jpg'], suiji=0)
                    if self.is_there_img(screen_shot_, 'img/duiwu.jpg'):
                        self.guochang(screen_shot_, ['img/xiayibu.jpg', 'img/qianwangdixiacheng.jpg'], suiji=0)
                        break
                    else:
                        tmp_cout = tmp_cout + 1
                        print('>>>无法识别到图像，坐标点击\r\n')
                        time.sleep(3)
                        self.d.click(828, 502)
                        break
                elif self.is_there_img(screen_shot_, 'img/chetui.jpg'):
                    time.sleep(3)
                    # 撤退
                    self.d.click(808, 435)
                    time.sleep(1)
                    self.d.click(588, 371)
                    break
            else:
                tmp_cout = 0
                print('>>>识别卡死跳过\r\n')
                break

        self.d.click(1, 1)  # 取消显示结算动画
        time.sleep(1)
        while True:  # 撤退地下城
            time.sleep(2)
            screen_shot_ = self.d.screenshot(format="opencv")
            if tmp_cout < 5:  # 预防卡死，10次错误失败后直接进行下一步
                tmp_cout = tmp_cout + 1
                if self.is_there_img(screen_shot_, 'img/chetui.jpg'):
                    for i in range(3):
                        # 保险措施
                        self.d.click(808, 435)
                        time.sleep(1)
                        self.d.click(588, 371)
                    self.guochang(screen_shot_, ['img/chetui.jpg'], suiji=0)
                    screen_shot = self.d.screenshot(format="opencv")
                    self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    break
                else:
                    tmp_cout = 0
                    print('>>>识别卡死跳过\r\n')
                    break
            self.d.click(1, 1)  #
            time.sleep(1)

        while True:  # 首页锁定
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/liwu.bmp'):
                break
            self.guochang(screen_shot_, ['img/xiayibu.jpg', 'img/qianwangdixiacheng.jpg'], suiji=0)  # 防卡死
            self.guochang(screen_shot_, ['img/chetui.jpg'], suiji=0)
            screen_shot = self.d.screenshot(format="opencv")
            self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
            self.d.click(100, 505)
            time.sleep(1)  # 保证回到首页

    def dixiachengzuobiao(self, x, y, auto, team=0):
        # 完整刷完地下城函数
        # 参数：
        # x：目标层数的x轴坐标
        # y：目标层数的y轴坐标
        # auto：取值为0/1,auto=0时不点击auto按钮，auto=1时点击auto按钮
        # team：取值为0/1/2，team=0时不换队，team=1时更换为队伍列表中的1队，team=2时更换为队伍列表中的2队

        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/chetui.jpg'):
                break
            self.d.click(1, 1)
            time.sleep(1)
        time.sleep(1)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/chetui.jpg'):
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
            if self.is_there_img(screen_shot_, 'img/zhandoukaishi.jpg'):
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
                if self.is_there_img(screen_shot_, 'img/zhandoukaishi.jpg'):
                    break
                time.sleep(0.5)

        self.d.click(837, 447)  # 战斗开始
        time.sleep(2)

        while True:  # 战斗中快进
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/caidan.jpg'):
                if auto == 1:
                    time.sleep(0.5)
                    self.d.click(912, 423)  # 点auto按钮
                    time.sleep(1)
                break
        while True:  # 结束战斗返回
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/shanghaibaogao.jpg'):
                while True:
                    screen_shot = self.d.screenshot(format="opencv")
                    if self.is_there_img(screen_shot, 'img/xiayibu.jpg'):
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
        self.d.click(480, 505)
        time.sleep(1)
        while True:  # 锁定地下城
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/dixiacheng.jpg'):
                break
            self.d.click(480, 505)
            time.sleep(1)
        self.d.click(734, 142)  # 探索
        time.sleep(3.5)
        while True:  # 锁定凯留头（划掉）返回按钮
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/fanhui.bmp', cut=(16, 12, 54, 48)):
                break
            self.d.click(1, 1)
            time.sleep(0.5)
        # 经验
        self.d.click(592, 255)  # 经验
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
            if self.is_there_img(screen_shot_, 'img/tiaozhan.jpg'):
                break
            time.sleep(0.5)
        self.d.drag(876, 329, 876, 329, 0.5)  # +号
        time.sleep(0.5)
        self.d.click(752, 327)  # 扫荡
        time.sleep(0.5)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/ok.bmp'):
                self.d.click(590, 363)  # ok
                time.sleep(0.5)
                break
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/home.jpg'):
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
            if self.is_there_img(screen_shot_, 'img/tiaozhan.jpg'):
                break
            time.sleep(0.5)
        self.d.drag(876, 329, 876, 329, 0.5)  # +号
        time.sleep(0.5)
        self.d.click(752, 327)  # 扫荡
        time.sleep(0.5)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/ok.bmp'):
                self.d.click(590, 363)  # ok
                time.sleep(0.5)
                break
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/home.jpg'):
                break
            self.d.click(1, 1)
            time.sleep(1)
        # 完成战斗后
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页

    def dixiachengDuanya(self):  # 地下城 断崖（第三个）
        self.d.click(480, 505)
        time.sleep(1)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/dixiacheng.jpg'):
                break
            self.d.click(480, 505)
            time.sleep(1)
        self.d.click(900, 138)
        time.sleep(1)

        # 下面这段因为调试而注释了，实际使用时要加上
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/chetui.jpg'):  # 避免某些农场号刚买回来已经进了地下城
                break
            if self.is_there_img(screen_shot_, 'img/yunhai.bmp'):
                self.d.click(712, 267)  # 断崖
                time.sleep(1)
                while True:
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if self.is_there_img(screen_shot_, 'img/ok.bmp'):
                        break
                self.d.click(592, 369)  # 点击ok
                time.sleep(1)
                break
        # 刷地下城
        self.dixiachengzuobiao(642, 371, 1, 1)  # 1层，点auto按钮
        self.dixiachengzuobiao(368, 276, 0)  # 2层
        self.dixiachengzuobiao(627, 263, 0, 2)  # 3层
        self.dixiachengzuobiao(427, 274, 1)  # 4层，点auto按钮
        self.dixiachengzuobiao(199, 275, 0)  # 5层
        self.dixiachengzuobiao(495, 288, 0)  # 6层
        self.dixiachengzuobiao(736, 291, 0)  # 7层
        self.dixiachengzuobiao(460, 269, 0)  # 8层
        self.dixiachengzuobiao(243, 274, 0)  # 9层
        self.dixiachengzuobiao(654, 321, 0, 1)  # 10层

        # 完成战斗后
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页

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
            if self.is_there_img(screen_shot_, lockpic, cut=screencut):
                break
            self.d.click(1, 138)
            time.sleep(1)
        self.d.click(x, y)
        time.sleep(1.5)
        self.d.click(840, 454)
        time.sleep(0.7)

        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.get_butt_stat(screen_shot_, ['img/kuaijin.jpg', 'img/kuaijin_1.jpg']) != {}:
                break
            self.d.click(840, 454)  # 点到进入战斗画面
            time.sleep(0.7)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            result = self.get_butt_stat(screen_shot_, ['img/kuaijin.jpg', 'img/auto.jpg', 'img/wanjiadengji.jpg'])
            if 'img/kuaijin.jpg' in result:
                x, y = result['img/kuaijin.jpg']
                self.d.click(x, y)
                time.sleep(1)
            if 'img/auto.jpg' in result:
                x, y = result['img/auto.jpg']
                self.d.click(x, y)
                time.sleep(1)
            if 'img/wanjiadengji.jpg' in result:  # 战斗结束
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
                if self.is_there_img(screen_shot_, lockpic, cut=screencut):
                    break
                elif self.is_there_img(screen_shot_, 'img/xiayibu.jpg'):
                    self.d.click(832, 506)
                else:
                    self.d.click(1, 100)
            while True:  # 两次确认回到挑战界面
                self.d.click(1, 100)
                time.sleep(0.5)
                screen_shot_ = self.d.screenshot(format="opencv")
                if self.is_there_img(screen_shot_, lockpic, cut=screencut):
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

            active_path = self.get_butt_stat(screen_shot_, ['img/liwu.bmp', 'img/jiaruhanghui.jpg', 'img/xiayibu.jpg',
                                                            'img/niudan_jiasu.jpg', 'img/wuyuyin.jpg',
                                                            'img/tiaoguo.jpg', 'img/zhuye.jpg', 'img/caidan_yuan.jpg'])
            if 'img/liwu.bmp' in active_path:
                break
            elif 'img/jiaruhanghui.jpg' in active_path:
                break
            elif 'img/xiayibu.jpg' in active_path:
                x, y = active_path['img/xiayibu.jpg']
                self.d.click(x, y)
                time.sleep(2)
            elif 'img/niudan_jiasu.jpg' in active_path:
                x, y = active_path['img/niudan_jiasu.jpg']
                self.d.click(x, y)
            elif 'img/wuyuyin.jpg' in active_path:
                x, y = active_path['img/wuyuyin.jpg']
                self.d.click(x, y)
                time.sleep(3)
            elif 'img/tiaoguo.jpg' in active_path:
                x, y = active_path['img/tiaoguo.jpg']
                self.d.click(x, y)
                time.sleep(3)
            elif 'img/zhuye.jpg' in active_path:
                x, y = active_path['img/zhuye.jpg']
                self.d.click(x, y)
            elif 'img/caidan_yuan.jpg' in active_path:
                x, y = active_path['img/caidan_yuan.jpg']
                self.d.click(x, y)
                time.sleep(0.7)
                self.d.click(804, 45)
                time.sleep(0.7)
                self.d.click(593, 372)
                time.sleep(2)
            else:
                self.d.click(1, 100)
                time.sleep(2)
            time.sleep(0.5)
        # 返回冒险
        self.d.click(480, 505)
        time.sleep(2)
        self.lockimg('img/zhuxianguanqia.jpg', elseclick=[(480, 513)], elsedelay=0.5)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/zhuxianguanqia.jpg'):
                self.d.click(562, 253)
                time.sleep(0.5)
            else:
                break
        time.sleep(3)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/normal.jpg'):
                break
            self.d.click(704, 84)
            time.sleep(0.5)

    def qianghua(self):
        time.sleep(3)
        self.d.click(215, 513)  # 角色
        time.sleep(3)
        self.d.click(177, 145)  # First
        time.sleep(3)
        for i in range(5):
            print("Now: ", i)
            while True:
                screen_shot_ = self.d.screenshot(format='opencv')
                if self.is_there_img(screen_shot_, 'img/keyihuode.jpg'):
                    self.d.click(374, 435)
                    time.sleep(1)
                    screen_shot_ = self.d.screenshot(format='opencv')
                    if self.is_there_img(screen_shot_, 'img/tuijianguanqia.jpg'):
                        if self.is_there_img(screen_shot_, 'img/sanxingtongguan.jpg'):
                            # 装备可刷
                            self.guochang(screen_shot_, ['img/sanxingtongguan.jpg'], suiji=0)
                            time.sleep(1)
                            self.d.click(877, 333)
                            time.sleep(0.3)
                            self.d.click(877, 333)
                            time.sleep(0.3)
                            self.d.click(752, 333)
                            time.sleep(0.7)
                            self.d.click(589, 371)
                            self.lockimg('img/zidongqianghua.jpg', elseclick=[(1, 100)], elsedelay=0.5, alldelay=1)
                            self.d.click(371, 437)
                            time.sleep(0.7)
                            self.d.click(501, 468)  # important
                            time.sleep(2)
                            continue
                        else:
                            # 装备不可刷
                            self.d.click(501, 468)  # important
                            time.sleep(1)
                            break
                    else:
                        self.d.click(501, 468)  # important
                        time.sleep(3)
                        continue
                else:
                    # 没有可以获得
                    if self.is_there_img(screen_shot_, 'img/ranktisheng.jpg'):
                        self.d.click(250, 338)
                        time.sleep(2)
                        screen_shot_ = self.d.screenshot(format='opencv')
                        active_list = self.get_butt_stat(screen_shot_, ['img/queren.jpg', 'img/ok.bmp'])
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

        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页
        self.lockimg('img/zhuxianguanqia.jpg', elseclick=[(480, 513)], elsedelay=3)
        self.d.click(562, 253)
        time.sleep(3)
        self.lockimg('img/normal.jpg', elseclick=[(704, 84)], elsedelay=0.5, alldelay=1)
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
    def baidu_ocr(self, x1, y1, x2, y2):
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
        part = screen_shot_[y1:y2, x1:x2]
        from numpy import rot90
        part = rot90(part)  # 图片旋转90度
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
            if self.is_there_img(screen_shot_, 'img/bangzhu.jpg'):
                break
        # cv2.imwrite('all.png',screen_shot_)
        # part = screen_shot_[526:649, 494:524]
        ret = self.baidu_ocr(494, 526, 524, 649)  # 获取体力区域的ocr结果
        if ret == -1:
            print('体力识别失败！')
            return -1
        else:
            return int(ret['words_result'][1]['words'].split('/')[0])
