import re
from os import getcwd

from core.usercentre import *

DOC_STR = {
    "title":
        """
        +-------------------------------------------------+
        +                用户配置文件编辑器                  +
        +          在没有GUI的时候先将就着使用一下             +
        +                            By:  TheAutumnOfRice +
        +-------------------------------------------------+
        输入 help 查看帮助
        输入 exit 退出
        """,
    "help?":
        """
        帮助手册  在命令后输入?查看具体使用方法
        user     创建或编辑一个新的用户信息
        task     创建或编辑一个任务列表
        group    创建或编辑一个用户组
        batch    创建或编辑一个批配置
        schedule 创建或编辑一个计划配置
        """,
    "user?":
        """
        帮助: user
        user -l 列举全部用户列表
        user Account 显示某用户的所有信息
        user -c Account Password 创建一个新用户。
            Account: 用户名    Password: 密码
            对已经存在的用户将覆盖原本的信息
        user -c -file Filename 从指定文件Filename创建用户
            该文件每一行要求分隔符（空格或Tab）隔开的两个元素 Account Password
            对已经存在的用户将覆盖原本的信息。
        user -d Account 删除指定Account的账户
        user -d -file Filename 从指定文件Filename删除用户
            该文件每一行为一个Account，表示要删除的用户
        user -d -all 删除全部用户
        user Account [-p Password] 更改某一账户的密码
        """,
    "task?":
        """
        帮助：task
        task -l 列举全部任务列表
        task TaskName 显示某项任务详细信息 
        task -c TaskName 创建一个名称为TaskName的任务
        task -e TaskName 进入TaskName的编辑模式
        task -d TaskName 删除某一Task
        task -d -all 删除全部Task
        """,
    "group?":
        """
        帮助：group
        group -l 列举全部组列表
        group GroupName 显示某个组的全部成员
        group的创建：非常简单，不写方法了。
        Step 1. 前往./groups 文件夹
        Step 2. 创建一个.txt文件，文件名为组名
        Step 3. 在该txt文件内每行一个用户名，表示该组的成员
        """,
    "batch?":
        """
        帮助：batch
        batch -l 列举全部批配置
        batch BatchName 显示某项批配置的详细信息
        batch -c BatchName 创建一个名称为BatchName的批配置
        batch -e BatchName 进入BatchName的编辑模式
        batch文件默认存放于./batches中。
        """,
    "schedule?":
        """
        帮助：schedule
        schedule -l 列举全部计划策略
        schedule ScheduleName 显示某个计划策略的详细信息
        schedule -c ScheduleName 创建一个名称为ScheduleName的计划策略
        schedule -e ScheduleName 进入ScheduleName的编辑模式
        batch文件默认存放于./schedules中。
        """
}


def TaskEditor(taskname):
    T = VALID_TASK.T
    print(f"Task编辑器  当前文件：  {taskname}")
    print("帮助： help  退出： exit  保存：save  重载：load 重写： clear")
    obj = AutomatorRecorder.gettask(taskname)
    while True:
        try:
            cmd = input("> ")
            cmds = cmd.split(" ")
            order = cmds[0]
            if order == "help":
                print("add Type 根据提示增加一个缩写为Type的指令")
                print("list -h 显示行会指令")
                print("list -d 显示地下城指令")
                print("list -j 显示竞技场指令")
                print("list -r 显示日常指令")
                print("list -t 显示工具指令")
                print("list -s 显示刷图指令")
                print("show 显示现在的任务情况")
                print("帮助： help  退出： exit  保存：save  重载：load 重写： clear")
                print("== 一定记住：先保存，再退出！！==")
            elif order == "exit":
                return
            elif order == "save":
                AutomatorRecorder.settask(taskname, obj)
            elif order == "load":
                obj = AutomatorRecorder.gettask(taskname)
            elif order == "clear":
                obj = {"tasks": []}
            elif order == "list":
                if len(cmds) > 1:
                    tag = cmds[1].lstrip("-")
                else:
                    tag = ""
                for i in T:
                    if i.startswith(tag):
                        print(i, "  ：  ", T[i]["title"])
                        print(T[i]["desc"])
            elif order == "show":
                for i in obj["tasks"]:
                    print(T[i["type"]]["title"])
            elif order == "add":
                if len(cmds) == 1:
                    continue
                typ = cmds[1]
                if typ not in T:
                    print("不存在的命令！")
                    continue
                cur = {"type": typ}
                print("添加新命令：", T[typ]["title"])
                for i in T[typ]["params"]:
                    print(">> ", i.title, " <<")
                    print(i.desc)
                    cur[i.key] = i.inputbox.create()
                obj['tasks'] += [cur]

            else:
                print("不认识的命令。")
        except Exception as e:
            print("输入错误！", e)


def show_account(account):
    A = AutomatorRecorder(account)
    print(A.getuser())


def create_account(account, password):
    A = AutomatorRecorder(account)
    d = dict(account=account, password=password)
    A.setuser(d)


def create_account_from_file(file):
    # 此处会有以前的task参数
    pattern = re.compile('\\s*(.*?)[\\s-]+([^\\s-]+)[\\s]*([^\\s]*)')
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            result = pattern.findall(line)
            if len(result) != 0:
                account, password, task = result[0]
            else:
                continue
            create_account(account, password)


def del_account(account):
    target = "%s/%s.txt" % (user_addr, account)
    if os.path.exists(target):
        os.remove(target)


def del_account_from_file(file):
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            cur = line.strip()
            if cur == "":
                continue
            del_account(cur)


def del_all_account():
    for acc in list_all_users(0):
        del_account(acc)


def edit_account(account, password=None):
    A = AutomatorRecorder(account)
    d = A.getuser()
    if password is not None:
        d["password"] = password
    A.setuser(d)


def show_task(TaskName):
    T = VALID_TASK.T
    obj = AutomatorRecorder.gettask(TaskName)
    for i in obj["tasks"]:
        print(T[i["type"]]["title"], end=" ")
        if "__disable__" in i and i["__disable__"]:
            print("(禁用)")
        else:
            print()


def create_task(TaskName):
    d = {"tasks": []}
    AutomatorRecorder.settask(TaskName, d)


def del_task(TaskName):
    target = "%s/%s.txt" % (task_addr, TaskName)
    if os.path.exists(target):
        os.remove(target)


def del_all_task():
    for t in list_all_tasks(0):
        del_task(t)


def show_group(GroupName):
    gp = AutomatorRecorder.getgroup(GroupName)
    users = list_all_users(0)
    for i in gp:
        if i in users:
            print(i)
        else:
            print(i, " 【未找到】")


def create_batch(BatchName):
    d = {"batch": []}
    AutomatorRecorder.setbatch(BatchName, d)


def show_batch(BatchName):
    obj = AutomatorRecorder.getbatch(BatchName)
    for i in obj["batch"]:
        if "group" in i:
            print("组", i["group"], "任务：", i["taskfile"], "优先级：", i["priority"])
        elif "account" in i:
            print("用户", i["account"], "任务：", i["taskfile"], "优先级：", i["priority"])


def edit_batch(BatchName):
    print(f"Batch编辑器  当前文件：  {BatchName}")
    print("帮助： help  退出： exit  保存：save  重载：load 重写： clear")
    print("什么是batch:  what")
    obj = AutomatorRecorder.getbatch(BatchName)
    while True:
        try:
            cmd = input("> ")
            cmds = cmd.split(" ")
            order = cmds[0]
            if order == "help":
                print("add account task [priority=0]")
                print("    增加一个优先级为priority的account做task的任务")
                print("add -g group task [priority=0]")
                print("    增加一个优先级为priorityd的组group做task的任务")
                print("add -file filename")
                print("    从文件中添加一组任务")
                print("    该文件由若干行组成，每一行应填入四个空格隔开的元素：")
                print("    若添加单独任务，则第一列写字母A，后面三个空依次填入account,task,priority。")
                print("    若添加组任务，则第一列写字母G，后面三个空依次填入group,task,priority")
                print("show 显示现在的任务情况")
                print("帮助： help  退出： exit  保存：save  重载：load 重写： clear")
                print("什么是batch:  what")
                print("== 一定记住：先保存，再退出！！==")
            elif order == "what":
                print("batch，批配置，为一系列X执行X的任务集合。")
                print("这可以是用户执行任务(account - task)，也可以是组执行任务(group - task)")
                print("每一个batch间的运行记录相互独立。对于同一个用户，在不同的两个batch中执行相同或"
                      "不同的任务时，各自的任务进度会被分别保留。")
                print("使用batch的好处在于将用户与任务脱钩，如果对于同一个用户需要频繁执行不同的任务，"
                      "则只需要制定两个独立的batch即可。这在40to1或早晚任务中非常有效。")
                print("在一个batch中可以给不同的任务指定优先级.同优先级任务会同批次完成，而高"
                      "优先级任务会优先进行。单开时，必然先执行高优先级任务，再执行低优先级任务，"
                      "但多开时，如果有空闲的设备，也可能高优先级任务和低优先级任务同时执行。")
                print("默认的优先级为0，也就是最低优先级，对于某些特殊任务（如大号的任务），可以调高优先级。")
            elif order == "exit":
                return
            elif order == "save":
                AutomatorRecorder.setbatch(BatchName, obj)
            elif order == "load":
                obj = AutomatorRecorder.getbatch(BatchName)
            elif order == "clear":
                obj = {"batch": []}
            elif order == "show":
                for i in obj["batch"]:
                    if "group" in i:
                        print("组", i["group"], "任务：", i["taskfile"], "优先级：", i["priority"])
                    elif "account" in i:
                        print("用户", i["account"], "任务：", i["taskfile"], "优先级：", i["priority"])
            elif order == "add":
                if len(cmds) in [4, 5] and cmds[1] == '-g':
                    group = cmds[2]
                    task = cmds[3]
                    if len(cmds) == 5:
                        priority = int(cmds[4])
                    else:
                        priority = 0
                    obj["batch"] += [dict(group=group, taskfile=task, priority=priority)]
                elif len(cmds) == 3 and cmds[1] == "-file":
                    with open(cmds[2], "r", encoding="utf-8") as f:
                        for line in f:
                            cur = line.strip()
                            curs = cur.split(" ")
                            assert len(curs) in [3, 4]
                            assert curs[0] in ['A', 'G']
                            d = {}
                            if len(curs) == 3:
                                d['priority'] = 0
                            else:
                                d['priority'] = int(curs[3])
                            if curs[0] == 'A':
                                d['account'] = curs[1]
                            elif curs[0] == 'G':
                                d['group'] = curs[1]
                            d['taskfile'] = curs[2]
                            obj["batch"] += d
                elif len(cmds) in [3, 4]:
                    account = cmds[1]
                    task = cmds[2]
                    if len(cmds) == 4:
                        priority = int(cmds[3])
                    else:
                        priority = 0
                    obj["batch"] += [dict(account=account, taskfile=task, priority=priority)]
                else:
                    print("add命令有误！")
            else:
                print("不认识的命令。")
        except Exception as e:
            print("输入错误！", e)


def create_schedule(ScheduleName):
    d = {"schedules": []}
    AutomatorRecorder.setschedule(ScheduleName, d)


def _show_schedule(obj):
    for ind, i in enumerate(obj["schedules"]):
        if i["type"] in ["asap", "wait"]:
            if i["type"] == "asap":
                print("ID", ind, "NAME", i["name"], "：** 立即执行 **")
            else:
                print("ID", ind, "NAME", i["name"], "：** 等待执行 **")
            if "batchfile" in i:
                print("+ 批配置: ", i["batchfile"])
            if "batchlist" in i:
                print("+ 批配置列表：")
                for j in i["batchlist"]:
                    print("+   ", j)
            if len(i["condition"]) > 0:
                print("+ 触发条件:")
                con = i["condition"]
                if "start_hour" in con and "end_hour" in con:
                    print("+ 时间段: ", con["start_hour"], "h ~ ", con["end_hour"], "h")
                if "can_juanzeng" in con:
                    print("+ 当", con["can_juanzeng"], "可以捐赠")
            if i["record"] == 1:
                print("+ 记录设置：持久运行")
            elif i["record"] == 2:
                print("+ 记录设置：循环运行")
        if i["type"] == "config":
            print("ID", ind, "：** 配置 **")
            if "restart" in i:
                print("+ 清除记录：", i["restart"], 'h')


def show_schedule(ScheduleName):
    obj = AutomatorRecorder.getschedule(ScheduleName)
    _show_schedule(obj)


def _edit_asap_wait_config(typ):
    obj = {}
    obj["type"] = typ
    mode = ""
    if typ in ["asap", "wait"]:
        while True:
            print("-- 批配置名称 --")
            I = input("请为这个子计划起个名字： ")
            obj["name"] = I
            print("-- 批配置模式 --")
            print("0: 只包含一个批配置（适用于大多数情况）")
            print("1: 多个批配置依次执行（适用于40to1等）")
            I = input(">").strip()
            if I == "0":
                mode = "batchfile"
                break
            elif I == "1":
                mode = "batchlist"
                break
            else:
                print("输入错误，重新输入")
        if mode == "batchfile":
            print("-- 批配置文件 --")
            I = input("请输入批配置文件：").strip()
            obj[mode] = I
        if mode == "batchlist":
            print("-- 批配置列表 --")
            print("请输入一系列批配置文件")
            print("它们将依次执行，且两批之间不共享进度。")
            obj[mode] = []
            while True:
                I = input("输入批配置文件（输入*结束）").strip()
                if I == "*":
                    break
                obj[mode] += [I]

        obj["condition"] = {}
        while True:
            print("-- 条件设置 --")
            print("0 退出设置")
            print("1 条件：指定时间段")
            print("2 条件：可以捐赠")
            I = input(">").strip()
            if I == '0':
                break
            elif I == '1':
                start = int(input("请输入起始小时： (0~23的整数）").strip())
                end = int(input("请输入结束小时：（0~23的整数）").strip())
                obj["condition"]["start_hour"] = start
                obj["condition"]["end_hour"] = end
            elif I == '2':
                acc = input("请输入检测的账号：").strip()
                obj["condition"]["can_juanzeng"] = acc
            else:
                print("输入错误!")
        obj["record"] = 0
        while True:
            print("-- 记录设置 --")
            print("0 正常运行（默认）")
            print("1 持久运行：不受到first或restart的影响，除非使用restart schedule name单独指定。")
            print("2 循环运行：适用于装备捐赠等条件，运行完毕后自动执行restart。")
            I = input(">").strip()
            if I == '0':
                break
            elif I == '1':
                obj["record"] = 1
                break
            elif I == '2':
                obj["record"] = 2
                break
            else:
                print("输入错误!")
        return obj
    elif typ == "config":
        while True:
            print("--Schedule配置--")
            print("0 退出设置")
            print("1 配置：清除记录时间")
            I = input(">").strip()
            if I == '0':
                break
            elif I == '1':
                tm = int(input("请输入小时： (0~23的整数）").strip())
                obj["restart"] = tm
            else:
                print("输入错误!")
        return obj


def edit_schedule(ScheduleName):
    print(f"Schedule编辑器  当前文件：  {ScheduleName}")
    print("帮助： help  退出： exit  保存：save  重载：load 重写： clear")
    print("什么是schedule:  what")
    obj = AutomatorRecorder.getschedule(ScheduleName)
    while True:
        try:
            cmd = input("> ")
            cmds = cmd.split(" ")
            order = cmds[0]
            if order == "help":
                print("add asap    按照提示添加一个立即执行的任务")
                print("add wait    按照提示增加一个等待执行的任务")
                print("add config  按照提示增加一个schedule配置")
                print("show 显示现在的计划情况")
                print("帮助： help  退出： exit  保存：save  重载：load 重写： clear")
                print("什么是batch:  what")
                print("== 一定记住：先保存，再退出！！==")
            elif order == "what":
                print("schedule，计划配置，为一种自动执行batch的方案")
                print("可以设定立刻执行、等待执行两种方法，在合适的条件被触发时执行既定的batch")
                print("schedule有三种类型： 立即执行 asap， 等待执行 wait， 计划配置 config")
                print("当设置为asap时，如果用户设置的条件成立，所设置的一个batch或一系列batch会立刻被执行；"
                      "若条件不成立，则该项schedule会被跳过，本次不再执行。")
                print("当设置为wait时，如果用户设置的条件成立，效果等效于asap;"
                      "但若用户设置的条件不成立，该计划不会被跳过，程序将一直运行直到条件成立为止。")
                print("当设置为config时，可以设置对schedule本身的控制参数。"
                      "如：restart参数可以控制清除记录的时间。")
            elif order == "exit":
                return
            elif order == "save":
                AutomatorRecorder.setschedule(ScheduleName, obj)
            elif order == "load":
                obj = AutomatorRecorder.getschedule(ScheduleName)
            elif order == "clear":
                obj = {"schedules": []}
            elif order == "show":
                _show_schedule(obj)
            elif order == "add" and len(cmds) == 2:
                if cmds[1] in ["asap", "wait", "config"]:
                    obj["schedules"] += [_edit_asap_wait_config(cmds[1])]
                else:
                    print("add命令有误！")
            else:
                print("不认识的命令。")
        except Exception as e:
            print("输入错误！", e)


if __name__ == "__main__":
    print(DOC_STR["title"])
    print("当前工作路径：", getcwd())
    while True:
        try:
            cmd = input("> ")
            cmds = cmd.split(" ")
            order = cmds[0]
            if order == "exit":
                break
            elif order == "help":
                print(DOC_STR["help?"])
            elif order == "user?" or cmd == "user":
                print(DOC_STR["user?"])
            elif order == "task?" or cmd == "task":
                print(DOC_STR["task?"])
            elif order == "group?" or cmd == "group":
                print(DOC_STR["group?"])
            elif order == "batch?" or cmd == "batch":
                print(DOC_STR["batch?"])
            elif order == "schedule?" or cmd == "schedule":
                print(DOC_STR["schedule?"])
            elif order == "user":
                if len(cmds) == 2 and cmds[1] == "-l":
                    list_all_users()
                elif len(cmds) == 4 and cmds[1] == "-c" and cmds[2] == "-file":
                    create_account_from_file(cmds[3])
                elif len(cmds) == 4 and cmds[1] == "-c":
                    create_account(cmds[2], cmds[3])
                elif len(cmds) == 4 and cmds[1] == '-d' and cmds[2] == "-file":
                    del_account_from_file(cmds[3])
                elif len(cmds) == 3 and cmds[1] == '-d' and cmds[2] == '-all':
                    del_all_account()
                elif len(cmds) == 3 and cmds[1] == "-d":
                    del_account(cmds[2])
                elif len(cmds) == 4 and cmds[2] == "-p":
                    edit_account(cmds[1], cmds[3])
                elif len(cmds) == 2 and cmds[1][0] != "-":
                    show_account(cmds[1])
                else:
                    print("Wrong Order!")
            elif order == "task":
                if len(cmds) == 2 and cmds[1] == "-l":
                    list_all_tasks()
                elif len(cmds) == 2 and cmds[1][0] != "-":
                    show_task(cmds[1])
                elif len(cmds) == 3 and cmds[1] == "-c":
                    create_task(cmds[2])
                elif len(cmds) == 3 and cmds[1] == "-e":
                    TaskEditor(cmds[2])
                elif len(cmds) == 3 and cmds[1] == "-d":
                    del_task(cmds[2])
                elif len(cmds) == 3 and cmds[1] == "-d" and cmds[2] == "-all":
                    del_all_task()
                else:
                    print("Wrong Order!")
            elif order == "group":
                if len(cmds) == 2 and cmds[1] == "-l":
                    list_all_groups()
                elif len(cmds) == 2:
                    show_group(cmds[1])
                else:
                    print("Wrong Order!")
            elif order == "batch":
                if len(cmds) == 2 and cmds[1] == "-l":
                    list_all_batches()
                elif len(cmds) == 3 and cmds[1] == "-c":
                    create_batch(cmds[2])
                elif len(cmds) == 3 and cmds[1] == "-e":
                    edit_batch(cmds[2])
                elif len(cmds) == 2:
                    show_batch(cmds[1])
                else:
                    print("Wrong Order!")
            elif order == "schedule":
                if len(cmds) == 2 and cmds[1] == '-l':
                    list_all_schedules()
                elif len(cmds) == 3 and cmds[1] == "-c":
                    create_schedule(cmds[2])
                elif len(cmds) == 3 and cmds[1] == "-e":
                    edit_schedule(cmds[2])
                elif len(cmds) == 2:
                    show_schedule(cmds[1])
                else:
                    print("Wrong Order!")
            else:
                print("Wrong Order!")
        except Exception as e:
            print("输入错误！", e)
