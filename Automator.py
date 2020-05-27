import uiautomator2 as u2
import time
from utils import *
from cv import *
import matplotlib.pylab as plt


class Automator:
    def __init__(self, auto_task=False, auto_policy=True,
                 auto_goods=False, speedup=True):
        """
        device: 如果是 USB 连接，则为 adb devices 的返回结果；如果是模拟器，则为模拟器的控制 URL 。
        """
        self.d = u2.connect()
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
            if self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_id_welcome_change").exists(timeout=0.1):
                self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_id_welcome_change").click(timeout=0.1)
            if self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_username_login").exists(timeout=0.1):
                self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_username_login").click(timeout=0.1)
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
        #此函数输入要判断的图片path,屏幕截图, 阈值,   返回大于阈值的path,坐标字典,
        self.dWidth, self.dHeight = self.d.window_size()
        return_dic = {}
        zhongxings, max_vals = UIMatcher.findpic(screen_shot, template_paths=template_paths)
        for i, name in enumerate(template_paths):
            print(name + '--' + str(round(max_vals[i], 3)), end=' ')
            if max_vals[i]>threshold:
                return_dic[name]=(zhongxings[i][0] *self.dWidth, zhongxings[i][1] * self.dHeight)
        print('')
        return return_dic


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



    def jiaoxue(self,screen_shot):
        x,y = UIMatcher.find_gaoliang(screen_shot)
        try:
            self.d.click(x*self.dWidth,y*self.dHeight+20)
        except:
            pass




    def is_there_img(self,screen,img):
        self.dWidth, self.dHeight = self.d.window_size()
        active_path = self.get_butt_stat(screen,[img])
        if img in active_path:
            return True
        else:
            return False




    def get_screen_state(self,screen):
        self.dWidth, self.dHeight = self.d.window_size()
        gray = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
        ret, binary = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)
        num_of_white = len(np.argwhere(binary == 255))
        active_path = self.get_butt_stat(screen, ['img/tiaozhan.jpg','img/yunhai.jpg','img/maoxian.jpg','img/liwu.jpg','img/zhiyuansheding.jpg','img/kuaijin.jpg','img/shouye.jpg','img/baoshigoumai.jpg','img/kuaijin_1.jpg'])

        if 'img/tiaozhan.jpg' in active_path:
            return 'tiaozhan'

        
        if 'img/yunhai.jpg' in active_path:
            return 'yunhai'

        if 'img/baoshigoumai.jpg' in active_path:
            return 'baoshigoumai'

        if 'img/maoxian.jpg' in active_path:
            return 'maoxian'

        if 'img/zhiyuansheding.jpg' in active_path:
            return 'hanghui'

        if 'img/liwu.jpg' in active_path:
            return 'home'

        if 'img/shouye.jpg' in active_path:
            return 'shouye'

        if 'img/kuaijin.jpg' in active_path or'img/kuaijin_1.jpg'in active_path:
            return 'zhandou'

        if num_of_white<50000:
            return 'dark'
        else:
            return 0



    def zhandou(self):
        #此函数在进入战斗后调用, 会一直运行直到战斗结束.

        print('尝试跳过战斗')
        screen_shot = self.d.screenshot(format="opencv")
        a.guochang(screen_shot, ['img/caidan.jpg'])
        time.sleep(0.5)
        screen_shot = self.d.screenshot(format="opencv")
        active_path = self.get_butt_stat(screen_shot, ['img/caidan_tiaoguo.jpg', 'img/zhandou_fanhui.jpg', 'img/ok.jpg'])
        if 'img/ok.jpg' in active_path:
            x,y = active_path['img/ok.jpg']
            print('可以跳过')
            self.d.click(x, y)
        elif 'img/zhandou_fanhui.jpg' in active_path:
            x, y = active_path['img/zhandou_fanhui.jpg']
            print('无法跳过,确认进入战斗模式,将进入战斗循环')
            self.d.click(x, y)
            while True:
                time.sleep(0.5)
                screen_shot = self.d.screenshot(format="opencv")
                active_path = self.get_butt_stat(screen_shot, ['img/wanjiadengji.jpg','img/kuaijin.jpg'])
                if 'img/kuaijin.jpg' in active_path:
                    x, y = active_path['img/kuaijin.jpg']
                    self.d.click(x, y)
                if 'img/wanjiadengji.jpg' in active_path:
                    print('战斗应该结束了. 跳出战斗循环')
                    break

        else:
            print('没有找到跳过或者战斗的确认信号,将返回大循环')
