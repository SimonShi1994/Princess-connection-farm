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


def change_acc():#切换账号
    time.sleep(1)
    a.d.click(871, 513)
    time.sleep(1)
    a.d.click(165, 411)
    time.sleep(1)
    a.d.click(591, 369)
    time.sleep(1)


def hanghui():#自动行会捐赠
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/liwu.jpg'):
            break
        a.d.click(100,505)
        time.sleep(1)#首页锁定，保证回到首页
    time.sleep(1)
    a.d.click(693, 436)
    time.sleep(1)
    while True:#6-17修改：减少opencv使用量提高稳定性
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/zhiyuansheding.jpg'):
            time.sleep(3)#加载行会聊天界面会有延迟
            screen_shot = a.d.screenshot(format="opencv")
            if a.is_there_img(screen_shot,'img/juanzengqingqiu.jpg'):
                a.d.click(367, 39)#点击定位捐赠按钮
                time.sleep(2)
                screen_shot = a.d.screenshot(format="opencv")
                a.guochang(screen_shot, ['img/juanzeng.jpg'],suiji=0)
                time.sleep(1)
                a.d.click(644, 385)#点击max
                time.sleep(1)
                screen_shot = a.d.screenshot(format="opencv")
                a.guochang(screen_shot, ['img/ok.jpg'],suiji=0)
                time.sleep(1)
                while True:
                    a.d.click(1, 1)
                    time.sleep(1)
                    screen_shot = a.d.screenshot(format="opencv")
                    if a.is_there_img(screen_shot,'img/zhiyuansheding.jpg'):
                        break
            break
        a.d.click(1, 1)#处理被点赞的情况
        time.sleep(1)

    a.d.click(100, 505)#回到首页
    time.sleep(1)
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/liwu.jpg'):
            break
        a.d.click(100,505)
        a.d.click(1,1)
        time.sleep(1)#首页锁定，保证回到首页

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
    hanghui()#行会捐赠
    change_acc()#退出当前账号，切换下一个