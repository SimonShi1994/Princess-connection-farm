# coding=utf-8
import uiautomator2 as u2
import time
from utils import *
from cv import *
from Automator import *
# import matplotlib.pylab as plt
import os
import threading


def runmain(address, account, password, kickflag=0):
    # 主功能体函数
    # 请在本函数中自定义需要的功能

    a = Automator(address)
    a.start()
    print('>>>>>>>即将登陆的账号为：', account, '密码：', password, '<<<<<<<', '\r\n')
    a.login_auth(account, password)  # 注意！请把账号密码写在zhanghao.txt内
    a.init_home()  # 初始化，确保进入首页
    a.sw_init()  # 初始化刷图

    a.gonghuizhijia()  # 家园一键领取
    # a.goumaimana(1)  # 购买mana 10次
    a.mianfeiniudan()  # 免费扭蛋
    # a.mianfeishilian()  # 免费十连
    a.dianzan(sortflag=1)  # 公会点赞
    # a.hanghui()  # 行会捐赠
    a.dixiacheng()  # 地下城
    # a.goumaitili(3)  # 购买3次体力
    a.shouqurenwu()  # 收取任务
    # shuatu_auth(a, account)  # 刷图控制中心，在下一次更新前建议暂停使用本函数
    # # a.shuajingyan(10) # 刷1-1经验（自带体力购买）,10为主图
    a.shouqu()  # 收取所有礼物

    if kickflag == 1:
        a.tichuhanghui()
    a.change_acc()  # 退出当前账号，切换下一个

def invitemain(address, account, password, inviteUID):
    # 邀请入会函数，请不要更改本函数中的功能
    a = Automator(address)
    a.start()
    print('>>>>>>>即将登陆的账号为：', account, '密码：', password, '<<<<<<<', '\r\n')
    a.login_auth(account, password)  # 注意！请把账号密码写在zhanghao.txt内
    a.init_home()
    a.yaoqinghanghui(inviteUID)
    a.change_acc()  # 退出当前账号，切换下一个

def acceptmain(address, account, password):
    # 接受入会邀请函数，请不要更改本函数中的功能
    a = Automator(address)
    a.start()
    print('>>>>>>>即将登陆的账号为：', account, '密码：', password, '<<<<<<<', '\r\n')
    a.login_auth(account, password)  # 注意！请把账号密码写在zhanghao.txt内
    a.init_home()
    a.jieshouhanghui()
    a.change_acc()  # 退出当前账号，切换下一个

def connect():  # 连接adb与uiautomator
    try:
        os.system('cd adb & adb connect 127.0.0.1:5554')  # 雷电模拟器
        # os.system('adb connect 127.0.0.1:7555') #mumu模拟器
        os.system('python -m uiautomator2 init')
    except:
        print('连接失败')

    result = os.popen('cd adb & adb devices')  # 返回adb devices列表
    res = result.read()
    lines = res.splitlines()[0:]
    while lines[0]!='List of devices attached ':
        del lines[0]
    del lines[0]  # 删除表头

    device_dic = {}  # 存储设备状态
    for i in range(0, len(lines)-1):
        lines[i],device_dic[lines[i]]= lines[i].split('\t')[0:]
    lines = lines[0:-1]
    for i in range(len(lines)):
        if device_dic[lines[i]]!='device':
            del lines[i]
    print(lines)
    emulatornum = len(lines)
    return lines, emulatornum


def read(filename):  # 读取账号
    account_dic = {}
    fun_dic = {}
    fun_list = []
    with open(filename, 'r') as f:  # 注意！请把账号密码写在zhanghao.txt内
        for i, line in enumerate(f):
            line = line.rstrip("\n")
            account, password = line.split('\t')[0:2]
            fun = line.split('\t')[2:]
            account_dic[account] = password.strip()
            fun_dic[account] = str(fun).strip()
            fun_list.append(fun_dic[account])
    account_list = list(account_dic.keys())
    accountnum = len(account_list)
    return account_list, account_dic, accountnum, fun_list, fun_dic

def readauth(filename):  # 读取记有大号和会长账号的txt
    with open(filename, 'r') as f:  # 注意！请把大号和会长账号密码写在zhanghao.txt内
        line = f.readline()
        account_boss,password_boss,UID = line.split('\t')
        line = f.readline()
        account_1,password_1 = line.split('\t')[0:2]
        line = f.readline()
        account_2,password_2 = line.split('\t')[0:2]
    return (account_boss, password_boss, UID, account_1, password_1, account_2, password_2)


def shuatu_auth(a, account):  # 刷图总控制
    shuatu_dic = {
        '08': 'a.shuatu8()',
        '10': 'a.shuatu10()',
        '11': 'a.shuatu11()'
    }
    _, _, _, fun_list, fun_dic = read('zhanghao.txt')
    if fun_dic[account] == '[]':
        eval(shuatu_dic['10'])
    else:
        eval(shuatu_dic[fun_dic[account][2:4]])


# 主程序
if __name__ == '__main__':

    # 连接adb与uiautomator
    lines, emulatornum = connect()
    # 读取账号
    account_list, account_dic, accountnum, _, _ = read('40_1.txt')

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

    #读取大号和会长账号
    account_boss, password_boss, UID, account_1, password_1, account_2, password_2 = readauth()
    #执行会长1的日常任务+踢出大号
    t = threading.Thread(target=runmain, 
                         args=(lines[0], account_1, password_1, kickflag=1))
    t.start()
    t.join()
    #执行会长2的邀请大号任务
    t = threading.Thread(target=invitemain, 
                         args=(lines[0], account_2, password_2, UID))
    t.start()
    t.join()
    #执行大号的接受邀请任务
    t = threading.Thread(target=acceptmain, 
                         args=(lines[0], account_boss, password_boss))
    t.start()
    t.join()
#==============================第二轮===========================
    # 读取账号
    account_list, account_dic, accountnum, _, _ = read('40_2.txt')

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

    #执行会长2的日常任务+踢出大号
    t = threading.Thread(target=runmain, 
                         args=(lines[0], account_2, password_2, kickflag=1))
    t.start()
    t.join()
    #执行会长1的邀请大号任务
    t = threading.Thread(target=invitemain, 
                         args=(lines[0], account_1, password_1, UID))
    t.start()
    t.join()
    #执行大号的接受邀请任务
    t = threading.Thread(target=acceptmain, 
                         args=(lines[0], account_boss, password_boss))
    t.start()
    t.join()

    # 退出adb
    os.system('cd adb & adb kill-server')


