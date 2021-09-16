import random
import time

from id_validator import validator

from core.constant import MAIN_BTN, ZHUCAIDAN_BTN, START_UI
from core.pcr_config import debug, captcha_wait_time, captcha_popup, captcha_skip, captcha_senderror, \
    captcha_senderror_times, use_my_id
from core.safe_u2 import timeout
from core.tkutils import TimeoutMsgBox
from core.usercentre import AutomatorRecorder
from core.utils import random_name
from ._base import BaseMixin
from ._base import DEBUG_RECORD
from ._captcha import CaptionSkip


class BadLoginException(Exception): pass


class LoginMixin(BaseMixin):
    """
    登录插片
    包含登录相关操作的脚本
    """

    @timeout(180, "start执行超时：超过3分钟")
    @DEBUG_RECORD
    def start(self):
        """
        项目地址:https://github.com/bbpp222006/Princess-connection
        作者：bbpp222006
        协议：MIT License
        启动脚本，请确保已进入游戏页面。
        """
        while True:
            self.phone_privacy()
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

    @DEBUG_RECORD
    def do_login(self, ac, pwd):  # 执行登陆逻辑
        """
        :param ac:
        :param pwd:
        :return:
        """
        # 也许你已经注意到，这个整个登陆函数已经成了屎山了，
        # 每次只要出现登陆部分的BUG都要改半天
        # 你永远不知道你程序当前运行在哪个函数里,auth?login_auth?login?do_login?init_home?lock_home?
        # 如果你想知道，建议在config中把disable_timeout_raise给开启，
        # 然后在程序运行时按Ctrl+C，如果你运气好，你会看到你程序卡在哪里。
        # 我放弃了。  新增自动点击“下载”，自动下载新增数据功能， 2020-11-23 By TheAutumnOfRice

        # 结构梳理下为：auth -> login_auth(是否需要实名认证<->login<->do_login[验证码处理]) -> init_home(lock_home)
        for retry in range(300):
            self._move_check()
            self.click(945, 13)  # 防止卡住
            if self.d(resourceId="com.bilibili.priconne:id/tv_gsc_wel_change").exists():
                self.d(resourceId="com.bilibili.priconne:id/tv_gsc_wel_change").click()
                time.sleep(0.8)
                continue
            if self.d(resourceId="com.bilibili.priconne:id/tv_gsc_record_login_change").exists():
                self.d(resourceId="com.bilibili.priconne:id/tv_gsc_record_login_change").click()
                time.sleep(0.8)
                continue
            if self.d(resourceId="com.bilibili.priconne:id/iv_gsc_account_login").exists():
                self.d(resourceId="com.bilibili.priconne:id/iv_gsc_account_login").click()
                time.sleep(0.8)
                continue
            if not self.d(resourceId="com.bilibili.priconne:id/et_gsc_account").exists():
                time.sleep(0.8)
            else:
                break
        else:
            raise Exception("进入登陆页面失败！")
        self.d(resourceId="com.bilibili.priconne:id/et_gsc_account").click()
        self.d.clear_text()
        self.d.send_keys(str(ac))
        self.d(resourceId="com.bilibili.priconne:id/et_gsc_account_pwd").click()
        self.d.clear_text()
        self.d.send_keys(str(pwd))
        time.sleep(random.uniform(0.2, 2))
        self.d(resourceId="com.bilibili.priconne:id/tv_gsc_account_login").click()
        # time.sleep(0.5)
        toast_message = self.d.toast.get_message()
        # print(toast_message)
        if toast_message == "密码错误":
            raise BadLoginException("密码错误！")
        elif "账号异常" in str(toast_message).split(" "):
            raise BadLoginException("账号异常！")

        while True:
            # 快速响应
            # 很容易在这里卡住
            time.sleep(1)
            sc = self.getscreen()
            if self.is_exists(MAIN_BTN["xiazai"], screen=sc):
                self.click(MAIN_BTN["xiazai"])
            if self.d(text="请滑动阅读协议内容").exists() or self.d(description="请滑动阅读协议内容").exists():
                break
            elif self.is_exists(MAIN_BTN["liwu"], screen=sc):
                break
            elif self.d(text="Geetest").exists() or self.d(description="Geetest").exists():
                break
            elif self.d(resourceId="com.bilibili.priconne:id/gsc_rl_realname_web").exists():
                return 1  # 说明要进行认证
            elif not self.d(resourceId="com.bilibili.priconne:id/tv_gsc_account_login").exists() and \
                    not self.d(resourceId="com.bilibili.priconne:id/gsc_rl_realname_web").exists():
                break

        def SkipAuth():
            for _ in range(2):
                # 有两个协议需要同意
                if debug:
                    print("等待认证")
                while self.d(text="请滑动阅读协议内容").exists() or self.d(description="请滑动阅读协议内容").exists():
                    if debug:
                        print("发现协议")
                    self._move_check()
                    self.d.touch.down(810, 378).sleep(1).up(810, 378)
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
            _time = 1
            _id = 0
            _pop = False

            def AutoCaptcha():

                # 初始化接码
                cs = CaptionSkip()

                nonlocal _time
                nonlocal _id
                nonlocal _pop

                sc1 = self.getscreen()

                time.sleep(5)
                screen = self.getscreen()
                screen = screen[1:575, 157:793]
                # 原来的 456, 489
                # 不要了，这是新的分辨率，需要包含游戏一部分截图 636,539
                if self.d(textContains="请点击此处重试").exists():
                    print(f">>>{self.account}-请点击此处重试")
                    # 点重试
                    self.click(482, 315, post_delay=3)

                elif self.d(textContains="异常").exists() or self.d(textContains="返回").exists():
                    print(f">>>{self.account}-网络异常，刷新验证码")
                    self.click(476, 262)
                    self.d(text="返回").click()

                elif self.d(textContains="请在下图依次").exists():
                    print(f">>>{self.account}-检测到图字结合题")
                    print("当出现这玩意时，请仔细核对你的账号密码是否已被更改找回！")
                    # 这是关闭验证码 self.click(667, 65, post_delay=3)
                    # 结果出来为四个字的坐标
                    answer_result, _len, _id = cs.skip_caption(captcha_img=screen, question_type="X6004")
                    for i in range(0, _len + 1):
                        x = int(answer_result[i].split(',')[0]) + 157
                        y = int(answer_result[i].split(',')[1]) + 1
                        print(f">{self.account}-验证码第{i}坐标识别：", x, ',', y)
                        self.click(x, y, post_delay=1)

                elif self.d(textContains="请点击").exists():
                    print(f">>>{self.account}-检测到图形题")
                    answer_result, _len, _id = cs.skip_caption(captcha_img=screen, question_type="X6001")
                    x = int(answer_result[0]) + 157
                    y = int(answer_result[1]) + 1
                    print(f">{self.account}-验证码坐标识别：", x, ',', y)
                    # print(type(x))
                    self.click(x, y, post_delay=1)

                elif self.d(textContains="拖动滑块").exists():
                    print(f">>>{self.account}-检测到滑块题")
                    answer_result, _len, _id = cs.skip_caption(captcha_img=screen, question_type="X8006")
                    x = int(answer_result[0]) + 157
                    y = int(answer_result[1]) + 1
                    print(f">{self.account}-滑块坐标识别：", x, 386)
                    # print(type(x))
                    # 从322,388 滑动到 x,y
                    self.d.drag_to(322, 388, x, 386, 3.6)

                else:
                    print(f"{self.account}-存在未知领域，无法识别到验证码（或许已经进入主页面了），有问题请加群带图联系开发者")
                    return False

                def PopFun():
                    time.sleep(1)
                    sc2 = self.getscreen()
                    p = self.img_equal(sc1, sc2, at=START_UI["imgbox"])
                    print(p)
                    if p <= 0.99:
                        self.d(text="确认").click()
                        return True
                    else:
                        return False

                if _id == 0:
                    time.sleep(4)
                    # 检测到题目id为0就重新验证
                    AutoCaptcha()

                # state = self.lock_fun(PopFun, retry=8, is_raise=False)# elseclick=START_UI["queren"]
                time.sleep(1)
                sc2 = self.getscreen()
                p = self.img_equal(sc1, sc2, at=START_UI["imgbox"])
                if p <= 0.99:
                    self.d(text="确认").click()
                    state = True
                else:
                    state = False

                toast_message = self.d.toast.get_message()
                # print(toast_message)
                if toast_message == "请检查网络,-662":
                    # print("请检查网络,-662")
                    time.sleep(15)
                    self.d(resourceId="com.bilibili.priconne:id/tv_gsc_account_login").click()
                    # raise BadLoginException("请检查网络，-662")

                if self.d(text="Geetest").exists() or self.d(description="Geetest").exists():
                    if _time >= 5:
                        print("重试次数太多啦，休息15s")
                        time.sleep(15)
                        _time = 0
                        AutoCaptcha()
                    # 如果次数大于两次，则申诉题目
                    elif _time > captcha_senderror_times and captcha_senderror:
                        print("—申诉题目:", _id)
                        cs.send_error(_id)
                    _time = + 1
                    print("验证码登陆验证重来！")
                    time.sleep(4)
                    # 如果还有验证码就返回重试
                    AutoCaptcha()
                return state

            manual_captcha = captcha_skip
            if captcha_skip is False:
                for retry in range(3):
                    if self.d(text="Geetest").exists() or self.d(description="Geetest").exists():
                        state = AutoCaptcha()
                        time.sleep(5)
                        if not state:
                            manual_captcha = True
                            break
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
                        self._move_check()
                        time.sleep(1)
                        if not (self.d(text="Geetest").exists() or self.d(description="Geetest").exists()):
                            flag = False
                            break
                    time.sleep(1)
                if not (self.d(text="Geetest").exists() or self.d(description="Geetest").exists()):
                    flag = False
                    SkipAuth()
        if self.d(resourceId="com.bilibili.priconne:id/gsc_rl_realname_web").exists(timeout=0.1):
            return 1  # 说明要进行认证
        if flag:
            return -1
        else:
            return 0  # 正常

    @DEBUG_RECORD
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
            self.lock_no_img(ZHUCAIDAN_BTN["bangzhu"], elseclick=[(871, 513), (165, 411), (591, 369), (678, 377)])
            self.lock_no_img('img/ok.bmp', elseclick=[(591, 369)], at=(495, 353, 687, 388))

            try_count = 0
            while True:
                self._move_check()
                try_count += 1
                if try_count % 5 == 0 and try_count > 10:
                    # 看一下会不会一直点右上角？
                    try:
                        screen_shot_ = self.getscreen()
                        r_list = self.img_where_all(img=MAIN_BTN["guanbi"], screen=screen_shot_)
                        if self.lock_no_img(img=MAIN_BTN["guanbi"], elseclick=(int(r_list[0]), int(r_list[1])),
                                            side_check=self.juqing_kkr):
                            time.sleep(6)
                            continue
                    except:
                        pass
                    if self.is_exists(MAIN_BTN["liwu"]):
                        # 已经登陆了老哥！
                        # 重 新 来 过
                        self.log.write_log("error", "可能出现了狂点右上角错误，换号")
                        self.lock_img(MAIN_BTN["liwu"], elseclick=MAIN_BTN["zhuye"], elsedelay=1)  # 回首页
                        self.change_acc()
                if try_count > 100:
                    # 点了100次了，重启吧
                    error_flag = 1
                    raise Exception("点了100次右上角了，重启罢！")

                # if self.d(resourceId="com.bilibili.priconne:id/unitySurfaceView").exists():
                #     self.d(resourceId="com.bilibili.priconne:id/unitySurfaceView").click()

                if self.d(resourceId="com.bilibili.priconne:id/tv_gsc_wel_change").exists():
                    self.d(resourceId="com.bilibili.priconne:id/tv_gsc_wel_change").click()
                    time.sleep(2)
                    continue
                if self.d(resourceId="com.bilibili.priconne:id/tv_gsc_record_login_change").exists():
                    self.d(resourceId="com.bilibili.priconne:id/tv_gsc_record_login_change").click()
                    time.sleep(2)
                    continue
                if self.d(resourceId="com.bilibili.priconne:id/iv_gsc_account_login").exists():
                    self.d(resourceId="com.bilibili.priconne:id/iv_gsc_account_login").click()
                    time.sleep(2)
                    continue
                if self.d(resourceId="com.bilibili.priconne:id/et_gsc_account").exists():
                    self.d(resourceId="com.bilibili.priconne:id/et_gsc_account").click()
                    break
                if self.d(text="Geetest").exists() or self.d(description="Geetest").exists():
                    self.click(667, 65, post_delay=3)
                    # 防止卡验证码
                    break
                if self.d(text="请滑动阅读协议内容").exists() or self.d(description="请滑动阅读协议内容").exists():
                    if debug:
                        print("发现协议")
                    self.d.touch.down(810, 378).sleep(1).up(810, 378)
                    if self.d(text="请滑动阅读协议内容").exists():
                        self.d(text="同意").click()
                    if self.d(description="请滑动阅读协议内容").exists():
                        # 雷电三
                        self.d(description="同意").click()
                    time.sleep(6)
                else:
                    self.click(945, 13)
                    self.click(678, 377)  # 下载
            return self.do_login(ac, pwd)
        except Exception as e:
            # if error_flag:
            #     raise e
            # # 异常重试登陆逻辑
            # return self.login(ac, pwd)  # 修改无限重复BUG
            raise e  # 应该报错的时候就应该报错，上面会处理的。

    @DEBUG_RECORD
    def auth(self, auth_name, auth_id):
        """
        项目地址:https://github.com/bbpp222006/Princess-connection
        作者：bbpp222006
        协议：MIT License
        :param auth_name:
        :param auth_id:
        :return:
        """

        ORIGIN_MODE = True  # css炸裂之前的版本，设置为True后应付CSS炸裂之后的版本

        if ORIGIN_MODE:
            if self.d(textContains="还剩1次实名认证机会").exists():
                self.log.write_log("error", message='%s账号实名仅剩1次验证机会了！' % self.account)
                raise Exception("实名仅剩1次验证机会了！")
            time.sleep(5)
            self._move_check()
            # self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_authentication_name").click()
            self.click(464, 205)
            # self.d.xpath(
            #     '//android.widget.RelativeLayout/android.webkit.WebView[1]/android.webkit.WebView[1]/android.view.View['
            #     '1]/android.view.View[1]/android.view.View[4]/android.widget.EditText[1]').click()
            self._move_check()
            self.d.clear_text()
            self._move_check()
            self.d.send_keys(str(auth_name))
            self._move_check()
            self.click(464, 280)
            # self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_authentication_id_number").click()
            # self.d.xpath(
            #     '//android.widget.RelativeLayout/android.webkit.WebView[1]/android.webkit.WebView[1]/android.view.View['
            #     '1]/android.view.View[1]/android.view.View[4]/android.widget.EditText[2]').click()
            self._move_check()
            self.d.clear_text()
            self._move_check()
            self.d.send_keys(str(auth_id))
            self._move_check()
            if self.d(text="提交实名").exists():
                self.d.xpath('//*[@text="提交实名"]').click()
                # self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_authentication_submit").click()
                self._move_check()
                # self.d(resourceId="com.bilibili.priconne:id/bagamesdk_auth_success_comfirm").click()

            if self.d(text="我知道了").exists():
                self._move_check()
                self.d(text="我知道了").click()
                time.sleep(3)
            else:
                # 阿B实名界面有两个。。。xpath在u2全局查找元素点击上有adb爆炸的bug，先用这个凑合着吧
                if self.d(textContains="还剩1次实名认证机会").exists():
                    self.log.write_log("error", message='%s账号实名仅剩1次验证机会了！' % self.account)
                    raise Exception("实名仅剩1次验证机会了！")
                time.sleep(5)
                self._move_check()
                self.click(464, 285)
                self._move_check()
                self.d.clear_text()
                self._move_check()
                self.d.send_keys(str(auth_name))
                self._move_check()
                self.click(464, 360)
                self._move_check()
                self.d.clear_text()
                self._move_check()
                self.d.send_keys(str(auth_id))
                self._move_check()
                self.d.xpath('//*[@text="提交实名"]').click()
                self._move_check()
                self.d(text="我知道了").click()
        else:

            # CSS炸裂，变大
            if self.d(textContains="还剩1次实名认证机会").exists():
                self.log.write_log("error", message='%s账号实名仅剩1次验证机会了！' % self.account)
                raise Exception("实名仅剩1次验证机会了！")
            time.sleep(5)
            self._move_check()
            self.d.drag(827, 488, 827, 80, 0.1)
            self._move_check()
            self.d.drag(827, 488, 827, 80, 0.1)
            self.click(431, 91)
            self._move_check()
            self.d.clear_text()
            self._move_check()
            self.d.send_keys(str(auth_name))
            self._move_check()
            self.click(460, 217)
            self._move_check()
            self.d.clear_text()
            self._move_check()
            self.d.send_keys(str(auth_id))
            self._move_check()
            self.click(469, 364)  # 提交实名
            time.sleep(3)
            self.click(475, 407)

    @timeout(300, "login_auth登录超时，超过5分钟")
    @DEBUG_RECORD
    def login_auth(self, ac, pwd):

        # CreatIDnum() 可能阿B升级了验证，不推荐使用了，没有合法性校验
        need_auth = self.login(ac=ac, pwd=pwd)
        if need_auth == -1:  # 这里漏了一句，无法检测验证码。
            return -1
        if need_auth == 1:
            if use_my_id:
                real_id = AutomatorRecorder.load("./idcard.json")
                id_list = list(real_id.keys())
                count = random.randint(0, len(id_list) - 1)
                self.auth(auth_name=id_list[count], auth_id=real_id[id_list[count]])
            else:
                birthday = str(random.randint(1970, 1999))
                auth_name, auth_id = random_name(), validator.fake_id(birthday=birthday)
                self.auth(auth_name=auth_name, auth_id=auth_id)

    @DEBUG_RECORD
    def change_acc(self):  # 切换账号
        self.lock_img(ZHUCAIDAN_BTN["bangzhu"], elseclick=[(871, 513)])  # 锁定帮助
        self.lock_img('img/ok.bmp', ifclick=[(591, 369)], elseclick=[(165, 411)], at=(495, 353, 687, 388))
        self.lock_no_img(ZHUCAIDAN_BTN["bangzhu"], elseclick=[(871, 513), (165, 411), (591, 369)])
        # 设备匿名
        self.phone_privacy()
        # pcr_log(self.account).write_log(level='info', message='%s账号完成任务' % self.account)
        # pcr_log(self.account).server_bot("warning", "%s账号完成任务" % self.account)
