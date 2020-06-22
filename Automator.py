# coding=utf-8
import uiautomator2 as u2
import time
from utils import *
from cv import *
#import matplotlib.pylab as plt


class Automator:
    def __init__(self, address,auto_task=False, auto_policy=True,
                 auto_goods=False, speedup=True):
        """
        device: 如果是 USB 连接，则为 adb devices 的返回结果；如果是模拟器，则为模拟器的控制 URL 。
        """
        self.d = u2.connect(address)
        self.dWidth, self.dHeight = self.d.window_size()
        self.appRunning = False


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


    def login(self,ac,pwd):
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
            return 1#说明要进行认证
        else:
            return 0#正常


    def auth(self,auth_name, auth_id):
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_authentication_name").click()
        self.d.clear_text()
        self.d.send_keys(str(auth_name))
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_authentication_id_number").click()
        self.d.clear_text()
        self.d.send_keys(str(auth_id))
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_authentication_submit").click()
        self.d(resourceId="com.bilibili.priconne:id/bagamesdk_auth_success_comfirm").click()


    def get_butt_stat(self,screen_shot,template_paths,threshold=0.84):
        #此函数输入要判断的图片path,屏幕截图,阈值,返回大于阈值的path坐标字典
        self.dWidth, self.dHeight = self.d.window_size()
        return_dic = {}
        zhongxings, max_vals = UIMatcher.findpic(screen_shot, template_paths=template_paths)
        for i, name in enumerate(template_paths):
            print(name + '--' + str(round(max_vals[i], 3)), end=' ')
            if max_vals[i]>threshold:
                return_dic[name]=(zhongxings[i][0] *self.dWidth, zhongxings[i][1] * self.dHeight)
        print('')
        return return_dic


    def is_there_img(self,screen,img):
        #输入要判断的图片path，屏幕截图，返回是否存在大于阈值的图片的布尔值
        self.dWidth, self.dHeight = self.d.window_size()
        active_path = self.get_butt_stat(screen,[img])
        if img in active_path:
            return True
        else:
            return False


    def guochang(self,screen_shot,template_paths,suiji = 1):
        # suji标号置1, 表示未找到时将点击左上角, 置0则不点击
        #输入截图, 模板list, 得到下一次操作

        self.dWidth, self.dHeight = self.d.window_size()
        screen_shot = screen_shot
        template_paths = template_paths
        active_path = self.get_butt_stat(screen_shot,template_paths)
        if active_path:
            print(active_path)
            if 'img/caidan_tiaoguo.jpg'in active_path:
                x,y = active_path['img/caidan_tiaoguo.jpg']
                self.d.click(x, y)
            else:
                for name, (x,y) in active_path.items():
                    print(name)
                    self.d.click(x, y)
            time.sleep(0.5)
        else:
            if suiji:
                print('未找到所需的按钮,将点击左上角')
                self.d.click( 0.1*self.dWidth,  0.1*self.dHeight)
            else:
                print('未找到所需的按钮,无动作')


    def login_auth(self,ac,pwd):
        need_auth = self.login(ac=ac,pwd=pwd)
        if need_auth:
            auth_name,auth_id = random_name(), CreatIDnum()
            self.auth(auth_name =auth_name ,auth_id = auth_id)


    def init_home(self):
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/liwu.jpg'):
                break
            self.d.click(1,1)
            time.sleep(0.5)#保证回到首页    
        time.sleep(0.5)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/liwu.jpg'):
                break
            self.d.click(1,1)
            time.sleep(0.2)#保证回到首页
            self.d.click(100,505)


    def gonghuizhijia(self):  # 家园领取
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/liwu.jpg'):
                break
            self.d.click(100, 505)
            time.sleep(1)  # 首页锁定，保证回到首页
        self.d.click(622, 509)
        time.sleep(8)
        while True:
            if self.is_there_img(screen_shot_, 'img/caidan_yuan.jpg'):
                self.d.click(917, 39)  # 菜单
                time.sleep(1)
                self.d.click(807, 44)  # 跳过
                time.sleep(1)
                self.d.click(589, 367)  # 跳过ok
                time.sleep(1)
                time.sleep(8)
            else:
                break
        for i in range(2):
            self.d.click(899, 429)  # 一键领取
            time.sleep(3)
            screen_shot_ = self.d.screenshot(format="opencv")
            self.guochang(screen_shot_, ['img/jyquanbushouqu.jpg'], suiji=0)
            screen_shot_ = self.d.screenshot(format="opencv")
            self.guochang(screen_shot_, ['img/guanbi.jpg'], suiji=0)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/liwu.jpg'):
                break
            self.d.click(100, 505)
            time.sleep(1)  # 首页锁定，保证回到首页


    def mianfeiniudan(self):
        # 免费扭蛋
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/liwu.jpg'):
                break
            self.d.click(100, 505)
            time.sleep(1)  # 首页锁定，保证回到首页
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/liwu.jpg'):
                self.d.click(750, 510) # 点进扭蛋界面
                time.sleep(1)
                break

        while True:
            # 跳过抽奖提示
            time.sleep(1)
            if self.is_there_img(screen_shot_, 'img/niudan_sheding.jpg'):
                screen_shot_ = self.d.screenshot(format="opencv")
                self.guochang(screen_shot_, ['img/niudan_sheding.jpg'], suiji=0)
                break
            else:
                time.sleep(1)
                self.d.click(473, 436)  # 手动点击
                time.sleep(2)
                break

        while True:
            if self.is_there_img(screen_shot_, 'img/niudanputong.jpg'):
                screen_shot_ = self.d.screenshot(format="opencv")
                self.guochang(screen_shot_, ['img/niudanputong.jpg'], suiji=0)
                self.d.click(722, 351)  # 点进扭蛋
                time.sleep(0.5)
                self.d.click(584, 384)
                break
            else:
                self.d.click(821, 75) # 手动点击
                time.sleep(0.5)
                self.d.click(722, 351)  # 点进扭蛋
                time.sleep(0.5)
                self.d.click(584, 384)
                break
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/liwu.jpg'):
                break
            self.d.click(100, 505)
            time.sleep(1)  # 首页锁定，保证回到首页


    def dianzan(self):  # 行会点赞
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/liwu.jpg'):
                break
            self.d.click(100,505)
            time.sleep(1)#首页锁定，保证回到首页
        # 进入行会
        time.sleep(3)
        screen_shot_ = self.d.screenshot(format="opencv")
        for i in range(2):
            time.sleep(3)
            self.guochang(screen_shot_, ['img/zhandou_ok.jpg'], suiji=0)
        self.d.click(688, 432)
        time.sleep(3)
        self.d.click(239, 351)
        time.sleep(2)
        self.d.click(829, 316)  #点赞 职务降序（默认） 第二个人，副会长
        time.sleep(2)
        self.d.click(479, 381)
        self.guochang(screen_shot_, ['img/ok.jpg'], suiji=0)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/liwu.jpg'):
                break
            self.d.click(100,505)
            self.d.click(1,1)
            time.sleep(1)#首页锁定，保证回到首页


    def shouqu(self):#收取全部礼物
        while True:#锁定回到首页
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/liwu.jpg'):
                break
            self.d.click(100,505)
            time.sleep(0.3)
            self.d.click(1,1)
        self.guochang(screen_shot_, ['img/liwu.jpg'],suiji=0)
        while True:#锁定收取履历（礼品盒）
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/shouqulvli.jpg'):
                self.d.click(809,471)#点击全部收取
                time.sleep(1)
                self.d.click(589,472)#2020-5-29 19:41 bug fixed
                break
        while True:#锁定回到首页
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/liwu.jpg'):
                break
            self.d.click(1,1)#礼品盒有特殊性，不能点（100,505），会被挡住
            time.sleep(0.3)


    def shouqurenwu(self):#收取任务报酬
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/renwu.jpg'):
                self.guochang(screen_shot_, ['img/renwu.jpg'],suiji=0)
                break
            self.d.click(1,1)
            time.sleep(1)
        time.sleep(2)
        self.d.click(846,437)#全部收取
        time.sleep(1)
        self.d.click(100,505)
        time.sleep(0.5)
        self.d.click(100,505)
        time.sleep(1.5)
        while True:#锁定回到首页
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/liwu.jpg'):
                break
            self.d.click(100,505)
            time.sleep(0.5)


    def goumaimana(self):#该函数只能在首页运行但未写首页锁定，请注意debug
        self.d.click(189,62)
        while True:#锁定取消2
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/quxiao2.jpg'):
                break
            self.d.click(189,62)
            time.sleep(0.5)
        self.d.click(596,471)#第一次购买的位置
        while True:#锁定ok
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/ok.jpg'):
                self.guochang(screen_shot_, ['img/ok.jpg'],suiji=0)
                break
        for i in range(7):#购买剩下的7次
            while True:#锁定取消2
                screen_shot_ = self.d.screenshot(format="opencv")
                if self.is_there_img(screen_shot_,'img/quxiao2.jpg'):
                    break
            self.d.click(816,478)#购买10次
            while True:#锁定ok
                screen_shot_ = self.d.screenshot(format="opencv")
                if self.is_there_img(screen_shot_,'img/ok.jpg'):
                    self.guochang(screen_shot_, ['img/ok.jpg'],suiji=0)
                    break
        while True:#锁定首页
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/liwu.jpg'):
                break
            self.d.click(1,1)
            time.sleep(0.5)#保证回到首页


    def change_acc(self):#切换账号
        self.d.click(871, 513)#主菜单
        while True:#锁定帮助
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/bangzhu.jpg'):
                break
        self.d.click(165, 411)#退出账号
        while True:#锁定帮助
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/ok.jpg'):
                break
        self.d.click(591, 369)#ok
        time.sleep(1)
        print('-----------------------------')
        print('完成该任务')
        print('-----------------------------')


    def goumaitili(self):#购买体力，注意此函数参数默认在首页执行，其他地方执行要调整参数
        for i in range(3):
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if self.is_there_img(screen_shot_,'img/liwu.jpg'):
                    break
                self.d.click(100,505)
                time.sleep(1)#首页锁定，保证回到首页
            self.d.click(320,31)
            time.sleep(1)
            screen_shot = self.d.screenshot(format="opencv")
            self.guochang(screen_shot,['img/ok.jpg'], suiji=0)
            time.sleep(1)
            screen_shot = self.d.screenshot(format="opencv")
            self.guochang(screen_shot,['img/zhandou_ok.jpg'], suiji=1)
            self.d.click(100,505)#点击一下首页比较保险


    def hanghui(self):#自动行会捐赠
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/liwu.jpg'):
                break
            self.d.click(100,505)
            time.sleep(1)#首页锁定，保证回到首页
        time.sleep(1)
        self.d.click(693, 436)
        time.sleep(1)
        while True:#6-17修改：减少opencv使用量提高稳定性
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/zhiyuansheding.jpg'):
                time.sleep(3)#加载行会聊天界面会有延迟
                screen_shot = self.d.screenshot(format="opencv")
                if self.is_there_img(screen_shot,'img/juanzengqingqiu.jpg'):
                    self.d.click(367, 39)#点击定位捐赠按钮
                    time.sleep(2)
                    screen_shot = self.d.screenshot(format="opencv")
                    self.guochang(screen_shot, ['img/juanzeng.jpg'],suiji=0)
                    time.sleep(1)
                    self.d.click(644, 385)#点击max
                    time.sleep(1)
                    screen_shot = self.d.screenshot(format="opencv")
                    self.guochang(screen_shot, ['img/ok.jpg'],suiji=0)
                    time.sleep(1)
                    while True:
                        self.d.click(1, 1)
                        time.sleep(1)
                        screen_shot = self.d.screenshot(format="opencv")
                        if self.is_there_img(screen_shot,'img/zhiyuansheding.jpg'):
                            break
                break
            self.d.click(1, 1)#处理被点赞的情况
            time.sleep(1)

        self.d.click(100, 505)#回到首页
        time.sleep(1)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/liwu.jpg'):
                break
            self.d.click(100,505)
            self.d.click(1,1)
            time.sleep(1)#首页锁定，保证回到首页


    def shuatuzuobiao(self,x,y,times):#刷图函数，xy为该图的坐标，times为刷图次数
        self.d.click(x,y)
        time.sleep(0.5)
        while True:#锁定加号
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/jiahao.jpg'):
                break
            self.d.click(x,y)
            time.sleep(0.5)
        screen_shot = self.d.screenshot(format="opencv")
        for i in range(times-1):#基础1次
            self.guochang(screen_shot,['img/jiahao.jpg'])
            time.sleep(0.2)
        time.sleep(0.3)
        self.d.click(758,330)#使用扫荡券的位置 也可以用OpenCV但是效率不够而且不能自由设定次数
        time.sleep(0.3)
        # screen_shot = self.d.screenshot(format="opencv")
        # self.guochang(screen_shot,['img/shiyongsanzhang.jpg'])
        screen_shot = self.d.screenshot(format="opencv") 
        self.guochang(screen_shot,['img/ok.jpg'])
        while True:
            self.d.click(1,1)
            time.sleep(0.3)
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/normal.jpg'):
                break


    def shuajingyan(self):
        """
        刷图刷1-1
        """
        # 体力单独设置
        for i in range(7):
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if self.is_there_img(screen_shot_, 'img/liwu.jpg'):
                    break
                self.d.click(100, 505)
                time.sleep(1)  # 首页锁定，保证回到首页
            self.d.click(320, 31)
            time.sleep(0.5)
            screen_shot = self.d.screenshot(format="opencv")
            self.guochang(screen_shot, ['img/ok.jpg'], suiji=0)
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
        for i in range(10):
            self.d.click(27, 272)
            time.sleep(3)
        shuatuzuobiao(106, 279, 160)  # 1-1 刷7次体力为佳

        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_, 'img/liwu.jpg'):
                break
            self.d.click(100, 505)
            time.sleep(1)  # 保证回到首页


    def shuatu(self):#刷图函数 注意此函数要在首页运行
        #进入冒险
        self.d.click(480, 505)
        time.sleep(0.5) 
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/dixiacheng.jpg'):
                break
        self.d.click(562, 253)
        time.sleep(1)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/normal.jpg'):
                break

        self.shuatuzuobiao(821,299,3)#10-17
        self.shuatuzuobiao(703,328,3)#10-16
        self.shuatuzuobiao(608,391,3)#10-15
        self.shuatuzuobiao(485,373,3)#10-14
        self.shuatuzuobiao(372,281,3)#10-13
        self.shuatuzuobiao(320,421,3)#10-12
        self.shuatuzuobiao(172,378,3)#10-11
        self.shuatuzuobiao(251,235,3)#10-10
        self.shuatuzuobiao(111,274,3)#10-9

        self.d.drag(200,270,600,270,0.1)#拖拽到最左
        time.sleep(2)

        self.shuatuzuobiao(690,362,3)#10-8
        self.shuatuzuobiao(594,429,3)#10-7
        self.shuatuzuobiao(411,408,3)#10-6
        self.shuatuzuobiao(518,332,3)#10-5
        self.shuatuzuobiao(603,238,3)#10-4
        self.shuatuzuobiao(430,239,3)#10-3
        self.shuatuzuobiao(287,206,3)#10-2
        self.shuatuzuobiao(146,197,3)#10-1

        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/liwu.jpg'):
                break
            self.d.click(100,505)
            time.sleep(1)#保证回到首页


    def dixiacheng(self):#地下城
        self.d.click(480, 505)
        time.sleep(1) 
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/dixiacheng.jpg'):
                break
            self.d.click(480, 505)
            time.sleep(1)
        self.d.click(900, 138)
        time.sleep(1)

        #下面这段因为调试而注释了，实际使用时要加上
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/chetui.jpg'):#避免某些农场号刚买回来已经进了地下城
                break
            if self.is_there_img(screen_shot_,'img/yunhai.jpg'):
                self.d.click(233, 311)
                time.sleep(1)
                while True:
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if self.is_there_img(screen_shot_,'img/ok.jpg'):
                        break
                self.d.click(592, 369)#点击ok
                time.sleep(1) 
                break


        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/chetui.jpg'):
                break
            if self.is_there_img(screen_shot_,'img/caidan_yuan.jpg'):
                self.d.click(917, 39)#菜单
                time.sleep(1)
                self.d.click(807, 44)#跳过
                time.sleep(1)
                self.d.click(589, 367)#跳过ok
                time.sleep(1)

        self.d.click(667, 360)#1层
        time.sleep(1)
        self.d.click(833, 456)#挑战
        time.sleep(1)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/zhiyuan.jpg'):
                break
        self.d.click(100, 173)#第一个人
        time.sleep(1)
        screen_shot = self.d.screenshot(format="opencv")
        self.guochang(screen_shot, ['img/zhiyuan.jpg'],suiji=0)
        
        if self.is_there_img(screen_shot_,'img/dengjixianzhi.jpg'):
            self.d.click(213, 208)#如果等级不足，就支援的第二个人
            time.sleep(1)    
        else:
            self.d.click(100, 173)#支援的第一个人
            time.sleep(1)
        
        self.d.click(833, 470)#战斗开始
        time.sleep(1)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/ok.jpg'):
                self.guochang(screen_shot_, ['img/ok.jpg'],suiji=0)
                break


        while True:#战斗中快进
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/caidan.jpg'):
                if self.is_there_img(screen_shot_,'img/kuaijin.jpg'):
                    self.d.click(913, 494)#点击快进
                    time.sleep(1)
                    self.d.click(913, 494)#点击快进
                if self.is_there_img(screen_shot_,'img/kuaijin_1.jpg'):
                    self.d.click(913, 494)#点击快进
                    time.sleep(1)
                break
        while True:#结束战斗返回
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/shanghaibaogao.jpg'):
                self.guochang(screen_shot_,['img/xiayibu.jpg','img/qianwangdixiacheng.jpg'], suiji=0)
                break
        self.d.click(1, 1)#取消显示结算动画
        time.sleep(1)
        while True:#撤退地下城
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/chetui.jpg'):
                break;#解决issues中截图可能截到撤退按钮的问题
        time.sleep(1)
        while True:#撤退地下城
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/chetui.jpg'):
                self.guochang(screen_shot_,['img/chetui.jpg'], suiji=0)
                screen_shot = self.d.screenshot(format="opencv")
                self.guochang(screen_shot,['img/ok.jpg'], suiji=0)
                break
            self.d.click(1, 1)#
            time.sleep(1)
        while True:#首页锁定
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/liwu.jpg'):
                break
            self.d.click(100,505)
            time.sleep(1)#保证回到首页


    def dixiachengzuobiao(self,x,y,auto,team=0):
    #完整刷完地下城函数
    #参数：
    # x：目标层数的x轴坐标
    # y：目标层数的y轴坐标
    # auto：取值为0/1,auto=0时不点击auto按钮，auto=1时点击auto按钮
    # team：取值为0/1/2，team=0时不换队，team=1时更换为队伍列表中的1队，team=2时更换为队伍列表中的2队

        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/chetui.jpg'):
                break
            self.d.click(1, 1)
            time.sleep(1)
        time.sleep(1)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/chetui.jpg'):
                break
            self.d.click(1, 1)
            time.sleep(1)
        self.d.click(1, 1)
        time.sleep(3)

        self.d.click(x, y)#层数
        time.sleep(2)
        self.d.click(833, 456)#挑战
        time.sleep(2)

        while True:#锁定战斗开始
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/zhandoukaishi.jpg'):
                break

        if team!=0:#换队
            self.d.click(866, 91)#我的队伍
            time.sleep(2)
            if team==1:
                self.d.click(792, 172)#1队
            elif team==2:
                self.d.click(789, 290)#2队
            time.sleep(0.5)
            while True:#锁定战斗开始
                screen_shot_ = self.d.screenshot(format="opencv")
                if self.is_there_img(screen_shot_,'img/zhandoukaishi.jpg'):
                    break
                time.sleep(0.5)
        
        self.d.click(837, 447)#战斗开始
        time.sleep(2)

        while True:#战斗中快进
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/caidan.jpg'):
                if auto==1:
                    time.sleep(0.5)
                    self.d.click(912, 423)#点auto按钮
                    time.sleep(1)
                break
        while True:#结束战斗返回
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/shanghaibaogao.jpg'):
                while True:
                    screen_shot = self.d.screenshot(format="opencv")
                    if self.is_there_img(screen_shot,'img/xiayibu.jpg'):
                        break
                self.d.click(830, 503)#点下一步 避免guochang可能失败
                break
        time.sleep(3)
        self.d.click(1, 1)#取消显示结算动画
        time.sleep(1)


    def tansuo(self):#探索函数
        self.d.click(480, 505)
        time.sleep(1) 
        while True:#锁定地下城
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/dixiacheng.jpg'):
                break
            self.d.click(480, 505)
            time.sleep(1)
        self.d.click(734, 142)#探索
        time.sleep(3.5)
        while True:#锁定凯留头
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/kailiu.jpg'):
                break
            self.d.click(1,1)
            time.sleep(0.5)
    #经验
        self.d.click(592, 255)#经验
        time.sleep(3)
        self.d.click(704, 152)#5级
        time.sleep(1.5)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/tiaozhan.jpg'):
                break
            time.sleep(0.5)
        self.d.drag(876,329,876,329,0.5)#+号
        time.sleep(0.5)
        self.d.click(752, 327)#扫荡
        time.sleep(0.5)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/ok.jpg'):
                self.d.click(590, 363)#ok
                time.sleep(0.5)
                break
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/home.jpg'):
                break
            self.d.click(1, 1)
            time.sleep(1)

    #mana
        self.d.click(802, 267)#mana
        time.sleep(3)
        self.d.click(704, 152)#5级
        time.sleep(1.5)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/tiaozhan.jpg'):
                break
            time.sleep(0.5)
        self.d.drag(876,329,876,329,0.5)#+号
        time.sleep(0.5)
        self.d.click(752, 327)#扫荡
        time.sleep(0.5)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/ok.jpg'):
                self.d.click(590, 363)#ok
                time.sleep(0.5)
                break
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/home.jpg'):
                break
            self.d.click(1, 1)
            time.sleep(1)
    #完成战斗后
        while True:#首页锁定
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/liwu.jpg'):
                break
            self.d.click(100,505)
            time.sleep(1)#保证回到首页



    def dixiachengDuanya(self):#地下城 断崖（第三个）
        self.d.click(480, 505)
        time.sleep(1) 
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/dixiacheng.jpg'):
                break
            self.d.click(480, 505)
            time.sleep(1)
        self.d.click(900, 138)
        time.sleep(1)

        #下面这段因为调试而注释了，实际使用时要加上
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/chetui.jpg'):#避免某些农场号刚买回来已经进了地下城
                break
            if self.is_there_img(screen_shot_,'img/yunhai.jpg'):
                self.d.click(712,267)#断崖
                time.sleep(1)
                while True:
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if self.is_there_img(screen_shot_,'img/ok.jpg'):
                        break
                self.d.click(592, 369)#点击ok
                time.sleep(1) 
                break
    #刷地下城
        self.dixiachengzuobiao(642,371,1,1)#1层，点auto按钮
        self.dixiachengzuobiao(368,276,0)#2层
        self.dixiachengzuobiao(627,263,0,2)#3层
        self.dixiachengzuobiao(427,274,1)#4层，点auto按钮
        self.dixiachengzuobiao(199,275,0)#5层
        self.dixiachengzuobiao(495,288,0)#6层
        self.dixiachengzuobiao(736,291,0)#7层
        self.dixiachengzuobiao(460,269,0)#8层
        self.dixiachengzuobiao(243,274,0)#9层
        self.dixiachengzuobiao(654,321,0,1)#10层

    #完成战斗后
        while True:#首页锁定
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.is_there_img(screen_shot_,'img/liwu.jpg'):
                break
            self.d.click(100,505)
            time.sleep(1)#保证回到首页
