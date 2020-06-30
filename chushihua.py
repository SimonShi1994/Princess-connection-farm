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

    need_auth = a.login(ac=account, pwd=password)
    if need_auth:
        auth_name, auth_id = random_name(), CreatIDnum()
        a.auth(auth_name=auth_name, auth_id=auth_id)


    # ========现在开始完成新手教程========
    """
    最高优先级
    引导， 结束标志

    高优先级
    同意，跳过，登记，OK，扭蛋跳过

    复合点击
    长条菜单->跳过 （只使用两次）
    圆Menu->跳过->跳过

    低优先级
    未激活的加速战斗

    默认，点击(1,100)
    """
    count = 0 #记录跳过战斗的数量
    times = 0 #记录主页出现的次数
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        num_of_white, x, y = UIMatcher.find_gaoliang(screen_shot_)
        if num_of_white < 70000:
            try:
                a.d.click(x * a.dWidth, y * a.dHeight + 20)
            except:
                pass
            time.sleep(1)
            continue
        template_path = ['img/tongyi.jpg', 'img/tiaoguo.jpg', 'img/dengji.jpg', 'img/ok.bmp', 'img/niudan_jiasu.jpg']
        active_path = a.get_butt_stat(screen_shot_, template_path)
        if len(active_path) > 0:
            for (x, y) in active_path.values():
                a.d.click(x, y)
                time.sleep(0.5)
                break
            continue
        template_path = ['img/caidan.jpg','img/caidan_yuan.jpg']
        active_path = a.get_butt_stat(screen_shot_, template_path)
        if count < 2 and ('img/caidan.jpg' in active_path): #有两场战斗是可以跳过的
            count += 1
            a.d.click(900, 25)
            time.sleep(0.8)
            a.d.click(591, 370)
            time.sleep(0.5)
            continue
        if 'img/caidan_yuan.jpg' in active_path:
            a.d.click(919, 45)
            time.sleep(0.8)
            a.d.click(806, 46)
            time.sleep(1)
            a.d.click(589, 370)
            time.sleep(0.5)
            continue
        if a.is_there_img(screen_shot_, 'img/kuaijin.jpg'):
            a.d.click(911, 493)
            time.sleep(3)
            continue
        if a.is_there_img(screen_shot_, 'img/liwu.bmp'):
            if times==2:
                break
            times += 1
            print('在主页的第',times,'次')
        # default
        a.d.click(1, 100)
        time.sleep(0.8)
    print('新手教程已完成')

    # ===========新手教程完成============
    # ===========开始前期准备============

    a.lockimg('img/liwu.jpg', elseclick=[(1,100)], elsedelay=0.5, alldelay=2)

    a.shouqu()  # 拿一点钻石用于买扫荡券，理论上至少能拿到300钻
    a.goumaimana(1)  # 买扫荡券
    a.goumaitili(2)
    a.goumaijingyan()

    a.setting()  # 设置无动画、低帧率

    a.lockimg('img/zhuxianguanqia.jpg', elseclick=[(480, 513)], elsedelay=0.5, alldelay=1)
    a.lockimg('img/zhuxianguanqia.jpg', ifclick=[(562, 235)], ifdelay=3, alldelay=0)

    # ===========前期准备结束============
    # =============开始刷图==============
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
    a.qianghua() #这个强化不要也大概率可以刷到3-1，但是不能满星，且有风险
    a.shoushuazuobiao(602, 380)  # 2-9 装备危险
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
