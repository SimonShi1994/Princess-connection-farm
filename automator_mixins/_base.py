import time
from typing import Optional

import uiautomator2 as u2

from core import log_handler
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

    def init(self, address, account):
        """
        device: 如果是 USB 连接，则为 adb devices 的返回结果；如果是模拟器，则为模拟器的控制 URL 。
        """
        self.appRunning = False
        self.account = account
        self.d = u2.connect(address)
        self.dWidth, self.dHeight = self.d.window_size()
        self.log = log_handler.pcr_log(account)  # 初始化日志
        self.AR = AutomatorRecorder(account)

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

    def click(self, x, y, pre_delay=0., post_delay=0.):
        """ 点击坐标 """
        time.sleep(pre_delay)
        self.d.click(x, y)
        time.sleep(post_delay)

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

    def lockimg(self, img, ifclick=None, ifbefore=0.5, ifdelay=1, elseclick=None, elsedelay=0.5, alldelay=0.5, retry=0,
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
        if elseclick is None:
            elseclick = []
        if ifclick is None:
            ifclick = []
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

    def lock_no_img(self, img, ifclick=None, ifbefore=0.5, ifdelay=1, elseclick=None, elsedelay=0.5, alldelay=0.5,
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
        if elseclick is None:
            elseclick = []
        if ifclick is None:
            ifclick = []
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
