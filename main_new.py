import sys
import traceback

from core.constant import USER_DEFAULT_DICT as UDD
from core.initializer import PCRInitializer, Schedule
from core.launcher import EMULATOR_DICT
from core.pcr_config import *
from core.usercentre import AutomatorRecorder, list_all_users, parse_batch, check_users_exists

PCR: Optional[PCRInitializer] = None
SCH: Optional[Schedule] = None
last_schedule = ""


def GetLastSchedule():
    global last_schedule
    if not os.path.exists("bind_schedule.txt"):
        last_schedule = ""
        return
    with open("bind_schedule.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        if len(lines) > 0:
            last_schedule = lines[0]


def StartPCR():
    global PCR
    if PCR is None:
        print("控制器正在连接中……")
        PCR = PCRInitializer()
        PCR.connect()
    PCR.devices.add_from_config()
    PCR.start()


def UnBind():
    global last_schedule
    last_schedule = ""
    with open("bind_schedule.txt", "w", encoding="utf-8") as f:
        f.write("")


def BindSchedule(schedule):
    global SCH, PCR, last_schedule
    if SCH is not None:
        raise Exception("无法绑定Schedule：请先结束之前的Schedule！")
    if schedule != "":
        last_schedule = schedule
    with open("bind_schedule.txt", "w", encoding="utf-8") as f:
        f.write(schedule)
    print("Schedule绑定成功：", schedule)


def RunningInput():
    if not running_input:
        if last_schedule == "":
            print("* 由于没有指定schedule，running_input自动开启。")
            print("* 可以在添加任务后，输入join屏蔽实时控制。")
            print("* 输入help，查看实时控制帮助。")
        else:
            print("* 实时控制已屏蔽，可以在config.ini - running_input中进行设置。")
            if end_shutdown:
                print("* end_shutdown配置启动，全部任务结束后，将自动关机。")
                JoinShutdown()
            else:
                print("* 全部任务结束后，将自动退出。")
                JoinExit()
    else:
        print("* 实时控制已经开启，可以在config.ini - running_input中进行设置。")
        print("* Tips：如果出现了子进程长时间未响应的情况，请输入join或在配置中关闭running_input。")
        print("* 输入help，查看实时控制帮助。")


def FirstSchedule():
    global SCH, last_schedule, PCR
    if PCR is None:
        StartPCR()
    if SCH is not None:
        raise Exception("Schedule已经运行，请先关闭！")
    SCH = Schedule(last_schedule, PCR)
    SCH.run_first_time()
    RunningInput()


def ContinueSchedule():
    global SCH, last_schedule, PCR
    if PCR is None:
        StartPCR()
    if SCH is not None:
        raise Exception("Schedule已经运行，请先关闭！")
    SCH = Schedule(last_schedule, PCR)
    SCH.run_continue()
    RunningInput()


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
        if ts['max'] is not None or ts["Hmax"] is not None:
            print("USER: ", acc, end=" ")
            if ts['max'] is not None:
                print("Normal ", ts["max"], end=" ")
            if ts["Hmax"] is not None:
                print("Hard ", ts["Hmax"], end=" ")
            print("")


def CheckState():
    global SCH, last_schedule
    if last_schedule == "":
        print("没有绑定具体的计划文件。")
        return
    if SCH is None:
        mysch = Schedule(last_schedule, None)
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


def ClearError(name):
    global last_schedule
    if last_schedule == "":
        print("没有绑定具体的计划文件。")
        return
    mysch = Schedule(last_schedule, None)
    mysch.clear_error(name)


def Restart(name):
    global last_schedule
    if last_schedule == "":
        print("没有绑定具体的计划文件。")
        return
    mysch = Schedule(last_schedule, None)
    mysch.restart(name)


def StopSchedule(force=False):
    global SCH, PCR
    if SCH is None:
        print("还没有运行任何Schedule")
        return
    SCH.stop(force)
    PCR = None
    SCH = None


def JoinExit(nowait=False):
    global SCH
    if SCH is None:
        print("还没有任何Schedule")
        return
    SCH.join(nowait)
    SCH.stop()
    sys.exit(0)


def JoinShutdown(nowait=False):
    global SCH
    if SCH is None:
        print("还没有任何Schedule")
        return
    SCH.join(nowait)
    SCH.stop()
    os.system("shutdown -s -f -t 120")


def ShowGuide():
    print("/docs/introduce_to_schedule.md  Schedule使用帮助")
    print("/INI文件配置解读.md               配置文件使用说明")
    print("/AboutUpdater.md                自动更新使用说明")
    print("/webclient/README.md            前端使用说明")
    print("/tasks_example/                 样例任务json文件")
    print("/equip/                         自动发起捐赠所用的样例装备")


def ShowServerChan():
    if s_sckey != "":
        print("* Server酱已配置！")
        print("  - 运行状态消息发送间隔(s) s_sentstate schedule：", s_sentstate)
        print("  - 记录过滤等级 log_lev：", log_lev)
        print("  - 记录最大累积条数 log_cache：", log_cache)
    else:
        print("* Server酱未配置，前往config.ini - s_sckey进行设置")


def ShowAutoConsole():
    print("* ADB文件路径 adb_dir：", os.path.abspath(adb_dir))
    print("* 自动添加至环境变量 add_adb_to_path：", "已开启" if add_adb_to_path else "未开启")
    if emulator_console != "":
        print("* 模拟器自动控制已配置！")
        print("  - 模拟器选择 selected_emulator：", selected_emulator)
        if selected_emulator in EMULATOR_DICT:
            launcher = EMULATOR_DICT[selected_emulator]()
            print("  - 控制器所在路径 emulator_console：", emulator_console)
            print("  - 自启动模拟器编号 emulator_id：", emulator_id)
            print("  - 自动分配模拟器地址 auto_emulator_address：", "已开启" if auto_emulator_address else "未开启")
            for i in emulator_id:
                print("  - ID: ", i, " Serial:", launcher.id_to_serial(i))
            print("  - 闲置自动关闭模拟器 quit_emulator_when_free：", "已开启" if quit_emulator_when_free else "未开启")
            if quit_emulator_when_free:
                print("  - - 最大闲置时间 max_free_time：", max_free_time)
        else:
            print("  !! 错误，不支持的模拟器。当前仅支持：雷电")
    else:
        print("* 模拟器自动控制未配置，前往config.ini - emulator_console进行配置")


def ShowOCR():
    print("* OCR模式 ocr_mode：", ocr_mode)
    if baidu_apiKey != "":
        print("* BaiduAPI 已配置！")
    else:
        print("* BaiduAPI 未配置，前往config.ini - baidu_apiKey进行配置")


def ShowPCRPerformance():
    print("* 快速截图 fast_screencut：", "已开启" if fast_screencut else "未开启")
    if fast_screencut:
        print("  - 强制快速截图 force_fast_screencut：", "已开启" if force_fast_screencut else "未开启")
        print("  - 截图强制延迟 fast_screencut_delay：", fast_screencut_delay)
        print("  - 最长等待时间 fast_screencut_timeout：", fast_screencut_timeout)
    print("* 异步检测间隔 async_screenshot_freq：", async_screenshot_freq)
    print("  - Connecting超时等待时间 bad_connecting_time：", bad_connecting_time)
    if not disable_timeout_raise:
        print("* 图像匹配最长等待时间 lockimg_timeout：", lockimg_timeout)
    else:
        print("* 图像匹配超时报错已屏蔽")
    print("* Shift+P脚本暂停 enable_pause：", "已开启" if enable_pause else "未开启")
    print("* 最大重启重试次数 max_reboot：", max_reboot)
    print("* 运行时实时控制 running_input：", "已开启" if running_input else "未开启")
    print("* 自动跳过验证码 captcha_skip：", "已开启" if captcha_skip else "未开启")
    print("* 出现验证码后等待时间 captcha_wait_time：", captcha_wait_time)
    print("* 出现验证码后是否弹出置顶提示框 captcha_popup：", "已开启" if captcha_popup else "未开启")


def ShowDebugInfo():
    print("* 输出Debug信息 debug：", "已开启" if debug else "未开启")
    print("* 忽略警告信息 ignore_warning：", "已开启" if ignore_warning else "未开启")
    print("* 保存错误堆栈 trace_exception_for_debug:", "已开启" if trace_exception_for_debug else "未开启")
    print("* 保存baiduocr的图片 baidu_ocr_img：", "已开启" if baidu_ocr_img else "未开启")
    print("* 屏蔽图像匹配超时报错 disable_timeout_raise：", "已开启" if disable_timeout_raise else "未开启")


def CheckConstantImgs():
    from core import constant
    import os
    ALLIMG = []
    BADIMG = []

    def CheckDict(d: dict):
        for k, v in d.items():
            if type(k) is str and k.startswith("__"):
                continue
            if type(v) is dict:
                CheckDict(v)
            elif type(v) is constant.PCRelement:
                if v.img is not None:
                    if v.img in ALLIMG:
                        continue
                    ALLIMG.append(v.img)
                    if not os.path.exists(v.img):
                        print("  - 文件缺失：", v.img)
                        BADIMG.append(v.img)

    print("* 检查本地图片")
    for obj in dir(constant):
        if type(constant.__dict__[obj]) is dict and not obj.startswith("__"):
            CheckDict(constant.__dict__[obj])
    if len(BADIMG) == 0:
        print("* 全部图片检测完毕")
    else:
        print("* 存在缺失的图片，脚本可能无法正常运行。")


def ShowInfo():
    ShowDebugInfo()
    ShowServerChan()
    ShowOCR()
    ShowPCRPerformance()
    ShowAutoConsole()
    CheckConstantImgs()


if __name__ == "__main__":
    GetLastSchedule()
    argv = sys.argv
    if len(argv) >= 2:
        if argv[1] == "first":
            assert len(argv) >= 3
            BindSchedule(argv[2])
            FirstSchedule()
        elif argv[1] == "continue":
            assert len(argv) >= 3
            BindSchedule(argv[2])
            ContinueSchedule()
    else:
        print("------------- 用户脚本控制台 --------------")
        print("Ver 2.1.20201031")
        print("help 查看帮助                   exit 退出")
        print("info 查看配置信息               guide 教程")
        print("By TheAutumnOfRice")
        print("----------------------------------------")
        print("* Tip：如果要使用任何OCR（包括本地和网络），请手动启动app.py！")
        print("* Tip：如果要自动填写验证码，请在config关闭captcha_skip")
        print("* Tip：如果某Schedule莫名无法运行，可能是存在未解决的错误，请参考introduce中错误解决相关部分！")
        if last_schedule != "":
            print("当前绑定计划：", last_schedule)
        print("新的脚本控制方法更新！输入help查看帮助。")
    while True:
        try:
            cmd = input("> ")
            cmds = cmd.split(" ")
            order = cmds[0]
            if order == "info":
                ShowInfo()
            elif order == "guide":
                ShowGuide()
            elif order == "break":
                break
            elif order == "help":
                if SCH is None:
                    print("脚本控制帮助 ()内的为需要填写的参数，[]内的参数可以不填写（使用默认参数）")
                    print("bind (schedule) 绑定一个计划")
                    if last_schedule == "":
                        print("first 启动脚本，此后可以输入指令添加计划")
                    else:
                        print("first 清除计划", last_schedule, "的运行记录并重新执行")
                        print("continue 继续执行计划", last_schedule)
                        print("state 显示计划", last_schedule, "的运行状态")
                        print("clear (name) 清除计划", last_schedule, "中名为Name的子计划的错误，name设置为-all时，全部清除。")
                        print("restart (name) 清除计划", last_schedule, "中名为Name的子计划的运行记录，name设置为-all时，全部清除。")
                        print("unbind", "解除与计划", last_schedule, "的绑定。")

                    print("state -tuitu 显示所有用户推图的状态")
                    print("edit 进入用户配置编辑模式")
                    print("screencut 进入截图小工具")
                else:
                    print("实时控制帮助")
                    print("stop [-f] 停止当前的Schedule，-f表示强制停止")
                    if last_schedule != "":
                        print("state 查看当前运行状态")
                    print("first -b (batchname) 向任务队列中增加一个batch")
                    print("first -g (groupname) (taskname) ([priority]=0) 向队列中增加组任务")
                    print("first (account) (taskname) ([priority]=0 向队列中增加账号任务")
                    print("注：上述三条指令若将first改为continue，则继续执行上次未完成的任务。")
                    print("device 查看当前设备状态")
                    print("queue 查看当前任务队列")
                    print("join [-nowait] 一直运行至队列为空，设备全部闲置后退出，设置-nowait后将忽略等待执行的任务")
                    print("join-shutdown [-nowait] 一直运行至队列为空、设备全部闲置时，关机，设置-nowait后将忽略等待执行的任务")
                    print("reconnect 重新搜索模拟器")
            elif order == "bind":
                assert SCH is None, "必须先停止正在运行的Schedule"
                assert len(cmds) == 2, "必须输入计划名称"
                BindSchedule(cmds[1])
            elif order == "unbind":
                assert SCH is None, "必须先停止正在运行的Schedule"
                UnBind()
            elif order == "first":
                if len(cmds) == 1:
                    assert SCH is None, "必须先停止正在运行的Schedule"
                    FirstSchedule()
                elif cmds[1] == "-b":
                    assert SCH is not None, "脚本未启动！"
                    assert len(cmds) == 3, "命令错误"
                    FirstBatch(cmds[2])
                elif cmds[1] == "-g":
                    assert SCH is not None, "脚本未启动！"
                    assert len(cmds) in [4, 5], "命令错误"
                    if len(cmds) == 4:
                        FirstTask(True, cmds[2], cmds[3], 0)
                    else:
                        FirstTask(True, cmds[2], cmds[3], int(cmds[4]))
                elif len(cmds) == 3:
                    assert SCH is not None, "脚本未启动！"
                    FirstTask(False, cmds[1], cmds[2], 0)
                elif len(cmds) == 4:
                    assert SCH is not None, "脚本未启动！"
                    FirstTask(False, cmds[1], cmds[2], int(cmds[3]))
                else:
                    raise Exception("命令错误")
            elif order == "continue":
                if len(cmds) == 1:
                    assert SCH is None, "必须先停止正在运行的Schedule"
                    assert last_schedule != "", "必须先绑定一个Schedule！"
                    ContinueSchedule()
                elif cmds[1] == "-b":
                    assert SCH is not None, "脚本未启动！"
                    assert len(cmds) == 3, "命令错误"
                    FirstBatch(cmds[2])
                elif cmds[1] == "-g":
                    assert SCH is not None, "脚本未启动！"
                    assert len(cmds) in [4, 5], "命令错误"
                    if len(cmds) == 4:
                        ContinueTask(True, cmds[2], cmds[3], 0)
                    else:
                        ContinueTask(True, cmds[2], cmds[3], int(cmds[4]))
                elif len(cmds) == 3:
                    assert SCH is not None, "脚本未启动！"
                    ContinueTask(False, cmds[1], cmds[2], 0)
                elif len(cmds) == 4:
                    assert SCH is not None, "脚本未启动！"
                    ContinueTask(False, cmds[1], cmds[2], int(cmds[3]))
                else:
                    raise Exception("命令错误")

            elif order == "state":
                if len(cmds) == 2 and cmds[1] == "-tuitu":
                    CheckTuitu()
                else:
                    CheckState()

            elif order == "clear":
                assert SCH is None, "必须先停止正在运行的Schedule"
                assert last_schedule != "", "需要先绑定具体的计划！"
                assert len(cmds) == 2, "需要指定具体名称"
                if cmds[1] == "-all":
                    ClearError(None)
                else:
                    ClearError(cmds[1])

            elif order == "restart":
                assert SCH is None, "必须先停止正在运行的Schedule"
                assert last_schedule != "", "需要先绑定具体的计划！"
                assert len(cmds) == 2, "需要指定具体名称"
                if cmds[1] == "-all":
                    Restart(None)
                else:
                    Restart(cmds[1])

            elif order == "edit":
                assert SCH is None, "必须先停止正在运行的Schedule"
                exec(open("CreateUser.py", "r", encoding="utf-8").read())

            elif order == "screencut":
                assert SCH is None, "必须先停止正在运行的Schedule"
                exec(open("screencut.py", "r", encoding="utf-8").read())

            elif order == "stop":
                assert SCH is not None, "脚本未启动！"
                if len(cmds) == 2 and cmds[1] == "-f":
                    StopSchedule(True)
                else:
                    StopSchedule(False)
            elif order == "device":
                assert SCH is not None, "脚本未启动！"
                CheckDevice()
            elif order == "queue":
                assert SCH is not None, "脚本未启动！"
                CheckQueue()
            elif order == "reconnect":
                assert SCH is not None, "脚本未启动！"
                ReconnectPCR()
            elif order == "join":
                assert SCH is not None, "脚本未启动！"
                if len(cmds) == 2 and cmds[1] == "-nowait":
                    JoinExit(True)
                else:
                    JoinExit(False)
            elif order == "join-shutdown":
                assert SCH is not None, "脚本未启动！"
                if len(cmds) == 2 and cmds[1] == "-nowait":
                    JoinShutdown(True)
                else:
                    JoinShutdown(False)
            else:
                print("未知的命令")
        except Exception as e:
            if trace_exception_for_debug:
                traceback.print_exc()
            print("出现错误:", e)
