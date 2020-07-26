from core.Automator import Automator
from initialize import execute, can_shuatu

# 仅适用于zhanghao.txt里面的帐号，可以判断是农场号，还是要捐装备的号
# 根据zhanghao.txt里边的帐号是否有标注图号（也就是第三个参数）来确定是不是捐装备的号
# 如果是农场号就没有动作，如果是要捐装备的号就登录游戏捐装备
account_filename = "zhanghao.txt"


# 过滤mana号 （在zhanghao.txt中没注明刷图图号的账号）
def acc_filter(acc_dic: dict, opcode_dic: dict):
    filter_acc_dic = dict()
    for acc_name, opcode in opcode_dic.items():
        if can_shuatu(opcode):
            filter_acc_dic[acc_name] = acc_dic[acc_name]
    return filter_acc_dic


def tasks(automator: Automator, opcode):
    # 主功能体函数，可以在本函数中自定义需要的功能
    automator.init_home()  # 初始化，确保进入首页
    automator.hanghui()  # 行会捐赠


# 主程序
if __name__ == '__main__':
    execute(account_filename, tasks, acc_filter)  # 如果不想过滤mana账号，可以把acc_filter去除
