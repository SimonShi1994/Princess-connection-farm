from core.constant import USER_DEFAULT_DICT as UDD
from core.initializer import PCRInitializer, Schedule
from core.usercentre import AutomatorRecorder, list_all_users
from pcr_config import selected_emulator


def RunFirstTime(schedule):
    PCR = PCRInitializer(selected_emulator)
    PCR.connect()
    PCR.start()
    SCH = Schedule(schedule, PCR)
    SCH.run_first_time()


def RunContinue(schedule):
    PCR = PCRInitializer(selected_emulator)
    PCR.connect()
    PCR.start()
    SCH = Schedule(schedule, PCR)
    SCH.run_continue()


def CheckTuitu():
    users = list_all_users(0)
    for acc in users:
        AR = AutomatorRecorder(acc)
        ts = AR.get("tuitu_status", UDD["tuitu_status"])
        if ts['max'] is not None:
            print("USER: ", acc, " Normal: ", ts['max'])


def CheckState(schedule):
    SCH = Schedule(schedule, None)
    SCH.show_schedule()


def ClearError(schedule, name):
    SCH = Schedule(schedule, None)
    SCH.clear_error(name)


def Restart(schedule, name):
    SCH = Schedule(schedule, None)
    SCH.restart(name)


if __name__ == "__main__":
    print("------------- 用户脚本控制台 --------------")
    print("help 查看帮助                   exit 退出")
    print("By TheAutumnOfRice")
    print("----------------------------------------")
    print("Update News:")
    print("2020-8-24 计划Schedule上线啦~")
    while True:
        try:
            cmd = input("> ")
            cmds = cmd.split(" ")
            order = cmds[0]
            if order == "exit":
                break
            elif order == "help":
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
            elif order == "first" and len(cmds) == 2:
                RunFirstTime(cmds[1])
            elif order == "continue" and len(cmds) == 2:
                RunContinue(cmds[1])
            elif order == "state":
                if len(cmds) == 2 and cmds[1] == "-tuitu":
                    CheckTuitu()
                elif len(cmds) == 2:
                    CheckState(cmds[1])
            elif order == "clear":
                if len(cmds) == 3:
                    if cmds[2] == "-all":
                        ClearError(cmds[1], None)
                    else:
                        ClearError(cmds[1], cmds[2])
                else:
                    print("需要指定Schedule和Name")
            elif order == "restart":
                if len(cmds) == 3:
                    if cmds[2] == "-all":
                        Restart(cmds[1], None)
                    else:
                        Restart(cmds[1], cmds[2])
                else:
                    print("需要指定Schedule和Name")
            elif order == "edit":
                exec(open("CreateUser.py", "r", encoding="utf-8").read())
            else:
                print("未知的命令")
        except Exception as e:
            print("出现错误:", e)
