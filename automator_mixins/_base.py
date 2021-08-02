import asyncio
import datetime
import os
import queue
import random
import subprocess
import threading
import time
from collections import OrderedDict
from pathlib import Path
from typing import Optional, Union, Type, Callable, Any

import cv2
import numpy as np
import requests
import uiautomator2 as u2

from core import log_handler
from core.MoveRecord import MoveSkipException
from core.MoveRecord import moveset
from core.constant import PCRelement, MAIN_BTN, JUQING_BTN
from core.cv import UIMatcher
from core.get_screen import ReceiveFromMinicap
from core.log_handler import pcr_log
from core.pcr_checker import ExceptionSet, ElementChecker, Checker, ReturnValue
from core.pcr_config import baidu_secretKey, baidu_apiKey, baidu_ocr_img, anticlockwise_rotation_times, ocr_mode
from core.pcr_config import debug, fast_screencut, lockimg_timeout, disable_timeout_raise, ignore_warning, \
    force_fast_screencut, adb_dir, clear_traces_and_cache, debug_record_size, debug_record_filter
from core.safe_u2 import SafeU2Handle, safe_u2_connect, timeout
from core.usercentre import AutomatorRecorder
from core.utils import make_it_as_number_as_possible
from scenes.errors import PCRError

lock = threading.Lock()

if ignore_warning:
    if debug:
        print("WARNING IGNORED.")
    import warnings
    import uiautomator2

    warnings.filterwarnings('ignore')
    uiautomator2.logger.disabled = True
    # logging.disable()


class ForceKillException(Exception):
    def __init__(self, *args):
        super().__init__()
        self.args = args


class FastScreencutException(Exception):
    def __init__(self, *args):
        super().__init__()
        self.args = args


class BeforeHomeException(Exception): pass


class DebugRecord:
    def __init__(self, record_size):
        self.Q = queue.Queue(record_size)
        self.running = OrderedDict()

    def clear(self):
        self.running.clear()

    def gettime(self):
        cur_time = time.time()
        time_str = datetime.datetime.fromtimestamp(cur_time).strftime("%H%M%S")
        return time_str

    def cutstr(self, s, length=30):
        s = str(s)
        s = s.replace("\n", "")
        if len(s) > length:
            s = s[:length] + "..."
        return s

    def getitemstr(self, item):
        if type(item) in [int, float, str, bool]:
            return self.cutstr(str(item), 100)
        elif isinstance(item, np.ndarray):
            return f"<array:{'x'.join([str(s) for s in item.shape])}>"
        else:
            return self.cutstr(str(item), 60)

    def add(self, item="()", *args, **kwargs):
        new_args = []
        for arg in args:
            new_args += [self.getitemstr(arg)]
        new_kwargs = {}
        for kw in kwargs:
            new_kwargs[kw] = self.getitemstr(kwargs[kw])
        str_args = ','.join(new_args)
        str_kwargs = ','.join(["%s:%s" % (str(k), str(v)) for k, v in new_kwargs.items()])
        cur = {"cmd": f"{item} -- {str_args} -- {str_kwargs}", "start": self.gettime(), "end": None}
        if item not in debug_record_filter:
            if self.Q.full():
                self.Q.get()
            self.Q.put(cur)
        return cur

    def get(self, running=False):
        L = self.Q.queue if not running else self.running.values()
        out = []
        for l in L:
            if l['end'] is None:
                out += [f"{l['start']} ~ Running: {l['cmd']}"]
            else:
                out += [f"{l['start']} ~ {l['end']} : {l['cmd']}"]
        return out


def DEBUG_RECORD(fun):
    def new_fun(*args, **kwargs):
        self = args[0]
        rd = self.debug_record
        cur = rd.add(fun.__name__, *args[1:], **kwargs)
        rd.running[id(cur)] = cur
        out = fun(self, *args[1:], **kwargs)
        cur['end'] = rd.gettime()
        try:
            del rd.running[id(cur)]
        except:
            pass
        return out

    return new_fun


class BaseMixin:
    """
    基础插片：包含设备信息(u2)，账户信息(account)
    辅助功能：日志，静态存储
    基本操作 （click,find_img,guochang,click_img,lock_img,lock_no_img，chulijiaocheng)
    需要在Automator中手动初始化，传入address和account参数。
    """

    def __init__(self):

        self.appRunning = False
        self.freeze = False  # 是否处于暂停状态（被_move_check检测） 由于与shift+P冲突，在enable_pause关闭时，该项才会生效
        self._task_index = {}  # 记录每个任务的index便于跳转
        self.debug_record = DebugRecord(debug_record_size)
        self.account = "debug"
        self._d: Optional[u2.Device] = None
        self.d: Optional[SafeU2Handle] = None
        self.scenes = []
        self.dWidth = 960
        self.dHeight = 540
        self.log: Optional[log_handler.pcr_log] = None
        self.AR: Optional[AutomatorRecorder] = None
        self.ms: Optional[moveset] = None
        self.debug_screen = None  # 如果debug_screen为None，则正常截图；否则，getscreen函数使用debug_screen作为读取的screen
        self.last_screen = None  # 每次调用getscreen会把图片暂存至last_screen
        self.fastscreencut_retry = 0  # 快速截图失败次数
        self.address = None
        self.today_date = datetime.date.today()
        self.cpu_occupy = 0
        self.change_time = 0.5
        self.last_screen_time = 0
        self.async_juqingtiaoguo_switch = False
        self.last_star = 0  # 上次战斗的星数
        self._move_method = ""  # 接收其它线程发送的处理方法
        self._move_msg = ""  # 接收其它线程发送的信息
        self._paused = False
        # fastscreencap
        if fast_screencut:
            self.lport: Optional[int] = None
            self.receive_minicap: Optional[ReceiveFromMinicap] = None

        self.ES = ExceptionSet(self)
        self.headers_group = {}
        self.register_basic_ES()

    def register_basic_ES(self):
        # Loading时，啥事不干（防止卡住，只检测last_screen）
        loading_fc = self.getFC(False).wait_for_loading()
        self.ES.register(loading_fc, "wait_for_loading")

    def save_last_screen(self, filename):
        dir = Path(filename).parent
        os.makedirs(dir, exist_ok=True)
        if self.last_screen is not None:
            try:
                cv2.imwrite(filename, self.last_screen)
            except Exception as e:
                self.log.write_log("error", f"保存最后一次截图失败：{e}")

    def clear_all_initFC(self, except_name=None):
        for scene in self.scenes:
            if except_name is None or scene.scene_name != except_name:
                scene.clear_initFC()

    def do_nothing(self):
        # 啥事不干
        # self.log.write_log("info", "Do nothing.")
        pass

    def _raise(self, e: Type[PCRError], *args, screen_log=True, text_log=True, error_dir=None):
        raise e(*args, automator=self, screen_log=screen_log, text_log=text_log, error_dir=error_dir)

    def check_ocr_running(self):
        # 以后可能会用
        return True

    @DEBUG_RECORD
    def init_fastscreen(self):
        if fast_screencut and Multithreading({}).program_is_stopped():
            from core.get_screen import ReceiveFromMinicap
            self.receive_minicap = ReceiveFromMinicap(self.address)
            self.receive_minicap.start()
            print("Device:", self._d.serial, "快速截图已打开，测试中……")
            for retry in range(3):
                try:
                    data = self.receive_minicap.receive_img()
                    if data is None:
                        raise Exception("读取数据超过最大尝试次数")
                    self.fastscreencut_retry = 0
                    print("Device:", self._d.serial, "快速截图运行正常。")
                    break
                except Exception as e:
                    self.receive_minicap.stop()
                    time.sleep(1)
                    if retry < 2:
                        print("Device:", self._d.serial, f"尝试重新开启快速截图...{e}")
                        self.receive_minicap = ReceiveFromMinicap(self.address)
                        self.receive_minicap.start()
            else:
                self.fastscreencut_retry = 3
                if force_fast_screencut:
                    raise FastScreencutException("快速截图打开失败！")
                else:
                    print("Device:", self._d.serial, f"快速截图打开失败！使用慢速截图。")

    @DEBUG_RECORD
    def init_device(self, address):
        """
        device: 如果是 USB 连接，则为 adb devices 的返回结果；如果是模拟器，则为模拟器的控制 URL 。
        """
        self.appRunning = False
        self.address = address
        if address != "debug":
            self._d = safe_u2_connect(address)
            self.d = SafeU2Handle(self._d)
            self.init_fastscreen()

    @DEBUG_RECORD
    def init_account(self, account, rec_addr="users"):
        self.account = account
        self.log = log_handler.pcr_log(account)  # 初始化日志
        self.AR = AutomatorRecorder(account, rec_addr)

    @DEBUG_RECORD
    def init(self, address, account, rec_addr="users"):
        # 兼容
        self.init_device(address)
        self.init_account(account, rec_addr)

    def force_kill(self):
        """
        强制结束Automator
        :return:
        """
        self.send_move_method("forcekill", "")

    @staticmethod
    def _get_at(at):
        # at参数的转换
        if isinstance(at, PCRelement):
            return at.at
        else:
            return at

    @DEBUG_RECORD
    def send_move_method(self, method, msg):
        """
        给主线程发送一条消息
        :param method: 处理方法
            restart: 重启
        :param msg: 附带信息
            restart: 重启时显示的错误提示
        """
        while self._move_method != "":
            pass
        self._move_msg = msg
        self._move_method = method
        while self._move_method != "":
            pass

    @DEBUG_RECORD
    def _move_check(self):
        """
        作为最小执行单元，接收暂停、退出等信息
        :return: False：无影响 True：造成影响
        """

        def _ck():
            if self._move_method == "restart":
                print(self.address, "- 重启")
                self._move_method = ""
                raise Exception(self._move_msg)
            if self._move_method == "forcekill":
                print(self.address, "- 强制停止")
                self._move_method = ""
                raise ForceKillException()
            if self._move_method == "skip":
                if self._move_msg is None:

                    next_id = self.ms.current_id + 1
                    if next_id in self._task_index:
                        print(self.address, "- 跳过当前任务")
                    else:
                        print(self.address, "- 已经是最后一个任务了！")
                else:
                    if str(self._move_msg).isnumeric():
                        next_id = int(self._move_msg)
                    else:
                        next_id = "asduasiudhsaiuheuifhBUNENGTIAO"
                    if next_id in self._task_index:
                        print(self.address, "- 跳转至：", self._move_msg)
                    else:
                        print(self.address, "- 不存在的任务，无法跳转！")
                self._move_method = ""
                raise MoveSkipException(self._move_msg)

        try:
            from automator_mixins._async import block_sw, enable_pause
            if enable_pause:
                if block_sw == 1:
                    print(self.address, "- 脚本暂停中~")
                    while block_sw == 1:
                        from automator_mixins._async import block_sw
                        time.sleep(1)
                        self._paused = True
                        _ck()
                    print(self.address, "- 脚本恢复~")
                    return True
            else:
                if self.freeze:
                    print(self.address, "- 脚本暂停中~")
                    while self.freeze:
                        time.sleep(1)
                        self._paused = True
                        _ck()
                    print(self.address, "- 脚本恢复~")
                    return True
        except Exception as error:
            print('暂停-错误:', error)
            return True
        _ck()

    def setFCHeader(self, group_name, FCFun: Callable[[ElementChecker], Any], enable=True, unique=True):
        """
        给self.getFC中添加一些header。
        默认的_move_check和ExceptionSet的header不会收到影响。
        <可用于with>
        :param group_name: 挂载header的名称
        :param FCFun: FC控制函数，参数为FC，里面应该调用一系列FC的成员函数
        :param enable: 初始化可用状态（自己被调用时，会设置自己enable=False防止重复调用）
        :param unique: 设置为True可以在自己被调用时屏蔽其它的Header
        """
        self.headers_group[group_name] = dict(FCFun=FCFun, enable=enable, unique=unique)
        outer = self

        class _clear_when_exit:
            def __enter__(self):
                pass

            def __exit__(self):
                outer.clearFCHeader(group_name)

        return _clear_when_exit()

    def clearFCHeader(self, group_name):
        if group_name in self.headers_group:
            del self.headers_group[group_name]

    def getFC(self, header=True):
        """
        获得包含自身实例及异常集的FunctionChecker
        """
        FC = ElementChecker(self)
        if header:
            FC.add(Checker(self._move_check, name="_move_check"), clear=True)
            FC.bind_ES(self.ES, name="ExceptionSet")
            FC.header = True
            for myheaders in self.headers_group.values():
                FCFun = myheaders["FCFun"]
                enable = myheaders["enable"]
                unique = myheaders["unique"]
                if enable is False:
                    continue
                enable_list = []

                def _set():
                    if unique:
                        for h in self.headers_group.values():
                            if h["enable"]:
                                enable_list.append(h)
                                h["enable"] = False
                    else:
                        enable_list.append(myheaders)
                        myheaders["enable"] = False

                def _unset():
                    for h in enable_list:
                        h["enable"] = True

                FC.add_process(_set, name="Enter My Header")
                FCFun(FC)
                FC.add_process(_unset, name="Exit My Header")
        else:
            FC.header = False
        return FC

    @DEBUG_RECORD
    def click_img(self, screen, img, threshold=0.84, at=None, pre_delay=0., post_delay=0., method=cv2.TM_CCOEFF_NORMED):
        """
        try to click the img
        :param screen:
        :param threshold:
        :param img:
        :return: success
        """
        self._move_check()
        img, at = self._get_img_at(img, at)
        position = UIMatcher.img_where(screen, img, threshold, at, method)
        if position:
            self.click(*position, pre_delay, post_delay)
            return True
        else:
            return False

    @DEBUG_RECORD
    def click(self, *args, pre_delay=0., post_delay=0., **kwargs):
        """
        点击函数
        2020-07-28 TheAutumnOfRice:把x,y参数换程args参数以遍兼容各种点击类型

        1.  若args为数字的x,y，则点击该位置。

            如:self.click(100,200)

        2.  若args为PCRelement类型（见core.constant），则：
            点击其坐标

        :param pre_delay: 前置延时
        :param post_delay: 后置延时
        :return: True
        """
        self._move_check()
        time.sleep(pre_delay)
        if len(args) >= 2 and isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
            # (x,y)型：点击坐标
            x = args[0]
            y = args[1]
            self.d.click(x, y)
            time.sleep(post_delay)
            return True
        elif len(args) == 1 and isinstance(args[0], PCRelement):
            # 点击一个PCRelement元素
            pe = args[0]
            self.d.click(pe.x, pe.y)
            time.sleep(post_delay)
            return True

    @staticmethod
    def _get_img_at(img, at):
        at = BaseMixin._get_at(at)
        if isinstance(img, PCRelement):
            if at is None:
                at = img.at
            img = img.img
        return img, at

    @DEBUG_RECORD
    def is_exists(self, img, threshold=0.84, at=None, screen=None, is_black=False,
                  black_threshold=1500, method=cv2.TM_CCOEFF_NORMED):
        """
        判断一个图片是否存在。
        :param black_threshold: 判断暗点的阈值
        :param is_black: 是否判断为暗色图片（多用于检测点击按钮后颜色变暗）灰色返回Ture,默认需要配合at，否则自行调整阈值
        :param method:
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
        return UIMatcher.img_where(screen, img, threshold, at, method, is_black, black_threshold) is not False

    @DEBUG_RECORD
    def img_prob(self, img, at=None, screen=None, method=cv2.TM_CCOEFF_NORMED):
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
        return UIMatcher.img_prob(screen, img, at, method)

    @DEBUG_RECORD
    def img_where_all(self, img, threshold=0.9, at=None, screen=None, method=cv2.TM_CCOEFF_NORMED):
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
        return UIMatcher.img_all_where(screen, img, threshold, at, method)

    @DEBUG_RECORD
    def img_where_all_prob(self, img, threshold=0.9, at=None, screen=None, method=cv2.TM_CCOEFF_NORMED):
        """
        返回一个图片所有的位置和prob
        :param img:
            一个字符串，表示图片的地址；或者为PCRelement类型。
            当img为PCRelement时，如果at参数为None，则会使用img.at。
        :param threshold: 阈值
        :param at: 搜素范围
        :param screen: 若设置为None，则重新截图；否则使用screen为截图
        :return: list[(prob,x,y,at)]
        """
        if screen is None:
            screen = self.getscreen()
        img, at = self._get_img_at(img, at)
        return UIMatcher.img_all_prob(screen, img, threshold, at, method)

    @DEBUG_RECORD
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
        eqt = np.sum(np.abs(img1 - img2) < similarity) / img1.size
        if debug:
            print("EQT:", eqt)
        return eqt

    @DEBUG_RECORD
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
            self._move_check()
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

    @DEBUG_RECORD
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
            self._move_check()
            retry += 1
            time.sleep(delay)
            sc2 = self.getscreen()
            value = self.img_equal(sc, sc2, at, similarity)
            if debug:
                print("Stable : ", value, " <? ", threshold)
            if value < threshold:
                return True
        return False

    def not_loading(self, screen=None):
        """
        判断是否在黑屏Loading 或者 右上角Connecting
        """
        if self.is_exists(img='img/error/connecting.bmp', at=(748, 20, 931, 53), screen=screen):
            return False
        sc_cut = UIMatcher.img_cut(screen, MAIN_BTN["loading_left"].at)
        if (sc_cut == 1).all():
            # 全黑
            return False
        return True

    @DEBUG_RECORD
    def wait_for_loading(self, screen=None, delay=0.5, timeout=30):
        """
        等待黑屏loading结束
        :param screen: 设置为None时，截图，否则使用screen
        :param delay: 检测间隔
        :param timeout: 超过timeout，报错
        Add 2020-08-15: 增加对Connect的检测。
        """
        time.sleep(delay)
        sc = self.getscreen() if screen is None else screen
        last_time = time.time()
        while True:
            self._move_check()
            if self.is_exists(img='img/error/connecting.bmp', at=(748, 20, 931, 53), screen=sc):
                time.sleep(delay)
                sc = self.getscreen()
                continue
            sc_cut = UIMatcher.img_cut(sc, MAIN_BTN["loading_left"].at)
            if not (sc_cut == 1).all():
                break
            if time.time() - last_time > timeout:
                raise Exception("Loading 超时！")
            time.sleep(delay)
            sc = self.getscreen()

    @DEBUG_RECORD
    def check_dict_id(self, id_dict, screen=None, max_threshold=0.8, diff_threshold=0.05, max_retry=3):
        """
        识别不同图的编号，比较其概率
        :param id_dict: 字典，{key:PCRElement}，表示{编号:图片}
        :param screen: 设置为None时，第一次重新截图
        :param max_threshold: 最大阈值，获得图片最大概率必须超过max_threshold
        :param diff_threshold: 相差阈值，第一大的概率和第二大的概率差必须超过diff_threshold
        :return:
            None: 识别失败
            Else: 识别的key
        """
        for retry in range(max_retry):
            sc = self.getscreen() if screen is None else screen
            screen = None
            pdict = {}
            for i, j in id_dict.items():
                pdict[i] = self.img_prob(j, screen=sc)
            tu = max(pdict, key=lambda x: pdict[x])
            l = sorted(pdict.values(), reverse=True)
            if debug:
                print(tu)
                print(l)
            if l[0] < max_threshold or l[0] - l[1] < diff_threshold:
                time.sleep(0.5)
                continue
            else:
                return tu
        return None

    def run_func(self, th_name, a, fun, async_sexitflag=False):
        if async_sexitflag:
            th_name.exit()
            pass
        else:
            self.do(a, fun)

    def do(self, a, fun):
        # 自定义，在此定义你要运行的参数
        getattr(asyncio, 'run')(fun)
        # getattr获取asyncio中run对象，然后进行调用
        # 凄凄惨惨的替代eval这类危险的函数
        pass

    def c_async(self, a, account, fun, sync=False, async_sexitflag=False):
        _async_infodic = {'a': a, 'account': account, 'fun': fun,
                          '"pack_Thread-" + str(account)': "pack_Thread-" + str(account),
                          'async_sexitflag': async_sexitflag}
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

    @DEBUG_RECORD
    def getscreen(self, filename=None):
        """
        包装了self.d.screenshot
        如果self.debug_screen为None，则
        :return: 截图的opencv格式
        """
        # 如果debug_screen为None，则正常截图；
        # 否则，getscreen函数使用debug_screen作为读取的screen

        try:
            from automator_mixins._async import block_sw, enable_pause
            if enable_pause:
                if block_sw == 1:
                    print(self.address, "- 截图暂停中~")
                    while block_sw == 1:
                        from automator_mixins._async import block_sw
                        time.sleep(1)
                        self._paused = True
                    print(self.address, "- 截图恢复~")
            else:
                if self.freeze:
                    print(self.address, "- 截图暂停中~")
                    while self.freeze:
                        time.sleep(1)
                        self._paused = True
                    print(self.address, "- 截图恢复~")
        except Exception as error:
            print('截图暂停-错误:', error)

        if self.debug_screen is None:
            if fast_screencut and self.fastscreencut_retry < 3:
                try:
                    data = self.receive_minicap.receive_img()
                    if data is None:
                        raise Exception("读取数据超过最大尝试次数")
                    # 改用内存缓存
                    self.last_screen = data
                    # 如果传入了文件路径参数，则保存文件
                    if filename is not None:
                        cv2.imwrite(filename, self.last_screen)
                    self.fastscreencut_retry = 0
                except Exception as e:
                    if force_fast_screencut:
                        raise FastScreencutException(*e.args)
                    else:
                        self.log.write_log("warning", f"快速截图出错 {e}， 使用低速截图")
                        self.fastscreencut_retry += 1
                        if self.fastscreencut_retry == 3:
                            self.log.write_log("error", f"快速截图连续出错3次，关闭快速截图。")
                            self.receive_minicap.stop()
                        self.last_screen = self.d.screenshot(filename, format="opencv")
            else:
                if filename is None:
                    self.last_screen = self.d.screenshot(filename, format="opencv")
                else:
                    self.d.screenshot(filename, format="opencv")
                    self.last_screen = cv2.imread(filename)
            self.last_screen_time = time.time()
            output_screen = UIMatcher.AutoRotateClockWise90(self.last_screen)
            if debug:
                if output_screen is None:
                    print("ERROR！截图为空！")
            if output_screen is not None and output_screen.shape != (540, 960, 3):
                print("Warning: 截屏大小为", output_screen.shape, "应为 (540,960,3)， 可能模拟器分辨率没有被正确设置！")
            return output_screen
        else:
            if isinstance(self.debug_screen, str):
                return cv2.imread(self.debug_screen)
            else:
                return self.debug_screen

    @DEBUG_RECORD
    def find_img(self, img, at=None, alldelay=0.5,
                 ifclick=None, ifbefore=0.5, ifdelay=1,
                 elseclick=None, elsedelay=0.5, retry=0):
        """
        前身：_lock_img

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
            self._move_check()
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

    @DEBUG_RECORD
    def guochang(self, screen_shot, template_paths, suiji=1):
        # suji标号置1, 表示未找到时将点击左上角, 置0则不点击
        # 输入截图, 模板list, 得到下一次操作
        # 2020-08-08 建议弃用该函数。

        screen_shot = screen_shot
        template_paths = template_paths
        active_path = UIMatcher.imgs_where(screen_shot, template_paths)
        if active_path:
            # print(active_path)
            if 'img/juqing/tiaoguo_1.bmp' in active_path:
                x, y = active_path['img/juqing/tiaoguo_1.bmp']
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

    @DEBUG_RECORD
    def lock_fun(self, RTFun, *args, ifclick=None, ifbefore=0., ifdelay=1., elseclick=None,
                 elsedelay=0.5, alldelay=0.5, retry=None, is_raise=False, timeout=None, elseafter=0., **kwargs):
        """
        任意方法锁定
        @RTFun 锁定的函数
            返回False，锁定失败
            返回其它，锁定成功，返回值为函数返回值
        """
        if elseclick is None:
            elseclick = []
        if ifclick is None:
            ifclick = []
        if type(ifclick) is not list:
            ifclick = [ifclick]
        if type(elseclick) is not list:
            elseclick = [elseclick]
        FC = self.getFC()
        if timeout is None:
            timeout = lockimg_timeout

        def f():
            rv = RTFun(*args, **kwargs)
            if rv is False:
                return False
            else:
                for clicks in ifclick:
                    time.sleep(ifbefore)
                    self.click(clicks[0], clicks[1], post_delay=elseafter)
                    time.sleep(ifdelay)
                raise ReturnValue(rv)

        def f2():
            for clicks in elseclick:
                self.click(clicks[0], clicks[1], post_delay=elseafter)

        FC.add(Checker(f, name="lock_fun - RTFun"))
        FC.add_intervalprocess(f2, retry, elsedelay, name="lock_fun - elseclick")
        FC.lock(alldelay, timeout, is_raise=False if disable_timeout_raise else is_raise)

    @DEBUG_RECORD
    def _lock_img(self, img: Union[PCRelement, str, dict, list], ifclick=None, ifbefore=0., ifdelay=1., elseclick=None,
                  elsedelay=0.5, alldelay=0.5, retry=None, side_check=None,
                  at=None, is_raise=False, lock_no=False, timeout=None, method=cv2.TM_CCOEFF_NORMED, threshold=0.84,
                  elseafter=0.):
        """
        @args:
            img:要匹配的图片目录
            2020-07-31: TheAutumnOfRice Add: img可以传入dict类型
                {PCRElement:return_value}
                或者：
                {(img,at):return_value}
                此时，at参数不起作用。
            2020-08-06： TheAutumnOfRice Add: img可以传入list类型
                [PCRElement]或者[(img,at)]
                此时，每一个找到的PCRElement，都会对应True
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
            side_check：传入字符串然后调用字符串里边的基于_base的函数方法
            elseafter: 点击elseclick后等待的时间
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
        # 2020-08-06 Add: img可以传入list了
        # 2020-8-19 Add:暂停+方法调用
        # 2021-1-10 大改，采用新框架FC
        if elseclick is None:
            elseclick = []
        if ifclick is None:
            ifclick = []
        if type(ifclick) is not list:
            ifclick = [ifclick]
        if type(elseclick) is not list:
            elseclick = [elseclick]
        if isinstance(img, list):
            tmp = img
            img = {}
            for i in tmp:
                img[i] = True
        if not isinstance(img, dict):
            img = {(img, at): True}
        if timeout is None:
            timeout = lockimg_timeout
        FC = self.getFC()
        FC.getscreen()
        if side_check is not None:
            def f(screen):
                return side_check(screen)

            FC.add(Checker(f, funvar=["screen"], name="lock_img - side_check"), clear=True)

        def f2():
            for clicks in ifclick:
                time.sleep(ifbefore)
                self.click(clicks[0], clicks[1], post_delay=elseafter)
                time.sleep(ifdelay)

        for i, j in img.items():
            if not isinstance(i, PCRelement):
                _img, _at = self._get_img_at(i[0], i[1])
            else:
                _img, _at = self._get_img_at(i, None)
            if lock_no:
                fun = FC.not_exist
            else:
                fun = FC.exist
            fun(PCRelement(img=_img, at=_at), dofunction=f2, rv=j, method=method, threshold=threshold)

        def f3():
            for clicks in elseclick:
                self.click(clicks[0], clicks[1], post_delay=elseafter)

        FC.add_intervalprocess(f3, retry, elsedelay, name="lock_img - elseclick")
        return FC.lock(alldelay, timeout, is_raise=False if disable_timeout_raise else is_raise)

    @DEBUG_RECORD
    def lock_img(self, img, ifclick=None, ifbefore=0., ifdelay=1., elseclick=None, elsedelay=2., alldelay=0.5, retry=0,
                 at=None, is_raise=True, timeout=None, method=cv2.TM_CCOEFF_NORMED, threshold=0.84, side_check=None,
                 elseafter=0.):
        """
        锁定图片，直到该图出现。
        图片出现后，点击ifclick；未出现，点击elseclick
        """
        return self._lock_img(img, ifclick=ifclick, ifbefore=ifbefore, ifdelay=ifdelay, elseclick=elseclick,
                              elsedelay=elsedelay,
                              alldelay=alldelay, retry=retry, at=at, is_raise=is_raise, lock_no=False, timeout=timeout,
                              method=method, threshold=threshold, side_check=side_check, elseafter=elseafter)

    @DEBUG_RECORD
    def lock_no_img(self, img, ifclick=None, ifbefore=0., ifdelay=1., elseclick=None, elsedelay=2., alldelay=0.5,
                    retry=0, at=None, is_raise=True, timeout=None, method=cv2.TM_CCOEFF_NORMED,
                    threshold=0.84, side_check=None, elseafter=0.):  # 锁定指定图像
        """
        锁定图片，直到该图消失
        图片消失后，点击ifclick；未消失，点击elseclick
        """
        return self._lock_img(img, ifclick=ifclick, ifbefore=ifbefore, ifdelay=ifdelay, elseclick=elseclick,
                              elsedelay=elsedelay,
                              alldelay=alldelay, retry=retry, at=at, is_raise=is_raise, lock_no=True, timeout=timeout,
                              method=method, threshold=threshold, side_check=side_check, elseafter=elseafter)

    @DEBUG_RECORD
    def click_btn(self, btn: PCRelement, elsedelay=8., timeout=30., wait_self_before=False,
                  until_appear: Optional[Union[PCRelement, dict, list]] = None,
                  until_disappear: Optional[Union[str, PCRelement, dict, list]] = "self",
                  retry=0, is_raise=True, method=cv2.TM_CCOEFF_NORMED, elseafter=None,
                  side_check=None):
        """
        稳定的点击按钮函数，合并了等待按钮出现与等待按钮消失的动作
        :param side_check: 检测
        :param retry: 尝试次数,少用
        :param btn: PCRelement类型，要点击的按钮
        :param elsedelay: 尝试点击按钮后等待响应的间隔
        :param timeout: lockimg和lock_no_img所用的超时参数
        :param wait_self_before: 是否等待本按钮出现，再进行点击
        :param until_appear: 是否在点击后等待该元素出现，再返回
            设置为None（默认）时不等待按钮出现
            设置为PCRelement的时候，检测该元素是否出现，出现则返回
        :param until_disappear: 是否在点击后等待该元素消失，再返回
            设置为None时不等待按钮消失
            设置为"self"（默认）时等待按钮自己消失
            设置为PCRelement的时候，检测该元素是否消失
            若指定元素没有消失，则每过elsedelay的时长点击一次按钮
        （until_disappear,until_appear不要同时使用）
        :param is_raise:
            是否报错。设置为False时，匹配失败，返回False
        :param method:
            用于lockimg的方法
        :param elseafter:
            默认值None，此时，若条件为until_disappear="self"，则设置为0.8，否则为0.
            点击之后的等待时间。
        """
        r = 0
        if isinstance(until_disappear, str):
            assert until_disappear == "self"
        if wait_self_before is True:
            r = self.lock_img(btn, timeout=timeout, retry=retry, is_raise=is_raise, method=method,
                              side_check=side_check)
        if until_disappear is None and until_appear is None:
            self.click(btn, post_delay=0.5)  # 这边不加延迟，点击的波纹会影响到until_disappear自己
        else:
            if until_appear is not None:
                r = self.lock_img(until_appear, elseclick=btn, elsedelay=elsedelay, timeout=timeout, retry=retry,
                                  is_raise=is_raise, method=method, elseafter=0 if elseafter is None else elseafter,
                                  side_check=side_check)
            elif until_disappear == "self":
                r = self.lock_no_img(btn, elseclick=btn, elsedelay=elsedelay, timeout=timeout, retry=retry,
                                     is_raise=is_raise, method=method,
                                     elseafter=0.8 if elseafter is None else elseafter, side_check=side_check)
            elif until_disappear is not None:
                r = self.lock_no_img(until_disappear, elseclick=btn, elsedelay=elsedelay, timeout=timeout,
                                     retry=retry, is_raise=is_raise, method=method,
                                     elseafter=0 if elseafter is None else elseafter, side_check=side_check)
        return r

    @timeout(300, "处理教程时间过长，超过5分钟！")
    @DEBUG_RECORD
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
        # 2021-1-10 FC改写
        count = [0]
        FC = self.getFC().getscreen()

        def f(screen):
            screen_shot_ = screen
            try:
                # 处理完教程后可能会卡活动提示
                r_list = self.img_where_all(img=MAIN_BTN["guanbi"], screen=screen_shot_, threshold=0.90)
                if self.lock_no_img(img=MAIN_BTN["guanbi"], elseclick=(int(r_list[0]), int(r_list[1])),
                                    side_check=self.juqing_kkr):
                    time.sleep(5)
            except:
                pass
            num_of_white, _, x, y = UIMatcher.find_gaoliang(screen_shot_)
            if num_of_white < 77000:
                try:
                    self.click(x * self.dWidth, y * self.dHeight + 20)
                except:
                    pass
                time.sleep(1)
                raise ReturnValue("continue")

            if UIMatcher.img_where(screen_shot_, 'img/liwu.bmp', at=(891, 413, 930, 452)):
                count[0] += 1
                if count[0] > 2:
                    raise ReturnValue("break")
                time.sleep(1)
                raise ReturnValue("continue")
            elif UIMatcher.img_where(screen_shot_, 'img/jiaruhanghui.jpg'):
                raise ReturnValue("break")
            elif self.is_exists(MAIN_BTN["xiazai"], screen=screen_shot_):
                self.click(MAIN_BTN["xiazai"])
            elif self.click_img(screen_shot_, 'img/xiayibu.jpg'):
                time.sleep(2)
            elif self.click_img(screen_shot_, 'img/niudan_jiasu.jpg', at=(700, 0, 960, 100)):
                pass
            elif self.click_img(screen_shot_, 'img/wuyuyin.jpg', at=(450, 355, 512, 374)):
                time.sleep(3)
            elif self.click_img(screen_shot_, 'img/juqing/tiaoguo_2.bmp'):
                time.sleep(3)
            elif self.click_img(screen_shot_, 'img/zhuye.jpg', at=(46, 496, 123, 537)):
                for _ in range(5):
                    self.click(MAIN_BTN["zhuye"])  # Speed  Up CLick
            elif self.click_img(screen_shot_, 'img/juqing/caidanyuan.bmp', at=(898, 23, 939, 62)):
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
                for _ in range(6):
                    self.click(1, 100)  # Speed Up Click
            count[0] = 0

        FC.add(Checker(f))
        FC.lock(delay=1, until="break")
        if turnback == "shuatu":
            # 返回冒险
            self.click(480, 505)
            time.sleep(2)
            self.lock_img('img/zhuxianguanqia.jpg', elseclick=[(480, 513), (390, 369)], elsedelay=0.5)

            def f2(screen):
                screen_shot_ = screen
                if UIMatcher.img_where(screen_shot_, 'img/zhuxianguanqia.jpg', at=(511, 286, 614, 314)):
                    self.click(562, 253)
                    time.sleep(0.5)
                else:
                    raise ReturnValue("break")

            self.getFC().getscreen().add(Checker(f2)).lock(timeout=lockimg_timeout, until="break")
            time.sleep(3)

            def f3(screen):
                screen_shot_ = screen
                if UIMatcher.img_where(screen_shot_, 'img/normal.jpg', at=(660, 72, 743, 94)):
                    raise ReturnValue("break")
                self.click(704, 84)
                time.sleep(0.5)

            self.getFC().getscreen().add(Checker(f3)).lock(timeout=lockimg_timeout, until="break")

    def task_start(self):
        # 标记这个用户开始重新刷图了
        d = self.AR.get_run_status()
        d["finished"] = False
        d["current"] = "..."
        self.AR.set_run_status(d)

    def task_finished(self):
        # 标记这个用户已经刷完了图
        d = self.AR.get_run_status()
        d["finished"] = True
        self.AR.set_run_status(d)

    def task_current(self, title):
        # 标记这个用户当前正在进行的项目
        d = self.AR.get_run_status()
        d["current"] = title
        self.AR.set_run_status(d)

    def task_error(self, error):
        # 标记某一项错误，并停止刷图
        d = self.AR.get_run_status()
        d["finished"] = True
        d["error"] = error
        self.AR.set_run_status(d)

    @DEBUG_RECORD
    def juqing_kkr(self, screen_shot=None):
        """
        处理剧情+剧情版的可可萝
        :return:
        """
        if screen_shot is None:
            screen_shot = self.getscreen()
        if self.is_exists(JUQING_BTN["caidanyuan"], screen=screen_shot):
            self.click_btn(JUQING_BTN["caidanyuan"], wait_self_before=True, until_appear=JUQING_BTN["tiaoguo_1"])  # 菜单
            self.click_btn(JUQING_BTN["tiaoguo_1"], until_appear=JUQING_BTN["tiaoguo_2"])  # 跳过
            self.click_btn(JUQING_BTN["tiaoguo_2"], until_disappear=JUQING_BTN["tiaoguo_2"])  # 蓝色跳过
            return True
        elif self.is_exists(img='img/kekeluo.bmp', at=(181, 388, 384, 451), screen=screen_shot):
            # 防妈骑脸
            self.lock_no_img('img/kekeluo.bmp', elseclick=[(1, 1)], at=(181, 388, 384, 451))
            return True
        return False

    @DEBUG_RECORD
    def right_kkr(self, screen=None):
        """
        处理提示kkr。一般在右边。
        处理方法：点屏幕
        :param screen:
        """
        flag = False
        if screen is None:
            screen = self.getscreen()
        cnt = 0
        while self.is_exists(MAIN_BTN["right_kkr"], screen=screen):
            self.click(1, 1, post_delay=1)
            flag = True
            cnt += 1
            if cnt >= 10:
                raise Exception("点了10次，可可罗依然没有消失！")
            screen = self.getscreen()
        return flag

    @DEBUG_RECORD
    def phone_privacy(self):
        """
        2020/7/10
        模拟器隐私函数
        '高'匿名 防记录(

        2021/7/27
        加点料，蓝叠不支持修改手机信息

        By：CyiceK
        ！未经许可，不可在本项目外使用！（不想惹事生非
        :return:
        """

        def luhn_residue(digits):
            return sum(sum(divmod(int(d) * (1 + i % 2), 10))
                       for i, d in enumerate(digits[::-1])) % 10

        def _get_imei(n):
            part = ''.join(str(random.randrange(0, 9)) for _ in range(n - 1))
            res = luhn_residue('{}{}'.format(part, 0))
            return '{}{}'.format(part, -res % 10)

        def run_cmd(commands):
            p = subprocess.Popen(f'{commands}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.stdout.readlines()

        # print("》》》匿名开始《《《", self.address)
        # tmp_rand = []
        tmp_rand = random.sample(range(1, 10), 3)
        phone_model = {
            1: 'LIO-AN00',
            2: 'TAS-AN00',
            3: 'TAS-AL00',
            4: 'AUSU-AT00',
            5: 'AAA-SN00',
            6: 'GMI1910',
            7: 'G-OXLPix',
            8: 'AM-1000',
            9: 'G7',
        }
        phone_manufacturer = {
            1: 'HUAWEI',
            2: 'MEIZU',
            3: 'XIAOMI',
            4: 'OPPO',
            5: 'VIVO',
            6: 'MOTO',
            7: 'GooglePix',
            8: 'Redmi',
            9: 'LG',
        }
        run_cmd('cd %s & adb -s %s shell setprop ro.product.model %s && exit' % (
            adb_dir, self.address, phone_model[tmp_rand[0]]))
        run_cmd('cd %s & adb -s %s shell setprop ro.product.brand %s && exit' % (
            adb_dir, self.address, phone_model[tmp_rand[0]]))
        run_cmd('cd %s & adb -s %s shell setprop ro.product.manufacturer %s && exit' % (adb_dir,
                                                                                        self.address,
                                                                                        phone_manufacturer[
                                                                                            tmp_rand[1]]))
        run_cmd('cd %s & adb -s %s shell setprop phone.imei %s && exit' % (adb_dir, self.address, _get_imei(15)))
        run_cmd('cd %s & adb -s %s shell setprop ro.product.name %s && exit' % (
            adb_dir, self.address, phone_model[tmp_rand[2]]))
        run_cmd('cd %s & adb -s %s shell setprop phone.imsi %s && exit' % (adb_dir, self.address, _get_imei(15)))
        run_cmd('cd %s & adb -s %s shell setprop phone.linenum %s && exit' % (adb_dir, self.address, _get_imei(11)))
        run_cmd('cd %s & adb -s %s shell setprop phone.simserial %s && exit' % (
            adb_dir, self.address, _get_imei(20)))
        # print("》》》匿名完毕《《《")
        if clear_traces_and_cache:
            # 清除痕迹和缓存
            clear_list = ["/storage/emulated/0/bilibili_data", "/storage/emulated/0/bilibili_time",
                          "data/data/com.bilibili.priconne/databases", "data/data/com.bilibili.priconne/shared_prefs"]
            not_clear_file = ["*.playerprefs.xml", "config_data.xml", "agree_license_info.xml"]
            for i in clear_list:
                if i == clear_list[3]:
                    for j in not_clear_file:
                        run_cmd(
                            f'cd {adb_dir} && adb -s {self.address} shell "su -c ' + "'" + f"cd {i} && mv -force {j} .. "
                                                                                           f"&& exit" + "'")
                run_cmd(
                    f'cd {adb_dir} && adb -s {self.address} shell "su -c ' + "'" + f"cd {i} && rm -rf * && exit" + "'")
                if i == clear_list[3]:
                    for j in not_clear_file:
                        run_cmd(
                            f'cd {adb_dir} && adb -s {self.address} shell "su -c ' + "'" + f"cd {i} && mv -force ../{j} "
                                                                                           f"&& exit" + "'")

            clear_list2 = ["time_*", "data_*"]
            for i in clear_list2:
                run_cmd(
                    f'cd {adb_dir} && adb -s {self.address} shell "su -c ' + "'" + f"cd /data/data/com.bilibili"
                                                                                   f".priconne/files && rm -rf "
                                                                                   f"{i} && exit" + "'")
            run_cmd(
                f'cd {adb_dir} && adb -s {self.address} shell "su -c ' + "'" + 'cd data/data/com.bilibili.priconne'
                                                                               '/lib && chmod 000 libsecsdk.so'
                                                                               ' && exit' + "'")
            # run_cmd(f'cd {adb_dir} && adb -s {self.address} shell "find. - name "time_*" | xargs rm - rf && exit"')
            # run_cmd(f'cd {adb_dir} && adb -s {self.address} shell "find. - name "data_*" | xargs rm - rf && exit"')
            # print("》》》匿名完毕《《《")

    def output_debug_info(self, running):
        return self.debug_record.get(running)

    @DEBUG_RECORD
    def ocr_center(self, x1, y1, x2, y2, screen_shot=None, size=1.0, credibility=0.91):
        """
        :param credibility: 结果可信度阈值,目前仅有本地OCR2才用到
        :param size: 放大的大小
        :param x1: 左上坐标
        :param y1: 左上坐标
        :param x2: 右下坐标
        :param y2: 右下坐标
        :param screen_shot: 截图
        :return:
        """
        global ocr_text

        try:
            requests.get(url="http://127.0.0.1:5000/ocr/")
        except:
            pcr_log(self.account).write_log(level='error', message='无法连接到OCR,请尝试重新开启app.py')
            return -1

        if len(ocr_mode) == 0:
            return -1
        # OCR识别任务分配
        if ocr_mode == "智能":
            baidu_ocr_ping = requests.get(url="https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic")
            code = baidu_ocr_ping.status_code
            if code == 200:
                ocr_text = self.baidu_ocr(x1, y1, x2, y2, screen_shot=screen_shot, size=size)
                if ocr_text == -1:
                    ocr_text = self.ocr_local(x1, y1, x2, y2, screen_shot=screen_shot, size=size)
            else:
                ocr_text = self.ocr_local(x1, y1, x2, y2, screen_shot=screen_shot, size=size)
        elif ocr_mode == "网络":
            ocr_text = self.baidu_ocr(x1, y1, x2, y2, screen_shot=screen_shot, size=size)
        elif ocr_mode == "本地":
            ocr_text = self.ocr_local(x1, y1, x2, y2, screen_shot=screen_shot, size=size)
        elif ocr_mode == "本地2":
            ocr_text = self.ocr_local2(x1, y1, x2, y2, screen_shot=screen_shot, size=size, credibility=credibility)
        elif ocr_mode == "混合":
            # 机器伪随机
            ocr_way = random.randint(1, 3)
            if ocr_way == 1:
                ocr_text = self.baidu_ocr(x1, y1, x2, y2, screen_shot=screen_shot, size=size)
            elif ocr_way == 2:
                ocr_text = self.ocr_local(x1, y1, x2, y2, screen_shot=screen_shot, size=size)
            elif ocr_way == 3:
                ocr_text = self.ocr_local2(x1, y1, x2, y2, screen_shot=screen_shot, size=size, credibility=credibility)

        # OCR返回的数据 纠错
        try:
            if ocr_text:
                return str(ocr_text)
            else:
                return -1
        except:
            raise Exception("ocr-error", "OCR识别错误。")

    def ocr_local(self, x1, y1, x2, y2, screen_shot=None, size=1.0):
        if screen_shot is None:
            screen_shot = self.getscreen()

        try:
            if screen_shot.shape[0] > screen_shot.shape[1]:
                if anticlockwise_rotation_times >= 1:
                    for _ in range(anticlockwise_rotation_times):
                        screen_shot = UIMatcher.AutoRotateClockWise90(screen_shot)
                screen_shot = UIMatcher.AutoRotateClockWise90(screen_shot)
            part = screen_shot[y1:y2, x1:x2]  # 对角线点坐标
            part = cv2.resize(part, None, fx=size, fy=size, interpolation=cv2.INTER_LINEAR)  # 利用resize调整图片大小
            img_binary = cv2.imencode('.png', part)[1].tobytes()
            files = {'file': ('tmp.png', img_binary, 'image/png')}
            local_ocr_text = requests.post(url="http://127.0.0.1:5000/ocr/local_ocr/", files=files)
            if debug:
                print('本地OCR识别结果：%s' % local_ocr_text.text)
            return local_ocr_text.text
        except Exception as ocr_error:
            pcr_log(self.account).write_log(level='error', message='本地OCR识别失败，原因：%s' % ocr_error)
            return -1

    # 对当前界面(x1,y1)->(x2,y2)的矩形内容进行OCR识别
    # 使用Baidu OCR接口
    def baidu_ocr(self, x1, y1, x2, y2, size=1.0, screen_shot=None):
        # size表示相对原图的放大/缩小倍率，1.0为原图大小，2.0表示放大两倍，0.5表示缩小两倍
        # 默认原图大小（1.0）
        if len(baidu_apiKey) == 0 or len(baidu_secretKey) == 0:
            pcr_log(self.account).write_log(level='error', message='读取SecretKey或apiKey失败！')
            return -1

        # 强制size为1.0，避免百度无法识图
        size = 1.0

        if screen_shot is None:
            screen_shot = self.getscreen()
        # from numpy import rot90
        # screen_shot_ = rot90(screen_shot_)  # 旋转90°
        if baidu_ocr_img:
            cv2.imwrite('baidu_ocr.bmp', screen_shot)
        if screen_shot.shape[0] > screen_shot.shape[1]:
            if anticlockwise_rotation_times >= 1:
                for _ in range(anticlockwise_rotation_times):
                    screen_shot = UIMatcher.AutoRotateClockWise90(screen_shot)
            screen_shot = UIMatcher.AutoRotateClockWise90(screen_shot)
            # cv2.imwrite('fuck_rot90_test.bmp', screen_shot_)
            # screen_shot_ = rot90(screen_shot_)  # 旋转90°
            pass
        part = screen_shot[y1:y2, x1:x2]  # 对角线点坐标
        part = cv2.resize(part, None, fx=size, fy=size, interpolation=cv2.INTER_LINEAR)  # 利用resize调整图片大小
        partbin = cv2.imencode('.jpg', part)[1]  # 转成base64编码（误）

        try:
            files = {'file': ('tmp.png', partbin, 'image/png')}
            result = requests.post(url="http://127.0.0.1:5000/ocr/baidu_ocr/", files=files)
            # 原生输出有助于开发者
            result = result.json().get('words_result')[0].get('words')
            if debug:
                print('百度OCR识别结果：%s' % result)
            return result
        except:
            pcr_log(self.account).write_log(level='error', message='百度OCR识别失败！请检查apikey和secretkey以及截图范围返回结果'
                                                                   '是否有误！')
            return -1

    def ocr_local2(self, x1, y1, x2, y2, screen_shot=None, size=1.0, credibility=0.91):
        if screen_shot is None:
            screen_shot = self.getscreen()

        try:
            if screen_shot.shape[0] > screen_shot.shape[1]:
                if anticlockwise_rotation_times >= 1:
                    for _ in range(anticlockwise_rotation_times):
                        screen_shot = UIMatcher.AutoRotateClockWise90(screen_shot)
                screen_shot = UIMatcher.AutoRotateClockWise90(screen_shot)
            part = screen_shot[y1:y2, x1:x2]  # 对角线点坐标
            part = cv2.resize(part, None, fx=size, fy=size, interpolation=cv2.INTER_LINEAR)  # 利用resize调整图片大小
            img_binary = cv2.imencode('.png', part)[1].tobytes()
            files = {'file': ('tmp.png', img_binary, 'image/png')}
            r = requests.post(url="http://127.0.0.1:5000/ocr/local_ocr2/", files=files).json().get("res")
            local_ocr_text = r[0]
            # local_ocr_text_credibility = float(local_ocr_text[1])  # 可信度
            if round(float(r[1]), 2) > credibility:
                if debug:
                    print('本地OCR-2识别结果：%s' % local_ocr_text)
                return local_ocr_text
            else:
                if debug:
                    print('本地OCR-2识别结果：%s,该结果可信度太低，丢弃！' % local_ocr_text)
                return -1
        except Exception as ocr_error:
            pcr_log(self.account).write_log(level='error', message='本地OCR-2识别失败，原因：%s' % ocr_error)
            return -1

    def ocr_int(self, x1, y1, x2, y2, screen_shot=None):
        out = self.ocr_center(x1, y1, x2, y2, screen_shot=screen_shot, size=2.0, credibility=0.97)
        if out == -1:
            raise OCRRecognizeError("整数OCR失败了！", outstr=str(out))
        out = make_it_as_number_as_possible(out)
        return int(out)

    def ocr_A_B(self, x1, y1, x2, y2, screen_shot=None):
        def ABfun(s):
            assert s != "-1", "什么都没有检测到"
            assert "/" in s, "字符串中应该有/"
            l = s.split("/")
            assert len(l) == 2, "字符串中有且只有一个/！"
            a, b = l
            return a, b

        out = self.ocr_center(x1, y1, x2, y2, screen_shot=screen_shot)
        try:
            a, b = ABfun(out)
            a = make_it_as_number_as_possible(a)
            b = make_it_as_number_as_possible(b)
            return int(a), int(b)
        except Exception as e:
            raise OCRRecognizeError("OCR失败了！", e, outstr=out)


class OCRRecognizeError(Exception):
    def __init__(self, *args, outstr):
        self.outstr = outstr
        super().__init__(*args)


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
    # 2020.8.9 修复了线程泄漏

    _stop_event = threading.Event()
    _run_event = threading.Event()

    def __init__(self, kwargs):
        if kwargs:
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
        else:
            # self._stop_event.set()
            pass

    def run(self):
        self._run_event.wait()
        self.run_func(self.th_name, self.a, self.fun)

    def state_sent_resume(self):
        self._run_event.set()  # 设置为True, 让线程停止阻塞

    def pause(self):
        self._stop_event.clear()  # 设置为False, 让线程阻塞

    def resume(self):
        self._stop_event.set()  # 设置为True, 让线程停止阻塞

    def state_sent_pause(self):
        self._run_event.clear()  # 设置为False, 让线程阻塞

    def program_is_stopped(self):
        return self._run_event.is_set()

    def is_stopped(self):
        return self._stop_event.is_set()

    pass
