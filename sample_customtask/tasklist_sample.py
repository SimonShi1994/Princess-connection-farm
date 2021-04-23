from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from core.Automator import Automator

from core.MoveRecord import movevar
from core.valid_task import ValidTask

__enable__ = True  # 设置为True后，该文件会被启用，能够被CreateUser相关程序搜索到。
__valid__ = ValidTask() \
    .add("abbr", "TaskList", "自定义任务标题", "一些描述")


# __valid__ 按照valid_tasks.py的格式为自己的任务创建描述
# 注意：TaskParam为传入的变量，其中不能出现self、var、pymodule、funcname这四个名字！！
# 如果不写入__valid__，则该函数不会被CreateUser相关程序检测到，但依然可以被成功调用。
# 如果出现重名abbr，自定义的脚本将覆盖原始脚本。

def TaskList(self: "Automator", var: Optional[dict] = None):
    """
    这个任务可以让你仿佛回到masterV1年代
    你在这里可以按照顺序写下很多task，从而就不需要写task文件了
    你还可以在这里写一些复杂的判断逻辑，比如检测扫荡券不够则购买扫荡券等。
    甚至还可以判断self.account，来手动实现switch功能。
    非常方便
    :param self: Automator本体，必须要有，通过self.XXX进行脚本控制。
    :param var: 中断恢复字典，利用movevar可以存取相关信息
    return: None 啥都不返回
    """
    mv = movevar(var)
    if mv.notflag("step_1"):
        self.buyExp()  # 购买经验
        mv.setflag("step_1")
    if mv.notflag("step_2"):
        self.goumaimana(1, 1, var=var)  # 购买10次mana
        mv.setflag("step_2")
    if mv.notflag("step_3"):
        # And So On...
        mv.setflag("step_3")
    # ...
    mv.clearflags()
