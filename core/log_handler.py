import logging
import os
from sys import stdout


class pcr_log:  # 帐号内部日志（从属于每一个帐号）
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
        elif lev == 'warning':
            self.norm_log.warning(message)
        elif lev == 'error':
            self.norm_log.error(message)
        else:
            self.norm_log.critical(message)


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
        self.acc_log.info('帐号：' + ac + '成功登出.')

    def Account_Login(self, ac):  # 帐号登陆记录
        self.acc_log.info('帐号：' + ac + '成功登录.')
