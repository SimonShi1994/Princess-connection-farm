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

# 仅适用于zhanghao.txt里面的帐号，可以判断是农场号，还是要捐装备的号
# 根据zhanghao.txt里边的帐号是否有标注图号（也就是第三个参数）来确定是不是捐装备的号
# 如果是农场号就没有动作，如果是要捐装备的号就登录游戏捐装备

def runmain(address, account, password):
    # 主功能体函数，可以在本函数中自定义需要的功能
    # 但是在这个py文件里不需要自定义，因为这是专门用来做捐赠工作的

    a = Automator(address, account)
    log = log_handler.LOG()#初始化日志
    a.start()
    print('>>>>>>>即将执行的账号为：', account, '密码：', password, '<<<<<<<', '\r\n')
    
    zhuangbeihao = shuatu_auth(a, account)  # 刷图控制中心，此处仅仅只用来判断是不是装备号，如果是装备号也不会刷图
    if zhuangbeihao:  # 仅注明了刷图图号的账号执行行会捐赠
        a.login_auth(account, password)  # 注意！请把账号密码写在zhanghao.txt内
        log.Account_Login(account)
        a.init_home()  # 初始化，确保进入首页
        a.sw_init()  # 初始化刷图
        a.hanghui()  # 行会捐赠
        a.change_acc()  # 退出当前账号，切换下一个
    else:   #不是送装备的号什么也不干，也不用登陆
        pass

    log.Account_Logout(account)

def connect():  # 连接adb与uiautomator
    try:
        os.system('cd adb & adb connect 127.0.0.1:5554')  # 雷电模拟器
        # os.system('cd adb & adb connect 127.0.0.1:7555') #mumu模拟器
        os.system('python -m uiautomator2 init')
    except:
        print('连接失败')

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
        print("账号{}不用捐赠\n".format(account))
        return False
    tu_hao = fun_dic[account][0:2]
    if tu_hao in shuatu_dic:
        print("账号{}将要捐赠\n".format(account))
        return True
    else:
        print("账号{}的图号填写有误，请检查zhanghao.txt里的图号，图号应为两位数字，该账号将不捐赠".format(account))
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
