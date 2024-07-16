import datetime
import time
import subprocess
import traceback

import requests
from requests.adapters import HTTPAdapter
from rich import print as rprint

from core.constant import USER_DEFAULT_DICT as UDD
from core.emulator_port import check_known_emulators
from core.initializer import PCRInitializer, Schedule
from core.launcher import EMULATOR_DICT
from core.pcr_config import *
from core.richutils import RTitle as RError, RValue as RWarn
from core.usercentre import AutomatorRecorder, list_all_users, parse_batch, check_users_exists
from core.utils import is_ocr_running
from core.safe_u2 import run_adb


def wprint(*args, **kwargs):
    rprint(RWarn(*args, **kwargs))


def eprint(*args, **kwargs):
    rprint(RError(*args, **kwargs))


def RTrue(s):
    return f"[green]{s}[/green]"


def RFalse(s):
    return f"[red]{s}[/red]"


import cv2

PCR: Optional[PCRInitializer] = None
SCH: Optional[Schedule] = None
last_schedule = ""

script_version = "Ver 2.8.20240716"


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
        run_adb("kill-server")
        run_adb("devices")
        time.sleep(5)
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
    try:
        Schedule(schedule, None)
    except Exception as e:
        eprint(f"* 绑定Schedule[{schedule}]出现错误: {e}")
    else:
        if schedule != "":
            last_schedule = schedule
        with open("bind_schedule.txt", "w", encoding="utf-8") as f:
            f.write(schedule)
        print("Schedule绑定成功：", schedule)


def RunningInput():
    if not running_input:
        if last_schedule == "":
            wprint("* 由于没有指定schedule，running_input自动开启。")
            wprint("* 可以在添加任务后，输入join屏蔽实时控制。")
            wprint("* 输入help，查看实时控制帮助。")
        else:
            wprint("* 实时控制已屏蔽，可以在config.ini - running_input中进行设置。")
            if end_shutdown:
                eprint("* end_shutdown配置启动，全部任务结束后，将自动关机。")
                JoinShutdown()
            else:
                wprint("* 全部任务结束后，将自动退出。")
                JoinExit()
    else:
        wprint("* 实时控制已经开启，可以在config.ini - running_input中进行设置。")
        wprint("* Tips：如果出现了子进程长时间未响应的情况，请输入join或在配置中关闭running_input。")
        wprint("* 输入help，查看实时控制帮助。")


def FirstSchedule():
    global SCH, last_schedule, PCR
    if PCR is None:
        StartPCR()
    if SCH is not None:
        raise Exception("Schedule已经运行，请先关闭！")
    if auto_start_app:
        Start_App()
    SCH = Schedule(last_schedule, PCR)
    SCH.run_first_time()
    RunningInput()


def ContinueSchedule():
    global SCH, last_schedule, PCR
    if PCR is None:
        StartPCR()
    if SCH is not None:
        raise Exception("Schedule已经运行，请先关闭！")
    if auto_start_app:
        Start_App()
    SCH = Schedule(last_schedule, PCR)
    SCH.run_continue()
    RunningInput()


def GetDataCenterTime():
    from DataCenter import LoadPCRData
    try:
        data = LoadPCRData()
    except:
        return None
    if data is None:
        return None
    else:
        return datetime.datetime.fromtimestamp(data.last_update_time).strftime("%Y-%m-%d %H:%M:%S")


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
        eprint("没有绑定具体的计划文件。")
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
        eprint("没有绑定具体的计划文件。")
        return
    mysch = Schedule(last_schedule, None)
    mysch.clear_error(name)


def Restart(name):
    global last_schedule
    if last_schedule == "":
        eprint("没有绑定具体的计划文件。")
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
        eprint("还没有任何Schedule")
        return
    SCH.join(nowait)
    SCH.stop()
    sys.exit(0)


def JoinShutdown(nowait=False):
    global SCH
    if SCH is None:
        eprint("还没有任何Schedule")
        return
    SCH.join(nowait)
    SCH.stop()
    os.system("shutdown -s -f -t 120")


def ShowGuide():
    print("/docs/introduce_to_schedule.md  Schedule使用帮助")
    print("/docs/switch_guide              开关使用说明 [<New!]")
    print("/docs/如何接入打码平台.md")
    print("/equip/                         自动发起捐赠所用的样例装备")
    print("/INI文件配置解读.md               配置文件使用说明")
    print("/AboutUpdater.md                自动更新使用说明（自动更新已经很久没更新过了，可能不能使用）")
    print("/webclient/README.md            前端使用说明  (前端还不能用）")
    print("/tasks_example/                 样例任务json文件")
    print("/example_customtask/            样例自定义任务文件")


def ShowServerChan():
    print = rprint
    if s_sckey != "":
        print("* Server酱已配置！")
        print("  - 运行状态消息发送间隔(s) sentstate schedule：", sentstate)
        print("  - 日志记录过滤等级 log_lev：", log_lev)
        print("  - 日志记录最大累积条数 log_cache：", log_cache)
    else:
        print("* Server酱未配置，可前往config.ini - s_sckey进行设置")
    if qqbot_key != "":
        print("* QQbot已配置！")
        print("选择的QQbot提供商 qqbot_select：", qqbot_select)
        print("QQbot私聊你的开关 qqbot_private_send_switch：", qqbot_private_send_switch)
        print("QQbot群聊的开关 qqbot_group_send_switch：", qqbot_group_send_switch)
        print("设置发送的QQ号/群号 qq：", qq)
        print("  - 运行状态消息发送间隔(s) sentstate schedule：", sentstate)
        print("  - 日志记录过滤等级 log_lev：", log_lev)
        print("  - 日志记录最大累积条数 log_cache：", log_cache)
    else:
        print("* QQbot未配置，可前往config.ini - qqbot_key进行设置")
    if tg_token != "":
        print("* TGbot已配置！")
        print("  - 是否消息铃声静音 tg_mute：", tg_mute)
        print("  - 运行状态消息发送间隔(s) sentstate schedule：", sentstate)
        print("  - 日志记录过滤等级 log_lev：", log_lev)
        print("  - 日志记录最大累积条数 log_cache：", log_cache)
    else:
        print("* TGbot未配置，可前往config.ini - tg_token进行设置")


def ShowAutoConsole():
    print = rprint
    print("* ADB文件路径 adb_dir：", os.path.abspath(adb_dir))
    print("* 忽略端口号 ignore_serials：", ignore_serials)
    print("* 自动添加至环境变量 add_adb_to_path：", RTrue("已开启") if add_adb_to_path else RFalse("未开启"))
    print("* 使用全局adb重连 global_adb_restart", RTrue("已开启") if global_adb_restart else RFalse("未开启"))
    if emulator_console != "":
        print("* 模拟器自动控制已配置！")
        print("  - 模拟器选择 selected_emulator：", selected_emulator)
        if selected_emulator in EMULATOR_DICT:
            launcher = EMULATOR_DICT[selected_emulator]()
            print("  - 控制器所在路径 emulator_console：", emulator_console)
            print("  - 自启动模拟器编号 emulator_id：", emulator_id)
            print("  - 自动分配模拟器地址 auto_emulator_address：",
                  RTrue("已开启") if auto_emulator_address else RFalse("未开启"))
            for i in emulator_id:
                print("  - ID: ", i, " Serial:", launcher.id_to_serial(i))
            print("  - 闲置自动关闭模拟器 quit_emulator_when_free：",
                  RTrue("已开启") if quit_emulator_when_free else RFalse("未开启"))
            if quit_emulator_when_free:
                print("  - - 最大闲置时间 max_free_time：", max_free_time)
            print(" - 打开模拟器时重连adb间隔 restart_adb_during_emulator_launch_delay： ",
                  restart_adb_during_emulator_launch_delay)

        else:
            eprint(f"  !! 错误，不支持的模拟器。当前仅支持：{EMULATOR_DICT.keys()}")
    else:
        print("* 模拟器自动控制未配置，前往config.ini - emulator_console进行配置")
    if selected_emulator == "蓝叠5HyperV":
        print("* 使用模拟器：蓝叠5HyperV")
        if bluestacks5_hyperv_conf_path == "" or not os.path.exists(bluestacks5_hyperv_conf_path):
            eprint("  -  !! 当前模拟器类型为 蓝叠5HyperV，"
                   "但并未设置 bluestacks5_hyperv_conf_path 或其指向的文件不存在。")
        else:
            print("  - 蓝叠5HyperV配置文件路径：", bluestacks5_hyperv_conf_path)
    print("* 自动启动app.py auto_start_app：", RTrue("已开启") if auto_start_app else RFalse("未开启"))
    print("* 内部方式启动app：", RTrue("已开启") if inline_app else RFalse("未开启"))


def ShowOCR():
    print = rprint
    print("* 主OCR模式 ocr_mode_main：", ocr_mode_main)
    print("* 次OCR模式 ocr_mode_secondary：", ocr_mode_secondary)
    print("* 主次一致才输出：", )
    print("* 主次不一致用此OCR模式 force_primary_equals_secondary_use：", force_primary_equals_secondary_use)
    if baidu_apiKey != "":
        print("* BaiduAPI 已配置！")
    else:
        print("* BaiduAPI 未配置，前往config.ini - baidu_apiKey进行配置")
    print("* 本地OCR状态：", end="")
    if is_ocr_running():
        wprint("运行中")
    else:
        print("未运行")
    print("* 使用PCR定制专属OCR提升精确度 use_pcrocr_to_process_basic_text",
          RTrue("已开启") if use_pcrocr_to_process_basic_text else RFalse("未开启"))


def ShowPCRPerformance():
    print = rprint
    print("* 快速截图 fast_screencut：", RTrue("已开启") if fast_screencut else RFalse("未开启"))
    if fast_screencut:
        print("  - 强制快速截图 force_fast_screencut：", RTrue("已开启") if force_fast_screencut else RFalse("未开启"))
        print("  - 截图强制延迟 fast_screencut_delay：", fast_screencut_delay)
        print("  - 最长等待时间 fast_screencut_timeout：", fast_screencut_timeout)
    print("* 异步检测间隔 async_screenshot_freq：", async_screenshot_freq)
    print("  - Connecting超时等待时间 bad_connecting_time：", bad_connecting_time)
    if not disable_timeout_raise:
        print("* 图像匹配最长等待时间 lockimg_timeout：", lockimg_timeout)
    else:
        print("* 图像匹配超时报错已屏蔽")
    print("* Shift+P脚本暂停 enable_pause：", RTrue("已开启") if enable_pause else RFalse("未开启"))
    print("* 最大重启重试次数 max_reboot：", max_reboot)
    print("* 强制重启模式 force_timeout_reboot：", RTrue("已开启") if force_timeout_reboot else RFalse("未开启"))
    print("* 运行时实时控制 running_input：", RTrue("已开启") if running_input else RFalse("未开启"))
    print("* 不使用自动打码 captcha_skip：", RTrue("已开启") if captcha_skip else RFalse("未开启"))
    if not captcha_skip:
        print("  - 自动打码已启用！")
        if captcha_userstr == "":
            print("  - ！！！警告：没有输入打码平台用户名 captcha_userstr！！！")
        else:
            print("  - 已经接入打码平台 captcha_userstr！")
        print("  - 错误打码时自动申诉 captcha_senderror：", RTrue("已开启") if captcha_senderror else RFalse("未开启"))
    print("* 出现验证码后等待时间 captcha_wait_time：", captcha_wait_time)
    print("* 出现验证码后是否弹出置顶提示框 captcha_popup：", RTrue("已开启") if captcha_popup else RFalse("未开启"))
    print("* 缓存清理 clear_traces_and_cache：", RTrue("已开启") if clear_traces_and_cache else RFalse("未开启"))
    print("* 装备名称模糊搜索 enable_zhuangbei_fuzzy_search：",
          RTrue("已开启") if enable_zhuangbei_fuzzy_search else RFalse("未开启"))
    if enable_zhuangbei_fuzzy_search:
        print("  - 模糊搜索阈值 zhuangbei_fuzzy_search_cutoff：", zhuangbei_fuzzy_search_cutoff)
    print("* 账号登录模式 account_login_mode：", account_login_mode)
    print("* 切换账号失败后回退登录模式 account_login_switch_fallback：", account_login_switch_fallback)


def ShowTaskInfo():
    print = rprint
    print("* 如果有OCR版本，强制使用OCR版本的任务 force_as_ocr_as_possible：",
          RTrue("已开启") if force_as_ocr_as_possible else RFalse("未开启"))
    print("* 使用pcrocr进行Rank识别 use_pcrocr_to_detect_rank：",
          RTrue("已开启") if use_pcrocr_to_detect_rank else RFalse("未开启"))
    print("* 使用pcrocr进行主线图号识别 use_pcrocr_to_detect_zhuxian：",
          RTrue("已开启") if use_pcrocr_to_detect_zhuxian else RFalse("未开启"))
    data = GetDataCenterTime()
    if data is None:
        print("* 干炸里脊数据库版本：未找到数据库或数据库异常！请更新数据库！")
    else:
        print("* 干炸里脊数据库版本：", data)


def ShowDebugInfo():
    print = rprint
    print("* 输出Debug信息 debug：", RTrue("已开启") if debug else RFalse("未开启"))
    print("* 把debug信息记录到文件中 write_debug_to_log：", RTrue("已开启") if write_debug_to_log else RFalse("未开启"))
    print("* 忽略警告信息 ignore_warning：", RTrue("已开启") if ignore_warning else RFalse("未开启"))
    print("* 保存错误堆栈 trace_exception_for_debug:",
          RTrue("已开启") if trace_exception_for_debug else RFalse("未开启"))
    print("* 保存baiduocr的图片 baidu_ocr_img：", RTrue("已开启") if baidu_ocr_img else RFalse("未开启"))
    print("* 屏蔽图像匹配超时报错 disable_timeout_raise：",
          RTrue("已开启") if disable_timeout_raise else RFalse("未开启"))
    print("* U2指令记录队列大小 u2_record_size：", u2_record_size)
    print("* U2指令过滤列表 u2_record_filter:", u2_record_filter)
    print("* Automator指令记录队列大小 debug_record_size: ", debug_record_size)
    print("* Automator指令过滤列表 debug_record_filter: ", debug_record_filter)
    print("* 使用colorlog库输出记录 colorlogsw：", RTrue("已开启") if colorlogsw else RFalse("未开启"))
    print("* 在log中显示函数名 show_codename_in_log：", RTrue("已开启") if show_codename_in_log else RFalse("未开启"))
    print("* 在log中显示文件名 show_filename_in_log：", RTrue("已开启") if show_filename_in_log else RFalse("未开启"))
    print("* 在log中显示行数 show_linenumber_in_log：", RTrue("已开启") if show_linenumber_in_log else RFalse("未开启"))
    print("* 以下文件中的信息不显示在debug中 do_not_show_debug_if_in_these_files：", do_not_show_debug_if_in_these_files)
    print("* 打印函数名时，跳过以下文件中的函数： skip_codename_output_if_in_these_files：",
          skip_codename_output_if_in_these_files)


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
                        eprint("  - 文件缺失：", v.img)
                        BADIMG.append(v.img)
                    else:
                        if v.at is not None:
                            img = cv2.imread(v.img)
                            h, w, _ = img.shape
                            x1, y1, x2, y2 = v.at
                            hh = y2 - y1 + 1
                            ww = x2 - x1 + 1
                            if h > hh or w > ww:
                                eprint(" - AT范围错误，图片的(h,w)为", (h, w), "但给出的范围为", (hh, ww), k, v)

    print("* 检查本地图片")
    for obj in dir(constant):
        if type(constant.__dict__[obj]) is dict and not obj.startswith("__"):
            CheckDict(constant.__dict__[obj])
    if len(BADIMG) == 0:
        wprint("* 全部图片检测完毕")
    else:
        eprint("* 存在缺失的图片，脚本可能无法正常运行。")


def ShowInfo():
    print(" ============ 调试配置 =============")
    ShowDebugInfo()
    print(" ============ 任务配置 =============")
    ShowTaskInfo()
    print(" ============ Bot配置 =============")
    ShowServerChan()
    print(" ============ OCR配置 =============")
    ShowOCR()
    print(" ============ 核心内容配置 =============")
    ShowPCRPerformance()
    print(" ============ 自启动配置 =============")
    ShowAutoConsole()
    print(" ============ 检查本地资源文件 =============")
    CheckConstantImgs()


def PrintQQ():
    print("------------------------------------------")
    print("QQ: 1130884619  - 公主连结国服代码交♂流群")
    print("进群请备注你从什么地方了解本脚本！")
    print("有BUG反馈或脚本问题欢迎进群讨论！")
    print("------------------------------------------")
    print("（原作者学业繁忙中因此）脚本最近更新速度将放缓，\n"
          "很多BUG来不及修，新功能也没有时间上线……")
    print("实在忙不过来了，如果你对python稍微有点了解，欢迎加入我们一起进行开发和维护！")
    print("-  Ver3开发 （随便会点vue/antdesign/flask)")
    print("-  完善使用教程（会用本脚本就行）")
    print("-  图号录入人 （每次更新时将坐标和相关图片录入即可）")
    print("-  BOT人 （有机器人推送、交互经验）")
    print("-  基础脚本开发和维护 （随便懂点基础python语法）")
    print("-  全自动养号向脚本开发和维护（会python最好再会点CV）")


def Start_App():
    if is_ocr_running():
        wprint("app 已经启动！")
        return
    if not inline_app:
        subprocess.Popen([sys.executable, "app.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        subprocess.Popen([sys.executable, "app.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("正在等待app启动完毕……")
    import time
    start_time = time.time()
    while time.time() - start_time <= 60:
        if is_ocr_running():
            print("app启动完毕！")
            return
    eprint("app可能启动失败。")
    wprint("！你可以尝试手动python app.py，检查是否缺少相关依赖。")
    wprint("  requirements.txt中含有四种OCR，但均被注释，你可以选择你需要的OCR依赖取消其注释，然后重新安装依赖。")
    wprint("  你也可以根据app.py给出的错误提示，使用pip install (依赖模块）来手动安装缺失的依赖。")
    wprint("  确认依赖安装无误后，尝试重新启动main_new.py。")
    wprint("！如果app.py的依赖无误，但仍然无法链接，如果你开着全局VPN，尝试关闭再试一次。")


def get_arg(argv, key, default):
    for ind, a in enumerate(argv):
        if a == key:
            return argv[ind + 1]
    return default


def has_arg(argv, key, default):
    for ind, a in enumerate(argv):
        if a == key:
            return True
    return default


if __name__ == "__main__":
    CheckConstantImgs()
    GetLastSchedule()
    argv = sys.argv
    # 自启动app
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
        try:
            s = requests.Session()
            s.mount('http://', HTTPAdapter(max_retries=2))
            s.mount('https://', HTTPAdapter(max_retries=2))
            # sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gb18030')  # 改变标准输出的默认编码
            api_url = f"https://api.github.com/repos/SimonShi1994/Princess-connection-farm/commits/{trace_tree}"
            all_info = s.get(api_url, timeout=5)
            if all_info.status_code == 403:
                update_info = "最新版本为 {请求频繁，当前无法连接到github！请休息2分钟后再试}"
            elif all_info.status_code == 200:
                all_info = all_info.json()
                new_time = all_info["commit"].get("committer").get("date")
                new_messages = all_info["commit"].get("message")
                update_info = f"{trace_tree}分支最新版本为 {new_time} -> 更新内容为 {new_messages}"
            else:
                update_info = "最新版本为 {当前无法连接到github！}"
        except:
            update_info = "最新版本为 {当前无法连接到github！}"

        print("------------- 用户脚本控制台 --------------")
        rprint(f"当前版本为 {script_version}")
        rprint(update_info)
        print("----------------------------------------")
        print("init 初始化模拟器环境      ")
        print("app 启动app.py", end=" ")
        print("[自启动：", "已开启" if auto_start_app else "未开启", "]", end=" ")
        print("[内部模式：", "已开启" if inline_app else "未开启", "]")
        print("help 查看帮助                   exit 退出")
        print("info 查看配置信息               guide 教程")
        print("edit 进入编辑模式                  qq QQ群")
        print("data 进入数据中心                 img 图坐标添加工具")
        print("adb 执行adb命令")
        print("screencut 截屏小工具")
        print("By TheAutumnOfRice")
        print("----------------------------------------")
        wprint("提示： config.ini会在启动main_new后自动生成或更新，如果修改了config.ini，重启程序后生效。")
        if end_shutdown:
            if not running_input:
                eprint("警告： 你设置了自动关机（end_shutdown）脚本运行结束后，会强制自动关机！")
            else:
                wprint(
                    "提示： 你设置了自动关机（end_shutdown），但开启了实时控制（running_input），所以除非手动输入join-shutdown，并不会自动关机。")
        if force_as_ocr_as_possible:
            wprint("提示： 你正在强制OCR模式下运行(force_as_ocr_as_possible)，app必须开启！")
        else:
            eprint(
                "警告： 你没有开启强制OCR模式(force_as_ocr_as_possible),目前基本上所有的非OCR版本都很难用了，请尽量使用OCR模式！")
        if clear_traces_and_cache:
            eprint(
                "警告： 你正在PCR干净模式下运行(clear_traces_and_cache)，这会导致退出账号后自动清理缓存，这将有利于减少验证码，但大大增加进号过剧情所用时间！")
        if enable_auto_find_emulator:
            eprint(
                "警告： 你开起了自动寻找模拟器（enable_auto_find_emulator），这会大大增加模拟器寻找时间。如果不想使用模拟器混搭，不需要开启该项。")
        if fast_screencut:
            eprint(
                "警告： 你正在快速截图（fast_screencut）模式下运行，这会大大增加截图速度，但可能降低脚本稳定性。如果出现奇怪的脚本错乱，试试关闭快速截图。")
        else:
            wprint("提示： 你没有开启快速截图（fast_screencut），这使得截图速度大大降低，但能确保稳定性提升。")
        if not captcha_skip:
            wprint("提示： 自动过验证码（captcha_skip）已经启用，输入info查看更多配置信息！")
        else:
            wprint("提示： 你没有开启自动过验证码（captcha_skip），如果出现验证码，需要手动点掉！")
        if not trace_exception_for_debug:
            wprint(
                "提示： 你没有打开错误追踪(trace_exception_for_debug)，这将不会在出错后显示错误位置，如果需要反馈错误，请打开该选项！")
        if emulator_console != "":
            wprint("提示： 你启用了模拟器自动控制（emulator_console），如果想要关闭，可以将该项字符串清空。")
        if enable_pause:
            eprint("警告： 你开起了全局的暂停控制（enable_pause），你在任何窗口按下Shift+P都可能导致脚本的暂停！")
        if running_input:
            eprint("警告： 你开起了运行时控制（running_input），虽然它功能强大又极其方便，但可能导致如果不按回车键脚本就不运行的情况！"
                   "但你仍可以随时输入join来避免这种状况。")
        DataCenterTime = GetDataCenterTime()
        if DataCenterTime is None:
            eprint("警告： 干炸里脊数据库异常或不存在，请进入数据中心data，然后输入update更新数据库！")
        print('----------------------------------------')
        if DataCenterTime is not None:
            rprint("干炸里脊数据库更新时间：", DataCenterTime)
        if last_schedule != "":
            rprint("当前绑定计划：", RWarn(last_schedule))
            error_schedules = Schedule(last_schedule, None).get_error_schedules()
            if len(error_schedules) > 0:
                eprint('----------------------------------------')
                eprint("警告：上次运行中存在未处理的错误，这将导致相关任务不会被运行！")
                eprint("更多关于异常处理的信息请移步docs/introduce_to_schedule.md中的2.4节进行了解。")
                eprint('----------------------------------------')
    while True:
        try:
            cmd = input(f"Main[{last_schedule}]> ")
            cmds = cmd.split(" ")
            order = cmds[0]
            if order == "info":
                ShowInfo()
            elif order == "guide":
                ShowGuide()
            elif order == "break":
                break
            elif order == "adb":
                run_adb(f'{cmd[3:]}', use_os_instead_of_subprocess=True)
            elif order == "init":
                emulator_ip = "127.0.0.1"
                if enable_auto_find_emulator:
                    port_list = set(check_known_emulators())
                    if sys.platform == "win32":
                        os.system("taskkill /im adb.exe /f")
                    else:
                        os.system("pkill adb")
                    # print(port_list)
                    print("自动搜寻模拟器：" + str(port_list))
                    for port in port_list:
                        run_adb(f'connect {emulator_ip}:{str(port)}')
                else:
                    run_adb("start-server")
                    if selected_emulator == "蓝叠5HyperV":
                        if bluestacks5_hyperv_conf_path == "" or not os.path.exists(bluestacks5_hyperv_conf_path):
                            print("当前模拟器类型为 蓝叠5HyperV，"
                                  "但并未设置 bluestacks5_hyperv_conf_path 或其指向的文件不存在。")
                        else:
                            conf = open(bluestacks5_hyperv_conf_path)
                            line = conf.readline()
                            port = -1
                            conf_key = "bst.instance.Nougat64.status.adb_port"
                            while line:
                                if not line.startswith(conf_key):
                                    line = conf.readline()
                                    continue
                                port = int(line[len(conf_key) + 2:len(line) - 2])
                                break
                            conf.close()
                            if port == -1:
                                print("未能从 bluestacks5_hyperv_conf_path 中读取到模拟器端口。")
                            else:
                                run_adb(f'connect {emulator_ip}:{str(port)}')
                    else:
                        for port in emulator_ports:
                            run_adb(f"connect {emulator_ip}:{str(port)}")

                os.system('python -m uiautomator2 init')
                # os.system(f"cd batches & ren *.txt *.json")
                # os.system(f"cd groups & ren *.txt *.json")
                # os.system(f"cd schedules & ren *.txt *.json")
                # os.system(f"cd tasks & ren *.txt *.json")
                # os.system(f'cd users & for /r %a in (*.txt) do ren "%a" "%~na.json"')
                if os.system('python -m uiautomator2 init') != 0:
                    # pcr_log('admin').write_log(level='error', message="初始化 uiautomator2 失败")
                    print("初始化 uiautomator2 失败,请检查是否有模拟器没有安装上ATX")
                    exit(1)
                else:
                    print("初始化 uiautomator2 或许成功，请自行打开模拟器内的ATX APP（小黄车）查看组件工作是否正常")
                    run_adb("kill-server")
            elif order == "app":
                Start_App()
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
                        print("clear (name) 清除计划", last_schedule,
                              "中名为Name的子计划的错误，name设置为-all时，全部清除。")
                        print("restart (name) 清除计划", last_schedule,
                              "中名为Name的子计划的运行记录，name设置为-all时，全部清除。")
                        print("unbind", "解除与计划", last_schedule, "的绑定。")

                    print("state -tuitu 显示所有用户推图的状态")
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
                    print(
                        "join-shutdown [-nowait] 一直运行至队列为空、设备全部闲置时，关机，设置-nowait后将忽略等待执行的任务")
                    print("reconnect 重新搜索模拟器")
                    print("以下device_id若不指定，默认将信息发给全部Device。device_id可通过device命令查看，为整数。")
                    if enable_pause:
                        print("<Shift+P> 暂停/继续 (关闭enable_pause，可以使用命令暂停/继续某一个指定device）")
                    else:
                        print("pause/resume [-d (device_id)] 暂停/继续 （开启enable_pause，可以用热键暂停device）")
                        print("pause_after_task [-d (device_id)] 在当前任务结束后暂停任务")
                    print("task [-d (device_id)] 查看某个device当前的task列表")
                    print("skip [-d (device_id)] [-t (task_id)] 跳过当前任务；若指定-t，则跳转到指定任务（通过task查看ID）")
                    print("restarttask [-d (device_id)] 重开当前任务")
                    print("!!!________FOR DEBUG________!!!")
                    # print("last_screen [-d (device_id)] 监视某一个设备的最后一次截图")
                    print("u2rec [-d (device_id)] 查看某个device的u2运行记录")
                    print("rec [-d (device_id)] [-r] 查看某个device的Automator运行记录,-r只查看running的记录。")
                    print(
                        "debug (on/off) [-d (device_id)] [-m (module_name)] 打开/关闭某个设备的调试显示，-m可指定某一个模块，默认为全部模块。")
                    print("debug show [-d (device_id)] 显示某一个设备的每个模块的调试启动状况。")
                    print("exec [-d (device_id)] [-f (script_file)] 进入python命令调试模式，若指定-f，则执行某一文件。")
            elif order == "qq":
                PrintQQ()
            elif order == "task":
                assert SCH is not None, "当前无运行的Schedule！"
                argv = cmds[1:]
                device_id = get_arg(argv, "-d", None)
                if device_id is not None:
                    device = SCH.pcr.devices.get_device_by_id(device_id)
                else:
                    device = None
                SCH.pcr.show_task_index(device)
            elif order == "u2rec":
                assert SCH is not None, "当前无运行的Schedule！"
                argv = cmds[1:]
                device_id = get_arg(argv, "-d", None)
                if device_id is not None:
                    device = SCH.pcr.devices.get_device_by_id(device_id)
                else:
                    device = None
                SCH.pcr.show_u2_record(device)
            elif order == "rec":
                assert SCH is not None, "当前无运行的Schedule！"
                argv = cmds[1:]
                device_id = get_arg(argv, "-d", None)
                running_mode = has_arg(argv, "-r", False)
                if device_id is not None:
                    device = SCH.pcr.devices.get_device_by_id(device_id)
                else:
                    device = None
                SCH.pcr.show_debug_record(running_mode, device)
            elif order == "skip":
                assert SCH is not None, "当前无运行的Schedule！"
                argv = cmds[1:]
                device_id = get_arg(argv, "-d", None)
                if device_id is not None:
                    device = SCH.pcr.devices.get_device_by_id(device_id)
                else:
                    device = None
                to_id = get_arg(argv, "-t", None)
                if to_id is not None:
                    to_id = int(to_id)
                SCH.pcr.skip_task(to_id, device)

            elif order == "restarttask":
                assert SCH is not None, "当前无运行的Schedule！"
                argv = cmds[1:]
                device_id = get_arg(argv, "-d", None)
                if device_id is not None:
                    device = SCH.pcr.devices.get_device_by_id(device_id)
                else:
                    device = None

                SCH.pcr.restart_task(device)
            elif order == "pause":
                assert SCH is not None, "当前无运行的Schedule！"
                argv = cmds[1:]
                device_id = get_arg(argv, "-d", None)
                if device_id is not None:
                    device = SCH.pcr.devices.get_device_by_id(device_id)
                else:
                    device = None
                SCH.pcr.set_freeze(True, device)
            elif order == "pause_after_task":
                assert SCH is not None, "当前无运行的Schedule！"
                argv = cmds[1:]
                device_id = get_arg(argv, "-d", None)
                if device_id is not None:
                    device = SCH.pcr.devices.get_device_by_id(device_id)
                else:
                    device = None
                SCH.pcr.pause_after_task(device)
            elif order == "resume":
                assert SCH is not None, "当前无运行的Schedule！"
                argv = cmds[1:]
                device_id = get_arg(argv, "-d", None)
                if device_id is not None:
                    device = SCH.pcr.devices.get_device_by_id(device_id)
                else:
                    device = None
                SCH.pcr.set_freeze(False, device)

            elif order == "debug":
                assert SCH is not None, "当前无运行的Schedule！"
                assert len(cmds) >= 2, "输入错误！"
                argv = cmds[2:]
                device_id = get_arg(argv, "-d", None)
                if device_id is not None:
                    device = SCH.pcr.devices.get_device_by_id(device_id)
                else:
                    device = None
                if cmds[1] == "on":
                    module_name = get_arg(argv, "-m", "__all__")
                    SCH.pcr.start_debug(True, module_name, device)
                elif cmds[1] == "off":
                    module_name = get_arg(argv, "-m", "__all__")
                    SCH.pcr.start_debug(False, module_name, device)
                elif cmds[1] == "show":
                    SCH.pcr.show_all_module_debug(device)
            elif order == "exec":
                assert SCH is not None, "当前无运行的Schedule！"
                argv = cmds[1:]
                device_id = get_arg(argv, "-d", None)
                if device_id is not None:
                    device = SCH.pcr.devices.get_device_by_id(device_id)
                else:
                    device = None
                script_file = get_arg(argv, "-f", None)
                if script_file is not None:
                    SCH.pcr.exec_script(script_file, device)
                else:
                    print("--------- EXEC调试模式 ----------")
                    print("直接输入 回车 : 退出调试模式")
                    print("输入其它： 会像指定的设备发送exec指令")
                    print("绑定设备：", "全部" if device is None else device)
                    print("--------------------------------")
                    while True:
                        cmd = input("")
                        if cmd == "":
                            break
                        else:
                            SCH.pcr.exec_command(cmd, device)

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
            elif order == "data":
                assert SCH is None, "必须先停止正在运行的Schedule"
                exec(open("DataCenter.py", "r", encoding="utf-8").read())
            elif order == "img":
                assert SCH is None, "必须先停止正在运行的Schedule"
                exec(open("img_helper.py", "r", encoding="utf-8").read())
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
            elif order == "exit":
                break
            else:
                eprint("未知的命令")
        except Exception as e:
            if trace_exception_for_debug:
                traceback.print_exc()
            eprint("出现错误:", e)
