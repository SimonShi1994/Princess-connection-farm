# coding=utf-8
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

def init_acc():#原作者的初始号初始化函数，不适用于农场号
    while True:

        screen_shot = a.d.screenshot(format="opencv")
        state_flag = a.get_screen_state(screen_shot)

        if state_flag=='dark':
            print('画面变暗,尝试进入引导模式点击')
            screen_shot = a.d.screenshot(format="opencv")
            a.jiaoxue(screen_shot)

        elif state_flag=='zhandou':
            print('侦测到加速按钮, 进入战斗模式')
            a.zhandou()
        elif state_flag=='shouye':
            print('恭喜完成所有教学内容, 跳出循环')
            a.d.click(1, 1)
            time.sleep(1)            
            break
        else:
            template_paths = ['img/tiaoguo.jpg', 'img/ok.jpg','img/xiayibu.jpg', 'img/caidan.jpg', 'img/caidan_yuan.jpg',
                                      'img/caidan_tiaoguo.jpg', 'img/dengji.jpg','img/tongyi.jpg','img/niudan_jiasu.jpg']
            a.guochang(screen_shot,template_paths)


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

def gonghuizhijia():  # 家园领取
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_, 'img/liwu.jpg'):
            break
        a.d.click(100, 505)
        time.sleep(1)  # 首页锁定，保证回到首页
    a.d.click(622, 509)
    time.sleep(8)
    while True:
        if a.is_there_img(screen_shot_, 'img/caidan_yuan.jpg'):
            a.d.click(917, 39)  # 菜单
            time.sleep(1)
            a.d.click(807, 44)  # 跳过
            time.sleep(1)
            a.d.click(589, 367)  # 跳过ok
            time.sleep(1)
            time.sleep(8)
        else:
            break
    for i in range(2):
        a.d.click(899, 429)  # 一键领取
        time.sleep(3)
        screen_shot_ = a.d.screenshot(format="opencv")
        a.guochang(screen_shot_, ['img/jyquanbushouqu.jpg'], suiji=0)
        screen_shot_ = a.d.screenshot(format="opencv")
        a.guochang(screen_shot_, ['img/guanbi.jpg'], suiji=0)
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_, 'img/liwu.jpg'):
            break
        a.d.click(100, 505)
        time.sleep(1)  # 首页锁定，保证回到首页

def dianzan():  # 行会点赞
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/liwu.jpg'):
            break
        a.d.click(100,505)
        time.sleep(1)#首页锁定，保证回到首页
    # 进入行会
    time.sleep(3)
    screen_shot_ = a.d.screenshot(format="opencv")
    for i in range(2):
        time.sleep(3)
        a.guochang(screen_shot_, ['img/zhandou_ok.jpg'], suiji=0)
    a.d.click(688, 432)
    time.sleep(3)
    a.d.click(239, 351)
    time.sleep(2)
    a.d.click(829, 316)  #点赞 职务降序（默认） 第二个人，副会长
    time.sleep(2)
    a.d.click(479, 381)
    a.guochang(screen_shot_, ['img/ok.jpg'], suiji=0)
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/liwu.jpg'):
            break
        a.d.click(100,505)
        a.d.click(1,1)
        time.sleep(1)#首页锁定，保证回到首页

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


def niudan():#扭蛋函数
    a.d.click(751,505)
    time.sleep(1)
    while True:
        time.sleep(1)
        active_list = ['img/sheding.jpg','img/ok.jpg','img/niudan_jiasu.jpg','img/zaicichouqu.jpg','img/shilian.jpg']
        screen_shot = a.d.screenshot(format="opencv")
        a.guochang(screen_shot,active_list, suiji=1)
        screen_shot_ = a.d.screenshot(format="opencv")
        state_flag = a.get_screen_state(screen_shot_)
        if state_flag == 'baoshigoumai':
            print('没钱了, 关闭')
            a.d.click(373, 370)
            break

def goumaimana():#该函数只能在首页运行但未写首页锁定，请注意debug
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



def write_log(account, pwd):#识别box函数
    time.sleep(1)
    a.d.click(209, 519)
    time.sleep(1)
    a.d.click(659, 30)
    time.sleep(1)
    a.d.click(728, 142)
    time.sleep(1)
    a.d.click(588, 481)
    time.sleep(1)

    base_path = 'img/touxiang/'
    touxiang_path_list = []
    for touxiang_path in os.listdir(base_path):
        touxiang_path_list.append(base_path+touxiang_path)
    screen_shot = a.d.screenshot(format="opencv")
    exist_list = a.get_butt_stat(screen_shot, touxiang_path_list)
    print(exist_list)
    st = ''
    for i in exist_list:
        st = st + str(os.path.basename(i).split('.')[0]) + ','
    with open('jieguo.txt', 'a') as f:
        f.write(account+'\t'+ pwd+'\t'+st+'\n')

def change_acc():#切换账号
    time.sleep(1)
    a.d.click(871, 513)
    time.sleep(1)
    a.d.click(165, 411)
    time.sleep(1)
    a.d.click(591, 369)
    time.sleep(1)
    print('-----------------------------')
    print('完成该任务')
    print('-----------------------------')

def goumaitili():#购买体力，注意此函数参数默认在首页执行，其他地方执行要调整参数
    for i in range(3):
        while True:
            screen_shot_ = a.d.screenshot(format="opencv")
            if a.is_there_img(screen_shot_,'img/liwu.jpg'):
                break
            a.d.click(100,505)
            time.sleep(1)#首页锁定，保证回到首页
        a.d.click(320,31)
        time.sleep(1)
        screen_shot = a.d.screenshot(format="opencv")
        a.guochang(screen_shot,['img/ok.jpg'], suiji=0)
        time.sleep(1)
        screen_shot = a.d.screenshot(format="opencv")
        a.guochang(screen_shot,['img/zhandou_ok.jpg'], suiji=1)
        a.d.click(100,505)#点击一下首页比较保险


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



def shuatu():#刷图函数 注意此函数要在首页运行
    #进入冒险
    a.d.click(480, 505)
    time.sleep(0.5) 
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/dixiacheng.jpg'):
            break
    a.d.click(562, 253)
    time.sleep(1)
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/normal.jpg'):
            break

    shuatuzuobiao(821,299,3)#10-17
    shuatuzuobiao(703,328,3)#10-16
    shuatuzuobiao(608,391,3)#10-15
    shuatuzuobiao(485,373,3)#10-14
    shuatuzuobiao(372,281,3)#10-13
    shuatuzuobiao(320,421,3)#10-12
    shuatuzuobiao(172,378,3)#10-11
    shuatuzuobiao(251,235,3)#10-10
    shuatuzuobiao(111,274,3)#10-9

    a.d.drag(200,270,600,270,0.1)#拖拽到最左
    time.sleep(2)

    shuatuzuobiao(690,362,3)#10-8
    shuatuzuobiao(594,429,3)#10-7
    shuatuzuobiao(411,408,3)#10-6
    shuatuzuobiao(518,332,3)#10-5
    shuatuzuobiao(603,238,3)#10-4
    shuatuzuobiao(430,239,3)#10-3
    shuatuzuobiao(287,206,3)#10-2
    shuatuzuobiao(146,197,3)#10-1

    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/liwu.jpg'):
            break
        a.d.click(100,505)
        time.sleep(1)#保证回到首页




def dixiacheng():#地下城
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
            a.d.click(233, 311)
            time.sleep(1)
            while True:
                screen_shot_ = a.d.screenshot(format="opencv")
                if a.is_there_img(screen_shot_,'img/ok.jpg'):
                    break
            a.d.click(592, 369)#点击ok
            time.sleep(1) 
            break


    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/chetui.jpg'):
            break
        if a.is_there_img(screen_shot_,'img/caidan_yuan.jpg'):
            a.d.click(917, 39)#菜单
            time.sleep(1)
            a.d.click(807, 44)#跳过
            time.sleep(1)
            a.d.click(589, 367)#跳过ok
            time.sleep(1)

    a.d.click(667, 360)#1层
    time.sleep(1)
    a.d.click(833, 456)#挑战
    time.sleep(1)
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/zhiyuan.jpg'):
            break
    a.d.click(100, 173)#第一个人
    time.sleep(1)
    screen_shot = a.d.screenshot(format="opencv")
    a.guochang(screen_shot, ['img/zhiyuan.jpg'],suiji=0)
    
    if a.is_there_img(screen_shot_,'img/dengjixianzhi.jpg'):
        a.d.click(213, 208)#如果等级不足，就支援的第二个人
        time.sleep(1)    
    else:
        a.d.click(100, 173)#支援的第一个人
        time.sleep(1)
    
    a.d.click(833, 470)#战斗开始
    time.sleep(1)
    while True:
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/ok.jpg'):
            a.guochang(screen_shot_, ['img/ok.jpg'],suiji=0)
            break


    while True:#战斗中快进
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/caidan.jpg'):
            if a.is_there_img(screen_shot_,'img/kuaijin.jpg'):
                a.d.click(913, 494)#点击快进
                time.sleep(1)
                a.d.click(913, 494)#点击快进
            if a.is_there_img(screen_shot_,'img/kuaijin_1.jpg'):
                a.d.click(913, 494)#点击快进
                time.sleep(1)
            break
    while True:#结束战斗返回
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/shanghaibaogao.jpg'):
            a.guochang(screen_shot_,['img/xiayibu.jpg','img/qianwangdixiacheng.jpg'], suiji=0)
            break
    a.d.click(1, 1)#取消显示结算动画
    time.sleep(1)
    while True:#撤退地下城
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/chetui.jpg'):
            break;#解决issues中截图可能截到撤退按钮的问题
    time.sleep(1)
    while True:#撤退地下城
        screen_shot_ = a.d.screenshot(format="opencv")
        if a.is_there_img(screen_shot_,'img/chetui.jpg'):
            a.guochang(screen_shot_,['img/chetui.jpg'], suiji=0)
            screen_shot = a.d.screenshot(format="opencv")
            a.guochang(screen_shot,['img/ok.jpg'], suiji=0)
            break
        a.d.click(1, 1)#
        time.sleep(1)
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

with open('zhanghao.txt','r') as f:
    for i,line in enumerate(f):
        account,password = line.split('\t')[0:2]
        account_dic[account]=password.strip()

for account in account_dic:
    print('>>>>>>>即将登陆的账号为：',account, '密码：',account_dic[account],'<<<<<<<')
    login_auth(account, account_dic[account])
    #init_acc()#账号初始化


    init_home()#初始化，确保进入首页
    gonghuizhijia()  #家园一键领取（请自行跳过剧情，我这没有= =）
    shouqu()  # 收取所有礼物
    dianzan()  # 公会点赞
    shouqu()# 收取所有礼物
    hanghui()#行会捐赠
    dixiacheng()#地下城
    goumaitili()#购买3次体力
    shouqurenwu()#收取任务
    shuatu()#刷全部10图3次

    #box管理功能，未启用
    # niudan()#扭蛋扭光钻石
    # write_log(account, account_dic[account])#列出box内容在jieguo.txt
    
    change_acc()#退出当前账号，切换下一个