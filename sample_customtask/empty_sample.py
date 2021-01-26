from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from core.Automator import Automator

from core.valid_task import ValidTask

__enable__ = True  # 设置为True后，该文件会被启用，能够被CreateUser相关程序搜索到。
__valid__ = ValidTask() \
    .add("abbr", "EmptyTask", "自定义任务标题", "一些描述")


# __valid__ 按照valid_tasks.py的格式为自己的任务创建描述
# 注意：TaskParam为传入的变量，其中不能出现self、var、pymodule、funcname这四个名字！！
# 如果不写入__valid__，则该函数不会被CreateUser相关程序检测到，但依然可以被成功调用。
# 如果出现重名abbr，自定义的脚本将覆盖原始脚本。

def EmptyTask(self: "Automator", var: Optional[dict] = None):
    """
    空的任务，你来写
    :param self: Automator本体，必须要有，通过self.XXX进行脚本控制。
    :param var: 中断恢复字典，利用movevar可以存取相关信息
    return: None 啥都不返回
    """
    self.lock_home()
    # Your Program Here
    self.lock_home()
