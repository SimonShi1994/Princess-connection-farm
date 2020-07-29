import time
from typing import Optional

import cv2
import numpy as np
import uiautomator2 as u2

from core import log_handler
from core.MoveRecord import moveset
from core.constant import PCRelement
from core.constant import USER_DEFAULT_DICT as UDD
from core.cv import UIMatcher
from core.usercentre import AutomatorRecorder


class BaseMixin:
    """
    基础插片：包含设备信息(u2)，账户信息(account)
    辅助功能：日志，静态存储
    基本操作 （click,find_img,guochang,click_img,lock_img,lock_no_img，chulijiaocheng)
    需要在Automator中手动初始化，传入address和account参数。
    """

    def __init__(self):

        self.appRunning = False
        self.account = ""
        self.d: Optional[u2.Device] = None
        self.dWidth = 0
        self.dHeight = 0
        self.log: Optional[log_handler.pcr_log] = None
        self.AR: Optional[AutomatorRecorder] = None
        self.ms: Optional[moveset] = None
        self.debug_screen = None  # 如果debug_screen为None，则正常截图；否则，getscreen函数使用debug_screen作为读取的screen
        self.last_screen = None  # 每次调用getscreen会把图片暂存至last_screen

    def init_device(self, address):
        """
        device: 如果是 USB 连接，则为 adb devices 的返回结果；如果是模拟器，则为模拟器的控制 URL 。
        """
        self.appRunning = False
        if address != "debug":
            self.d = u2.connect(address)
            self.dWidth, self.dHeight = self.d.window_size()

    def init_account(self, account):
        self.account = account
        self.log = log_handler.pcr_log(account)  # 初始化日志
        self.AR = AutomatorRecorder(account)

    def init(self, address, account):
        # 兼容
        self.init_device(address)
        self.init_account(account)

    def click_img(self, screen, img, threshold=0.84, at=None, pre_delay=0., post_delay=0.):
        """
        try to click the img
        :param screen:
        :param threshold:
        :param img:
        :return: success
        """
        position = UIMatcher.img_where(screen, img, threshold, at)
        if position:
            self.click(*position, pre_delay, post_delay)
            return True
        else:
            return False

    def click(self, *args, pre_delay=0., post_delay=0., **kwargs):
        """
        点击函数
        2020-07-28 TheAutumnOfRice:把x,y参数换程args参数以遍兼容各种点击类型

        1.  若args为数字的x,y，则点击该位置。

            如:self.click(100,200)

        2.  若args为PCRelement类型（见core.constant），则：
            a.  若PCRelement不带任何附加信息，则仅点击其坐标
            b.  若PCRelement含有img属性，则执行click_img操作
                若PCRelement还带有at属性，则将at传入click_img
                    注：若kwargs中带有at参数，则优先使用此at

            如：
            from core.constant import DXC_ELEMENT
            self.click(DXC_ELEMENT["chetui"])

        3.  若args仅为一个字符串，则执行click_img操作
            如:self.click("img/chetui2.bmp")
        注：当点击的对象为一个图片时：
            若kwargs中带有screen参数，则将其传入click_img，否则重新截图
            若kwargs中带有threshold参数，则将其传入click_img
            若kwargs中带有at参数，则将将其传入click_img

        :param pre_delay: 前置延时
        :param post_delay: 后置延时
        :return: True or False，是否成功点击
            如果点击对象为坐标，则必定返回True
            如果点击对象为图片，则当图片不存在时，返回False，否则返回True
        """
        time.sleep(pre_delay)
        if len(args) == 2 and isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
            # (x,y)型：点击坐标
            x = args[0]
            y = args[1]
            self.d.click(x, y)
            time.sleep(post_delay)
            return True
        elif len(args) == 1 and isinstance(args[0], PCRelement):
            # 点击一个PCRelement元素
            pe = args[0]
            if pe.img is None:
                self.d.click(*pe)
                time.sleep(post_delay)
                return True
            else:
                if "at" in kwargs:
                    at = kwargs["at"]
                elif pe.at is not None:
                    at = pe.at
                else:
                    at = None
                if "screen" in kwargs:
                    screen = kwargs["screen"]
                else:
                    screen = self.d.screenshot(format="opencv")
                if "threshold" in kwargs:
                    threshold = kwargs["threshold"]
                else:
                    threshold = 0.84
                self.click_img(screen, pe.img, threshold, at, 0, post_delay)
        elif len(args) == 1 and isinstance(args[0], str):
            # 点击一个图片
            img = args[0]
            if "at" in kwargs:
                at = kwargs["at"]
            else:
                at = None
            if "screen" in kwargs:
                screen = kwargs["screen"]
            else:
                screen = self.d.screenshot(format="opencv")
            if "threshold" in kwargs:
                threshold = kwargs["threshold"]
            else:
                threshold = 0.84
            return self.click_img(screen, img, threshold, at, 0, post_delay)

    def is_exists(self, img, threshold=0.84, at=None, screen=None):
        """
        判断一个图片是否存在。
        :param img:
            一个字符串，表示图片的地址；或者为PCRelement类型。
            当img为PCRelement时，如果at参数为None，则会使用img.at。
        :param threshold: 判定阈值
        :param at: 搜素范围
        :param screen: 若设置为None，则重新截图；否则使用screen为截图
        :return: 是否存在
        """
        if screen is None:
            screen = self.d.screenshot(format="opencv")
        if isinstance(img, PCRelement):
            if at is None:
                at = img.at
            img = img.img
        return UIMatcher.img_where(screen, img, threshold, at) != False

    def img_prob(self, img, at=None, screen=None):
        """
        返回一个图片存在的阈值
        通过比较两幅图片的阈值大小可以分辨它“更”是什么图
        :param img:
            一个字符串，表示图片的地址；或者为PCRelement类型。
            当img为PCRelement时，如果at参数为None，则会使用img.at。
        :param at: 搜素范围
        :param screen: 若设置为None，则重新截图；否则使用screen为截图
        :return: 是否存在
        """
        if screen is None:
            screen = self.d.screenshot(format="opencv")
        if isinstance(img, PCRelement):
            if at is None:
                at = img.at
            img = img.img
        return UIMatcher.img_prob(screen, img, at)

    def img_equal(self, img1, img2, at=None, similarity=0.01) -> float:
        """
        输出两张图片对应像素相似程度
        要求两张图片大小一致
        :return: 相似度 0~1
        """
        if isinstance(img1, str):
            img1 = cv2.imread(img1)
        if isinstance(img2, str):
            img2 = cv2.imread(img2)
        if at is not None:
            img1 = UIMatcher.img_cut(img1, at)
            img2 = UIMatcher.img_cut(img2, at)
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY) / 255
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY) / 255

        return np.sum(np.abs(img1 - img2) < similarity) / img1.size

    def wait_for_stable(self, delay=0.5, threshold=0.2, similarity=0.001, max_retry=5, at=None, screen=None):
        """
        等待动画结束,画面稳定。此时相邻两帧的相似度大于threshold
        :param similarity: 近似程度0~1
        :param delay: 每次刷新间隔。
        :param max_retry: 最大重试次数
        :param at: 缩小范围
        :param screen: 设置为None时，参照图截图获得，否则参照图
        :return: True：动画结束 False：动画未结束
        """
        sc = self.getscreen() if screen is None else screen
        for retry in range(max_retry):
            time.sleep(delay)
            sc2 = self.getscreen()
            value = self.img_equal(sc, sc2, at, similarity)
            print("Stable : ", value, " >? ", threshold)
            if value > threshold:
                return True
            sc = sc2
        return False

    def wait_for_change(self, delay=0.5, threshold=0.10, similarity=0.01, max_retry=5, at=None, screen=None):
        """
        等待画面跳转变化，此时尾帧与头帧的相似度小于threshold
        :param similarity: 近似程度0~1
        :param delay: 每次刷新间隔。
        :param max_retry: 最大重试次数
        :param at: 缩小范围
        :param screen: 设置为None时，参照图截图获得，否则参照图
        :return: True：动画改变 False：动画未改变
        """
        sc = self.getscreen() if screen is None else screen
        for retry in range(max_retry):
            time.sleep(delay)
            sc2 = self.getscreen()
            value = self.img_equal(sc, sc2, at, similarity)
            print("Stable : ", value, " <? ", threshold)
            if value < threshold:
                return True
        return False

    def getscreen(self, filename=None):
        """
        包装了self.d.screenshot
        如果self.debug_screen为None，则
        :return: 截图的opencv格式
        """
        if self.debug_screen is None:
            self.last_screen = self.d.screenshot(filename, format="opencv")
            return self.last_screen
        else:
            if isinstance(self.debug_screen, str):
                return cv2.imread(self.debug_screen)
            else:
                return self.debug_screen

    def find_img(self, img, at=None, alldelay=0.5,
                 ifclick=None, ifbefore=0.5, ifdelay=1,
                 elseclick=None, elsedelay=0.5, retry=0):
        """
        前身：lockimg
        匹配图片并点击指定坐标

            Parameters:
                img (str): 要匹配的图片目录
                at (:tuple: `(int: 左上x, int: 左上y, int: 右下x, int: 右下y)`): 查找范围
                ifbefore (float): 识别成功后延迟点击时间
                ifclick (:list: ``): 在识别到图片时要点击的坐标，列表，列表元素为坐标如(1,1)
                ifdelay: 上述点击后延迟的时间
                elseclick: 在找不到图片时要点击的坐标，列表，列表元素为坐标如(1,1)
                elsedelay: 上述点击后延迟的时间
                retry: elseclick最多点击次数, `0为无限次`

            Returns:
                success (bool): 是否在retry次内点击成功
        """
        # 2020-07-12 Add: 增加了ifclick,elseclick参数对Tuple的兼容性
        # 2020-07-14 Add: added retry
        if elseclick is None:
            elseclick = []
        if ifclick is None:
            ifclick = []
        if type(ifclick) is tuple:
            ifclick = [ifclick]
        if type(elseclick) is tuple:
            elseclick = [elseclick]

        inf_attempt = True if retry == 0 else False
        attempt = 0
        while inf_attempt or attempt < retry:
            screen_shot = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot, img, at=at):
                # 成功匹配图片
                for clicks in ifclick:
                    self.click(clicks[0], clicks[1], pre_delay=ifbefore, post_delay=ifdelay)
                break

            for clicks in elseclick:
                self.click(clicks[0], clicks[1], post_delay=elsedelay)
            time.sleep(alldelay)
            attempt += 1
        return True if inf_attempt or attempt < retry else False

    def guochang(self, screen_shot, template_paths, suiji=1):
        # suji标号置1, 表示未找到时将点击左上角, 置0则不点击
        # 输入截图, 模板list, 得到下一次操作

        self.dWidth, self.dHeight = self.d.window_size()
        screen_shot = screen_shot
        template_paths = template_paths
        active_path = UIMatcher.imgs_where(screen_shot, template_paths)
        if active_path:
            # print(active_path)
            if 'img/caidan_tiaoguo.jpg' in active_path:
                x, y = active_path['img/caidan_tiaoguo.jpg']
                self.d.click(x, y)
            else:
                for name, (x, y) in active_path.items():
                    # print(name)
                    self.d.click(x, y)
            time.sleep(0.5)
        else:
            if suiji:
                # print('未找到所需的按钮,将点击左上角')
                self.d.click(0.1 * self.dWidth, 0.1 * self.dHeight)
            else:
                # print('未找到所需的按钮,无动作')
                pass

    def lockimg(self, img, ifclick=None, ifbefore=0.5, ifdelay=1, elseclick=None, elsedelay=0.5, alldelay=0.5, retry=0,
                at=None):
        """
        @args:
            img:要匹配的图片目录
                2020-07-28：TheAutumnOfRice Add: img支持兼容PCRelement格式
                传入PCRelement后,自动填充img和at。
                如果PCRelement含有at属性而外部设置了at，以lockimg的参数为准
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
        if elseclick is None:
            elseclick = []
        if ifclick is None:
            ifclick = []
        if type(ifclick) is tuple:
            ifclick = [ifclick]
        if type(elseclick) is tuple:
            elseclick = [elseclick]
        if isinstance(img, PCRelement):
            if at is None:
                at = img.at
            img = img.img
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

    def lock_no_img(self, img, ifclick=None, ifbefore=0.5, ifdelay=1, elseclick=None, elsedelay=0.5, alldelay=0.5,
                    retry=0, at=None):  # 锁定指定图像
        """
        @args:
            img:要匹配的图片目录
            2020-07-28：TheAutumnOfRice Add: img支持兼容PCRelement格式
                传入PCRelement后,自动填充img和at。
                如果PCRelement含有at属性而外部设置了at，以lock_no_img的参数为准
            ifbefore:识别成功后延迟点击时间
            ifclick:在识别不到图片时要点击的坐标，列表，列表元素为坐标如(1,1)
            ifdelay:上述点击后延迟的时间
            elseclick:在找到图片时要点击的坐标，列表，列表元素为坐标如(1,1)
            retry:elseclick最多点击次数，0为无限次
        @return:是否在retry次内点击成功
        """
        # 2020-07-13 Added By Dr-Blueomnd

        if elseclick is None:
            elseclick = []
        if ifclick is None:
            ifclick = []
        if type(ifclick) is tuple:
            ifclick = [ifclick]
        if type(elseclick) is tuple:
            elseclick = [elseclick]
        if isinstance(img, PCRelement):
            if at is None:
                at = img.at
            img = img.img
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

    def chulijiaocheng(self, turnback="shuatu"):  # 处理教程, 最终返回刷图页面
        """
        有引导点引导
        有下一步点下一步
        有主页点主页
        有圆menu就点跳过，跳过
        有跳过点跳过
        都没有就点边界点
        # 有取消点取消
        :turnback:
            shuatu: 返回刷图页面
            None: 不返回任何页面
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
            elif self.click_img(screen_shot_, 'img/xiayibu.jpg'):
                time.sleep(2)
            elif self.click_img(screen_shot_, 'img/niudan_jiasu.jpg', at=(700, 0, 960, 100)):
                pass
            elif self.click_img(screen_shot_, 'img/wuyuyin.jpg', at=(450, 355, 512, 374)):
                time.sleep(3)
            elif self.click_img(screen_shot_, 'img/tiaoguo.jpg'):
                time.sleep(3)
            elif self.click_img(screen_shot_, 'img/zhuye.jpg', at=(46, 496, 123, 537)):
                pass
            elif self.click_img(screen_shot_, 'img/caidan_yuan.jpg', at=(898, 23, 939, 62)):
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
        if turnback == "shuatu":
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

    def task_start(self):
        # 标记这个用户开始重新刷图了
        d = self.AR.get("run_status", UDD["run_status"])
        d["finished"] = False
        d["current"] = "..."
        self.AR.set("run_status", d)

    def task_finished(self):
        # 标记这个用户已经刷完了图
        d = self.AR.get("run_status", UDD["run_status"])
        d["finished"] = True
        self.AR.set("run_status", d)

    def task_current(self, title):
        # 标记这个用户当前正在进行的项目
        d = self.AR.get("run_status", UDD["run_status"])
        d["current"] = title
        self.AR.set("run_status", d)

    def task_error(self, error):
        # 标记某一项错误，并停止刷图
        d = self.AR.get("run_status", UDD["run_status"])
        d["finished"] = True
        d["current"] = "..."
        d["error"] = error
        self.AR.set("run_status", d)
