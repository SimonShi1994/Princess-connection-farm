import os
from multiprocessing import Pool, Manager

import keyboard

from automator_mixins._base import Multithreading
from core import log_handler
from core.Automator import Automator
from core.emulator_port import check_known_emulators, emulator_ip
# 账号日志
from core.log_handler import pcr_log
# 临时解决方案，可以改进
from core.pcr_config import trace_exception_for_debug, end_shutdown, enable_auto_find_emulator, selected_emulator, \
    emulator_ports
from core.usercentre import list_all_users, AutomatorRecorder

acclog = log_handler.pcr_acc_log()
# 注意！目前逻辑仅支持雷电多开
all_emulators = {
    '雷电': '127.0.0.1:5554',
    '网易MUMU': '127.0.0.1:7555',
    '逍遥': '127.0.0.1:21503',
    '天天': '127.0.0.1:6555',
    '海马': '127.0.0.1:53001',
    'Genymotion': '127.0.0.1:5555',
    '谷歌原生': '不支持',
    '夜神1': '127.0.0.1:62001',
    '夜神2': '127.0.0.1:52001',
    '蓝叠': '127.0.0.1:5555',
    'BlueStacks': '127.0.0.1:5555',
    '安卓模拟器大师': '127.0.0.1:54001',
    '腾讯': '127.0.0.1:5555'
}
# 选定模拟器
selected_emulator = all_emulators[selected_emulator]


def runmain(params):
    acc = params[0]
    tas = params[1]
    queue = params[2]
    continue_ = params[3]
    max_retry = params[4]
    address = queue.get()
    try:
        # 这是一个奇妙的bug，需要在启动异步前实例化keyboard，否则暂停无法使用
        # 按住p即可堵塞
        keyboard.release('p')
        # 传递程序启动的flags
        Multithreading({}).state_sent_resume()
        a = Automator(address)
        a.init_account(acc, "users")
        a.start()
        user = a.AR.getuser()
        account = user["account"]
        password = user["password"]
        a.log.write_log("info", f"即将登陆： 用户名 {account}")  # 显然不需要输出密码啊喂！
        # a.log.server_bot("warning", f"即将登陆： 用户名 {account}")

        a.start_th()  # 提前开启异步：截的图可以给login函数使用
        a.start_async()
        # 使用协程，里面的Exception出不来
        """
        gevent.joinall([
            # 这里是协程初始化的一个实例
            gevent.spawn(a.login_auth, account, password),
            gevent.spawn(acclog.Account_Login, account),
            gevent.spawn(a.sw_init())
        ])
        """
        a.start_shuatu()
        a.login_auth(account, password)
        acclog.Account_Login(account)

        # 日志记录
        # 还是日志
        # 初始化刷图
        # 开始异步
        a.RunTasks(tas, continue_, max_retry)  # 执行主要逻辑
        """
        gevent.joinall([
            # 这里是协程的一个实例
            gevent.spawn(a.change_acc()),
            gevent.spawn(acclog.Account_Logout, account)
        ])
        """
        a.change_acc()
        acclog.Account_Logout(account)
    except Exception as e:
        if trace_exception_for_debug:
            raise e
        pcr_log(acc).write_log(level='error', message=f'initialize-检测出异常: <{type(e)}> {e}')
        try:
            a.fix_reboot(False)
        except:
            pass
    finally:
        # 停止异步
        a.stop_th()
    # 退出当前账号，切换下一个
    queue.put(address)


def connect():  # 连接adb与uiautomator
    try:
        if enable_auto_find_emulator:
            port_list = check_known_emulators()
            print("自动搜寻模拟器：" + str(port_list))
            for port in port_list:
                os.system('cd adb & adb connect ' + emulator_ip + ':' + str(port))
        if len(emulator_ports) != 0:
            for port in emulator_ports:
                os.system('cd adb & adb connect ' + emulator_ip + ':' + str(port))
        # os.system 函数正常情况下返回是进程退出码，0为正常退出码，其余为异常
        if os.system('cd adb & adb connect ' + selected_emulator) != 0:
            pcr_log('admin').write_log(level='error', message="连接模拟器失败")
            exit(1)
        if os.system('python -m uiautomator2 init') != 0:
            pcr_log('admin').write_log(level='error', message="初始化 uiautomator2 失败")
            exit(1)
    except Exception as e:
        pcr_log('admin').write_log(level='error', message='连接失败, 原因: {}'.format(e))
        exit(1)

    result = os.popen('cd adb & adb devices')  # 返回adb devices列表
    res = result.read()
    lines = res.splitlines()[0:]
    while lines[0] != 'List of devices attached ':
        del lines[0]

    del lines[0]  # 删除表头

    device_dic = {}  # 存储设备状态
    for i in range(0, len(lines) - 1):
        lines[i], device_dic[lines[i]] = lines[i].split('\t')[0:]
    lines = lines[0:-1]
    out = []
    for i in range(len(lines)):
        if device_dic[lines[i]] == 'device':
            out += [lines[i]]
    print(out)
    return out


def readjson():  # 读取账号
    # 2020-07-18 增加读取json账号
    # 等待一段时间再上限，建议将配置逻辑合并到AutomatorRecord中，调用getuser函数获取配置
    # 等刷图等逻辑合并到配置文件中后，可以弃用read()函数，runmain传参只需传入配置文件路径
    # 然后在Automator内部调用getuser获取account,password等一系列配置
    return list_all_users(0)


def execute(continue_=False, max_retry=3):
    """
    执行脚本
    :param continue_: 是否继续执行上次没执行完的脚本
    :param max_retry: 最大报错重试次数
    """
    try:
        # 连接adb与uiautomator
        devices = connect()
        # 读取账号
        all_accounts = readjson()
        # 读取任务，把有任务的账号加入队列
        accounts = []
        tasks = []
        for acc in all_accounts:
            AR = AutomatorRecorder(acc)
            user_dict = AR.getuser()
            if user_dict["taskfile"] == "":
                # 无任务，跳过
                continue
            run_status = AR.get_run_status()
            if run_status["error"] is not None:
                # 报错
                print("账号 ", acc, " 含有未解决的错误：", run_status["error"])
                continue
            elif run_status["finished"]:
                # 已经完成的
                print("账号 ", acc, " 已经完成！跳过。")
                continue
            try:
                tas = AR.gettask(user_dict["taskfile"])
            except Exception as e:
                print("账号 ", acc, " 所读取的任务文件 ", user_dict["task_file"], "有异常：", e, "跳过。")
                continue
            # 完好的账号
            tasks += [tas]
            accounts += [acc]
            print("导入任务： 账号 ", acc, " 任务 ", user_dict["taskfile"], " 进度 ", run_status["current"])

        # 这个队列用来保存设备, 初始化的时候先把所有的模拟器设备放入队列
        queue = Manager().Queue()

        # 进程池参数列表
        params = list()
        for acc, tas in zip(accounts, tasks):
            params.append((acc, tas, queue, continue_, max_retry))

        # 初始化队列, 先把所有的模拟器设备放入队列
        for device in devices:
            queue.put(device)

        # 这里是脱离了runmain的异步
        address = queue.get()
        a = Automator(address)
        # 传递程序启动的flags
        Multithreading({}).state_sent_resume()
        # 随着进程的异步
        a.program_start_async()
        # 放回address
        queue.put(address)

        # 进程池大小为模拟器数量, 保证同一时间最多有模拟器数量个进程在运行
        if trace_exception_for_debug:
            runmain(params[0])
        else:
            with Pool(len(devices)) as mp:
                mp.map(runmain, params)

        # 传递程序关闭的flags
        Multithreading({}).state_sent_pause()

        for _ in range(len(devices)):
            address = queue.get()
            a = Automator(address)
            # 关闭PCR
            a.d.app_stop("com.bilibili.priconne")
        # 退出adb
        os.system('cd adb & adb kill-server')
        pcr_log('admin').write_log(level='info', message='任务全部完成')
        pcr_log('admin').server_bot('', message='任务全部完成')
        if end_shutdown:
            os.system("shutdown -s -f -t 120")
    except Exception as e:
        if trace_exception_for_debug:
            raise e
        pcr_log("admin").write_log(level="error", message=f"execute发生了错误：{e}")
