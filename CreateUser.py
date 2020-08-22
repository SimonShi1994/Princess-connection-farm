import re
from os import getcwd

from core.usercentre import *

DOC_STR = {
    "title":
        """
        +-------------------------------------------------+
        +                用户配置文件编辑器                 +
        +          在没有GUI的时候先将就着使用一下           +
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
        batch    创建或编辑一个批策略
        """,
    "user?":
        """
        帮助: user
        user -l 列举全部用户列表
        user Account 显示某用户的所有信息
        user -c Account Password [Task] 创建一个新用户。
            Account: 用户名    Password: 密码   Task: 任务列表，需要从task中创建
            如果Task留空，则表示该账号不进行脚本任务
            对已经存在的用户将覆盖原本的信息
        user -c -file Filename 从指定文件Filename创建用户
            该文件每一行要求分隔符（空格或Tab）隔开的两到三个元素 Account Password [Task]
            若Task为空，则表示该账号不进行脚本任务
            对已经存在的用户将覆盖原本的信息。
        user -d Account 删除指定Account的账户
        user -d -file Filename 从指定文件Filename删除用户
            该文件每一行为一个Account，表示要删除的用户
        user -d -all 删除全部用户
        user Account [-p Password] [-t [Task]] 更改某一账户的密码或任务
            若需要删除某一个账户的任务，则写-t后不写Task
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


def create_account(account, password, taskfile):
    A = AutomatorRecorder(account)
    d = dict(account=account, password=password, taskfile=taskfile)
    A.setuser(d)


def create_account_from_file(file):
    pattern = re.compile('\\s*(.*?)[\\s-]+([^\\s-]+)[\\s]*([^\\s]*)')
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            result = pattern.findall(line)
            if len(result) != 0:
                account, password, task = result[0]
            else:
                continue
            create_account(account, password, task)


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


def edit_account(account, password=None, taskfile=None):
    A = AutomatorRecorder(account)
    d = A.getuser()
    if password is not None:
        d["password"] = password
    if taskfile is not None:
        d["taskfile"] = taskfile
    A.setuser(d)


def show_task(TaskName):
    T = VALID_TASK.T
    obj = AutomatorRecorder.gettask(TaskName)
    for i in obj["tasks"]:
        print(T[i["type"]]["title"])


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
            elif order == "user":
                if len(cmds) == 2 and cmds[1] == "-l":
                    list_all_users()
                elif len(cmds) == 5 and cmds[1] == "-c":
                    create_account(cmds[2], cmds[3], cmds[4])
                elif len(cmds) == 4 and cmds[1] == "-c" and cmds[2] == "-file":
                    create_account_from_file(cmds[3])
                elif len(cmds) == 4 and cmds[1] == "-c":
                    create_account(cmds[2], cmds[3], "")
                elif len(cmds) == 4 and cmds[1] == '-d' and cmds[2] == "-file":
                    del_account_from_file(cmds[3])
                elif len(cmds) == 3 and cmds[1] == '-d' and cmds[2] == '-all':
                    del_all_account()
                elif len(cmds) == 3 and cmds[1] == "-d":
                    del_account(cmds[2])
                elif len(cmds) in [3, 4, 5, 6] and cmds[1][0] != '-':
                    p = 2
                    while p < len(cmds):
                        if cmds[p] == "-p" and p + 1 < len(cmds):
                            edit_account(cmds[1], password=cmds[p + 1])
                            p += 2
                        elif cmds[p] == "-t" and p + 1 < len(cmds) and cmds[p + 1] not in ["-p", "-t"]:
                            edit_account(cmds[1], taskfile=cmds[p + 1])
                            p += 2
                        elif cmds[p] == "-t" and (p + 1 >= len(cmds) or cmds[p + 1] in ["-p", "-t"]):
                            edit_account(cmds[1], taskfile="")
                            p += 1
                        else:
                            print("Wrong Order!")
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
            else:
                print("Wrong Order!")
        except Exception as e:
            print("输入错误！", e)
