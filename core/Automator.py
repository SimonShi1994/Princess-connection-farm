# coding=utf-8
import time

from automator_mixins._async import AsyncMixin
from automator_mixins._base import BaseMixin
from automator_mixins._dxc import DXCMixin
from automator_mixins._hanghui import HanghuiMixin
from automator_mixins._jjc import JJCMixin
from automator_mixins._login import LoginMixin
from automator_mixins._routine import RoutineMixin
from automator_mixins._shuatu import ShuatuMixin
from automator_mixins._tools import ToolsMixin
from core.MoveRecord import moveset
from core.log_handler import pcr_log
from core.usercentre import check_task_dict
from core.valid_task import VALID_TASK

# 2020.7.19 如果要记录日志 采用如下格式 self.pcr_log.write_log(level='info','<your message>') 下同
from pcr_config import trace_exception_for_debug


class Automator(HanghuiMixin, LoginMixin, RoutineMixin, ShuatuMixin, JJCMixin, DXCMixin, AsyncMixin, ToolsMixin):
    def __init__(self, address):
        """
        device: 如果是 USB 连接，则为 adb devices 的返回结果；如果是模拟器，则为模拟器的控制 URL 。
        """
        BaseMixin.__init__(self)
        ShuatuMixin.__init__(self)
        DXCMixin.__init__(self)
        self.init_device(address)

    def RunTasks(self, tasks: dict, continue_=True, max_retry=3):
        """
        运行任务集
        By TheAutumnOfRice 2020-07-26
        2020-7-27 Fix: 把tasks参数放在外面读，防止多进程同时读某一个文件造成的问题
        :param tasks: 合法的任务字典
        :param continue_: 是否继续上次未完成的任务
        :param max_retry:  最大试错次数，超过max_retry却还不停报错则只能下次再见！
        """
        user = self.AR.getuser()  # 获取配置文件
        account = user["account"]
        check_task_dict(tasks, True)
        self.ms = moveset(account, "rec")  # 创建行为列表用于断点恢复
        self.ms.startw(None, start=True)  # 使用自动序列创建的起手式

        def funwarper(funname, title, kwargs):
            # 将funname包装为一个函数，调用self.funname(**kwargs)
            def fun(var):
                # var参数：用于断点恢复的变量
                # 使用try来保证兼容性：如果函数没有var参数，则不传入var参数。
                self.log.write_log("info", f"正在执行： {title}")
                # 标记当前执行的位置！
                self.task_current(title)
                try:
                    self.__getattribute__(funname)(**kwargs, var=var)
                except TypeError:
                    self.__getattribute__(funname)(**kwargs)
                try:
                    from automator_mixins._async import block_sw
                    if block_sw == 1:
                        print("脚本暂停中~")
                        while block_sw == 1:
                            from automator_mixins._async import block_sw
                            time.sleep(1)
                except Exception as error:
                    print('暂停-错误:', error)
            return fun

        self.log.write_log("info", f"任务列表：")
        # 解析任务列表
        for task in tasks["tasks"]:
            typ = task["type"]
            cur = VALID_TASK.T[typ]
            kwargs = {}
            for param in task:
                if param == "type":
                    continue
                kwargs[param] = task[param]
            for v_p in cur["params"]:  # Valid Param: Default Param
                if v_p.default is not None and v_p.key not in kwargs:
                    kwargs[v_p.key] = v_p.default

            self.ms.nextwv(funwarper(cur["funname"], cur['title'], kwargs))  # 自动创建序列
            self.log.write_log("info", f"  +任务 {cur['title']}")  # 打印该任务
            for key in kwargs:
                self.log.write_log("info", f"    参数 {key} ： {kwargs[key]}")
        self.ms.exitw(None)  # 结束自动序列创建
        # 异常检测及恢复跳转逻辑
        self.ms.addcatch("reboot", "reboot_logic")  # 从异步线程中接收到重启逻辑。遇事不决，直接重启，最为保险。
        self.ms.addmove("reboot_logic", moveset.w(self.fix_reboot, "__last__"))  # 重启逻辑：执行fix_reboot，然后回到上一步

        # 未知异常：仍然是重启哒！万能的重启万岁！
        last_exception = None

        if continue_ is False:
            # 初次执行，记录一下
            self.task_start()

        self.init_home()  # 处理第一次进home的一系列问题
        for retry in range(max_retry):
            try:
                self.ms.run(continue_=continue_)
                # 刷完啦！标记一下”我刷完了“
                self.task_finished()
                break
            except Exception as e:
                continue_ = True
                pcr_log(account).write_log(level='error', message=f'main-检测出异常{e}，重启中 次数{retry + 1}/{max_retry}')
                if trace_exception_for_debug:
                    raise e
                last_exception = e
                self.fix_reboot()
        else:
            # 超出最大重试次数,放弃啦！
            pcr_log(account).write_log(level="error", message="超出最大重试次数，跳过账号！")
            # 标记错误！
            self.task_error(str(last_exception))


if __name__ == "__main__":
    print(Automator.mro())
