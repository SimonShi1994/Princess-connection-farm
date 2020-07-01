# coding=utf-8
import uiautomator2 as u2
import time
from utils import *
from cv import *
from Automator import *
import os
import threading


def create_main(address, account, password, token):
    a = Automator(address)
    a.start()

    print('>>>>>>>会长账号为：', account, '密码：', password, '<<<<<<<')
    print('>>>>>>>即将创建公会名为：', token, '<<<<<<<')
    t0 = time.time()
    a.login(ac=account, pwd=password)

    a.init_home()
    a.d.click(689, 430)
    a.lockimg('img/jiaruhanghui.jpg', elseclick=[(1, 100)], elsedelay=0.5)
    a.d.click(844, 446)
    time.sleep(1)
    a.d.click(318, 162)
    time.sleep(1)
    a.d.send_keys(token)
    a.lockimg('img/xvyaoshenhe.bmp', elseclick=[(559, 342)], elsedelay=0.5)
    a.lockimg('img/xvyaoshenhe.bmp', ifclick=[(481, 128), (589, 477)], ifdelay=0.5)
    time.sleep(1)
    a.d.click(589, 477)
    time.sleep(1)
    a.d.click(1, 100)
    time.sleep(1)

    a.change_acc()  # 退出当前账号，切换下一个
    t = time.time()
    print('>>>>>>>公会', token, '创建完成，用时', t - t0, '秒<<<<<<<')


def accept_main(address, account, password, token):
    a = Automator(address)
    a.start()

    print('>>>>>>>会长账号为：', account, '密码：', password, '<<<<<<<')
    print('>>>>>>>接受申请<<<<<<<')
    t0 = time.time()
    a.login(ac=account, pwd=password)
    a.init_home()
    a.d.click(691, 432)
    time.sleep(4)
    a.d.click(239, 352)
    time.sleep(2)
    a.d.click(548, 32)
    time.sleep(1)
    while True:
        screen_shot_ = a.d.screenshot(format='opencv')
        if a.is_there_img(screen_shot_, 'img/xvke.bmp'):
            a.d.click(845, 177)
            time.sleep(0.8)
            a.d.click(1, 100)
            time.sleep(0.8)
            continue
        else:
            break

    a.change_acc()  # 退出当前账号，切换下一个
    t = time.time()
    print('>>>>>>>done<<<<<<<')


def apply_main(address, account, password, token):
    a = Automator(address)
    a.start()

    print('>>>>>>>成员账号：', account, '密码：', password, '<<<<<<<')
    print('>>>>>>>即将加入公会名为：', token, '<<<<<<<')
    t0 = time.time()
    a.login(ac=account, pwd=password)

    a.init_home()
    a.d.click(689, 430)
    a.lockimg('img/jiaruhanghui.jpg', elseclick=[(1, 100)], elsedelay=0.5)
    a.d.click(861, 79)
    time.sleep(1.5)
    a.d.click(368, 181)
    a.d.send_keys(token)
    for _ in range(2):
        a.d.click(480, 87)
        time.sleep(0.5)
    a.d.click(590, 435)
    time.sleep(4)
    a.d.click(691, 163)
    time.sleep(1)
    a.d.click(838, 440)
    time.sleep(1.5)
    a.d.click(591, 371)
    time.sleep(1.5)
    a.d.click(482, 373)
    time.sleep(1.5)

    a.change_acc()  # 退出当前账号，切换下一个
    t = time.time()
    print('>>>>>>>账号：', account, '已进入公会, 用时', t - t0, '秒<<<<<<<')


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
    with open('zhanghao_init.txt', 'r') as f:  # 注意！请把账号密码写在zhanghao_init.txt内,不是zhanghao.txt!!!!!
        for i, line in enumerate(f):
            account, password = line.split('\t')[0:2]
            account_dic[account] = password.strip()
    account_list = list(account_dic.keys())
    accountnum = len(account_list)
    return (account_list, account_dic, accountnum)


# 主程序
if __name__ == '__main__':

    # 连接adb与uiautomator
    lines, emulatornum = connect()
    # 读取账号
    account_list, account_dic, accountnum = read()
    # 随机生成公会名称
    token = token()  # 公会名称可以自己更改，请保证唯一性和不包含敏感词
    # 默认第一个账号为会长，创建新的公会
    create_main(lines[0], account_list[0], account_dic[account_list[0]], token)
    # 多线程添加成员
    count = 1  # 完成账号数
    thread_list = []
    # 完整循环 join()方法确保完成后再进行下一次循环
    for i in range(int((accountnum - 1) / emulatornum)):
        for j in range(emulatornum):
            t = threading.Thread(target=apply_main, args=(
                lines[j], account_list[i * emulatornum + j + 1], account_dic[account_list[i * emulatornum + j + 1]],
                token))
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
        t = threading.Thread(target=apply_main,
                             args=(lines[i], account_list[count], account_dic[account_list[count]], token))
        thread_list.append(t)
        i += 1
        count += 1
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()

    accept_main(lines[0], account_list[0], account_dic[account_list[0]], token)

    # 退出adb
    os.system('cd adb & adb kill-server')
