from core.Automator import Automator
from core.log_handler import pcr_log
from initialize import execute, can_shuatu

# 仅适用于zhanghao.txt里面的帐号，可以判断是农场号，还是要捐装备的号
# 根据zhanghao.txt里边的帐号是否有标注图号（也就是第三个参数）来确定是不是捐装备的号
# 如果是农场号就没有动作，如果是要捐装备的号就登录游戏捐装备
account_filename = "zhanghao.txt"


def tasks(a: Automator, account, opcode):
    # 主功能体函数，可以在本函数中自定义需要的功能
    try:
        a.c_async(a, account, a.screenshot(), sync=False)  # 异步眨眼截图,开异步必须有这个
        a.init_home()  # 初始化，确保进入首页
        a.c_async(a, account, a.juqingtiaoguo(), sync=False)  # 异步剧情跳过
        a.c_async(a, account, a.bad_connecting(), sync=False)  # 异步异常处理

        a.gonghuizhijia()  # 家园一键领取
        # a.goumaimana(1)  # 购买mana 10次
        a.mianfeiniudan()  # 免费扭蛋
        # a.mianfeishilian()  # 免费十连
        a.shouqu()  # 收取所有礼物
        a.dianzan(sortflag=1)  # 公会点赞，sortflag=1表示按战力排序
        a.dixiacheng_ocr(skip=False)  # 地下城 skip是否开启战斗跳过
        # a.goumaitili(3)  # 购买3次体力
        # a.buyExp() # 买药
        # a.doActivityHard() # 刷活动hard
        # a.do1to3Hard() # 刷hard 4-1图, 需已开Hard 4-1
        # a.do11to3Hard() # 刷hard 11-3图，需已开Hard 11图
        a.shouqurenwu()  # 收取任务
        # a.tansuo() # 刷探索,注意mana号没开探索可能会卡死
        if can_shuatu(opcode):  # 仅当刷图被激活(即注明了刷图图号)的账号执行行会捐赠，不刷图的认为是mana号不执行行会捐赠。
            '''
            目前支持刷图图号，（请将需要的图号填入zhanghao.txt）
            'h00': # h00为不刷任何hard图
            'h01': # 刷hard 1-11图
            'tsk': # 探索开,注意mana号没开探索可能会卡死
            'n07': # 刷7图
            'n08': # 刷8图
            'n10': # 刷10图
            'n11': # 刷11图
            'n12': # 刷12图
            '''
            a.shuatu(opcode)  # 刷normal和探索图，需要再zhanghao.txt里注明，不然不会刷
            a.shuatu_hard(opcode)  # 刷hard图，需要再zhanghao.txt里注明，不然不会刷
            a.hanghui()  # 刷图后进行行会捐赠
        else:  # 刷图没有被激活的可以去刷经验
            # a.goumaitili(times=3)  # 购买times次体力
            a.shuajingyan(map=3)  # 刷1-1经验,map为主图
            pass
        a.shouqurenwu()  # 二次收取任务
    except Ellipsis as e:
        pcr_log(account).write_log(level='error', message='main-检测出异常{}'.format(e))


# 主程序
if __name__ == '__main__':
    execute(account_filename, tasks)
