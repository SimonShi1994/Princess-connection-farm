import time

import keyboard
import psutil

from core.cv import UIMatcher
from core.log_handler import pcr_log
from pcr_config import bad_connecting_time, async_screenshot_freq, fast_screencut, s_sentstate, s_sckey, enable_pause
from ._base import BaseMixin, Multithreading

block_sw = 0


class AsyncMixin(BaseMixin):
    """
    异步插片
    包含异步函数
    """

    async def juqingtiaoguo(self):
        # 异步跳过教程 By：CyiceK
        # 废弃
        cumulative_time = 0.1
        while Multithreading({}).is_stopped():
            time.sleep(0.8+self.change_time)
            # print('juqing', self.change_time)
            try:
                # await asyncio.sleep(10)
                # time.sleep(10)
                # 过快可能会卡
                time.sleep(cumulative_time)
                screenshot = self.d.screenshot(format="opencv")
                if self.is_exists(screen=screenshot, img='img/juqing/caidanyuan.bmp', at=(860, 0, 960, 100)):
                    self.lock_img('img/juqing/caidanyuan.bmp', ifclick=[(917, 39)], ifdelay=self.change_time, retry=15)  # 菜单
                    self.lock_img('img/juqing/tiaoguo_1.bmp', ifclick=[(807, 44)], ifdelay=self.change_time,
                                  retry=15)  # 跳过
                    self.lock_img('img/juqing/tiaoguo_2.bmp', ifclick=[(589, 367)], ifdelay=self.change_time, retry=15)  # 跳过
                    cumulative_time = 0.1
                elif self.is_exists(screen=screenshot, img='img/kekeluo.bmp', at=(181, 388, 384, 451)):
                    # 防妈骑脸
                    self.lock_no_img('img/kekeluo.bmp', elseclick=[(1, 1)], at=(181, 388, 384, 451))
                    cumulative_time = 0.1
                elif self.is_exists(screen=screenshot, img='img/dxc_tb_1.bmp', at=(0, 390, 147, 537)):
                    self.lock_no_img('img/dxc_tb_1.bmp', ifclick=[(131, 533)], elsedelay=self.change_time)  # 回首页
                    cumulative_time = 0.1
                elif self.is_exists(screen=screenshot, img='img/dxc_tb_2.bmp', at=(580, 320, 649, 468)):
                    self.lock_no_img('img/dxc_tb_2.bmp', ifclick=[(610, 431)], elsedelay=self.change_time)
                    self.lock_img('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=self.change_time)  # 回首页
                    self.click(480, 505, pre_delay=0.5, post_delay=self.change_time)
                    cumulative_time = 0.1
                    if self.is_exists('img/dixiacheng.jpg', at=(837, 92, 915, 140)):
                        self.lock_no_img('img/dixiacheng.jpg', elseclick=(900, 138), elsedelay=self.change_time, retry=10)
                        raise Exception("地下城吃塔币跳过完成，重启")
                elif cumulative_time < 20:
                    cumulative_time = cumulative_time + 1

            except Exception as e:
                pcr_log(self.account).write_log(level='error', message='juqingtiaoguo-异步线程终止并检测出异常{}'.format(e))
                # sys.exit()
                break

    async def bad_connecting(self):
        # 异步判断异常 By：CyiceK
        # 测试
        _time = 0
        cumulative_time = 0.1
        while Multithreading({}).is_stopped():
            time.sleep(0.8+self.change_time)
            # print('bad', self.change_time)
            try:
                time.sleep(bad_connecting_time+cumulative_time)
                # 过快可能会卡
                screenshot = self.d.screenshot(format="opencv")
                time_start = time.time()
                if self.is_exists(screen=screenshot, img='img/connecting.bmp', at=(748, 20, 931, 53)):
                    cumulative_time = 0.1
                    # 卡连接
                    time.sleep(1)
                    time_end = time.time()
                    _time = time_end - time_start
                    _time = _time + _time
                    if _time > bad_connecting_time:
                        _time = 0
                        # LOG().Account_bad_connecting(self.account)
                        raise Exception("connecting时间过长")
                elif self.is_exists(screen=screenshot, img='img/loading.bmp', threshold=0.8):
                    # 卡加载
                    # 不知道为什么，at 无法在这里使用
                    cumulative_time = 0.1
                    time.sleep(1)
                    time_end = time.time()
                    _time = time_end - time_start
                    _time = _time + _time
                    if _time > bad_connecting_time:
                        pcr_log(self.account).write_log(level='error',
                                                        message='%s卡connecting/loading了，qwq' % self.account)
                        _time = 0
                        raise Exception("loading时间过长")

                elif self.is_exists(screen=screenshot, img='img/fanhuibiaoti.bmp', at=(377, 346, 581, 395)):
                    cumulative_time = 0.1
                    # 返回标题
                    raise Exception("reboot", "网络错误，重启。")

                elif self.is_exists(screen=screenshot, img='img/shujucuowu.bmp', at=(407, 132, 559, 297)):
                    cumulative_time = 0.1
                    # 数据错误
                    raise Exception("数据错误，重启。")

                elif cumulative_time < 10:
                    cumulative_time = cumulative_time + 1

            except Exception as e:
                    pcr_log(self.account).write_log(level='error', message='bad_connecting-异步线程终止并检测出异常{}'.format(e))

                # sys.exit()
                # break

    async def screenshot(self):
        """
        截图共享函数
        异步‘眨眼’截图
        暂时废弃，等优化
        """
        global screenshot
        screenshot = self.d.screenshot(format="opencv")
        while Multithreading({}).is_stopped():
            time.sleep(0.8+self.change_time)
            # print('screen', self.change_time)
            time.sleep(async_screenshot_freq)
            # 如果之前已经截过图了，就不截图了
            if time.time() - self.last_screen_time > async_screenshot_freq:
                screenshot = self.d.screenshot(format="opencv")
            else:
                if self.last_screen is not None:
                    screenshot = self.last_screen
                else:
                    screenshot = self.d.screenshot(format="opencv")
            # print('截图中')
            # cv2.imwrite('test.bmp', screenshot)

    async def same_img(self):
        """
        判断是否一直在同一界面
        :return:
        """
        time.sleep(self.change_time)
        # print('c', UIMatcher.img_similar(screenshot))
        _cout = 0
        while Multithreading({}).is_stopped():
            time.sleep(self.change_time)
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

    async def auto_time_sleep(self):
        """
        根据CPU负载调控time sleep
        By:CyiceK
        测试
        :return:
        """
        while Multithreading({}).is_stopped():
            # print(psutil.cpu_times())
            self.cpu_occupy = psutil.cpu_percent(interval=None, percpu=False)
            # print(self.cpu_occupy)
            # 游戏拿不了fps
            # 最大忍受5s
            if self.change_time >= 5 and self.cpu_occupy >= 100:
                self.change_time = 5
            if self.change_time <= 0.0:
                # print('重置', self.change_time)
                self.change_time = 0.5
            if self.cpu_occupy >= 100:
                self.change_time = self.change_time + 0.5
            elif self.cpu_occupy <= 30 and self.change_time - 0.5 > 0.0:
                self.change_time = self.change_time - 0.1

    async def Report_Information(self):
        """
        Server酱播报系统
        By:CyiceK
        :return:
        """
        _time_start = time.time()
        # print(Multithreading({}).program_is_stopped())
        while Multithreading({}).program_is_stopped() and len(s_sckey) != 0:
            time.sleep(1)
            _time_end = time.time()
            _time = int(_time_end - _time_start)/60
            # print(_time)
            # 5分钟播报一次
            if _time >= s_sentstate:
                pcr_log('admin').server_bot('STATE', message='')
                _time_start = time.time()

    async def aor_purse(self):
        """
        脚本暂停函数
        By:CyiceK
        测试
        :return:
        """
        global block_sw
        if not enable_pause:
            return
        # print(Multithreading({}).is_stopped())
        while Multithreading({}).is_stopped():
            keyboard.wait('shift+p')
            block_sw = 1
            print("下一步，脚本暂停,按shift+p恢复")
            time.sleep(0.8)
            keyboard.wait('shift+p')
            block_sw = 0
            print("恢复运行")
            time.sleep(0.8)

    def start_th(self):
        Multithreading({}).resume()

    def stop_th(self):
        Multithreading({}).pause()
        if fast_screencut:
            self.receive_minicap.stop()
        # print(Multithreading({}).is_stopped())

    def start_async(self):
        # 随着账号开启而开启
        account = self.account
        self.c_async(self, account, self.screenshot(), sync=False)  # 异步眨眼截图,开异步必须有这个
        # self.c_async(self, account, self.juqingtiaoguo(), sync=False)  # 异步剧情跳过
        self.c_async(self, account, self.bad_connecting(), sync=False)  # 异步异常处理
        # self.c_async(self, account, self.same_img(), sync=False)  # 异步卡死判断
        self.c_async(self, account, self.aor_purse(), sync=False)  # 异步暂停判断
        self.c_async(self, account, self.auto_time_sleep(), sync=False)  # 异步根据CPU负载调控time sleep

    def program_start_async(self):
        # 随着程序开启而开启
        account = 'admin'
        self.c_async(self, account, self.Report_Information(), sync=False)  # 异步Server酱播报系统

    def fix_reboot(self, back_home=True):
        # 重启逻辑：重启应用，重启异步线程
        self.d.session("com.bilibili.priconne")
        time.sleep(8)
        if back_home:
            self.lock_img('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=self.change_time)  # 回首页

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
