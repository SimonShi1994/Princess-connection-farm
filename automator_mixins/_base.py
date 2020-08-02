import asyncio
import os
import threading
import time
from typing import Optional, Union

import cv2
import numpy as np
import uiautomator2 as u2

from core import log_handler
from core.MoveRecord import moveset
from core.constant import PCRelement, MAIN_BTN
from core.constant import USER_DEFAULT_DICT as UDD
from core.cv import UIMatcher
from core.usercentre import AutomatorRecorder
from pcr_config import debug, fast_screencut, lockimg_timeout, fast_screencut_delay, fast_screencut_timeout

if fast_screencut:
    import adbutils
    import websocket


class BaseMixin:
    """
    基础插片：包含设备信息(u2)，账户信息(account)
    辅助功能：日志，静态存储
    基本操作 （click,find_img,guochang,click_img,lock_img,lock_no_img，chulijiaocheng)
    需要在Automator中手动初始化，传入address和account参数。
    """

    def __init__(self):

        self.appRunning = False
        self.account = "debug"
        self.d: Optional[u2.Device] = None
        self.dWidth = 0
        self.dHeight = 0
        self.log: Optional[log_handler.pcr_log] = None
        self.AR: Optional[AutomatorRecorder] = None
        self.ms: Optional[moveset] = None
        self.debug_screen = None  # 如果debug_screen为None，则正常截图；否则，getscreen函数使用debug_screen作为读取的screen
        self.last_screen = None  # 每次调用getscreen会把图片暂存至last_screen
        self.last_screen_time = 0

        # fastscreencap
        if fast_screencut:
            # Switch:
            # -1 出错
            # 0 关闭
            # 1 启动中
            # 2 待续
            # 3 截图中
            # 4 截图完毕
            self.fast_screencut_switch = 0
            self.lport: Optional[int] = None
            self.ws: Optional[websocket.WebSocket] = None
            os.makedirs("screenshots", exist_ok=True)

    def init_device(self, address):
        """
        device: 如果是 USB 连接，则为 adb devices 的返回结果；如果是模拟器，则为模拟器的控制 URL 。
        """
        self.appRunning = False
        if address != "debug":
            self.d = u2.connect(address)
            self.dWidth, self.dHeight = self.d.window_size()
            if fast_screencut:
                d = adbutils.adb.device(address)
                self.lport = d.forward_port(7912)
                self.ws = websocket.WebSocket()

    def init_account(self, account):
        self.account = account
        self.log = log_handler.pcr_log(account)  # 初始化日志
        self.AR = AutomatorRecorder(account)

    def init(self, address, account):
        # 兼容
        self.init_device(address)
        self.init_account(account)

    @staticmethod
    def _get_at(at):
        # at参数的转换
        if isinstance(at, PCRelement):
            return at.at
        else:
            return at

    def click_img(self, screen, img, threshold=0.84, at=None, pre_delay=0., post_delay=0.):
        """
        try to click the img
        :param screen:
        :param threshold:
        :param img:
        :return: success
        """
        at = self._get_at(at)
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
                    at = self._get_at(kwargs["at"])
                elif pe.at is not None:
                    at = pe.at
                else:
                    at = None
                if "screen" in kwargs:
                    screen = kwargs["screen"]
                else:
                    screen = self.getscreen()
                if "threshold" in kwargs:
                    threshold = kwargs["threshold"]
                else:
                    threshold = 0.84
                self.click_img(screen, pe.img, threshold, at, 0, post_delay)
        elif len(args) == 1 and isinstance(args[0], str):
            # 点击一个图片
            img = args[0]
            if "at" in kwargs:
                at = self._get_at(kwargs["at"])
            else:
                at = None
            if "screen" in kwargs:
                screen = kwargs["screen"]
            else:
                screen = self.getscreen()
            if "threshold" in kwargs:
                threshold = kwargs["threshold"]
            else:
                threshold = 0.84
            return self.click_img(screen, img, threshold, at, 0, post_delay)

    @staticmethod
    def _get_img_at(img, at):
        at = BaseMixin._get_at(at)
        if isinstance(img, PCRelement):
            if at is None:
                at = img.at
            img = img.img
        return img, at

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
            screen = self.getscreen()
        img, at = self._get_img_at(img, at)
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
            screen = self.getscreen()
        img, at = self._get_img_at(img, at)
        return UIMatcher.img_prob(screen, img, at)

    def img_where_all(self, img, threshold=0.9, at=None, screen=None):
        """
        返回一个图片所有的位置
        :param img:
            一个字符串，表示图片的地址；或者为PCRelement类型。
            当img为PCRelement时，如果at参数为None，则会使用img.at。
        :param threshold: 阈值
        :param at: 搜素范围
        :param screen: 若设置为None，则重新截图；否则使用screen为截图
        :return: list[(x,y,at)]
        """
        if screen is None:
            screen = self.getscreen()
        img, at = self._get_img_at(img, at)
        return UIMatcher.img_all_where(screen, img, threshold, at)

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
        at = self._get_at(at)
        if at is not None:
            img1 = UIMatcher.img_cut(img1, at)
            img2 = UIMatcher.img_cut(img2, at)
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY) / 255
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY) / 255

        return np.sum(np.abs(img1 - img2) < similarity) / img1.size

    def wait_for_stable(self, delay=0.5, threshold=0.2, similarity=0.001, max_retry=0, at=None, screen=None):
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
        retry = 0
        at = self._get_at(at)
        while retry < max_retry or max_retry == 0:
            retry += 1
            time.sleep(delay)
            sc2 = self.getscreen()
            value = self.img_equal(sc, sc2, at, similarity)
            if debug:
                print("Stable : ", value, " >? ", threshold)
            if value > threshold:
                return True
            sc = sc2
        return False

    def wait_for_change(self, delay=0.5, threshold=0.10, similarity=0.01, max_retry=0, at=None, screen=None):
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
        retry = 0
        at = self._get_at(at)
        while retry < max_retry or max_retry == 0:
            retry += 1
            time.sleep(delay)
            sc2 = self.getscreen()
            value = self.img_equal(sc, sc2, at, similarity)
            if debug:
                print("Stable : ", value, " <? ", threshold)
            if value < threshold:
                return True
        return False

    def wait_for_loading(self, screen=None, delay=0.5, timeout=30):
        """
        等待黑屏loading结束
        :param screen: 设置为None时，截图，否则使用screen
        :param delay: 检测间隔
        :param timeout: 超过timeout，报错
        """
        time.sleep(delay)
        sc = self.getscreen() if screen is None else screen
        last_time = time.time()
        while True:
            sc_cut = UIMatcher.img_cut(sc, MAIN_BTN["loading_left"].at)
            if not (sc_cut == 1).all():
                break
            if time.time() - last_time > timeout:
                raise Exception("Loading 超时！")
            time.sleep(delay)
            sc = self.getscreen()

    def check_dict_id(self, at, id_dict, screen=None, max_threshold=0.8, diff_threshold=0.05):
        """
        识别固定区域内不同图的编号
        :param at: 固定区域
        :param id_dict: 字典，{key:PCRElement}，表示{编号:图片}
        :param screen: 设置为None时，第一次重新截图
        :param max_threshold: 最大阈值，获得图片最大概率必须超过max_threshold
        :param diff_threshold: 相差阈值，第一大的概率和第二大的概率差必须超过diff_threshold
        :return:
            None: 识别失败
            Else: 识别的key
        """
        at = self._get_at(at)
        sc = self.getscreen() if screen is None else screen
        sc_cut = UIMatcher.img_cut(sc, at)
        pdict = {}
        for i, j in id_dict.items():
            pdict[i] = self.img_prob(j.img, screen=sc_cut)
        tu = max(pdict, key=lambda x: pdict[x])
        l = sorted(pdict.values(), reverse=True)
        if l[0] < max_threshold or l[0] - l[1] < diff_threshold:
            return None
        else:
            return tu

    def run_func(self, th_name, a, fun, async_sexitflag=False):
        if async_sexitflag:
            th_name.exit()
            pass
        else:
            try:
                self.do(a, fun)
                pass
            except:
                pass
        pass

    def do(self, a, fun):
        # 自定义，在此定义你要运行的参数
        getattr(asyncio, 'run')(fun)
        # getattr获取asyncio中run对象，然后进行调用
        # 凄凄惨惨的替代eval这类危险的函数
        pass

    def c_async(self, a, account, fun, sync=False):
        _async_infodic = {'a': a, 'account': account, 'fun': fun,
                          '"pack_Thread-" + str(account)': "pack_Thread-" + str(account)}
        th = Multithreading(kwargs=_async_infodic)
        # print(threading.currentThread().ident)
        # id, name
        th.start()
        if sync:
            # 线程同步异步开关，True/False
            th.join()
            # 线程等待，执行完才能进入下一个线程
            pass
        else:
            # 异步，推荐
            pass
        pass

    def start_async_fastscreen(self):
        account = self.account
        self.c_async(self, account, self.async_fast_screen(), sync=False)

    async def async_fast_screen(self):
        while True:
            try:
                if self.fast_screencut_switch == 1:
                    self.ws.connect("ws://localhost:{}/minicap".format(self.lport))
                    self.fast_screencut_switch = 2
                elif self.fast_screencut_switch == 2:
                    while self.fast_screencut_switch in [2, 4]:
                        data = self.ws.recv()
                elif self.fast_screencut_switch == 3:
                    time.sleep(0.1)
                    while True:
                        data = self.ws.recv()
                        if not isinstance(data, (bytes, bytearray)):
                            continue
                        if fast_screencut_delay > 0:
                            time.sleep(fast_screencut_delay)  # 防止过快不兼容
                        with open("screenshots/%s.jpg" % self.account, "wb") as f:
                            f.write(data)
                            self.fast_screencut_switch = 4
                            break
                elif self.fast_screencut_switch <= 0:
                    break
            except Exception as e:
                self.log.write_log("error", f"fast_screencut出错 {e}")
                self.fast_screencut_switch = -1
        self.ws.abort()

    def getscreen(self, filename=None):
        """
        包装了self.d.screenshot
        如果self.debug_screen为None，则
        :return: 截图的opencv格式
        """
        if self.debug_screen is None:
            if fast_screencut:
                if self.fast_screencut_switch <= 0:
                    self.fast_screencut_switch = 1
                    self.start_async_fastscreen()
                last_time = time.time()
                while self.fast_screencut_switch not in [-1, 2, 3, 4]:
                    if time.time() - last_time > fast_screencut_timeout:
                        self.fast_screencut_switch = -1
                        break
                if self.fast_screencut_switch == 2:
                    self.fast_screencut_switch = 3
                    last_time = time.time()
                    while self.fast_screencut_switch not in [-1, 4]:
                        if time.time() - last_time > fast_screencut_timeout:
                            self.fast_screencut_switch = -1
                            break
                if self.fast_screencut_switch == -1:
                    self.last_screen = self.d.screenshot(filename, format="opencv")
                else:

                    self.last_screen = cv2.imread("screenshots/%s.jpg" % self.account)
                    if filename is not None:
                        cv2.imwrite(filename, self.last_screen)
                    self.fast_screencut_switch = 2
            else:
                self.last_screen = self.d.screenshot(filename, format="opencv")
            self.last_screen_time = time.time()
            return UIMatcher.AutoRotateClockWise90(self.last_screen)
        else:
            if isinstance(self.debug_screen, str):
                return cv2.imread(self.debug_screen)
            else:
                return self.debug_screen

    def find_img(self, img, at=None, alldelay=0.5,
                 ifclick=None, ifbefore=0.5, ifdelay=1,
                 elseclick=None, elsedelay=0.5, retry=0):
        """
        前身：lock_img
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
            screen_shot = self.getscreen()
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
                self.click(x, y)
            else:
                for name, (x, y) in active_path.items():
                    # print(name)
                    self.click(x, y)
            time.sleep(0.5)
        else:
            if suiji:
                # print('未找到所需的按钮,将点击左上角')
                self.click(0.1 * self.dWidth, 0.1 * self.dHeight)
            else:
                # print('未找到所需的按钮,无动作')
                pass

    def _lock_img(self, img: Union[PCRelement, str, dict], ifclick=None, ifbefore=0., ifdelay=1, elseclick=None,
                  elsedelay=0.5, alldelay=0.5, retry=0,
                  at=None, is_raise=False, lock_no=False, timeout=None):
        """
        @args:
            img:要匹配的图片目录
            2020-07-31: TheAutumnOfRice Add: img可以传入dict类型
                {PCRElement:return_value}
                或者：
                {(img,at):return_value}
                此时，at参数不起作用。
            2020-07-28：TheAutumnOfRice Add: img支持兼容PCRelement格式
            传入PCRelement后,自动填充img和at。
            如果PCRelement含有at属性而外部设置了at，以lockimg的参数为准
            ifbefore:识别成功后延迟点击时间
            ifclick:在识别到图片时要点击的坐标，列表，列表元素为坐标如(1,1)
            ifdelay:上述点击后延迟的时间
            elseclick:在找不到图片时要点击的坐标，列表，列表元素为坐标如(1,1)
            elsedelay:上述点击后延迟的时间
            retry:elseclick最多点击次数，0为无限次
            is_raise: 失败时，是否弹出错误
            lock_no: False: lock_img True: lock_no_img
            timeout: 设置为None时，使用pcr_config中的lockimg_timeout，否则用自己的。
        @pcr_config:
            lockimg_timeout: 设置为0时，不做超时处理；否则，如果超过该时间，报错
        @return:是否在retry次内点击成功
        """

        # 2020-07-12 Add: 增加了ifclick,elseclick参数对Tuple的兼容性
        # 2020-07-14 Add: added retry
        # 2020-07-30 Add: 整合了lockimg 和 lock_no_img，增加timeout
        # 2020-08-01 Add: 取消了elseclick两个click之间的间隔，elsedelay表
        #                 示elseclick操作之后的等待时间，该时间内会一直检测。
        # 2020-08-01 Add: 增加了局部timeout参数
        if elseclick is None:
            elseclick = []
        if ifclick is None:
            ifclick = []
        if type(ifclick) is not list:
            ifclick = [ifclick]
        if type(elseclick) is not list:
            elseclick = [elseclick]
        if not isinstance(img, dict):
            img = {(img, at): True}
        attempt = 0
        lasttime = time.time()
        ec_time = 0  # else click time: 上次点elseclick的时间
        if timeout is None:
            timeout = lockimg_timeout
        while True:
            screen_shot = self.getscreen()
            for i, j in img.items():
                if not isinstance(i, PCRelement):
                    _img, _at = self._get_img_at(i[0], i[1])
                else:
                    _img, _at = self._get_img_at(i, None)
                if self.is_exists(_img, at=_at, screen=screen_shot) is not lock_no:
                    if ifclick != []:
                        for clicks in ifclick:
                            time.sleep(ifbefore)
                            self.click(clicks[0], clicks[1])
                            time.sleep(ifdelay)
                    return j
            if ec_time == 0:
                # 第一次：必点
                # 此后每次等待elsedelay
                ec_time = time.time() - elsedelay
            if time.time() - ec_time >= elsedelay:
                if elseclick != []:
                    for clicks in elseclick:
                        self.click(clicks[0], clicks[1])
                    attempt += 1
                    ec_time = time.time()
            time.sleep(alldelay)
            if retry != 0 and attempt > retry:
                return False
            if timeout != 0 and time.time() - lasttime > timeout:
                if is_raise:
                    raise Exception("lock_img 超时！")
                return False

    def lock_img(self, img, ifclick=None, ifbefore=0., ifdelay=1, elseclick=None, elsedelay=2., alldelay=0.5, retry=0,
                 at=None, is_raise=True, timeout=None):
        """
        锁定图片，直到该图出现。
        图片出现后，点击ifclick；未出现，点击elseclick
        """
        return self._lock_img(img, ifclick=ifclick, ifbefore=ifbefore, ifdelay=ifdelay, elseclick=elseclick,
                              elsedelay=elsedelay,
                              alldelay=alldelay, retry=retry, at=at, is_raise=is_raise, lock_no=False, timeout=timeout)

    def lock_no_img(self, img, ifclick=None, ifbefore=0., ifdelay=1, elseclick=None, elsedelay=2., alldelay=0.5,
                    retry=0, at=None, is_raise=True, timeout=None):  # 锁定指定图像
        """
        锁定图片，直到该图消失
        图片消失后，点击ifclick；未消失，点击elseclick
        """
        return self._lock_img(img, ifclick=ifclick, ifbefore=ifbefore, ifdelay=ifdelay, elseclick=elseclick,
                              elsedelay=elsedelay,
                              alldelay=alldelay, retry=retry, at=at, is_raise=is_raise, lock_no=True, timeout=timeout)

    def click_btn(self, btn: PCRelement, elsedelay=8., timeout=30,
                  wait_for_appear: Optional[Union[str, PCRelement]] = None,
                  wait_for_disappear: Optional[Union[str, PCRelement]] = "self"):
        """
        稳定的点击按钮函数，合并了等待按钮出现与等待按钮消失的动作
        :param btn: PCRelement类型，要点击的按钮
        :param elsedelay: 尝试点击按钮后等待响应的间隔
        :param timeout: lockimg和lock_no_img所用的超时参数
        :param wait_for_appear:
            设置为None（默认）时不等待按钮出现
            设置为"self"时等待按钮自己出现
            设置为PCRelement的时候，检测该元素是否出现，出现则按下btn
        :param wait_for_disappear:
            设置为None时不等待按钮消失
            设置为"self"（默认）时等待按钮自己消失
            设置为PCRelement的时候，检测该元素是否消失
            若指定元素没有消失，则美国elsedelay的时长点击一次按钮
        """
        if isinstance(wait_for_disappear, str):
            assert wait_for_disappear == "self"
        if isinstance(wait_for_appear, str):
            assert wait_for_appear == "self"
        if wait_for_appear is not None:
            if wait_for_appear == "self":
                self.lock_img(btn, timeout=timeout)
            else:
                self.lock_img(wait_for_appear, timeout=timeout)
        if wait_for_disappear is None:
            self.click(*btn)
        else:
            if wait_for_disappear == "self":
                self.lock_no_img(btn, elseclick=btn, elsedelay=elsedelay, timeout=timeout)
            else:
                self.lock_no_img(wait_for_disappear, elseclick=btn, elsedelay=elsedelay, timeout=timeout)

    def chulijiaocheng(self, turnback="shuatu"):  # 处理教程, 最终返回刷图页面
        """
        这个处理教程函数是给chushihua.py用的

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
            screen_shot_ = self.getscreen()
            num_of_white, x, y = UIMatcher.find_gaoliang(screen_shot_)
            if num_of_white < 77000:
                try:
                    self.click(x * self.dWidth, y * self.dHeight + 20)
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
                self.click(804, 45)
                time.sleep(0.7)
                self.click(593, 372)
                time.sleep(2)
            elif UIMatcher.img_where(screen_shot_, 'img/qianwanghuodong.bmp'):
                for _ in range(3):
                    self.click(390, 369)
                    time.sleep(1)
            else:
                self.click(1, 100)
            count = 0
            time.sleep(1)
        if turnback == "shuatu":
            # 返回冒险
            self.click(480, 505)
            time.sleep(2)
            self.lock_img('img/zhuxianguanqia.jpg', elseclick=[(480, 513), (390, 369)], elsedelay=0.5)
            while True:
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/zhuxianguanqia.jpg', at=(511, 286, 614, 314)):
                    self.click(562, 253)
                    time.sleep(0.5)
                else:
                    break
            time.sleep(3)
            while True:
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/normal.jpg', at=(660, 72, 743, 94)):
                    break
                self.click(704, 84)
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


class Multithreading(threading.Thread, BaseMixin):
    """
    a 为连接Automator
    ac 为账号
    fun 为Automator中功能函数
    th_id 为线程id
    th_name 为线程名
    BY:CyiceK
    """

    # 多线程异步
    # 2020.7.11 已封装
    # 2020.7.15 改装为进程池
    # 2020.7.16 我又改了回去

    def __init__(self, kwargs):
        threading.Thread.__init__(self)
        self.th_sw = 0
        self.exitFlag = 0
        # print(kwargs)
        # kwargs = kwargs['kwargs']
        self.th_id = kwargs['account']
        self.th_name = kwargs['"pack_Thread-" + str(account)']
        self.a = kwargs['a']
        self.fun = kwargs['fun']
        self.account = kwargs['account']
        self._stop_event = threading.Event()
        pass

    def run(self):
        self.run_func(self.th_name, self.a, self.fun)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    pass
