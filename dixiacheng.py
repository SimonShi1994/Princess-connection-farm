import uiautomator2 as u2
import time
from utils import *
from cv import *
from Automator import *
import matplotlib.pylab as plt


plt.ion()
fig, ax = plt.subplots(1)
plt.show()

a = Automator()
a.start()

def login_auth(ac,pwd):
    need_auth = a.login(ac=ac,pwd=pwd)
    if need_auth:
        auth_name,auth_id = random_name(), CreatIDnum()
        a.auth(auth_name =auth_name ,auth_id = auth_id)


def init_home():
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/liwu.jpg'):
            break
        a.d.click(1,1)
        time.sleep(0.5)#保证回到首页    
    time.sleep(0.5)
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/liwu.jpg'):
            break
        a.d.click(1,1)
        time.sleep(0.2)#保证回到首页
        a.d.click(100,505)



def shouqu():#收取全部礼物

    while True:#锁定回到首页
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/liwu.jpg'):
            break
        a.d.click(100,505)
        time.sleep(0.3)
        a.d.click(1,1)
    a.guochang(screen_shot_, ['img/liwu.jpg'],suiji=0)
    while True:#锁定收取履历（礼品盒）
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/shouqulvli.jpg'):
            a.d.click(809,471)#点击全部收取
            time.sleep(1)
            a.d.click(589,472)#2020-5-29 19:41 bug fixed
            break
    while True:#锁定回到首页
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/liwu.jpg'):
            break
        a.d.click(1,1)#礼品盒有特殊性，不能点（100,505），会被挡住
        time.sleep(0.3)


def shouqurenwu():#收取任务报酬

    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/renwu.jpg'):
            a.guochang(screen_shot_, ['img/renwu.jpg'],suiji=0)
            break
        a.d.click(1,1)
        time.sleep(1)
    time.sleep(2)
    a.d.click(846,437)#全部收取
    time.sleep(1)
    a.d.click(100,505)
    time.sleep(0.5)
    a.d.click(100,505)
    time.sleep(1.5)
    while True:#锁定回到首页
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/liwu.jpg'):
            break
        a.d.click(100,505)
        time.sleep(0.5)




def change_acc():#切换账号
    time.sleep(1)
    a.d.click(871, 513)
    time.sleep(1)
    a.d.click(165, 411)
    time.sleep(1)
    a.d.click(591, 369)
    time.sleep(1)



def shuatuzuobiao(x,y,times):#刷图函数，xy为该图的坐标，times为刷图次数
    a.d.click(x,y)
    time.sleep(0.5)
    while True:#锁定加号
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/jiahao.jpg'):
            break
        a.d.click(x,y)
        time.sleep(0.5)
    screen_shot = a.d.screenshot(format="opencv")
    for i in range(times-1):#基础1次
        a.guochang(screen_shot,['img/jiahao.jpg'])
        time.sleep(0.2)
    time.sleep(0.3)
    a.d.click(758,330)#使用扫荡券的位置 也可以用OpenCV但是效率不够而且不能自由设定次数
    time.sleep(0.3)
    # screen_shot = a.d.screenshot(format="opencv")
    # a.guochang(screen_shot,['img/shiyongsanzhang.jpg'])
    screen_shot = a.d.screenshot(format="opencv") 
    a.guochang(screen_shot,['img/ok.jpg'])
    while True:
        a.d.click(1,1)
        time.sleep(0.3)
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/normal.jpg'):
            break



def dixiachengzuobiao(x,y,auto,team=0):
#完整刷完地下城函数
#参数：
# x：目标层数的x轴坐标
# y：目标层数的y轴坐标
# auto：取值为0/1,auto=0时不点击auto按钮，auto=1时点击auto按钮
# team：取值为0/1/2，team=0时不换队，team=1时更换为队伍列表中的1队，team=2时更换为队伍列表中的2队

    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/chetui.jpg'):
            break
        a.d.click(1, 1)
        time.sleep(1)
    time.sleep(1)
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/chetui.jpg'):
            break
        a.d.click(1, 1)
        time.sleep(1)
    a.d.click(1, 1)
    time.sleep(3)

    a.d.click(x, y)#层数
    time.sleep(2)
    a.d.click(833, 456)#挑战
    time.sleep(2)

    while True:#锁定战斗开始
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/zhandoukaishi.jpg'):
            break

    if team!=0:#换队
        a.d.click(866, 91)#我的队伍
        time.sleep(2)
        if team==1:
            a.d.click(792, 172)#1队
        elif team==2:
            a.d.click(789, 290)#2队
        time.sleep(0.5)
        while True:#锁定战斗开始
            screen_shot_ = a.d.screenshot(format="opencv")
            if a.is_there_img(screen_shot_,'img/zhandoukaishi.jpg'):
                break
            time.sleep(0.5)
    
    a.d.click(837, 447)#战斗开始
    time.sleep(2)

    while True:#战斗中快进
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/caidan.jpg'):
            if auto==1:
                time.sleep(0.5)
                a.d.click(912, 423)#点auto按钮
                time.sleep(1)
            break
    while True:#结束战斗返回
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/shanghaibaogao.jpg'):
            while True:
                screen_shot = a.d.screenshot(format="opencv")
                if a.is_there_img(screen_shot,'img/xiayibu.jpg'):
                    break
            a.d.click(830, 503)#点下一步 避免guochang可能失败
            break
    time.sleep(3)
    a.d.click(1, 1)#取消显示结算动画
    time.sleep(1)

def tansuo():#探索函数
    a.d.click(480, 505)
    time.sleep(1) 
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/dixiacheng.jpg'):
            break
        a.d.click(480, 505)
        time.sleep(1)
    a.d.click(734, 142)#探索
    time.sleep(3.5)

#经验
    a.d.click(592, 255)#经验
    time.sleep(3)
    a.d.click(704, 152)#5级
    time.sleep(1.5)
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/tiaozhan.jpg'):
            break
        time.sleep(0.5)
    a.d.drag(876,329,876,329,0.5)#+号
    time.sleep(0.5)
    a.d.click(752, 327)#扫荡
    time.sleep(0.5)
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/ok.jpg'):
            a.d.click(590, 363)#ok
            time.sleep(0.5)
            break
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/home.jpg'):
            break
        a.d.click(1, 1)
        time.sleep(1)

#mana
    a.d.click(802, 267)#mana
    time.sleep(3)
    a.d.click(704, 152)#5级
    time.sleep(1.5)
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/tiaozhan.jpg'):
            break
        time.sleep(0.5)
    a.d.drag(876,329,876,329,0.5)#+号
    time.sleep(0.5)
    a.d.click(752, 327)#扫荡
    time.sleep(0.5)
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/ok.jpg'):
            a.d.click(590, 363)#ok
            time.sleep(0.5)
            break
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/home.jpg'):
            break
        a.d.click(1, 1)
        time.sleep(1)
#完成战斗后
    while True:#首页锁定
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/liwu.jpg'):
            break
        a.d.click(100,505)
        time.sleep(1)#保证回到首页




def dixiachengDuanya():#地下城 断崖（第三个）
    a.d.click(480, 505)
    time.sleep(1) 
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/dixiacheng.jpg'):
            break
        a.d.click(480, 505)
        time.sleep(1)
    a.d.click(900, 138)
    time.sleep(1)

    #下面这段因为调试而注释了，实际使用时要加上
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/chetui.jpg'):#避免某些农场号刚买回来已经进了地下城
            break
        if a.is_there_img(screen_shot_,'img/yunhai.jpg'):
            a.d.click(712,267)#断崖
            time.sleep(1)
            while True:
                screen_shot_ = a.d.screenshot(format="opencv")
                if a.is_there_img(screen_shot_,'img/ok.jpg'):
                    break
            a.d.click(592, 369)#点击ok
            time.sleep(1) 
            break
#刷地下城
    dixiachengzuobiao(642,371,1,1)#1层
    dixiachengzuobiao(368,276,0)#2层
    dixiachengzuobiao(627,263,0,2)#3层
    dixiachengzuobiao(427,274,1)#4层
    dixiachengzuobiao(199,275,0)#5层
    dixiachengzuobiao(495,288,0)#6层
    dixiachengzuobiao(736,291,0)#7层
    dixiachengzuobiao(460,269,0)#8层
    dixiachengzuobiao(243,274,0)#9层
    dixiachengzuobiao(654,321,0,1)#10层

#完成战斗后
    while True:#首页锁定
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/liwu.jpg'):
            break
        a.d.click(100,505)
        time.sleep(1)#保证回到首页
#%%
#==============================================================================
#主程序
account_dic = {}

with open('zhanghao2.txt','r') as f:#注意！请把账号密码写在zhanghao2.txt内
    for i,line in enumerate(f):
        account,password = line.split('\t')[0:2]
        account_dic[account]=password.strip()

for account in account_dic:
    print(account, account_dic[account])
    login_auth(account, account_dic[account])#注意！请把账号密码写在zhanghao2.txt内
    init_home()#初始化，确保进入首页
    
    tansuo()#探索
    dixiachengDuanya()#地下城，请把队伍列表里1队设置为打boss队，2队设置为aoe队
    shouqurenwu()#收取任务
    shouqu()#收取所有礼物

    change_acc()#退出当前账号，切换下一个