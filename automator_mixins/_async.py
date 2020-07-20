import asyncio
import time

from core.cv import UIMatcher
from ._base import BaseMixin


class AsyncMixin(BaseMixin):
    """
    异步插片
    包含异步函数
    """

    async def juqingtiaoguo(self):
        # 异步跳过教程 By：CyiceK
        # 测试
        f = 0
        while f == 0:
            await asyncio.sleep(10)
            # 过快可能会卡
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/caidan_yuan.jpg', at=(860, 0, 960, 100), debug=False):
                self.d.click(917, 39)  # 菜单
                await asyncio.sleep(1)
                self.d.click(807, 44)  # 跳过
                await asyncio.sleep(3)
                self.d.click(589, 367)  # 跳过ok
                await asyncio.sleep(5)

    async def bad_connecting(self):
        # 异步判断异常 By：CyiceK
        # 测试
        f = 0
        _time = 0
        while f == 0:
            try:
                await asyncio.sleep(30)
                # 过快可能会卡
                time_start = time.time()
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/connecting.bmp', at=(748, 20, 931, 53), debug=False):
                    time_end = time.time()
                    _time = time_end - time_start
                    _time = _time + _time
                    if _time > 15:
                        # LOG().Account_bad_connecting(self.account)
                        # 2020.7.19 如果要记录日志 采用如下格式 self.pcr_log.write_log(level='info','<your message>') 下同
                        self.d.session("com.bilibili.priconne")
                        await asyncio.sleep(8)
                        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1,
                                     at=(891, 413, 930, 452))  # 回首页
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/loading.bmp', threshold=0.8, debug=False):
                    # 不知道为什么，at 无法在这里使用
                    time_end = time.time()
                    _time = time_end - time_start
                    _time = _time + _time
                    if _time > 15:
                        # LOG().Account_bad_connecting(self.account)
                        self.d.session("com.bilibili.priconne")
                        await asyncio.sleep(8)
                        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1,
                                     at=(891, 413, 930, 452))  # 回首页
                if UIMatcher.img_where(screen_shot_, 'img/fanhuibiaoti.bmp', debug=False):
                    self.guochang(screen_shot_, ['img/fanhuibiaoti.bmp'], suiji=0)
                    await asyncio.sleep(8)
                    self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
            except Exception as e:
                print('异步线程终止并检测出异常{}'.format(e))
                break
