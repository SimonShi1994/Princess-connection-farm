# coding=utf-8
import uiautomator2 as u2
import time
from utils import *
from cv import *
from Automator import *
# import matplotlib.pylab as plt
import os
import threading
import log_handler
import re
import random
import asyncio
import gevent

LOG().log_init()  # 初始化日志 new


# 多线程异步
class Multithreading(threading.Thread):
    """
    a 为连接Automator
    ac 为账号
    fun 为Automator中功能函数
    th_id 为线程id
    th_name 为线程名
    BY:CyiceK
    """

    def __init__(self, a, ac, fun, th_id, th_name):
        threading.Thread.__init__(self)
        self.th_id = th_id
        self.th_name = th_name
        self.a = a
        self.fun = fun
        self.account = ac
        pass

    def run(self):
        run_func(self.th_name, self.a, self.fun)

    pass


exitFlag = 0


def run_func(th_name, a, fun):
    if exitFlag:
        th_name.exit()
        pass
    else:
        do(th_name, a, fun)
        pass
    pass


# 自定义，在此定义你要运行的参数
# 2020.7.11 已封装
def do(th_name, a, fun):
    # print(fun)
    tmp = 'asyncio.run(%s)' % fun
    eval(tmp)
    # 异步
    pass


def _async(a, account, fun, sync=False):
    th = Multithreading(a, account, fun, account, "pack_Thread-" + str(account))
    # id, name
    th.start()
    if sync:
        # 线程同步异步开关，True/False
        th.join()
        # 线程等待，执行完才能进入下一个线程
        pass
    else:
        # 异步，推荐
        pass
    pass


def runmain(address, account, password):
    # 主功能体函数
    # 请在本函数中自定义需要的功能

    a = Automator(address, account)
    a.start()
    print('>>>>>>>即将登陆的账号为：', account, '密码：', password, '<<<<<<<', '\r\n')
    gevent.joinall([
        # 这里是协程初始化的一个实例
        gevent.spawn(Multithreading, a, _, _, _, _),
        gevent.spawn(a.login_auth, account, password),
        gevent.spawn(LOG().Account_Login, account),
        gevent.spawn(a.sw_init())
    ])
    # 异步初始化
    # 注意！请把账号密码写在zhanghao.txt内
    # 日志记录
    # 初始化刷图
    a.init_home()  # 初始化，确保进入首页

    # _async(a, account, 'a.juqingtiaoguo()', sync=False)  # 异步剧情跳过
    # _async(a, account, 'a.bad_connecting()', sync=False)  # 异步异常处理

    a.gonghuizhijia()  # 家园一键领取
    a.goumaimana(1)  # 购买mana 10次
    a.mianfeiniudan()  # 免费扭蛋
    # a.mianfeishilian()  # 免费十连
    a.shouqu()  # 收取所有礼物
    a.dianzan(sortflag=1)  # 公会点赞，sortflag=1表示按战力排序
    a.dixiacheng(skip=True)  # By:Dr-Bluemond, 地下城 skip是否开启战斗跳过
    # a.goumaitili(3)  # 购买3次体力
    # a.buyExp() # 买药
    # a.doActivityHard() # 刷活动hard
    # a.do1to3Hard() # 刷hard 4-1图, 需已开Hard 4-1
    # a.do11to3Hard() # 刷hard 11-3图，需已开Hard 11图
    a.shouqurenwu()  # 收取任务
    ok = shuatu_auth(a, account)  # 刷图控制中心
    if ok:  # 仅当刷图被激活(即注明了刷图图号)的账号执行行会捐赠，不刷图的认为是mana号不执行行会捐赠。
        a.hanghui()  # 行会捐赠
    else:  # 刷图没有被激活的可以去刷经验
        # a.goumaitili(times=3)  # 购买times次体力
        # a.shuajingyan(map=3)  # 刷1-1经验,map为主图
        pass
    a.shouqurenwu()  # 二次收取任务

    gevent.joinall([
        # 这里是协程的一个实例
        gevent.spawn(a.change_acc()),
        gevent.spawn(LOG().Account_Logout, account)
    ])
    # 退出当前账号，切换下一个


def connect():  # 连接adb与uiautomator
    try:
        # os.system 函数正常情况下返回是进程退出码，0为正常退出码，其余为异常
        # 雷电模拟器
        if os.system('cd adb & adb connect 127.0.0.1:5554') != 0:
            print("连接模拟器失败")
            exit(1)
        # os.system('cd adb & adb connect 127.0.0.1:7555') #mumu模拟器
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
    emulatornum = len(lines)
    return lines, emulatornum


def read():  # 读取账号
    account_dic = {}
    fun_dic = {}
    fun_list = []
    pattern = re.compile('\\s*(.*?)[\\s-]+([^\\s-]+)[\\s-]*(.*)')
    with open('zhanghao.txt', 'r') as f:  # 注意！请把账号密码写在zhanghao.txt内
        for line in f:
            result = pattern.findall(line)
            if len(result) != 0:
                account, password, fun = result[0]
            else:
                continue
            account_dic[account] = password
            fun_dic[account] = fun
            fun_list.append(fun_dic[account])
    account_list = list(account_dic.keys())
    accountnum = len(account_list)
    return account_list, account_dic, accountnum, fun_list, fun_dic


def shuatu_auth(a, account):  # 刷图总控制
    shuatu_dic = {
        '08': 'a.shuatu8()',
        '10': 'a.shuatu10()',
        '11': 'a.shuatu11()'
    }
    _, _, _, fun_list, fun_dic = read()
    if len(fun_dic[account]) < 2:
        print("账号{}不刷图".format(account))
        return False
    tu_hao = fun_dic[account][0:2]
    if tu_hao in shuatu_dic:
        print("账号{}将刷{}图".format(account, tu_hao))
        eval(shuatu_dic[tu_hao])
        return True
    else:
        print("账号{}的图号填写有误，请检查zhanghao.txt里的图号，图号应为两位数字，该账号将不刷图".format(account))
        return False



# 主程序
if __name__ == '__main__':

    # 连接adb与uiautomator
    lines, emulatornum = connect()
    # 读取账号
    account_list, account_dic, accountnum, _, _ = read()

    # 多线程执行
    count = 0  # 完成账号数
    thread_list = []
    # 完整循环 join()方法确保完成后再进行下一次循环
    for i in range(int(accountnum / emulatornum)):  # 完整循环 join()方法确保完成后再进行下一次循环
        for j in range(emulatornum):
            t = threading.Thread(target=runmain, args=(
                lines[j], account_list[i * emulatornum + j], account_dic[account_list[i * emulatornum + j]]))
            thread_list.append(t)
            count += 1
        for t in thread_list:
            t.start()
        for t in thread_list:
            t.join()
        thread_list = []
    # 剩余账号
    i = 0
    while count != accountnum:
        t = threading.Thread(target=runmain,
                             args=(lines[i], account_list[count], account_dic[account_list[count]]))
        thread_list.append(t)
        i += 1
        count += 1
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()

    # 退出adb
    os.system('cd adb & adb kill-server')
