import gc
import time

from core.constant import MAIN_BTN, ZHUCAIDAN_BTN, START_UI
from core.pcr_config import debug, captcha_wait_time, captcha_popup, captcha_skip, captcha_senderror, \
    captcha_senderror_times
from core.safe_u2 import timeout
from core.tkutils import TimeoutMsgBox
from core.utils import random_name, CreatIDnum
from ._base import BaseMixin
from ._captcha import skip_caption, send_error


class LoginMixin(BaseMixin):
    """
    登录插片
    包含登录相关操作的脚本
    """

    @timeout(180, "start执行超时：超过3分钟")
    def start(self):
        """
        项目地址:https://github.com/bbpp222006/Princess-connection
        作者：bbpp222006
        协议：MIT License
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

    def do_login(self, ac, pwd):  # 执行登陆逻辑
        """
        :param ac:
        :param pwd:
        :return:
        """
        for retry in range(30):
            if self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_id_tourist_switch").exists():
                self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_id_tourist_switch").click()
                time.sleep(2)
                continue
            if not self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_username_login").exists():
                time.sleep(2)
            else:
                break
        else:
            raise Exception("进入登陆页面失败！")
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_username_login").click()
        self.d.clear_text()
        self.d.send_keys(str(ac))
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_password_login").click()
        self.d.clear_text()
        self.d.send_keys(str(pwd))
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_buttonLogin").click()
        time.sleep(12)

        def SkipAuth():
            for _ in range(2):
                # 有两个协议需要同意
                if debug:
                    print("等待认证")
                while self.d(text="请滑动阅读协议内容").exists() or self.d(description="请滑动阅读协议内容").exists():
                    if debug:
                        print("发现协议")
                    self.d.touch.down(814, 367).sleep(1).up(814, 367)
                    if self.d(text="请滑动阅读协议内容").exists():
                        self.d(text="同意").click()
                    if self.d(description="请滑动阅读协议内容").exists():
                        # 雷电三
                        self.d(description="同意").click()
                    time.sleep(6)
                if debug:
                    print("结束认证")

        SkipAuth()
        flag = False
        if self.d(text="Geetest").exists() or self.d(description="Geetest").exists():
            flag = True
            self.phone_privacy()
            _time = 1
            _id = 0

            def AutoCaptcha():
                nonlocal _time
                nonlocal _id
                time.sleep(5)
                screen = self.getscreen()
                screen = screen[22:512, 254:711]
                # 456, 489
                if self.d(textContains="请在下图依次").exists():
                    print(">>>检测到图字结合题!")
                    # 当出现这玩意时，请仔细核对你的账号密码是否已被更改找回！

                    # 结果出来为四个字的坐标
                    # answer_result, _len, _id = skip_caption(captcha_img=screen, question_type="X6004")
                    # for i in range(0, _len):
                    #     # Y轴
                    #     self.click(answer_result[i][1] + 22, post_delay=1)
                    #     # X轴
                    #     self.click(answer_result[i][0] + 254, post_delay=1)
                    # print(">验证码坐标识别：", answer_result)
                if self.d(textContains="请点击").exists():
                    print(">>>检测到图形题")
                    answer_result, _len, _id = skip_caption(captcha_img=screen, question_type="X6001")
                    x = int(answer_result[0]) + 254
                    y = int(answer_result[1]) + 22
                    print(">验证码坐标识别：", x, ',', y)
                    # print(type(x))
                    self.click(x, y, post_delay=1)
                sc1 = self.getscreen()

                def PopFun():
                    sc2 = self.getscreen()
                    p = self.img_equal(sc1, sc2, at=START_UI["imgbox"])
                    if p < 0.85:
                        return True
                    else:
                        return False

                if _id == 0:
                    time.sleep(4)
                    # 检测到题目id为0就重新验证
                    return AutoCaptcha()

                state = self.lock_fun(PopFun, elseclick=START_UI["queren"], elsedelay=8, retry=5, is_raise=False)

                if (self.d(text="Geetest").exists() or self.d(description="Geetest").exists()):
                    if _time >= 5:
                        print("重试次数太多啦，休息15s")
                        time.sleep(15)
                        _time = 0
                        return AutoCaptcha()
                    # 如果次数大于两次，则申诉题目
                    elif _time > captcha_senderror_times and captcha_senderror:
                        print("—申诉题目:", _id)
                        send_error(_id)
                    _time = + 1
                    time.sleep(4)
                    # 如果还有验证码就返回重试
                    return AutoCaptcha()
                return state

            manual_captcha = captcha_skip
            if captcha_skip is False:
                for retry in range(3):
                    if self.d(text="Geetest").exists() or self.d(description="Geetest").exists():
                        state = AutoCaptcha()
                        time.sleep(5)
                        if not state:
                            manual_captcha = True
                    else:
                        SkipAuth()
                        flag = False
                        break
                else:
                    manual_captcha = True
            if manual_captcha:
                if self.d(text="Geetest").exists() or self.d(description="Geetest").exists():
                    self.log.write_log("error", message='%s账号出现了验证码，请在%d秒内手动输入验证码' % (self.account, captcha_wait_time))
                    if captcha_popup:
                        TimeoutMsgBox("!", f"{self.address}出现验证码\n账号：{self.account}", geo="200x80",
                                      timeout=captcha_wait_time)
                    now_time = time.time()
                    while time.time() - now_time < captcha_wait_time:
                        time.sleep(1)
                        if not (self.d(text="Geetest").exists() or self.d(description="Geetest").exists()):
                            flag = False
                            break
                    time.sleep(1)
                if not (self.d(text="Geetest").exists() or self.d(description="Geetest").exists()):
                    flag = False
                    SkipAuth()
        if flag:
            return -1
        if self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_authentication_name").exists(timeout=0.1):
            return 1  # 说明要进行认证
        else:
            return 0  # 正常

    def login(self, ac, pwd):
        """
        项目地址:https://github.com/bbpp222006/Princess-connection
        作者：bbpp222006
        协议：MIT License
        :param ac:
        :param pwd:
        :return:
        """
        error_flag = 0
        try:
            # 看是否跳出主菜单
            self.lock_no_img(ZHUCAIDAN_BTN["bangzhu"], elseclick=[(871, 513), (165, 411), (591, 369)])
            self.lock_no_img('img/ok.bmp', elseclick=[(591, 369)], at=(495, 353, 687, 388))

            try_count = 0
            while True:
                try_count += 1
                if try_count % 10 == 0 and try_count > 500:
                    # 看一下会不会一直点右上角？
                    if self.last_screen is not None:
                        if self.is_exists(MAIN_BTN["liwu"], screen=self.last_screen):
                            # 已经登陆了老哥！
                            # 重 新 来 过
                            self.log.write_log("error", "可能出现了狂点右上角错误，换号")
                            self.lock_img(MAIN_BTN["liwu"], elseclick=MAIN_BTN["zhuye"], elsedelay=1)  # 回首页
                            self.change_acc()
                if try_count > 1000:
                    # 点了1000次了，重启吧
                    error_flag = 1
                    raise Exception("点了1000次右上角了，重启罢！")
                # todo 登陆失败报错：-32002 Client error: <> data: Selector [
                #  resourceId='com.bilibili.priconne:id/bsgamesdk_id_welcome_change'], method: None
                if self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_authentication_name").exists(timeout=0.1):
                    return True
                if self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_id_welcome_change").exists():
                    self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_id_welcome_change").click()
                if self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_id_tourist_switch").exists():
                    self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_id_tourist_switch").click()
                    time.sleep(2)
                    continue
                if self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_username_login").exists():
                    self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_username_login").click()
                    break
                if self.d(text="Geetest").exists() or self.d(description="Geetest").exists():
                    self.click(667, 65, post_delay=3)
                    # 防止卡验证码
                    break
                else:
                    self.click(945, 13)
            return self.do_login(ac, pwd)
        except Exception as e:
            if error_flag:
                raise e
            # 异常重试登陆逻辑
            return self.do_login(ac, pwd)

    def auth(self, auth_name, auth_id):
        """
        项目地址:https://github.com/bbpp222006/Princess-connection
        作者：bbpp222006
        协议：MIT License
        :param auth_name:
        :param auth_id:
        :return:
        """
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_authentication_name").click()
        self.d.clear_text()
        self.d.send_keys(str(auth_name))
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_authentication_id_number").click()
        self.d.clear_text()
        self.d.send_keys(str(auth_id))
        self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_authentication_submit").click()
        self.d(resourceId="com.bilibili.priconne:id/bagamesdk_auth_success_comfirm").click()

    @timeout(300, "login_auth登录超时，超过5分钟")
    def login_auth(self, ac, pwd):
        need_auth = self.login(ac=ac, pwd=pwd)
        if need_auth == -1:  # 这里漏了一句，无法检测验证码。
            return -1
        if need_auth == 1:
            auth_name, auth_id = random_name(), CreatIDnum()
            self.auth(auth_name=auth_name, auth_id=auth_id)

    def change_acc(self):  # 切换账号
        self.lock_img(ZHUCAIDAN_BTN["bangzhu"], elseclick=[(871, 513)])  # 锁定帮助
        self.lock_img('img/ok.bmp', ifclick=[(591, 369)], elseclick=[(165, 411)], at=(495, 353, 687, 388))
        self.lock_no_img(ZHUCAIDAN_BTN["bangzhu"], elseclick=[(871, 513), (165, 411), (591, 369)])
        self.phone_privacy()
        gc.collect()
        # pcr_log(self.account).write_log(level='info', message='%s账号完成任务' % self.account)
        # pcr_log(self.account).server_bot("warning", "%s账号完成任务" % self.account)
