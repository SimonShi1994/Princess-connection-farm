# coding=utf-8
import os
import re
import threading

from core.Automator import *

# 初始号加入指定行会函数
'''
1. 创建两个行会，设置成任何人都可以加入
2. 在本程序中把clubname1和clubname2分别改成两个行会的名字
3. 在40_1.txt中输入要加入行会1的账号，40_2.txt中输入要加入行会2的账号
4. 运行本程序
'''

clubname1 = '行会1的名字，请自行修改'
clubname2 = '行会2的名字，请自行修改'


def runmain(address, account, password, clubname):
    # 主功能体函数
    # 请在本函数中自定义需要的功能

    a = Automator(address, account)
    a.start()
    print('>>>>>>>即将登陆的账号为：', account, '密码：', password, '<<<<<<<', '\r\n')
    a.login_auth(account, password)  # 注意！请把账号密码写在zhanghao.txt内
    a.init_home()  # 初始化，确保进入首页

    a.joinhanghui(clubname)  # 加入行会

    a.change_acc()  # 退出当前账号，切换下一个


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


def read(filename):  # 读取账号
    account_dic = {}
    fun_dic = {}
    fun_list = []
    pattern = re.compile('\\s*(.*?)[\\s-]+([^\\s-]+)[\\s-]*(.*)')
    with open(filename, 'r') as f:
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
                lines[j], account_list[i * emulatornum + j], account_dic[account_list[i * emulatornum + j]], clubname1))
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
                             args=(lines[i], account_list[count], account_dic[account_list[count]], clubname1))
        thread_list.append(t)
        i += 1
        count += 1
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()

    # 读取账号
    account_list, account_dic, accountnum, _, _ = read('40_2.txt')

    # 多线程执行
    count = 0  # 完成账号数
    thread_list = []
    # 完整循环 join()方法确保完成后再进行下一次循环
    for i in range(int(accountnum / emulatornum)):  # 完整循环 join()方法确保完成后再进行下一次循环
        for j in range(emulatornum):
            t = threading.Thread(target=runmain, args=(
                lines[j], account_list[i * emulatornum + j], account_dic[account_list[i * emulatornum + j]], clubname2))
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
                             args=(lines[i], account_list[count], account_dic[account_list[count]], clubname2))
        thread_list.append(t)
        i += 1
        count += 1
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()

    # 退出adb
    os.system('cd adb & adb kill-server')
