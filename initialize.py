import os
import re
from multiprocessing import Pool, Manager

import gevent

from core import log_handler
from core.Automator import Automator

# 账号日志
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
    address = queue.get()

    a = Automator(address, account)
    a.start()
    a.log.write_log(level='info', message='>>>>>>>即将登陆的账号为：%s 密码：%s <<<<<<<\n' % (account, password))
    gevent.joinall([
        # 这里是协程初始化的一个实例
        gevent.spawn(a.login_auth, account, password),
        gevent.spawn(acclog.Account_Login, account),
        gevent.spawn(a.sw_init())
    ])
    # 异步初始化
    # 日志记录
    # 初始化刷图
    tasks(a)

    gevent.joinall([
        # 这里是协程的一个实例
        gevent.spawn(a.change_acc()),
        gevent.spawn(acclog.Account_Logout, account)
    ])
    # 退出当前账号，切换下一个
    queue.put(address)


def connect():  # 连接adb与uiautomator
    try:
        # os.system 函数正常情况下返回是进程退出码，0为正常退出码，其余为异常
        if os.system('cd adb & adb connect ' + selected_emulator) != 0:
            print("连接模拟器失败")
            exit(1)
        if os.system('python -m uiautomator2 init') != 0:
            print("初始化 uiautomator2 失败")
            exit(1)
    except Exception as e:
        print('连接失败, 原因: {}'.format(e))
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


def shuatu_auth(account, fun):  # 刷图总控制
    shuatu_dic = {
        '08': 'a.shuatu8()',
        '10': 'a.shuatu10()',
        '11': 'a.shuatu11()'
    }
    if len(fun) < 2:
        return False
    tu_hao = fun[0:2]
    if tu_hao in shuatu_dic:
        print("账号{}将要捐赠".format(account))
        return True
    else:
        print("账号{}的图号填写有误，请检查zhanghao.txt里的图号，图号应为两位数字，该账号将不捐赠".format(account))
        return False


def read_account(filename):  # 读取账号
    account_dic = {}
    fun_dic = {}
    fun_list = []
    pattern = re.compile('\\s*(.*?)[\\s-]+([^\\s-]+)[\\s-]*(.*)')
    with open(filename, 'r') as f:  # 注意！请把账号密码写在zhanghao.txt内
        for line in f:
            result = pattern.findall(line)
            if len(result) != 0:
                account, password, fun = result[0]
            else:
                continue
            if not shuatu_auth(account, fun):
                continue
            account_dic[account] = password
            fun_dic[account] = fun
            fun_list.append(fun_dic[account])
    account_list = list(account_dic.keys())
    accountnum = len(account_list)
    return account_list, account_dic, accountnum, fun_list, fun_dic


def execute(account_filename, tasks):
    """
    执行脚本
    """
    # 连接adb与uiautomator
    devices = connect()
    # 读取账号
    account_list, account_dic, accountnum, _, _ = read_account(account_filename)

    # 这个队列用来保存设备, 初始化的时候先把所有的模拟器设备放入队列
    queue = Manager().Queue()

    # 进程池参数列表
    params = list()
    for account, password in account_dic.items():
        params.append((account, password, queue, tasks))

    # 初始化队列, 先把所有的模拟器设备放入队列
    for device in devices:
        queue.put(device)

    # 进程池大小为模拟器数量, 保证同一时间最多有模拟器数量个进程在运行
    with Pool(len(devices)) as mp:
        mp.map(runmain, params)

    # 退出adb
    os.system('cd adb & adb kill-server')
