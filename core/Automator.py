# coding=utf-8
from automator_mixins._async import AsyncMixin
from automator_mixins._base import BaseMixin
from automator_mixins._dxc import DXCMixin
from automator_mixins._hanghui import HanghuiMixin
from automator_mixins._jjc import JJCMixin
from automator_mixins._login import LoginMixin
from automator_mixins._routine import RoutineMixin
from automator_mixins._shuatu import ShuatuMixin
from automator_mixins._tools import ToolsMixin


# 2020.7.19 如果要记录日志 采用如下格式 self.pcr_log.write_log(level='info','<your message>') 下同

class Automator(HanghuiMixin, LoginMixin, RoutineMixin, ShuatuMixin, JJCMixin, DXCMixin, AsyncMixin, ToolsMixin):
    def __init__(self, address, account, auto_task=False, auto_policy=True,
                 auto_goods=False, speedup=True):
        """
        device: 如果是 USB 连接，则为 adb devices 的返回结果；如果是模拟器，则为模拟器的控制 URL 。
        """
        BaseMixin.__init__(self)
        ShuatuMixin.__init__(self)
        DXCMixin.__init__(self)
        self.init(address, account)


if __name__ == "__main__":
    print(Automator.mro())
