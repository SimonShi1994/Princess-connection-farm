import CreateUser as cu
import core.usercentre as uc
import os
import shutil
import main
import re
from core.log_handler import pcr_log
from guild_40to1_resource.guild_setting import *

def create_daily_task():
    """
    创建公会日常任务
    """
    print("----------------写入日常任务 start---------------")
    if task_name_daily in cu.list_all_tasks():
        cu.del_task(task_name_daily)
    cu.create_task(task_name_daily)
    # 读取引用的日常任务
    obj_ref = uc.AutomatorRecorder.gettask(task_name_refer)
    # 写入
    uc.AutomatorRecorder.settask(task_name_daily, obj_ref)
    print("----------------写入日常任务 end---------------")


def create_switch_guild_task():
    """
    创建切换公会任务（分为两个任务，加入公会1和加入公会2）
    """
    print("----------------写入切换公会任务 start---------------")
    # 如果存在任务，则删除
    if task_goto_guild2 in cu.list_all_tasks():
        cu.del_task(task_goto_guild2)
    if task_goto_guild1 in cu.list_all_tasks():
        cu.del_task(task_goto_guild1)
    if task_remove_guild in cu.list_all_tasks():
        cu.del_task(task_remove_guild)

    # 修改行会名称
    def write_the_guild_name(guild_name, task_path):
        f1 = open(task_path, 'r', encoding='UTF-8')
        content = f1.read()
        f1.close()
        t = re.sub(r'"clubname": ".*?"', '"clubname": "' + guild_name + '"', content)
        # t = content.replace('hangHuiMingCheng',guild_name)
        with open(task_path, 'w', encoding='UTF-8') as f:
            f.write(t)

    write_the_guild_name(guild1_name, task_goto_guild1_path)
    write_the_guild_name(guild2_name, task_goto_guild2_path)

    shutil.copy(task_goto_guild2_path, './tasks/' + task_goto_guild2 + '.txt')
    shutil.copy(task_goto_guild1_path, './tasks/' + task_goto_guild1 + '.txt')
    shutil.copy(task_remove_guild_path, './tasks/' + task_remove_guild + '.txt')
    print("----------------写入切换公会任务 end---------------")


def bak_accounts():
    """
    备份用户信息
    """
    # 用户信息路径
    users_path = './users'
    # 用户备份路径
    users_bak_path = './users_bak'
    if not os.path.exists(users_path):
        return
    if os.path.exists(users_bak_path):
        shutil.rmtree(users_path)
        return
    shutil.copytree(users_path, users_bak_path)


def resume_accounts():
    """
    还原用户信息
    """
    # 用户信息路径
    users_path = './users'
    # 用户备份路径
    users_bak_path = './users_bak'
    shutil.rmtree(users_path)
    shutil.copytree(users_bak_path, users_path)
    shutil.rmtree(users_bak_path)


def log_by_admin(message, level='info'):
    """
    日志输出工具函数
    以admin身份输出日志到文件与控制台
    """
    pcr_log('admin').write_log(level=level, message=message)
    pcr_log('admin').server_bot('', message)


if __name__ == "__main__":
    create_daily_task()
    create_switch_guild_task()

    # 先备份原用户数据
    log_by_admin('备份用户数据')
    bak_accounts()

    # 导入公会1数据
    cu.del_all_account()
    log_by_admin('导入公会1数据')
    cu.create_account_from_file(guild1_info)
    # 开始公会1
    log_by_admin('开始运行公会1')
    main.RunFirstTime()

    # 踢出公会
    cu.del_all_account()
    log_by_admin('导入公会2会长数据')
    cu.create_account(account_guild2_name, account_guild2_pwd, task_remove_guild)
    log_by_admin('开始踢出公会2')
    main.RunFirstTime()

    # 切换大号，去公会一
    cu.del_all_account()
    log_by_admin('导入大号数据')
    cu.create_account(account_name, account_pwd, task_goto_guild1)
    log_by_admin('开始加入公会1')
    main.RunFirstTime()

    # 还原用户数据
    log_by_admin('开始还原用户数据')
    resume_accounts()

    log_by_admin('全部完成！')
