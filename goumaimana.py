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



def goumaimana():
    a.d.click(189,62)
    while True:#锁定取消2
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/quxiao2.jpg'):
            break
        a.d.click(189,62)
        time.sleep(0.5)
    a.d.click(596,471)#第一次购买的位置
    while True:#锁定ok
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/ok.jpg'):
            a.guochang(screen_shot_, ['img/ok.jpg'],suiji=0)
            break
    for i in range(7):#购买剩下的7次
        while True:#锁定取消2
            screen_shot_ = a.d.screenshot(format="opencv")
            if a.is_there_img(screen_shot_,'img/quxiao2.jpg'):
                break
        a.d.click(816,478)#购买10次
        while True:#锁定ok
            screen_shot_ = a.d.screenshot(format="opencv")
            if a.is_there_img(screen_shot_,'img/ok.jpg'):
                a.guochang(screen_shot_, ['img/ok.jpg'],suiji=0)
                break
    while True:#锁定首页
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/liwu.jpg'):
            break
        a.d.click(1,1)
        time.sleep(0.5)#保证回到首页



def change_acc():#切换账号
    time.sleep(1)
    a.d.click(871, 513)
    time.sleep(1)
    a.d.click(165, 411)
    time.sleep(1)
    a.d.click(591, 369)
    time.sleep(1)

#%%
#==============================================================================
#主程序
account_dic = {}

with open('zhanghao.txt','r') as f:
    for i,line in enumerate(f):
        account,password = line.split('\t')[0:2]
        account_dic[account]=password.strip()

for account in account_dic:
    print(account, account_dic[account])
    login_auth(account, account_dic[account])



    init_home()#初始化，确保进入首页
    goumaimana()#购买70次mana
    change_acc()#退出当前账号，切换下一个