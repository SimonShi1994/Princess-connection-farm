import os

from core.constant import USER_DEFAULT_DICT as UDD
from core.usercentre import AutomatorRecorder, list_all_users
from initialize import execute


# 主程序


def RunFirstTime():
    execute(False, 3)


def RunContinue():
    execute(True, 3)


def CheckState():
    users = list_all_users(0)
    for acc in users:
        AR = AutomatorRecorder(acc)
        uj = AR.getuser()
        print("USER: ", acc, " TASK: ", uj["taskfile"], "STATUS ", end="")
        rs = AR.get("run_status", UDD["run_status"])
        if rs["error"] is None:
            if rs["finished"]:
                print("FINISHED.")
            else:
                print("CURRENT: ", rs["current"])
        else:
            print("ERROR: ", rs["error"])


def ClearError(acc):
    """
    重启某用户的错误让他继续跑
    :param acc: 要处理的用户名字
    """
    AR = AutomatorRecorder(acc)
    rs = AR.get("run_status", UDD["run_status"])
    rs["error"] = None
    rs["finished"] = False
    AR.set("run_status", rs)


def Restart(acc):
    """
    重置某一个用户，让它重头跑
    Restart之后，再次调用RunContinue时，该用户会从头跑
    :param acc: 要处理的用户的名字
    """
    AR = AutomatorRecorder(acc)
    rs = AR.get("run_status", UDD["run_status"])
    rs["error"] = None
    rs["finished"] = False
    rs["current"] = "..."
    AR.set("run_status", rs)
    target = "rec\\%s.rec" % acc
    if os.path.exists(target):
        os.remove(target)  # 删除行动记录文件


def SetFinished(acc):
    """
    设置某一个用户的状态为已经跑完
    :param acc: 用户
    """
    AR = AutomatorRecorder(acc)
    rs = AR.get("run_status", UDD["run_status"])
    rs["error"] = None
    rs["finished"] = True
    rs["current"] = "..."
    AR.set("run_status", rs)


if __name__ == '__main__':
    print("------------- 用户脚本控制台 ------------")
    print("help 查看帮助                   exit 退出")
    print("By TheAutumnOfRice")
    print("----------------------------------------")
    while True:
        cmd = input("> ")
        cmds = cmd.split(" ")
        order = cmds[0]
        if order == "exit":
            break
        elif order == "help":
            print("脚本控制帮助")
            print("first 所有脚本全部重跑")
            print("continue 所有脚本从上次断点开始继续跑")
            print("state 显示所有用户的状态")
            print("clear ACCOUNT 清除Account的错误状态让它继续跑")
            print("restart ACCOUNT 清除Account的运行记录，让它重新开始")
            print("finish ACCOUNT 标记Account已经刷完，不再继续刷")
            print("edit 进入用户配置编辑模式")
        elif order == "first":
            RunFirstTime()
        elif order == "continue":
            RunContinue()
        elif order == "state":
            CheckState()
        elif order == "clear":
            if len(cmds) > 1:
                ClearError(cmds[1])
            else:
                print("需要指定Account")
        elif order == "restart":
            if len(cmds) > 1:
                Restart(cmds[1])
            else:
                print("需要指定Account")
        elif order == "finish":
            if len(cmds) > 1:
                SetFinished(cmds[1])
            else:
                print("需要指定Account")
        elif order == "edit":
            exec(open("CreateUser.py", "r", encoding="utf-8e").read())
        else:
            print("未知的命令")
