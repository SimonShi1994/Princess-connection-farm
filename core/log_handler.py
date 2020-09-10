import logging
import os
import time
from sys import stdout

import psutil
import requests

# 临时，等待config的创建
from core.pcr_config import s_sckey, log_lev, log_cache

# 各项需要累积的初始化
acc_cout = 0
star_time = 0
end_time = 0


class pcr_log():  # 帐号内部日志（从属于每一个帐号）
    dst_folder = os.path.join(os.getcwd(), 'log')  # 设置日志文件存储位置 位置为log文件夹下
    acc_message = {}

    def __init__(self, acc):  # acc为账户名
        os.makedirs("log", exist_ok=True)
        self.acc_name = acc  # 账户名
        self.acc_message[self.acc_name] = []
        # self.clean()

        self.norm_log = logging.getLogger(acc)
        self.norm_log.setLevel('INFO')  # 设置日志级别
        self.norm_hdl_std = logging.StreamHandler(stdout)
        self.norm_hdl_std.setLevel('INFO')  # 设置Handler级别

        self.norm_hdl = logging.FileHandler(os.path.join(self.dst_folder, '%s.log' % (acc)), encoding='utf-8')
        self.norm_hdl.setLevel('INFO')

        self.norm_fomatter = logging.Formatter('%(asctime)s\t%(name)s\t--%(levelname)s\t%(message)s')  # 设置输出格式
        self.norm_hdl_std.setFormatter(self.norm_fomatter)

        self.norm_hdl.setFormatter(self.norm_fomatter)
        if not self.norm_log.handlers:
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
            pcr_log("__ERROR_LOG__").write_log("info", f"账号 {self.acc_name} ： {message}")
            self.server_bot(lev, message)
        else:
            self.norm_log.critical(message)

    def server_bot(self, s_level, message='', acc_state=''):
        """
        server酱连接 2020/7/21 by:CyiceK
        s_level 为日志级别
        """
        # 日志级别所区分的头
        # STATE头为任务状态头，发送及包含STATE
        lev_0 = ['info', 'warning', 'error', 'STATE', '']
        lev_1 = ['warning', 'error', 'STATE', '']
        lev_2 = ['error', 'STATE', '']
        # 3为0级消息，是消息队列的最高级别,无视log_cache堵塞
        lev_3 = ['STATE', '']
        # 日志级别
        lev_dic = {
            '0': lev_0,
            '1': lev_1,
            '2': lev_2,
            '3': lev_3
        }
        # 先不填acc_state
        if len(s_sckey) != 0:
            message = ''.join(message).replace('\n', '')
            if s_level in lev_dic[log_lev]:
                self.acc_message.setdefault(self.acc_name,[])
                self.acc_message[self.acc_name].append(message)
                self.acc_message[self.acc_name].append('\n')
            # print(self.acc_message[self.acc_name])
            # print(len(self.acc_message[self.acc_name]))
            if s_level in lev_dic['3'] or (
                    s_level in lev_dic[log_lev] and len(self.acc_message[self.acc_name]) >= log_cache):
                message = ''.join(self.acc_message[self.acc_name]).replace(',', '\n').replace("'", '')
                # print(message)
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_info = "CPU使用率：%i%%" % cpu_percent
                # print(cpu_info)
                virtual_memory = psutil.virtual_memory()
                used_memory = virtual_memory.used / 1024 / 1024 / 1024
                free_memory = virtual_memory.free / 1024 / 1024 / 1024
                memory_percent = virtual_memory.percent
                memory_info = "内存使用：%0.2fG||使用率%0.1f%%||剩余内存：%0.2fG" % (used_memory, memory_percent, free_memory)
                # print(memory_info)
                info = {
                    'text': 'Princess-connection——公主连结农场脚本',
                    'desp': '#### 系统运行信息：\n- %s\n- %s\n\n------\n\n农场信息：\n\n```\n\n%s\n\n%s\n\n```\n\n'
                            '来自GITHUB一款开源脚本: https://github.com/SimonShi1994/Princess-connection-farm\n\n ' % (
                                cpu_info, memory_info, message, acc_state)

                }
                url = "https://sc.ftqq.com/%s.send" % s_sckey
                try:
                    requests.get(url, params=info)
                except Exception as e:
                    pcr_log("__SERVER_BOT__").write_log("error", f"ServerBot发送失败：{e}")
                # 不因为0级消息而清空消息队列
                if s_level not in lev_dic['3']:
                    # 发送完后清空消息队列
                    self.acc_message = {}


class pcr_acc_log:  # 帐号日志（全局）
    dst_folder = os.path.join(os.getcwd(), 'log')  # 设置日志文件存储位置 位置为log文件夹下

    def __init__(self):
        os.makedirs(self.dst_folder, exist_ok=True)
        with open(os.path.join(self.dst_folder, 'Account.log'), 'w+'):
            pass
        self.acc_log = logging.getLogger('AccountLogger')  # 设置帐号日志
        self.acc_log.setLevel('INFO')  # 设置日志级别
        self.acc_hdl = logging.FileHandler(os.path.join(self.dst_folder, 'Account.log'), encoding='utf-8')  # 输出到文件
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
        # pcr_log(ac).server_bot('', message="账号信息：（单个模拟器）第%s个，%s账号完成任务,耗时%s" % (acc_cout, ac, _time))

    def Account_Login(self, ac):  # 帐号登陆记录
        global star_time
        star_time = time.time()
        self.acc_log.info('帐号：' + ac + '成功登录.')
        # pcr_log('admin').server_bot('', message="账号信息：%s成功登陆\n" % ac)
