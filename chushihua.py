# coding=utf-8
import uiautomator2 as u2
import time
from utils import *
from cv import *
from Automator import *
# import matplotlib.pylab as plt
import os
import threading


def runmain(address, account, password):
    a = Automator(address)
    a.start()

    print('>>>>>>>即将登陆的账号为：', account, '密码：', password, '<<<<<<<')
    t0 = time.time()
    a.login_auth(account, password)  # 注意！请把账号密码写在zhanghao2.txt内
    a.init_home()  # 初始化，确保进入首页
    time.sleep(2)
    a.setting()  # 设置无动画、低帧率

    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_, 'img/zhuxianguanqia.jpg'):
            break
        a.d.click(480, 513)
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_, 'img/zhuxianguanqia.jpg'):
            a.d.click(562, 253)
            continue
        break
    time.sleep(3)
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_, 'img/normal.jpg'):
            break
        a.d.click(704, 84)
    # 初始化至主线关卡结束

    a.shoushuazuobiao(313, 341)  # 1-3
    a.shoushuazuobiao(379, 240, 1)  # 1-4
    a.shoushuazuobiao(481, 286)  # 1-5
    a.shoushuazuobiao(545, 381, 1)  # 1-6
    a.shoushuazuobiao(607, 304)  # 1-7
    a.shoushuazuobiao(620, 209)  # 1-8
    a.shoushuazuobiao(747, 243)  # 1-9
    a.qianghua()
    a.shoushuazuobiao(824, 348, 1)  # 1-10 虽然没有繁琐教程，但解锁东西过多，还是去用函数
    a.shoushuazuobiao(129, 413, 1)  # 2-1
    a.shoushuazuobiao(255, 413, 1)  # 2-2
    a.qianghua()
    a.shoushuazuobiao(379, 379)  # 2-3
    a.shoushuazuobiao(332, 269)  # 2-4
    a.shoushuazuobiao(237, 206, 1)  # 2-5
    a.shoushuazuobiao(353, 161)  # 2-6
    a.shoushuazuobiao(453, 231)  # 2-7
    a.shoushuazuobiao(479, 316, 1)  # 2-8
    a.shoushuazuobiao(602, 380)  # 2-9 装备危险 602 375 -> 527,380
    a.shoushuazuobiao(646, 371)  # 2-10
    a.shoushuazuobiao(757, 344)  # 2-11
    a.shoushuazuobiao(745, 229, 1)  # 2-12
    a.shoushuazuobiao(138, 188, 1)  # 3-1

    a.change_acc()  # 退出当前账号，切换下一个
    t = time.time()
    print('>>>>>>>账号：', account, '已刷完, 用时', t - t0, '秒<<<<<<<')


def connect():  # 连接adb与uiautomator
    try:
        os.system('cd adb & adb connect 127.0.0.1:5554')  # 雷电模拟器
        # os.system('adb connect 127.0.0.1:7555') #mumu模拟器
        os.system('python -m uiautomator2 init')
    except:
        print('连接失败')

    result = os.popen('cd adb & adb devices')  # 返回adb devices列表
    res = result.read()
    lines = res.splitlines()[1:]

    for i in range(0, len(lines)):
        lines[i] = lines[i].split('\t')[0]
    lines = lines[0:-1]
    print(lines)
    emulatornum = len(lines)
    return lines, emulatornum


def read():  # 读取账号
    account_dic = {}
    with open('zhanghao_init.txt', 'r') as f:  # 注意！请把账号密码写在zhanghao2.txt内,不是zhanghao.txt!!!!!
        for i, line in enumerate(f):
            account, password = line.split('\t')[0:2]
            account_dic[account] = password.strip()
    account_list = list(account_dic.keys())
    accountnum = len(account_list)
    return account_list, account_dic, accountnum


# 主程序
if __name__ == '__main__':

    # 连接adb与uiautomator
    lines, emulatornum = connect()
    # 读取账号
    account_list, account_dic, accountnum = read()

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
