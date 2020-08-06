import time

import keyboard
import psutil

from core.cv import UIMatcher
from core.log_handler import pcr_log
from pcr_config import bad_connecting_time, async_screenshot_freq
from ._base import BaseMixin

screenshot = None
th_sw = 0
block_sw = 0


class AsyncMixin(BaseMixin):
    """
    异步插片
    包含异步函数
    """

    async def juqingtiaoguo(self):
        # 异步跳过教程 By：CyiceK
        # 测试
        global th_sw
        global screenshot
        while th_sw == 0:
            cpu_occupy = psutil.cpu_percent(interval=5, percpu=False)
            if screenshot is None:
                time.sleep(0.8)
                continue
            if cpu_occupy >= 80:
                # print('ka')
                time.sleep(0.8)
            try:
                # await asyncio.sleep(10)
                # time.sleep(10)
                # 过快可能会卡
                if UIMatcher.img_where(screenshot, 'img/caidan_yuan.jpg', at=(860, 0, 960, 100)):
                    self.lock_img('img/caidan_yuan.jpg', ifclick=[(917, 39)], ifdelay=1, retry=15)  # 菜单
                    self.lock_img('img/caidan_tiaoguo.jpg', ifclick=[(807, 44)], ifdelay=1, retry=15)  # 跳过
                    self.lock_img('img/ok.bmp', ifclick=[(589, 367)], ifdelay=5, retry=15)  # 跳过ok
                if UIMatcher.img_where(screenshot, 'img/kekeluo.bmp', at=(181, 388, 384, 451)):
                    # 防妈骑脸
                    self.lock_no_img('img/kekeluo.bmp', elseclick=[(1, 1)], at=(181, 388, 384, 451))
                if UIMatcher.img_where(screenshot, 'img/dxc_tb_1.bmp', at=(0, 390, 147, 537)):
                    self.lock_no_img('img/dxc_tb_1.bmp', ifclick=[(131, 533)], elsedelay=1)  # 回首页
                if UIMatcher.img_where(screenshot, 'img/dxc_tb_2.bmp', at=(580, 320, 649, 468)):
                    self.lock_no_img('img/dxc_tb_2.bmp', ifclick=[(610, 431)], elsedelay=1)
                    self.lock_img('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页
            except Exception as e:
                pcr_log(self.account).write_log(level='error', message='异步线程终止并检测出异常{}'.format(e))
                th_sw = 1
                # sys.exit()
                break

    async def bad_connecting(self):
        # 异步判断异常 By：CyiceK
        # 测试
        _time = 0
        global th_sw
        global screenshot
        while th_sw == 0:
            if screenshot is None:
                time.sleep(0.8)
                continue
            cpu_occupy = psutil.cpu_percent(interval=5, percpu=False)
            if cpu_occupy >= 80:
                # print('ka')
                time.sleep(0.8)
            try:
                time.sleep(bad_connecting_time)
                # 过快可能会卡
                time_start = time.time()
                if UIMatcher.img_where(screenshot, 'img/connecting.bmp', at=(748, 20, 931, 53)):
                    # 卡连接
                    time.sleep(1)
                    time_end = time.time()
                    _time = time_end - time_start
                    _time = _time + _time
                    if _time > bad_connecting_time:
                        _time = 0
                        # LOG().Account_bad_connecting(self.account)
                        raise Exception("connecting时间过长")
                if UIMatcher.img_where(screenshot, 'img/loading.bmp', threshold=0.8):
                    # 卡加载
                    # 不知道为什么，at 无法在这里使用
                    time.sleep(1)
                    time_end = time.time()
                    _time = time_end - time_start
                    _time = _time + _time
                    if _time > bad_connecting_time:
                        pcr_log(self.account).write_log(level='error',
                                                        message='%s卡connecting/loading了，qwq' % self.account)
                        _time = 0
                        raise Exception("loading时间过长")

                if UIMatcher.img_where(screenshot, 'img/fanhuibiaoti.bmp', at=(377, 346, 581, 395)):
                    # 返回标题
                    raise Exception("reboot", "网络错误，重启。")

                if UIMatcher.img_where(screenshot, 'img/shujucuowu.bmp', at=(407, 132, 559, 297)):
                    # 数据错误
                    raise Exception("数据错误，重启。")

            except Exception as e:
                    pcr_log(self.account).write_log(level='error', message='异步线程终止并检测出异常{}'.format(e))
                    th_sw = 1

                # sys.exit()
                # break

    async def screenshot(self):
        """
        截图共享函数
        异步‘眨眼’截图
        """
        global screenshot
        while th_sw == 0:
            cpu_occupy = psutil.cpu_percent(interval=5, percpu=False)
            if cpu_occupy >= 80:
                # print('ka')
                time.sleep(async_screenshot_freq)
            time.sleep(async_screenshot_freq)
            # 如果之前已经截过图了，就不截图了
            if time.time() - self.last_screen_time > async_screenshot_freq:
                screenshot = self.getscreen()
            else:
                if self.last_screen is not None:
                    screenshot = self.last_screen
                else:
                    screenshot = self.getscreen()
            # print('截图中')
            # cv2.imwrite('test.bmp', screenshot)

    async def same_img(self):
        """
        判断是否一直在同一界面
        :return:
        """
        time.sleep(1)
        # print('c', UIMatcher.img_similar(screenshot))
        _cout = 0
        while th_sw == 0:
            time.sleep(5)
            # print('c', UIMatcher.img_similar(screenshot))
            # print(UIMatcher.img_similar(screenshot))
            _same = UIMatcher.img_similar(screenshot, at=(834, 497, 906, 530))
            # at在右下角的主菜单
            if _same >= 0.9:
                # print('相似', _same)
                _cout = _cout + 1
                if _cout >= 3000:
                    raise Exception('%s卡同一界面过长（10min），即将重启qwq' % self.account)
                    # print('重启')
            else:
                # print('不相似', _same)
                pass

    async def aor_purse(self):
        """
        脚本暂停函数
        By:CyiceK
        测试
        :return:
        """
        global block_sw
        while th_sw == 0:
            keyboard.wait('shift+p')
            block_sw = 1
            print("下一步，脚本暂停,按shift+p恢复")
            time.sleep(0.8)
            keyboard.wait('shift+p')
            block_sw = 0
            print("恢复运行")
            time.sleep(0.8)

    def start_th(self):
        global th_sw
        th_sw = 0

    def stop_th(self):
        global th_sw
        th_sw = 1

    def start_async(self):
        account = self.account
        self.c_async(self, account, self.screenshot(), sync=False)  # 异步眨眼截图,开异步必须有这个
        self.c_async(self, account, self.juqingtiaoguo(), sync=False)  # 异步剧情跳过
        self.c_async(self, account, self.bad_connecting(), sync=False)  # 异步异常处理
        # self.c_async(self, account, self.same_img(), sync=False)  # 异步卡死判断
        self.c_async(self, account, self.aor_purse(), sync=False)  # 异步暂停判断

    def fix_reboot(self, back_home=True):
        # 重启逻辑：重启应用，重启异步线程
        self.stop_th()
        self.d.session("com.bilibili.priconne")
        time.sleep(8)
        self.start_th()
        self.start_async()
        if back_home:
            self.lock_img('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页

    def fix_fanhuibiaoti(self):
        # 返回标题逻辑
        # 放弃不用，没有重启来的稳
        self.stop_th()
        self.guochang(screenshot, ['img/fanhuibiaoti.bmp'], suiji=0)
        time.sleep(8)
        self.start_th()
        self.start_async()
        self.lock_img('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页

    def fix_shujucuowu(self):
        # 数据错误逻辑
        # 放弃不用，没有重启来的稳
        time.sleep(1)
        self.click(479, 369)
        time.sleep(8)
        self.click(1, 1)
