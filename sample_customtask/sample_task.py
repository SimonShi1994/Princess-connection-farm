from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from core.Automator import Automator

from core.MoveRecord import movevar
from core.valid_task import ValidTask, TaskParam

__enable__ = True  # 设置为True后，该文件会被启用，能够被CreateUser相关程序搜索到。
__valid__ = ValidTask() \
    .add("CT1", "CustomTask", "自定义任务标题", "一些描述",
         [TaskParam("a", int, "测试变量a", "变量a的描述", 10),
          TaskParam("b", str, "测试变量b", "变量b的描述", "字符串类型变量b的默认值")])


# __valid__ 按照valid_tasks.py的格式为自己的任务创建描述
# 注意：TaskParam为传入的变量，其中不能出现self、var、pymodule、funcname这四个名字！！
# 如果不写入__valid__，则该函数不会被CreateUser相关程序检测到，但依然可以被成功调用。
# 如果出现重名abbr，自定义的脚本将覆盖原始脚本。

def CustomTask(self: "Automator", a: int = 10, b: str = "字符串类型变量b的默认值", var: Optional[dict] = None):
    """
    这是一个样例任务
    :param self: Automator本体，必须要有，通过self.XXX进行脚本控制。
    :param a: 测试用变量
    :param b: 测试用变量
    :param var: 中断恢复字典，利用movevar可以存取相关信息
    return: None 啥都不返回
    """
    print("这是一个样例程序。")
    print("--------------------------------------------------------------------")
    print("在__valid__中定义了a,b两个变量，它们已经被成功传入了。")
    print("a: ", a)
    print("b: ", b)
    print("--------------------------------------------------------------------")
    print("一个完整的脚本必须以self.lock_home()开头。")
    print("这条语句将会让PCR回到主界面。")
    self.lock_home()
    print("--------------------------------------------------------------------")
    print("利用movevar可以保存一些变量，记录程序运行的状态。")
    print("先定义一个Handle")
    mv = movevar(var)
    print("setflag命令可以做一个标记。")
    print("使用mv.flag和mv.notflag命令可以判断一个标记是否被标记过")
    if mv.notflag("flag1"):
        print("做了一些事情。")
        mv.setflag("flag1")
        print("setflag将会把标记写入rec文件，如果程序中断，再次进入该脚本时，")
        print("程序会自动将之前的标记从文件中读入，传给var参数。")
        print("如果已经执行过setflag，则notflag将会返回False")
        print("这一段文字将不会被输出第二次。")
    if mv.notflag("flag2"):
        print("又做了一些事情。")
        mv.setflag("flag2")
    print("反复使用notflag - setflag可以很方便地让脚本按顺序执行一系列指令，")
    print("且已经执行过的指令不会执行第二次。")
    mv.clearflags()
    print("一定记住最后需要执行clearflags，不然之前做的标记将会一直伴随脚本执行后续的任务，")
    print("如果后续任务中也存在相关的flag指令，则会受到此任务的影响，可能会跳过一些任务。")
    print("--------------------------------------------------------------------")
    print("当然也可以手动存储一些命令。")
    var["times"] = 0
    print("调用save命令可以手动将其存入rec文件。")
    mv.save()
    print("使用regflag命令将该变量注册为flag，")
    print("则此后调用clearflags时，就会自动将该变量从字典中删去。")
    print("也可以不注册，手动使用 del var[...] 后mv.save也行。")
    mv.regflag("times")
    mv.clearflags()
    print("--------------------------------------------------------------------")
    print("movevar所保存的变量将会在该task全部执行完成后自我销毁。")
    print("使用AutomatorRecorder可以长久保存一些变量。")
    print("self.AR可以调出这个对象。")
    print("AR.get(key,default) 将会调取静态存储中key的值，若key不存在，返回default。")
    print("在constant.py的USER_DEFAULT_DICT中有一些在其它task中被使用的key，下以此举例。")
    from core.constant import USER_DEFAULT_DICT as UDD
    print("获取一些时间状态。")
    status = self.AR.get("time_status", UDD["time_status"])
    print("输出上次捐赠的时间。")
    from datetime import datetime
    if status["juanzeng"] == 0:
        print("还未捐赠。")
    else:
        print("上次捐赠时间：", datetime.fromtimestamp(status["juanzeng"]).strftime("%Y-%m-%d %H:%M:%S"))
    print("使用AR.set可以将某值保存在静态存储区域中。")
    print("比如希望增加一条刷图记录：已经刷了H1-1了。")
    status = self.AR.get("daily_status", UDD["daily_status"])
    print("记录1-1刷了3次。")
    status["hard"]["1-1"] = 3
    print("保存到文件。")
    self.AR.set("daily_status", status)
    print("--------------------------------------------------------------------")
    print("以下为一些基础指令：")
    print("click指令：点击(x,y)，在那之前延迟pre_delay秒，在那之后延迟post_delay秒。")
    self.click(1, 1, pre_delay=2, post_delay=2)
    print("可以使用PCRElement的格式（推荐）进行传参。")
    print("在constant中已经出现了很多例子了，可以参考。")
    from core.constant import PCRelement as p
    left_up_point = p(1, 1)
    print("用constant的方式实现click：")
    self.click(left_up_point, pre_delay=2, post_delay=2)
    print()
    print("is_exists指令：判断某个图片是否存在。")
    print("使用screencut截图小工具可以轻松获得某一个图片的PCRelemnt格式。")
    print("在constant.py中也有大量已经存在的元素。")
    print("如演示：判断礼物图标是否存在：")
    liwu = p(908, 432, img="img/home/liwu.bmp", at=(891, 417, 927, 448))
    if self.is_exists(liwu):
        print("liwu图标存在！")
    else:
        print("未找到liwu图标！")
    print()
    print("lock_img指令：循环直到img出现。")
    print("以下代码会不断循环检测直到liwu出现，并且每隔8秒点击left_up_point。")
    self.lock_img(liwu, elseclick=left_up_point, elsedelay=8)
    print("lock_no_img同理，只不过为循环直到img消失。")
    print()
    print("click_btn指令：按下某一个元素。")
    print("以下代码节选自self.enter_zhuxian，进入主线地图。")
    from core.constant import MAIN_BTN, MAOXIAN_BTN
    print("如果设置了until_appear，则会等待其出现，在那之前不断尝试按下按钮。")
    print("以下命令表示按下主页下方冒险按钮，直到主线的三个人头图片出现。")
    self.click_btn(MAIN_BTN["maoxian"], until_appear=MAIN_BTN["zhuxian"])
    # 进入地图
    print("如果还设置了wait_self_before，则在不断点击按钮之前还会先检测本身是否已经出现，防止误操作。")
    self.click_btn(MAIN_BTN["zhuxian"], wait_self_before=True, until_appear=MAOXIAN_BTN["ditu"])
    print("如果没有设置until_appear，则为按下按钮等待自己消失。")
    print("更多细节请见click_btn的doc。")
    print()
    print("--------------------------------------------------------------------")
    print("在执行完全部任务后，别忘了回到主页。")
    self.lock_home()
    print("以及记得清除flag。")
    mv.clearflags()
    print("--------------------------------------------------------------------")
