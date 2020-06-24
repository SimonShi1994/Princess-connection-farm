# coding=utf-8
import uiautomator2 as u2
import time
from utils import *
from cv import *
from Automator import *
#import matplotlib.pylab as plt
import os
import threading


def runmain(address,account,password):
    #主功能体函数
    #请在本函数中自定义需要的功能

    a = Automator(address)
    a.start()

    # #opencv识别可视化 无法在多线程中使用
    # plt.ion()
    # fig, ax = plt.subplots(1)
    # plt.show()

    print('>>>>>>>即将登陆的账号为：',account,'密码：',password,'<<<<<<<')
    a.login_auth(account, password)#注意！请把账号密码写在zhanghao2.txt内
    a.init_home()#初始化，确保进入首页
    

    a.hanghui()#行会捐赠


    a.change_acc()#退出当前账号，切换下一个


def connect():#连接adb与uiautomator
    try:
        os.system('adb connect 127.0.0.1:5554')#雷电模拟器
        # os.system('adb connect 127.0.0.1:7555') #mumu模拟器
        os.system('python -m uiautomator2 init')
    except:
        print('连接失败')

    result = os.popen('adb devices')#返回adb devices列表
    res = result.read()
    lines=res.splitlines()[1:]

    for i in range(0,len(lines)):
        lines[i]=lines[i].split('\t')[0]
    lines=lines[0:-1]
    print(lines)
    emulatornum=len(lines)
    return(lines,emulatornum)

def read():#读取账号
    account_dic = {}
    with open('zhanghao.txt','r') as f:#注意！请把账号密码写在zhanghao.txt内
        for i,line in enumerate(f):
            account,password = line.split('\t')[0:2]
            account_dic[account]=password.strip()
    account_list=list(account_dic.keys())
    accountnum=len(account_list)
    return(account_list,account_dic,accountnum)



#主程序
if __name__ == '__main__':
    
    #连接adb与uiautomator
    lines,emulatornum = connect()
    #读取账号
    account_list,account_dic,accountnum = read()

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

    #退出adb
    os.system('cd adb & adb kill-server')