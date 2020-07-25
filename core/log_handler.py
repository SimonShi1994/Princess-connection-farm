import logging
import os
import time

import requests
from sys import stdout

# 临时，等待config的创建
from pcr_config import s_sckey, log_lev

# 各项需要累积的初始化
acc_cout = 0
star_time = 0
end_time = 0


class pcr_log():  # 帐号内部日志（从属于每一个帐号）
    dst_folder = os.path.join(os.getcwd(), 'log')  # 设置日志文件存储位置 位置为log文件夹下

    def __init__(self, acc):  # acc为账户名
        self.acc_name = acc  # 账户名
        # self.clean()

        self.norm_log = logging.getLogger(acc)
        self.norm_log.setLevel('INFO')  # 设置日志级别
        self.norm_hdl_std = logging.StreamHandler(stdout)
        self.norm_hdl_std.setLevel('INFO')  # 设置Handler级别

        self.norm_hdl = logging.FileHandler(os.path.join(self.dst_folder, '%s.log' % (acc)))
        self.norm_hdl.setLevel('INFO')

        self.norm_fomatter = logging.Formatter('%(asctime)s\t%(name)s\t--%(levelname)s\t%(message)s')  # 设置输出格式
        self.norm_hdl_std.setFormatter(self.norm_fomatter)

        self.norm_hdl.setFormatter(self.norm_fomatter)

        self.norm_log.addHandler(self.norm_hdl_std)
        self.norm_log.addHandler(self.norm_hdl)

    def clean(self):
        with open(os.path.join(self.dst_folder, 'Account.log'), 'w')as fp:
            pass

    def write_log(self, level, message):
        lev = level.lower()
        if lev == 'debug':
            self.norm_log.debug(message)
        elif lev == 'info':
            self.norm_log.info(message)
            self.server_bot(lev, message)
        elif lev == 'warning':
            self.norm_log.warning(message)
            self.server_bot(lev, message)
        elif lev == 'error':
            self.norm_log.error(message)
            self.server_bot(lev, message)
        else:
            self.norm_log.critical(message)

    def server_bot(self, s_level, message):
        """
        server酱连接 2020/7/21 by:CyiceK
        s_level 为日志级别
        """
        lev_0 = ['info', 'warning', 'error', '']
        lev_1 = ['warning', 'error', '']
        lev_2 = ['error', '']
        lev_3 = ['']
        lev_dic = {
            '0': lev_0,
            '1': lev_1,
            '2': lev_2,
            '3': lev_3
        }
        tmp_message = ''
        if message != tmp_message and len(s_sckey) != 0:
            # 过滤掉重复信息
            tmp_message = message
            if s_level in lev_dic[log_lev]:
                message = "农场脚本运行信息：%s" % message
                url = "https://sc.ftqq.com/%s.send?text='Princess-connection——公主连结农场脚本'&desp=%s" % (s_sckey, message)
                requests.get(url)


class pcr_acc_log:  # 帐号日志（全局）
    dst_folder = os.path.join(os.getcwd(), 'log')  # 设置日志文件存储位置 位置为log文件夹下

    def __init__(self):
        os.makedirs(self.dst_folder, exist_ok=True)
        with open(os.path.join(self.dst_folder, 'Account.log'), 'w+'):
            pass
        self.acc_log = logging.getLogger('AccountLogger')  # 设置帐号日志
        self.acc_log.setLevel('INFO')  # 设置日志级别
        self.acc_hdl = logging.FileHandler(os.path.join(self.dst_folder, 'Account.log'))  # 输出到文件
        self.acc_hdl.setLevel('INFO')  # 设置Handler级别
        self.acc_fomatter = logging.Formatter('%(asctime)s\t%(name)s\t--%(levelname)s\t%(message)s')  # 设置输出格式
        self.acc_hdl.setFormatter(self.acc_fomatter)
        self.acc_log.addHandler(self.acc_hdl)
        # 以上是账户日志的初始化

    def Account_Logout(self, ac):  # 帐号登出记录
        global acc_cout
        global end_time
        end_time = time.time()
        _time = end_time - star_time
        self.acc_log.info('帐号：' + ac + '成功登出.耗时%s' % _time)
        acc_cout = acc_cout + 1
        pcr_log(ac).server_bot('', message="账号信息：（单个模拟器）第%s个，%s账号完成任务,耗时%s" % (acc_cout, ac, _time))

    def Account_Login(self, ac):  # 帐号登陆记录
        global star_time
        star_time = time.time()
        self.acc_log.info('帐号：' + ac + '成功登录.')
        pcr_log('admin').server_bot('', message="账号信息：%s成功登陆\n" % ac)
