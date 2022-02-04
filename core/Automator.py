# coding=utf-8
import datetime
import os
import traceback

import cv2

from automator_mixins._async import AsyncMixin
from automator_mixins._base import BaseMixin, ForceKillException, FastScreencutException
from automator_mixins._dxc import DXCMixin
from automator_mixins._hanghui import HanghuiMixin
from automator_mixins._haoyou import HaoYouMixin
from automator_mixins._jjc import JJCMixin
from automator_mixins._login import LoginMixin, BadLoginException
from automator_mixins._routine import RoutineMixin
from automator_mixins._shuatu import ShuatuMixin
from automator_mixins._juqing import JuQingMixin
from automator_mixins._shop import ShopMixin
from automator_mixins._tools import ToolsMixin
from automator_mixins._enhance import EnhanceMixin
from core.MoveRecord import moveset, UnknownMovesetException
from core.bot import Bot
from core.log_handler import pcr_log
# 2020.7.19 如果要记录日志 采用如下格式 self.pcr_log.write_log(level='info','<your message>') 下同
from core.pcr_config import trace_exception_for_debug, captcha_skip
from core.safe_u2 import OfflineException, ReadTimeoutException
from core.usercentre import check_task_dict, list_all_flags, is_in_group
from core.valid_task import VALID_TASK, getcustomtask


class Automator(HanghuiMixin, LoginMixin, RoutineMixin, ShuatuMixin, JJCMixin, DXCMixin, AsyncMixin,HaoYouMixin,
                JuQingMixin, EnhanceMixin, ShopMixin):
    def __init__(self, address):
        """
        device: 如果是 USB 连接，则为 adb devices 的返回结果；如果是模拟器，则为模拟器的控制 URL 。
        """
        BaseMixin.__init__(self)
        ShuatuMixin.__init__(self)
        DXCMixin.__init__(self)
        self.init_device(address)

    def run_custom_task(self, pymodule: str, funcname: str, var=None, **kwargs):
        func = None
        try:
            self.log.write_log('info', "导入模块中……")
            py = getcustomtask(pymodule)
            func = getattr(py, funcname)
            self.log.write_log('info',"导入成功！")
        except Exception as e:
            self.log.write_log("error", f"自定义脚本导入失败！{e}")
        if func is not None:
            func(self=self, var=var, **kwargs)

    def SkipTask(self, to_id=None):
        self.send_move_method("skip", to_id)

    def RunTasks(self, tasks: dict, continue_=True, max_retry=3,
                 first_init_home=True, rec_addr="rec"):
        """
        运行任务集
        By TheAutumnOfRice 2020-07-26
        2020-7-27 Fix: 把tasks参数放在外面读，防止多进程同时读某一个文件造成的问题
        :param tasks: 合法的任务字典
        :param continue_: 是否继续上次未完成的任务
        :param max_retry:  最大试错次数，超过max_retry却还不停报错则只能下次再见！
        :param first_init_home: 是否一开始执行init_home。
        :param rec_addr: 记录文件存放目录
        """
        user = self.AR.getuser()  # 获取配置文件
        account = user["account"]
        password = user["password"]
        check_task_dict(tasks, True)
        self.ms = moveset(account, rec_addr)  # 创建行为列表用于断点恢复
        self.ms.startw(None, start=True)  # 使用自动序列创建的起手式

        def funwarper(funname, title, kwargs):
            # 将funname包装为一个函数，调用self.funname(**kwargs)
            def fun(var):
                # var参数：用于断点恢复的变量
                # 使用try来保证兼容性：如果函数没有var参数，则不传入var参数。
                self.log.write_log("info", f"正在执行： {title} 记录存放目录： {rec_addr}")
                # 标记当前执行的位置！
                self.task_current(title)
                flag = False
                try:
                    self.__getattribute__(funname)(**kwargs, var=var)
                except TypeError:
                    flag = True
                if flag:
                    self.__getattribute__(funname)(**kwargs)

            return fun

        self.log.write_log("info", f"任务列表：")
        # 解析任务列表
        self._task_index = {}
        for task in tasks["tasks"]:
            typ = task["type"]

            if "__disable__" in task:
                # 存在禁用配置
                if task["__disable__"] is True:
                    typ = "nothing"  # 直接禁用
                elif task["__disable__"] is not False:
                    # 有开关
                    FLAGS = list_all_flags()
                    detail = None
                    for flag, details in FLAGS.items():
                        if task["__disable__"] == flag:
                            detail = details
                            break
                    if detail is not None:
                        use_default = True
                        if self.account in detail["user"] and detail["user"][self.account] is True:
                            typ = "nothing"  # 针对用户特殊：直接禁用
                            use_default = False
                        elif self.account in detail["user"] and detail["user"][self.account] is False:
                            use_default = False
                        else:
                            # 针对组特殊：
                            for group, set in detail["group"].items():
                                if is_in_group(self.account, group):
                                    if set is False:
                                        use_default = False
                                    else:
                                        typ = "nothing"
                                        use_default = False
                                    break
                        if use_default:
                            # 使用默认设置
                            if detail["default"] is True:
                                typ = "nothing"

            cur = VALID_TASK.T[typ]
            kwargs = {}
            if typ != "nothing":  # 未禁用
                for param in task:
                    if param == "type":
                        continue
                    if param == "__disable__":
                        continue
                    kwargs[param] = task[param]
            for v_p in cur["params"]:  # Valid Param: Default Param
                if v_p.default is not None and v_p.key not in kwargs:
                    kwargs[v_p.key] = v_p.default

            idx = self.ms.nextwv(funwarper(cur["funname"], cur['title'], kwargs))  # 自动创建序列
            if typ != "nothing":
                self.log.write_log("info", f"  +任务 {cur['title']}")  # 打印该任务
                for key in kwargs:
                    self.log.write_log("info", f"    参数 {key} ： {kwargs[key]}")
                self._task_index[idx] = cur['title']
        self.ms.exitw(None)  # 结束自动序列创建
        # 未知异常：仍然是重启哒！万能的重启万岁！
        last_exception = None
        before_ = True
        retry = 0
        while retry <= max_retry:
            # 防止泄露全局影响
            self.ES.FCs.clear()  # 清除全部ES
            self.headers_group.clear()  # 清除全部header
            self.register_basic_ES()
            try:
                if before_:
                    self.task_current("登录")
                    _return_code = self.login_auth(account, password)
                    if _return_code == -1:
                        # 标记错误！
                        self.task_error(str('%s账号出现了验证码' % self.account))
                        if captcha_skip:
                            self.fix_reboot(False)
                            return False
                    if continue_ is False:
                        # 初次执行，记录一下
                        self.task_start()
                    if first_init_home:
                        self.init_home()  # 处理第一次进home的一系列问题
                    before_ = False
                try:
                    self.ms.run(continue_=continue_)
                except UnknownMovesetException as e:
                    pcr_log(account).write_log("warning", message=f'记录文件冲突，自动刷新运行记录：{str(e)}')
                    self.ms.run(continue_=False)
                # 刷完啦！标记一下”我刷完了“
                self.task_finished()
                return True
            except ForceKillException as e:
                pcr_log(account).write_log(level='info', message=f'强制终止')
                try:
                    self.fix_reboot(False)
                except:
                    pcr_log(account).write_log(level='warning', message=f'强制终止-重启失败！')
                raise e
            except FastScreencutException as e:
                pcr_log(account).write_log(level='error', message=f'快速截图出现错误，{str(e)},尝试重新连接……')
                self.fix_reboot(not before_)
                self.init_fastscreen()
            except OfflineException as e:
                pcr_log(account).write_log('error', message=f'main-检测到设备离线：{str(e)}')
                return False
            except ReadTimeoutException as e:
                pcr_log(account).write_log('error', message=f'main-检测到连接超时，{str(e)}，尝试重新连接……')
                self.init_device(self.address)
            except BadLoginException as e:
                pcr_log(account).write_log('error', message=f'main-严重登录错误，{e}跳过账号！')
                self.task_error(str(e))
                self.fix_reboot(False)
                return False
            except Exception as e:
                retry += 1
                try:
                    os.makedirs(f"error_screenshot/{account}", exist_ok=True)
                    nowtime = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d_%H%M%S")
                    target = f"error_screenshot/{account}/{nowtime}_RT{retry}.jpg"
                    cv2.imwrite(target, self.last_screen)
                    pcr_log(account).write_log(level="error", message=f"错误截图已经保存至{target}")
                    # 错误截图日志为0级消息，后面可能会改成warning级别或者error
                    Bot().server_bot('', '', '', self.last_screen, f"模拟器：{self.address}\n"
                                                                   f"账号：{self.account}的运行错误重启截图\n"
                                                                   f"错误原因：{str(e)}")
                except Exception as es:
                    pcr_log(account).write_log(level="error", message=f"错误截图保存失败：{str(es)}")
                if trace_exception_for_debug:
                    tb = traceback.format_exc()
                    pcr_log(account).write_log(level="error", message=tb)
                last_exception = e
                continue_ = True
                if retry == max_retry:
                    pcr_log(account).write_log(level="error", message=f"main-检测出异常{str(e)} 超出最大重试次数，跳过账号！")
                    # 标记错误！
                    self.task_error(str(last_exception))
                    self.fix_reboot(False)
                    return False
                pcr_log(account).write_log(level='error', message=f'main-检测出异常{str(e)}，重启中 次数{retry}/{max_retry}')

                try:
                    self.fix_reboot(not before_)
                except Exception as e:
                    pcr_log(account).write_log(level='error', message=f'main-自动重启失败，跳过账号!{str(e)}')
                    self.task_error(str(last_exception))
                    try:
                        self.fix_reboot(False)
                    except:
                        pass
                    return False


if __name__ == "__main__":
    # TODO LOG:?
    print(Automator.mro())
