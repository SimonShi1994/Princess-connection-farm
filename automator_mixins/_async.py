import asyncio
import time

import keyboard
import psutil

from automator_mixins._base import DEBUG_RECORD
from core.cv import UIMatcher
from core.log_handler import pcr_log
from core.pcr_config import bad_connecting_time, async_screenshot_freq, fast_screencut, enable_pause, sentstate, \
    sent_state_img, clear_traces_and_cache
from core.safe_u2 import timeout
from ._base import Multithreading
from ._tools import ToolsMixin

block_sw = 0
async_block_sw = 0
async_blocking_sw = 0


class AsyncMixin(ToolsMixin):
    """
    异步插片
    包含异步函数
    """

    async def juqingtiaoguo(self):
        # 异步跳过教程 By：CyiceK
        # 废弃
        cumulative_time = 0.1
        while Multithreading({}).is_stopped():
            if not self.async_juqingtiaoguo_switch:
                await asyncio.sleep(1)
                continue
            # print('juqing', self.change_time)
            try:
                # await asyncio.sleep(10)
                # time.sleep(10)
                # 过快可能会卡
                await asyncio.sleep(cumulative_time)
                screenshot = self.last_screen
                if self.is_exists(screen=screenshot, img='img/juqing/caidanyuan.bmp', at=(860, 0, 960, 100)):
                    self.lock_img('img/juqing/caidanyuan.bmp', ifclick=[(917, 39)], ifdelay=self.change_time,
                                  retry=15)  # 菜单
                    self.lock_img('img/juqing/tiaoguo_1.bmp', ifclick=[(807, 44)], ifdelay=self.change_time,
                                  retry=15)  # 跳过
                    self.lock_img('img/juqing/tiaoguo_2.bmp', ifclick=[(589, 367)], ifdelay=self.change_time,
                                  retry=15)  # 跳过
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
                        self.lock_no_img('img/dixiacheng.jpg', elseclick=(900, 138), elsedelay=self.change_time,
                                         retry=10)
                        raise Exception("地下城吃塔币跳过完成，重启")
                elif cumulative_time < 20:
                    cumulative_time = cumulative_time + 1

            except Exception as e:
                pcr_log(self.account).write_log(level='error', message='juqingtiaoguo-异步线程终止并检测出异常{}'.format(e))
                # sys.exit()
                break
            await asyncio.sleep(0.8 + self.change_time)

    async def bad_connecting(self):
        # 异步判断异常 By：CyiceK
        # 测试
        _time = 0
        cumulative_time = 0.1
        while Multithreading({}).is_stopped():
            try:

                if self.last_screen is None:
                    screenshot = self.getscreen()
                else:
                    screenshot = self.last_screen

                if time.time() - self.last_screen_time > async_screenshot_freq:
                    continue
                time_start = time.time()
                if self.is_exists(screen=screenshot, img='img/error/connecting.bmp', at=(774, 476, 867, 506)):
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
                elif self.is_exists(screen=screenshot, img='img/error/loading.bmp', threshold=0.8):
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

                elif self.is_exists(screen=screenshot, img='img/error/fanhuibiaoti.bmp', at=(377, 346, 581, 395)):
                    cumulative_time = 0.1
                    # 返回标题
                    raise Exception("reboot", "网络错误，重启。")

                elif self.is_exists(screen=screenshot, img='img/error/shujucuowu.bmp', at=(407, 132, 559, 297)):
                    cumulative_time = 0.1
                    # 数据错误
                    raise Exception("数据错误，重启。")

                elif self.is_exists(screen=screenshot, img='img/error/lianjiechaoshi.bmp', at=(245, 132, 713, 408)):
                    cumulative_time = 0.1
                    # 连接超时
                    self.lock_no_img(img='img/error/chongshi.bmp', elseclick=[(587, 373)], elseafter=1, retry=5)

                elif cumulative_time < 8:
                    cumulative_time = cumulative_time + 1

                await asyncio.sleep(bad_connecting_time + cumulative_time)
                # 过快可能会卡

            except Exception as e:
                self.send_move_method("restart", f"bad_connecting-{e}")
                await asyncio.sleep(1)
            await asyncio.sleep(0.8 + self.change_time)
            # print('bad', self.change_time)

            # sys.exit()
            # break

    async def screenshot(self):
        """
        截图共享函数
        异步‘眨眼’截图
        暂时废弃，等优化
        """
        while Multithreading({}).is_stopped():
            try:
                if time.time() - self.last_screen_time > async_screenshot_freq:
                    self.getscreen()
                else:
                    if self.last_screen is None:
                        self.getscreen()
                await asyncio.sleep(0.8 + self.change_time)
                # print('screen', self.change_time)
                await asyncio.sleep(async_screenshot_freq)
                # 如果之前已经截过图了，就不截图了
                # print('截图中')
                # cv2.imwrite('test.bmp', screenshot)
            except Exception as e:
                pass

    async def same_img(self):
        """
        判断是否一直在同一界面
        :return:
        """
        await asyncio.sleep(self.change_time)
        # print('c', UIMatcher.img_similar(screenshot))
        _cout = 0
        while Multithreading({}).is_stopped():
            time.sleep(self.change_time)
            # print('c', UIMatcher.img_similar(screenshot))
            # print(UIMatcher.img_similar(screenshot))
            _same = UIMatcher.img_similar(self.last_screen, at=(834, 497, 906, 530))
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
            # 我休眠我自己
            await asyncio.sleep(self.change_time)
            self.cpu_occupy = psutil.cpu_percent(interval=30, percpu=False)
            # print(self.cpu_occupy)
            # 游戏拿不了fps
            # 最大忍受5s
            if self.change_time >= 5 and self.cpu_occupy >= 99:
                self.change_time = 5
            if self.change_time <= 0.0:
                # print('重置', self.change_time)
                self.change_time = 0.5
            if self.cpu_occupy >= 99:
                self.change_time = self.change_time + 0.5
            elif self.cpu_occupy <= 30 and self.change_time - 0.5 > 0.0:
                self.change_time = self.change_time - 0.1

    async def Report_Information(self):
        """
        Server酱播报系统
        By:CyiceK
        :return:
        """
        # 2020-8-26 播报系统移动至core.initializer._run
        pass

    async def c_img_server_bot(self):
        """
        此函数会定时发送截图给sever_bot
        :return:
        """
        while Multithreading({}).is_stopped():
            if sentstate != 0:
                account = self.account
                address = self.address
                await asyncio.sleep(sentstate * 60 + 1)
                sent_img = self.getscreen()
                pcr_log(account).server_bot('STATE', '', '', img=sent_img, img_title=f"server_bot运行截图播报\n"
                                                                                     f"账号:{account}\n"
                                                                                     f"所运行的设备:{address}")

    async def aor_purse(self):
        """
        脚本暂停函数
        By:CyiceK
        测试
        :return:
        """
        # TODO:堵塞造成了线程泄漏,暂停函数需要放置在父进程而不是在子进程
        global block_sw
        global async_blocking_sw
        if not enable_pause:
            return
        # print(Multithreading({}).is_stopped())
        while Multithreading({}).is_stopped():
            keyboard.wait('shift+p')
            block_sw = 1
            self.log.write_log('info',"下一步，脚本暂停,按shift+p恢复")
            await asyncio.sleep(0.8)
            keyboard.wait('shift+p')
            block_sw = 0
            self.log.write_log('info',"恢复运行")
            await asyncio.sleep(0.8)
            async_blocking_sw = 0

    def start_th(self):
        Multithreading({}).resume()

    def stop_th(self):
        global async_block_sw
        # 解锁异步
        async_block_sw = 0
        Multithreading({}).pause()
        if fast_screencut and self.fastscreencut_retry < 3:
            if self.receive_minicap is not None:
                self.receive_minicap.stop()
        # print(Multithreading({}).is_stopped())

    def start_async(self):
        global async_block_sw
        global async_blocking_sw
        # 随着账号开启而开启
        account = self.account
        # self.c_async(self, account, self.screenshot(), sync=False)  # 异步眨眼截图,开异步必须有这个
        # self.c_async(self, account, self.juqingtiaoguo(), sync=False)  # 异步剧情跳过
        self.c_async(self, account, self.bad_connecting(), sync=False)  # 异步异常处理
        # self.c_async(self, account, self.same_img(), sync=False)  # 异步卡死判断
        if not async_block_sw:
            async_block_sw = 1
            # 马上锁上，仅运行一次，非随账号运行
            if async_blocking_sw == 0:
                # 用于判断堵塞的异步开关
                async_blocking_sw = 1
                self.c_async(self, account, self.aor_purse(), sync=False)  # 异步暂停判断
            if sent_state_img:
                self.c_async(self, account, self.c_img_server_bot(), sync=False)  # 异步server截图发送播报
                # self.c_async(self, account, self.bot_get_command(), sync=False)  # 异步获取远端命令
        self.c_async(self, account, self.auto_time_sleep(), sync=False)  # 异步根据CPU负载调控time sleep

    def program_start_async(self):
        # 随着程序开启而开启
        # account = 'admin'
        # self.c_async(self, account, self.Report_Information(), sync=False)  # 异步Server酱播报系统
        pass

    @timeout(180, "重启超时，三分钟仍然未响应")
    def _fix_reboot(self, back_home):
        self.debug_record.clear()
        # 重启逻辑：重启应用，重启异步线程
        self.stop_th()
        self.d.session("com.bilibili.priconne")
        time.sleep(8)
        self.d.app_wait("com.bilibili.priconne")
        if back_home:
            self.start_th()
            self.init_fastscreen()
            self.start_async()
            # 临时堆放，用于重启后跳过协议
            for _ in range(3):
                # 有两个协议需要同意
                self.click(1, 1)
                while self.d(text="请滑动阅读协议内容").exists() or self.d(description="请滑动阅读协议内容").exists():
                    self.d.touch.down(810, 378).sleep(1).up(810, 378)
                    if self.d(text="请滑动阅读协议内容").exists():
                        self.d(text="同意").click()
                    if self.d(description="请滑动阅读协议内容").exists():
                        # 雷电三
                        self.d(description="同意").click()
                    time.sleep(6)

            # 清理痕迹后需要重新登录账号
            if clear_traces_and_cache:
                try:
                    self.phone_privacy()
                except Exception as e:
                    self.log.write_log('error',f"重启匿名化错误：{e}")

            self.lock_home()

    @DEBUG_RECORD
    def fix_reboot(self, back_home=True):
        self._fix_reboot(back_home)
