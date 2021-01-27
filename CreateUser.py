import re
from os import getcwd

from core.usercentre import *
from core.utils import PrettyEnter
from core.valid_task import BoolInputer, IntInputer

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
        帮助手册    在命令后输入?查看具体使用方法
        user       创建或编辑一个新的用户信息
        task       创建或编辑一个任务列表
        customtask 生成自定义任务文件
        group      创建或编辑一个用户组
        batch      创建或编辑一个批配置
        schedule   创建或编辑一个计划配置
        switch     创建或编辑一个开关配置
        flag [-a]  查看当前flag的激活情况 -a参数会显示全部flag（包括未激活）
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
        task TaskName 显示TaskName信息
        task TaskName detail 显示TaskName详细信息
        task TaskName moredetail 显示TaskName更详细信息 
        task -c TaskName 创建一个名称为TaskName的任务
        task -e TaskName 进入TaskName的编辑模式
        task -d TaskName 删除某一Task
        task -d -all 删除全部Task
        """,
    "customtask?":
        """
        帮助：customtask
        默认任务的力量是有极限的，
            我要超越默认任务！！！！！！！
        customtask -l 列举全部自定义任务程序文件
        在sample_customtask中有很多模板任务
        可以查看sample_customtask/sample_task.py中详细的自定义任务说明
        在/customtask中的.py文件会被自动识别并加入CreateUser（重启程序有效）
        可以复制相关的sample到其中并自己编写相关代码。        
        """,
    "group?":
        """
        帮助：group
        group -l 列举全部组列表
        group GroupName [-g] 显示某个组的全部成员，输入-g后还会显示其成员全部所在组
        group的创建：非常简单，不写方法了。
        Step 1. 前往./groups 文件夹
        Step 2. 创建一个.json文件，文件名为组名
        Step 3. 在该json文件内每行一个用户名，表示该组的成员  <- 由于某些原因，它其实以txt结尾最好，毕竟一行一个明显不是json吧……
        [新增方法] 以下方法中如果组不存在将被自动创建
        group add (GroupName) (UserName1) [(UserNameN) ...]
            将UserName或一系列空格隔开的UserNames添加到组GroupName
        group add (GroupName) *TargetGroup
            将TargetGroup中的用户添加到组GroupName，注：*TargetGroup表示在名称前加*号，如*xiaohao。
        group del (GroupName) (UserName1) [(UserNameN) ...] 从组GroupName中移除一个或多个空格隔开的UserName
        group del (GroupName) * 删除GroupName中全部组成员
        group del (GroupName) *TargetGroup 删除GroupName中全部TargetGroup中的组成员
        group move (GroupName1) (GroupName2) (UserName1) [(UserNameN) ...] 将一个或多个用户从组GroupName1移动到GroupName2
        group move (GroupName1) (GroupName2) * 将GroupName1中组成员全部移动至GroupName2
        group move (GroupName1) (GroupName2) *TargetGroup 将GroupName1中TargetGroup中的组成员全部移动至GroupName2
        group user (UserName) 显示某一个用户所在的全部组
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
        schedule文件默认存放于./schedules中。
        """,
    "switch?":
        """
        帮助：switch
        switch -l 列举全部开关配置
        switch SwitchName 显示某个开关配置的详细信息
        switch -c SwitchName 创建一个名称为SwitchName的开关配置
        switch -e SwitchName 进入SwitchName的编辑模式
        switch enable/disable SwitchName 启用/禁用某个开关配置
        switch文件默认存放于./switches中。
        """
}

T = VALID_TASK.T


def show_task_simple(ind, i):
    print(ind, ":", T[i["type"]]["title"], end="  ")
    if "__disable__" in i:
        if i["__disable__"] is True:
            print("（禁用）")
        elif i["__disable__"] is not False:
            print("（禁用当：", i["__disable__"], "）")
        else:
            print()
    else:
        print()


def show_task_detail(ind, i, more=False):
    show_task_simple(ind, i)
    for k, v in i.items():
        if k in ["type", "__disable__"]:
            continue
        if k not in T[i["type"]]["param_dict"]:
            continue
        print("  -", T[i["type"]]["param_dict"][k].title, ":", v)
        if more:
            PrettyEnter(T[i["type"]]["param_dict"][k].desc, "     ", "   * ")


def show_tasks_simple(obj):
    for ind, i in enumerate(obj["tasks"]):
        show_task_simple(ind, i)


def show_tasks_detail(obj, more=False):
    for ind, i in enumerate(obj["tasks"]):
        show_task_detail(ind, i, more)


def edit_one_task(i, show_value=True):
    while True:
        print("当前编辑：", i["type"], "--", T[i["type"]]["title"])
        for ind, par in enumerate(T[i["type"]]["params"]):
            print(ind, " - ", par.key, " : ", par.title)
            if show_value:
                if par.key in i:
                    print("    值：", i[par.key])
                elif par.default is not None:
                    print("    值： [默认] ", par.default)
                else:
                    print("    值： 错误！未设置")
        print("-1 - 退出")
        choose = IntInputer(-1, len(T[i["type"]]["params"]) - 1).create()
        if choose == -1:
            return
        cur_par = T[i["type"]]["params"][choose]
        print("当前编辑： ", cur_par.title)
        PrettyEnter(cur_par.desc, "    ", "  * ")
        if cur_par.key in i:
            i[cur_par.key] = cur_par.inputbox.edit(i[cur_par.key])
        else:
            i[cur_par.key] = cur_par.inputbox.create()


def TaskEditor(taskname):
    print(f"Task编辑器  当前文件：  {taskname}")
    print("帮助： help  退出： exit  保存：save  重载：load 重写： clear")
    obj = AutomatorRecorder.gettask(taskname)
    while True:
        try:
            cmd = input("> ")
            cmds = cmd.split(" ")
            order = cmds[0]
            if order == "help":
                print("add (Type) 根据提示增加一个缩写为Type的指令")
                print("del (ID) 删除指定ID的任务")
                print("move (ID1) (ID2) 将原来编号为ID1的任务移动至ID2")
                print("detail [(ID)] 查看指定ID的详细参数，若ID不指定，查看全部任务的详细参数")
                print("moredetail [(ID)] 查看指定ID的更详细参数，若ID不指定，查看全部任务的更详细参数")
                print("edit (ID) [-s] 修改某一个任务 设置了-s后，不会显示具体数值。")
                print("list -h 显示行会指令")
                print("list -d 显示地下城指令")
                print("list -j 显示竞技场指令")
                print("list -r 显示日常指令")
                print("list -t 显示工具指令")
                print("list -s 显示刷图指令")
                print("enable (ID) 启用编号为ID的任务")
                print("disable (ID) 禁用编号为ID的任务")
                print("flag (flagname) (ID) 当flagname被激活时，禁用编号为ID的任务（详见switch）")
                print("show 显示现在的任务情况及其ID")
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
                        PrettyEnter(T[i]["desc"], "    ", "  * ")
            elif order == "show":
                show_tasks_simple(obj)
            elif order == "enable" and len(cmds) == 2:
                ind = int(cmds[1])
                obj["tasks"][ind]["__disable__"] = False
            elif order == "disable" and len(cmds) == 2:
                ind = int(cmds[1])
                obj["tasks"][ind]["__disable__"] = True
            elif order == "flag" and len(cmds) == 3:
                ind = int(cmds[2])
                obj["tasks"][ind]["__disable__"] = cmds[1]
            elif order == "add":
                if len(cmds) == 1:
                    print("需要指定Type！")
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
            elif order == "del":
                if len(cmds) == 1:
                    print("需要指定ID！")
                    continue
                ID = int(cmds[1])
                del obj["tasks"][ID]
            elif order == "move":
                if len(cmds) <= 2:
                    print("需要指定ID1和ID2！")
                    continue
                else:
                    ID1 = int(cmds[1])
                    ID2 = int(cmds[2])
                    assert ID2 < len(obj["tasks"]), "数组越界！"
                    if ID2 < ID1:
                        tmp = obj["tasks"][ID1]
                        del obj["tasks"][ID1]
                        obj["tasks"].insert(ID2, tmp)
                    elif ID2 > ID1:
                        tmp = obj["tasks"][ID1]
                        obj["tasks"].insert(ID2 + 1, tmp)
                        del obj["tasks"][ID1]
            elif order == "detail":
                if len(cmds) == 1:
                    show_tasks_detail(obj)
                else:
                    show_task_detail(int(cmds[1]), obj["tasks"][int(cmds[1])])
            elif order == "moredetail":
                if len(cmds) == 1:
                    show_tasks_detail(obj, True)
                else:
                    show_task_detail(int(cmds[1]), obj["tasks"][int(cmds[1])], True)
            elif order == "edit" and len(cmds) >= 2:
                if len(cmds) >= 3 and cmds[2] == "-s":
                    edit_one_task(obj["tasks"][int(cmds[1])], False)
                else:
                    edit_one_task(obj["tasks"][int(cmds[1])], True)
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
    target = "%s/%s.json" % (user_addr, account)
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
    obj = AutomatorRecorder.gettask(TaskName)
    show_tasks_simple(obj)

def create_task(TaskName):
    d = {"tasks": []}
    AutomatorRecorder.settask(TaskName, d)


def del_task(TaskName):
    target = "%s/%s.json" % (task_addr, TaskName)
    if os.path.exists(target):
        os.remove(target)


def del_all_task():
    for t in list_all_tasks(0):
        del_task(t)


def show_group(GroupName, all_group=False):
    gp = AutomatorRecorder.getgroup(GroupName, False)
    users = list_all_users(0)
    if all_group:
        groups = list_all_groups(0)
        detailed_group = {}
        for g in groups:
            detailed_group[g] = AutomatorRecorder.getgroup(g)
    for i in gp:
        if i in users:
            print(i, end=" ")
            if all_group:
                print("所在组：", get_all_group(i, detailed_group))
            else:
                print()
        else:
            print(i, " 【未找到】")


def show_group_user(UserName):
    gps = get_all_group(UserName)
    print(gps)


def group_add(GroupName, UserNames: List[str]):
    gp = AutomatorRecorder.getgroup(GroupName, False)
    for acc in UserNames:
        if acc not in gp:
            gp += [acc]
        else:
            print("用户", acc, "已经存在在", GroupName, "中，不再重复添加！")
    AutomatorRecorder.setgroup(GroupName, gp)


def group_add_group(GroupName, TargetGroup):
    group_add(GroupName, AutomatorRecorder.getgroup(TargetGroup, False))


def group_del(GroupName, UserNames: List[str]):
    gp = AutomatorRecorder.getgroup(GroupName, False)
    for acc in UserNames:
        if acc in gp:
            gp.remove(acc)
        else:
            print("用户", acc, "不存在于", GroupName, "中。")
    AutomatorRecorder.setgroup(GroupName, gp)


def group_del_group(GroupName, TargetGroup):
    group_del(GroupName, AutomatorRecorder.getgroup(TargetGroup, False))


def group_del_all(GroupName):
    AutomatorRecorder.setgroup(GroupName, [])


def group_move(GroupName1, GroupName2, UserNames: List[str]):
    assert GroupName1 != GroupName2, "两个组不能相同！"
    group_add(GroupName2, UserNames)
    group_del(GroupName1, UserNames)


def group_move_group(GroupName1, GroupName2, TargetGroup):
    assert GroupName1 != GroupName2, "两个组不能相同！"
    UserNames = AutomatorRecorder.getgroup(TargetGroup, False)
    group_add(GroupName2, UserNames)
    group_del(GroupName1, UserNames)


def group_move_all(GroupName1, GroupName2):
    assert GroupName1 != GroupName2, "两个组不能相同！"
    group_add(GroupName2, AutomatorRecorder.getgroup(GroupName1, False))
    group_del_all(GroupName1)


def create_batch(BatchName):
    d = {"batch": []}
    AutomatorRecorder.setbatch(BatchName, d)


def print_batch(obj):
    for ind, i in enumerate(obj["batch"]):
        if "group" in i:
            print("ID: ", ind, "组", i["group"], "任务：", i["taskfile"], "优先级：", i["priority"], end=" ")
        elif "account" in i:
            print("ID: ", ind, "用户", i["account"], "任务：", i["taskfile"], "优先级：", i["priority"], end=" ")
        if "random" in i and i["random"] is True:
            print(" [随机模式]")
        else:
            print()


def show_batch(BatchName):
    obj = AutomatorRecorder.getbatch(BatchName)
    print_batch(obj)


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
                print("random enable/disable (ID)  随机编号为ID的batch的优先级（优先级将±0.5浮动）")
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
                print_batch(obj)
            elif order == "random":
                if len(cmds) >= 3:
                    ind = int(cmds[2])
                    if cmds[1] == "enable":
                        obj["batch"][ind]["random"] = True
                    elif cmds[1] == "disable":
                        obj["batch"][ind]["random"] = False
                    else:
                        print("只能输入enable或者disable！")
                else:
                    print("random命令有误！")
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


def del_schedule(ScheduleName):
    target = "%s/%s.txt" % (schedule_addr, ScheduleName)
    if os.path.exists(target):
        os.remove(target)


def _show_schedule(obj):
    FLAGS = list_all_flags()
    for ind, i in enumerate(obj["schedules"]):
        if i["type"] != "config":
            if "__disable__" in i:
                if i["__disable__"] is True:
                    print("ID", ind, "NAME", i["name"], "已禁用")
                    continue
                elif i["__disable__"] is not False:
                    print("ID", ind, "NAME", i["name"], "禁用当：", i["__disable__"], end=" ")
                    tmp = False
                    for flag, detail in FLAGS.items():
                        if flag == i["__disable__"] and detail["default"] is True:
                            print("已禁用")
                            tmp = True
                            break
                        else:
                            break
                    if tmp:
                        continue

                else:
                    print("ID", ind, "NAME", i["name"], end=" ")
            else:
                print("ID", ind, "NAME", i["name"], end=" ")

        if i["type"] in ["asap", "wait"]:
            if i["type"] == "asap":
                print("：** 立即执行 **")
            else:
                print("：** 等待执行 **")
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


def _get_subschedule_id(obj, name):
    for i, s in enumerate(obj["schedules"]):
        if s["name"] == name:
            return i
    return -1

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
                print("add asap           按照提示添加一个立即执行的任务")
                print("add wait           按照提示增加一个等待执行的任务")
                print("add config         按照提示增加一个schedule配置")
                print("enable name        激活名称为name的子计划")
                print("disable name       禁用名称为name的子计划")
                print("flag flagname name 当flag设置为真时，禁用名称为name的子计划（详见switch)")
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
            elif order == "enable" and len(cmds) == 2:
                ind = _get_subschedule_id(obj, cmds[1])
                if ind == -1:
                    print("未找到", cmds[1])
                else:
                    obj["schedules"][ind]["__disable__"] = False
            elif order == "disable" and len(cmds) == 2:
                ind = _get_subschedule_id(obj, cmds[1])
                if ind == -1:
                    print("未找到", cmds[1])
                else:
                    obj["schedules"][ind]["__disable__"] = True
            elif order == "flag" and len(cmds) == 3:
                ind = _get_subschedule_id(obj, cmds[2])
                if ind == -1:
                    print("未找到", cmds[2])
                else:
                    obj["schedules"][ind]["__disable__"] = cmds[1]
            else:
                print("不认识的命令。")
        except Exception as e:
            print("输入错误！", e)


def show_all_switches():
    # 按优先级顺序显示全部开关配置
    switches = list_all_switches()
    for s in switches:
        switch = AutomatorRecorder.getswitch(s)
        print(switch["order"], "-", s, "" if switch["enable"] else "（禁用）")


def show_switch(obj):
    # 显示某一个开关的详细细节
    print("状态:", "启用" if obj["enable"] else "禁用")
    print("优先级：", obj["order"])
    for ind, switch in enumerate(obj["switches"]):
        print("ID: ", ind)
        print("   Flags:", switch["flags"])
        print("   默认状态:", switch["default"])
        if "group" in switch and len(switch["group"]) > 0:
            print("   针对用户组特殊设置：")
            for group, set in switch["group"].items():
                print("      <", group, "> - ", set)
        if "user" in switch and len(switch["user"]) > 0:
            print("   针对用户特殊设置：")
            for user, set in switch["user"].items():
                print("      ", user, " - ", set)


def create_switch(SwitchName):
    d = {"enable": True, "order": 0, "switches": []}
    AutomatorRecorder.setswitch(SwitchName, d)


def enable_switch(SwitchName):
    d = AutomatorRecorder.getswitch(SwitchName)
    d["enable"] = True
    AutomatorRecorder.setswitch(SwitchName, d)


def disable_switch(SwitchName):
    d = AutomatorRecorder.getswitch(SwitchName)
    d["enable"] = False
    AutomatorRecorder.setswitch(SwitchName, d)


def show_flag(all=False):
    if all:
        flags, other_flag = list_all_flags(False)
        other_flag = [(o, None) for o in other_flag]
    else:
        flags = list_all_flags()
        other_flag = []
    for flag, detail in flags.items():
        if detail["default"] is False and len(detail["user"]) == 0 and len(detail["group"]) == 0:
            if all:
                other_flag += [(flag, detail)]
            continue
        print("<", flag, ">", end=" ")
        print("激活" if detail["default"] else "未激活")
        for group, set in detail["group"].items():
            print("   Group <", group, "> - ", set)
        for user, set in detail["user"].items():
            print("   User ", user, " - ", set)
    if all:
        for flag, detail in other_flag:
            print("<", flag, ">", "未激活")


def _add_switch():
    print("请输入要设置的flag的名称，多个flag间用单个空格隔开。")
    obj = {}
    flags_str = input("> ")
    obj["flags"] = flags_str.split(" ")
    print("请输入默认激活状态")
    obj["default"] = BoolInputer().create()
    obj["user"] = {}
    obj["group"] = {}
    obj["special"] = {}
    while True:
        print("0 - 退出")
        print("1 - 添加一条针对用户特殊配置")
        print("2 - 添加一条针对用户组特殊配置")
        i = IntInputer(0, 2).create()
        if i == 0:
            break
        elif i == 1:
            user = input("请输入用户名：")
            print("请输入特殊激活状态：")
            set = BoolInputer().create()
            obj["user"][user] = set
        elif i == 2:
            group = input("请输入用户组名：")
            print("请输入特殊激活状态：")
            set = BoolInputer().create()
            obj["group"][group] = set
    return obj


def edit_switch(SwitchName):
    print(f"Switch编辑器  当前文件：  {SwitchName}")
    print("帮助： help  退出： exit  保存：save  重载：load 重写： clear")
    print("什么是switch:  what")
    obj = AutomatorRecorder.getswitch(SwitchName)
    while True:
        try:
            cmd = input("> ")
            cmds = cmd.split(" ")
            order = cmds[0]
            if order == "help":
                print("enable/disable 设置为启用/禁用状态")
                print("order 修改优先级")
                print("add 根据向导添加一个子开关")
                print("show 显示现在的配置情况")
                print("帮助： help  退出： exit  保存：save  重载：load 重写： clear")
                print("什么是switch:  what")
                print("== 一定记住：先保存，再退出！！==")
            elif order == "what":
                print("Switch，开关，控制一系列flag的激活与否。\n"
                      "flag的激活将影响到task和schedule中对disable配置的生效与否。\n"
                      """对task：
    如果对某一个子task中设置了：
        "__disable__":true,
        则该项task将处于禁用状态，并且显示 XXX（禁用），该task将在加入时被替换为nothing任务
    如果设置了：
        "__disable__":false,
        或者并未设置"__disable__",则该task将被正常导入。
    如果设置了：
        "__disable__":"flag"
        则当flag处于激活状态时，该任务被禁用，并显示 XXX（禁用当：flag）

对schedule：
    同task，当某一个子schedule的__disable__被激活，
    该schedule将处于禁用状态，不会被检测。\n"""
                      "此外，还可以针对特定user和group设置例外情况。具体json配置如下：\n"
                      """"enable":True,  # 开关配置处于启动状态
"order":0,  # 开关文件被读取的优先级
"switches":[
    {
        "flags":["flagname1","flagname2",...] 受到同一配置的多个flag的名称字符串
        "default":true  # 该flag的默认启动状态
        "user":{"username":false, "username2":true, ...}  # 针对用户的特殊设置
        "group":{"groupname":false, ...}  # 针对用户组的特殊设置
        "special":{}  # 预留的特殊判断
    },
]}
注：
1.  在某一开关文件中，如果default设置为true，且不进行其它设置，则该flag将被设置为激活状态。
2.  如果default设置为true，但是针对用户设置了username:false，
    则在导入task时，如果该task设置了disable flag，但执行用户为username，则依然会被导入。
3.  如果default设置为true，但是针对用户组设置了groupname:false，
    则在导入task时，如果该task设置了disable flag，但执行用户所属用户组groupname，则依然会被导入。
4.  user优先级大于group。如果同时设置了group的false和user的true，且user处于group中，则对该用户而言其flag处于激活状态。
5.  如果default设置为false，且不进行其它设置，则该flag将被设置为未激活状态。
6.  如果default设置为false，但是针对用户设置了username:true，则仅对该用户禁用任务。
7.  如果default设置为false，但是针对用户组设置了groupname:true，则仅对该用户组中用户禁用任务。
8.  对于多个启动的开关文件中含有相同flag时，按照优先级顺序决定。order越大的开关配置将被优先读取，order相同时按照文件名排序。
    对于高优先级的开关文件，确定了某一个flag处于激活或非激活状态后，将无视后来低优先级开关文件对次flag状态的更改。
9.  如果同一组配置中包含了针对某一用户的矛盾的两个组，则按照名称顺序以第一个组为判断结果。""")
            elif order == "exit":
                return
            elif order == "save":
                AutomatorRecorder.setswitch(SwitchName, obj)
            elif order == "load":
                obj = AutomatorRecorder.getswitch(SwitchName)
            elif order == "clear":
                obj["switches"] = []
            elif order == "show":
                show_switch(obj)
            elif order == "order":
                obj["order"] = IntInputer().create()
            elif order == "enable":
                obj["enable"] = True
            elif order == "disable":
                obj["enable"] = False
            elif order == "add":
                obj["switches"] += [_add_switch()]
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
            elif order == "customtask?" or cmd == "customtask":
                print(DOC_STR["customtask?"])
            elif order == "group?" or cmd == "group":
                print(DOC_STR["group?"])
            elif order == "batch?" or cmd == "batch":
                print(DOC_STR["batch?"])
            elif order == "schedule?" or cmd == "schedule":
                print(DOC_STR["schedule?"])
            elif order == "switch?" or cmd == "switch":
                print(DOC_STR["switch?"])
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
                elif len(cmds) == 3 and cmds[1][0] != "-" and cmds[2] == "detail":
                    show_tasks_detail(AutomatorRecorder.gettask(cmds[1]), False)
                elif len(cmds) == 3 and cmds[1][0] != "-" and cmds[2] == "moredetail":
                    show_tasks_detail(AutomatorRecorder.gettask(cmds[1]), True)
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
            elif order == "customtask":
                if len(cmds) == 2 and cmds[1] == "-l":
                    list_all_customtasks()
                else:
                    print("Wrong Order!")
            elif order == "group":
                if len(cmds) == 2 and cmds[1] == "-l":
                    list_all_groups()
                elif len(cmds) == 4 and cmds[1] == "add" and cmds[3].startswith("*") and cmds[3] != "*":
                    TargetGroup = cmds[3][1:]
                    GroupName = cmds[2]
                    group_add_group(GroupName, TargetGroup)
                elif len(cmds) >= 4 and cmds[1] == "add":
                    UserNames = cmds[3:]
                    GroupName = cmds[2]
                    group_add(GroupName, UserNames)
                elif len(cmds) == 4 and cmds[1] == "del" and cmds[3] == "*":
                    GroupName = cmds[2]
                    group_del_all(GroupName)
                elif len(cmds) == 4 and cmds[1] == "del" and cmds[3].startswith("*"):
                    GroupName = cmds[2]
                    TargetGroup = cmds[3][1:]
                    group_del_group(GroupName, TargetGroup)
                elif len(cmds) >= 4 and cmds[1] == "del":
                    UserNames = cmds[3:]
                    GroupName = cmds[2]
                    group_del(GroupName, UserNames)
                elif len(cmds) == 5 and cmds[1] == "move" and cmds[4] == "*":
                    GroupName1 = cmds[2]
                    GroupName2 = cmds[3]
                    group_move_all(GroupName1, GroupName2)
                elif len(cmds) == 5 and cmds[1] == "move" and cmds[4].startswith("*"):
                    GroupName1 = cmds[2]
                    GroupName2 = cmds[3]
                    TargetGroup = cmds[4][1:]
                    group_move_group(GroupName1, GroupName2, TargetGroup)
                elif len(cmds) >= 5 and cmds[1] == "move":
                    UserNames = cmds[4:]
                    GroupName1 = cmds[2]
                    GroupName2 = cmds[3]
                    group_move(GroupName1, GroupName2, UserNames)
                elif len(cmds) == 3 and cmds[1] == "user":
                    show_group_user(cmds[2])
                elif len(cmds) == 3 and cmds[2] == "-g":
                    show_group(cmds[1], True)
                elif len(cmds) == 2:
                    show_group(cmds[1], False)
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
            elif order == "switch":
                if len(cmds) == 2 and cmds[1] == '-l':
                    show_all_switches()
                elif len(cmds) == 3 and cmds[1] == "-c":
                    create_switch(cmds[2])
                elif len(cmds) == 3 and cmds[1] == "-e":
                    edit_switch(cmds[2])
                elif len(cmds) == 3 and cmds[1] == "enable":
                    enable_switch(cmds[2])
                elif len(cmds) == 3 and cmds[1] == "disable":
                    disable_switch(cmds[2])
                elif len(cmds) == 2:
                    show_switch(AutomatorRecorder.getswitch(cmds[1]))
                else:
                    print("Wrong Order!")
            elif order == "flag":
                if len(cmds) == 2 and cmds[1] == "-a":
                    show_flag(True)
                else:
                    show_flag(False)
            else:
                print("Wrong Order!")
        except Exception as e:
            print("输入错误！", e)
