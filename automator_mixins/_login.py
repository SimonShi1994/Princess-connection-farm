import time

from core.constant import MAIN_BTN
from core.cv import UIMatcher
from core.utils import random_name, CreatIDnum
from ._base import BaseMixin


class LoginMixin(BaseMixin):
    """
    登录插片
    包含登录相关操作的脚本
    """

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

    def do_login(self, ac, pwd):  # 执行登陆逻辑
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

    def login(self, ac, pwd):
        try:
            try_count = 0
            while True:
                try_count += 1
                if try_count % 10 == 0:
                    # 看一下会不会一直点右上角？
                    if self.last_screen is not None:
                        print("找到截屏，检测礼物:", self.img_prob(MAIN_BTN["liwu"], screen=self.last_screen))
                        if self.is_exists(MAIN_BTN["liwu"], screen=self.last_screen):
                            # 已经登陆了老哥！
                            # 重 新 来 过
                            self.log.write_log("error", "可能出现了狂点右上角错误，换号")
                            self.lockimg(MAIN_BTN["liwu"], elseclick=MAIN_BTN["zhuye"], elsedelay=1)  # 回首页
                            self.change_acc()
                if try_count > 1000:
                    # 点了1000次了，重启吧
                    raise Exception("点了1000次右上角了，重启罢！")
                # todo 登陆失败报错：-32002 Client error: <> data: Selector [
                #  resourceId='com.bilibili.priconne:id/bsgamesdk_id_welcome_change'], method: None
                if self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_id_welcome_change").exists():
                    self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_id_welcome_change").click()
                if self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_username_login").exists():
                    self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_username_login").click()
                    break
                else:
                    self.click(945, 13)
            return self.do_login(ac, pwd)
        except Exception as e:
            print(e)
            # 异常重试登陆逻辑
            return self.do_login(ac, pwd)

    def auth(self, auth_name, auth_id):
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_authentication_name").click()
        self.d.clear_text()
        self.d.send_keys(str(auth_name))
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_authentication_id_number").click()
        self.d.clear_text()
        self.d.send_keys(str(auth_id))
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_authentication_submit").click()
        self.d(resourceId="com.bilibili.priconne:id/bagamesdk_auth_success_comfirm").click()

    def login_auth(self, ac, pwd):
        need_auth = self.login(ac=ac, pwd=pwd)
        if need_auth:
            auth_name, auth_id = random_name(), CreatIDnum()
            self.auth(auth_name=auth_name, auth_id=auth_id)

    def change_acc(self):  # 切换账号
        self.click(871, 513)  # 主菜单
        while True:  # 锁定帮助
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/bangzhu.bmp'):
                break
        self.click(165, 411)  # 退出账号
        while True:  # 锁定帮助
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                break
        self.click(591, 369)  # ok
        time.sleep(1)
        # pcr_log(self.account).write_log(level='info', message='%s账号完成任务' % self.account)
