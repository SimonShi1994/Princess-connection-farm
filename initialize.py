import os
import re
from multiprocessing import Pool, Manager

import gevent

from core import log_handler
from core.Automator import Automator
from automator_mixins._async import AsyncMixin

# 临时解决方案，可以改进
from automator_mixins._shuatu import operation_dic

# 账号日志
from core.log_handler import pcr_log

acclog = log_handler.pcr_acc_log()
# 雷电模拟器
ld_emulator = '127.0.0.1:5554'
# Mumu模拟器
mumu_emulator = '127.0.0.1:7555'
# 选定模拟器
selected_emulator = ld_emulator


def runmain(params):
    account = params[0]
    password = params[1]
    queue = params[2]
    tasks = params[3]
    opcode = params[4]
    address = queue.get()
    try:
        a = Automator(address, account)
        a.start()
        a.log.write_log(level='info', message='>>>>>>>即将登陆的账号为：%s 密码：%s <<<<<<<' % (account, password))
        gevent.joinall([
            # 这里是协程初始化的一个实例
            gevent.spawn(a.login_auth, account, password),
            gevent.spawn(acclog.Account_Login, account),
            gevent.spawn(a.sw_init())
            ])
        # 日志记录
        # 还是日志
        # 初始化刷图
        # 开始异步
        AsyncMixin().start_th()

        tasks(a, account, opcode)

        gevent.joinall([
            # 这里是协程的一个实例
            gevent.spawn(a.change_acc()),
            gevent.spawn(acclog.Account_Logout, account)
        ])
        # 停止异步
        AsyncMixin().stop_th()
    except Exception as e:
        pcr_log(account).write_log(level='error', message='initialize-检测出异常{}'.format(e))
    finally:
        # 退出当前账号，切换下一个
        queue.put(address)


def connect():  # 连接adb与uiautomator
    try:
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
    for i in range(len(lines)):
        if device_dic[lines[i]] != 'device':
            del lines[i]
    print(lines)
    return lines


def can_shuatu(opcode):
    return True if len(opcode) >= 3 else False


def is_valid_operation_code(acc_name, opcode):  # 刷图总控制
    if len(opcode) == 0:
        pcr_log(acc_name).write_log(level='info', message="账号{}不刷图".format(acc_name))
        return True
    if len(opcode) % 3 != 0:
        pcr_log(acc_name).write_log(level='error', message="账号{}的图号填写有误，请检查zhanghao.txt里的图号，图号应为三位字符".format(acc_name))
        return False
    for i in range(0, len(opcode), 3):
        if opcode[i:i + 3] in operation_dic:
            pcr_log(acc_name).write_log(level='info', message="账号{}将刷{}图".format(acc_name, opcode[i:i + 3]))
        else:
            pcr_log(acc_name).write_log(level='error', message="账号{}的图号填写有误，请检查zhanghao.txt里的图号，图号应为三位字符".format(acc_name))
            return False
    return True


def readjson():  # 读取账号
    # 2020-07-18 增加读取json账号
    # 等待一段时间再上限，建议将配置逻辑合并到AutomatorRecord中，调用getuser函数获取配置
    # 等刷图等逻辑合并到配置文件中后，可以弃用read()函数，runmain传参只需传入配置文件路径
    # 然后在Automator内部调用getuser获取account,password等一系列配置
    return list_all_users()


def read_account(filename):  # 读取账号
    acc_dic = {}  # acc_name:acc_pwd
    opcode_dic = {}  # acc_name:operation_code
    pattern = re.compile('\\s*(.*?)[\\s-]+([^\\s-]+)[\\s-]*(.*)')
    with open(filename, 'r') as f:  # 注意！请把账号密码写在zhanghao.txt内
        for line in f:
            result = pattern.findall(line)
            if len(result) == 0:
                continue
            acc_name, acc_pwd, opcode = result[0]

            # 检查刷图号
            if not is_valid_operation_code(acc_name, opcode):
                continue
            acc_dic[acc_name] = acc_pwd
            opcode_dic[acc_name] = opcode
    return acc_dic, opcode_dic


def execute(account_filename, tasks,  acc_filter=None):
    """
    执行脚本
    """
    # 连接adb与uiautomator
    devices = connect()
    # 读取账号
    account_dic, opcode_dic = read_account(account_filename)
    # 过滤账号
    if acc_filter != None:
        account_dic = acc_filter(account_dic, opcode_dic)
        
    # 这个队列用来保存设备, 初始化的时候先把所有的模拟器设备放入队列
    queue = Manager().Queue()

    # 进程池参数列表
    params = list()
    for account, password in account_dic.items():
        opcode = opcode_dic[account]
        params.append((account, password, queue, tasks, opcode))

    # 初始化队列, 先把所有的模拟器设备放入队列
    for device in devices:
        queue.put(device)

    # 进程池大小为模拟器数量, 保证同一时间最多有模拟器数量个进程在运行
    with Pool(len(devices)) as mp:
        mp.map(runmain, params)

    # 退出adb
    os.system('cd adb & adb kill-server')
    pcr_log('admin').write_log(level='info', message='任务全部完成')
    pcr_log('admin').server_bot('', message='任务全部完成')
