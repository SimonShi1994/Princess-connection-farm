import os
import traceback
from typing import Optional

from core.constant import USER_DEFAULT_DICT as UDD
from core.initializer import PCRInitializer, Schedule
from core.pcr_config import trace_exception_for_debug
from core.usercentre import AutomatorRecorder, list_all_users, parse_batch, check_users_exists

PCR: Optional[PCRInitializer] = None
SCH: Optional[Schedule] = None
last_schedule = ""


def StartPCR():
    global PCR
    if PCR is None:
        PCR = PCRInitializer()
        PCR.connect()
    PCR.devices.add_from_config()
    PCR.start()


def BindSchedule(schedule):
    global SCH, PCR, last_schedule
    if PCR is None:
        StartPCR()

    if SCH is not None:
        raise Exception("无法绑定Schedule：请先结束之前的Schedule！")
    SCH = Schedule(schedule, PCR)
    last_schedule = schedule
    print("Schedule绑定成功：", schedule)


def FirstSchedule():
    global SCH
    if SCH is None:
        raise Exception("请先绑定Schedule！")

    if SCH.state == 1:
        raise Exception("Schedule已经运行，请先关闭！")

    SCH.run_first_time()


def ContinueSchedule():
    global SCH
    if SCH is None:
        raise Exception("请先绑定Schedule！")

    if SCH.state == 1:
        raise Exception("Schedule已经运行，请先关闭！")

    SCH.run_continue()


def FirstBatch(batch):
    global PCR
    if PCR is None:
        StartPCR()
    bj = AutomatorRecorder.getbatch(batch)
    parsed = parse_batch(bj)
    PCR.add_tasks(parsed, False, f"rec/__batch__/{batch}")


def ContinueBatch(batch):
    global PCR
    if PCR is None:
        StartPCR()
    bj = AutomatorRecorder.getbatch(batch)
    parsed = parse_batch(bj)
    PCR.add_tasks(parsed, True, f"rec/__batch__/{batch}")


def FirstTask(is_group, name, taskname, priority):
    global PCR
    if PCR is None:
        StartPCR()
    if is_group:
        accs = AutomatorRecorder.getgroup(name)
    else:
        accs = [name]
        check_users_exists(accs)
    for acc in accs:
        PCR.add_task((priority, acc, taskname), False, "rec/__directly__")


def ContinueTask(is_group, name, taskname, priority):
    global PCR
    if PCR is None:
        StartPCR()
    if is_group:
        accs = AutomatorRecorder.getgroup(name)
    else:
        accs = [name]
        check_users_exists(accs)
    for acc in accs:
        PCR.add_task((priority, acc, taskname), True, "rec/__directly__")


def CheckTuitu():
    users = list_all_users(0)
    for acc in users:
        AR = AutomatorRecorder(acc)
        ts = AR.get("tuitu_status", UDD["tuitu_status"])
        if ts['max'] is not None:
            print("USER: ", acc, " Normal: ", ts['max'])


def CheckState(schedule=None):
    global SCH, last_schedule
    if schedule is None:
        schedule = last_schedule
    if SCH is None:
        mysch = Schedule(schedule, None)
        mysch.show_schedule(True)
    else:
        SCH.show_schedule()


def CheckDevice():
    global PCR
    if PCR is None:
        PCR = PCRInitializer()
        PCR.connect()
    PCR.devices.show()


def CheckQueue():
    global PCR
    if PCR is None:
        PCR = PCRInitializer()
        PCR.connect()
    PCR.show()


def ReconnectPCR():
    global PCR
    if PCR is None:
        PCR = PCRInitializer()
    PCR.connect()
    PCR.start()


def ClearError(schedule, name):
    mysch = Schedule(schedule, None)
    mysch.clear_error(name)


def Restart(schedule, name):
    mysch = Schedule(schedule, None)
    mysch.restart(name)


def StopSchedule():
    global SCH
    if SCH is None:
        print("还没有运行任何Schedule")
        return
    SCH.stop()
    SCH = None


def JoinShutdown():
    global SCH
    if SCH is None:
        print("还没有任何Schedule")
        return
    SCH.join()
    os.system("shutdown -s -f -t 120")

def ShowInfo():
    print("更新信息:")
    print("2020-8-24 计划Schedule上线啦~")
    print("2020-8-25 修复自动推图，新增推H图，小号每日刷H图 <- 测试中")
    print("当前BUG：")
    print("竞技场经常会失灵")


if __name__ == "__main__":

    print("------------- 用户脚本控制台 --------------")
    print("help 查看帮助                   exit 退出")
    print("info 查看版本信息")
    print("By TheAutumnOfRice")
    print("----------------------------------------")
    print("注：关于running_input配置")
    print("开启后，可以在运行时向控制台输入参数来监测运行状态，")
    print("但是可能会造成u2不响应的情况。该配置已经默认关闭。")
    while True:
        try:
            cmd = input("> ")
            cmds = cmd.split(" ")
            order = cmds[0]
            if order == "exit":
                if SCH is not None:
                    StopSchedule()
                break
            elif order == "info":
                ShowInfo()
            elif order == "break":
                break
            elif order == "help":
                if SCH is None:
                    print("脚本控制帮助")
                    print("first schedule 清空schedule的全部记录，重新跑")
                    print("continue schedule  继续schedule上次的记录")
                    print("state schedule 显示schedule当前状态")
                    print("state -tuitu 显示所有用户推图的状态")
                    print("clear schedule name 忽略schedule中名称为name子计划的错误记录")
                    print("clear schedule -all 忽略schedule中全部子计划的错误记录")
                    print("restart schedule name 清除schedule中名称为name子计划的运行记录")
                    print("restart schedule -all 清除schedule中全部子计划的运行记录")
                    print("edit 进入用户配置编辑模式")
                    print("screencut 进入截图小工具")
                else:
                    print("实时控制帮助")
                    print("exit 终止并退出")
                    print("stop 停止当前的Schedule")
                    print("state 查看当前运行状态")
                    print("device 查看当前设备状态")
                    print("queue 查看当前任务队列")
                    print("join-shutdown 一直运行至队列为空、设备全部闲置时，关机")
                    print("reconnect 重新搜索模拟器 （貌似还有BUG）")
            elif order == "first" and len(cmds) == 2:
                if SCH is None:
                    RunFirstTime(cmds[1])
                else:
                    print("请先关闭当前的计划！")
            elif order == "continue" and len(cmds) == 2:
                if SCH is None:
                    RunContinue(cmds[1])
                else:
                    print("请先关闭当前的计划！")
            elif order == "state":
                if len(cmds) == 2 and cmds[1] == "-tuitu":
                    CheckTuitu()
                elif len(cmds) == 2:
                    CheckState(cmds[1])
                elif len(cmds) == 1:
                    if SCH is None:
                        print("请输入具体的计划名称")
                    else:
                        CheckState()
                else:
                    print("state 命令输入错误！")
            elif order == "clear":
                if SCH is None:
                    if len(cmds) == 3:
                        if cmds[2] == "-all":
                            ClearError(cmds[1], None)
                        else:
                            ClearError(cmds[1], cmds[2])
                    else:
                        print("需要指定Schedule和Name")
                else:
                    print("请先关闭当前的计划！")
            elif order == "restart":
                if SCH is None:
                    if len(cmds) == 3:
                        if cmds[2] == "-all":
                            Restart(cmds[1], None)
                        else:
                            Restart(cmds[1], cmds[2])
                    else:
                        print("需要指定Schedule和Name")
                else:
                    print("请先关闭当前的计划！")
            elif order == "edit":
                if SCH is None:
                    exec(open("CreateUser.py", "r", encoding="utf-8").read())
                else:
                    print("请先关闭当前的计划！")
            elif order == "screencut":
                if SCH is None:
                    exec(open("screencut.py", "r", encoding="utf-8").read())
                else:
                    print("请先关闭当前的计划！")
            elif SCH is not None:
                # 实时控制
                if order == "stop":
                    StopSchedule()
                elif order == "device":
                    CheckDevice()
                elif order == "queue":
                    CheckQueue()
                elif order == "reconnect":
                    ReconnectPCR()
                elif order == "join-shutdown":
                    JoinShutdown()
                else:
                    print("未知的命令！")
            else:
                print("未知的命令")
        except Exception as e:
            if trace_exception_for_debug:
                traceback.print_exc()
            print("出现错误:", e)
