import datetime
import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler

import colorlog  # 控制台日志输入颜色
from sys import stdout

from core.bot import Bot

# 各项需要累积的初始化
from core.pcr_config import debug, colorlogsw, write_debug_to_log, do_not_show_debug_if_in_these_files, \
    skip_codename_output_if_in_these_files, show_codename_in_log, show_linenumber_in_log, show_filename_in_log

acc_cout = 0
star_time = 0
end_time = 0


class pcr_log():  # 帐号内部日志（从属于每一个帐号）
    dst_folder = os.path.join(os.getcwd(), 'log')  # 设置日志文件存储位置 位置为log文件夹下
    acc_message = {}
    log_colors_config = {
        'DEBUG': 'cyan',
        'INFO': 'purple',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }

    def __init__(self, acc):  # acc为账户名
        # 此处为兼容连接
        self._bot = Bot()
        self.server_bot = self._bot.server_bot
        os.makedirs("log", exist_ok=True)
        self.acc_name = acc  # 账户名
        # self.acc_message[self.acc_name] = []
        # self.clean()

        self.norm_log = logging.getLogger(acc)
        self.norm_log.setLevel('DEBUG')  # 设置日志级别
        self.norm_hdl_std = logging.StreamHandler(stdout)
        if debug:
            self.norm_hdl_std.setLevel('DEBUG')  # 设置Handler级别
        else:
            self.norm_hdl_std.setLevel('INFO')  # 设置Handler级别

        # self.norm_hdl = logging.FileHandler(os.path.join(self.dst_folder, '%s.log' % acc), encoding='utf-8')
        # self.norm_hdl.setLevel('INFO')

        if colorlogsw:
            self.norm_fomatter = colorlog.ColoredFormatter('%(log_color)s[%(asctime)s] '
                                                           '%(message)s',
                                                           log_colors=self.log_colors_config)
        else:
            self.norm_fomatter = logging.Formatter('%(asctime)s\t%(name)s\t--%(levelname)s\t%(message)s')  # 设置输出格式

        # 创建一个FileHandler，用于写到本地
        self.fhbacker = RotatingFileHandler(filename=os.path.join(self.dst_folder, '%s.log' % acc),
                                            mode='a+', maxBytes=1024 * 1024 * 5, backupCount=5,
                                            encoding='utf-8')  # 使用RotatingFileHandler类，滚动备份日志
        self.fhbacker.setLevel('DEBUG')
        self.fhbacker.setFormatter(self.norm_fomatter)

        self.norm_hdl_std.setFormatter(self.norm_fomatter)
        # self.norm_hdl.setFormatter(self.norm_fomatter)

        if not self.norm_log.handlers:
            self.norm_log.addHandler(self.norm_hdl_std)
            # self.norm_log.addHandler(self.norm_hdl)
            self.norm_log.addHandler(self.fhbacker)
        else:
            self.norm_log.removeHandler(self.norm_hdl_std)
        #     # self.norm_log.removeHandler(self.norm_hdl)
            self.norm_log.removeHandler(self.fhbacker)
            self.norm_log.addHandler(self.norm_hdl_std)
        #     # self.norm_log.addHandler(self.norm_hdl)
            self.norm_log.addHandler(self.fhbacker)

    def get_log_object(self, _name):
        if logging.getLogger(_name):
            return logging.getLogger(_name)
        else:
            return None

    def exist_log_handles(self):
        if self.norm_log.handlers:
            return True
        else:
            return False

    def get_file_sorted(self, file_path):
        """最后修改时间顺序升序排列 os.path.getmtime()->获取文件最后修改时间"""
        dir_list = os.listdir(file_path)
        if not dir_list:
            return
        else:
            dir_list = sorted(dir_list, key=lambda x: os.path.getmtime(os.path.join(file_path, x)))
            return dir_list

    def TimeStampToTime(self, timestamp):
        """格式化时间"""
        timeStruct = time.localtime(timestamp)
        return str(time.strftime('%Y-%m-%d', timeStruct))

    def handle_logs(self):
        """处理日志过期天数和文件数量"""
        dir_list = ['log']  # 要删除文件的目录名
        for dir in dir_list:
            dirPath = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + '\\' + dir  # 拼接删除目录完整路径
            file_list = self.get_file_sorted(dirPath)  # 返回按修改时间排序的文件list
            if file_list:  # 目录下没有日志文件
                for i in file_list:
                    file_path = os.path.join(dirPath, i)  # 拼接文件的完整路径
                    t_list = self.TimeStampToTime(os.path.getctime(file_path)).split('-')
                    now_list = self.TimeStampToTime(time.time()).split('-')
                    t = datetime.datetime(int(t_list[0]), int(t_list[1]),
                                          int(t_list[2]))  # 将时间转换成datetime.datetime 类型
                    now = datetime.datetime(int(now_list[0]), int(now_list[1]), int(now_list[2]))
                    if (now - t).days > 6:  # 创建时间大于6天的文件删除
                        self.delete_logs(file_path)
                if len(file_list) > 4:  # 限制目录下记录文件数量
                    file_list = file_list[0:-4]
                    for i in file_list:
                        file_path = os.path.join(dirPath, i)
                        # print(file_path)
                        self.delete_logs(file_path)

    def delete_logs(self, file_path):
        try:
            os.remove(file_path)
            # print(file_path)
        except PermissionError as e:
            # self.norm_log.error('删除日志文件失败：{}'.format(e))
            pass

    def write_log(self, level, message):
        """
        :param message: str
        :param level: debug/info/warning/error|critical
        """

        frame = sys._getframe().f_back
        funcName = frame.f_code.co_name
        lineNumber = frame.f_lineno
        fileName = frame.f_code.co_filename
        show_funcName = show_codename_in_log
        show_lineNumber = show_linenumber_in_log
        show_fileName = show_filename_in_log

        # print(">>>",level,message)

        if level == 'debug':
            for badfile in do_not_show_debug_if_in_these_files:
                if fileName.endswith(badfile):
                    return

        while frame is not None:
            flag = True
            for skipfile in skip_codename_output_if_in_these_files:
                if fileName.endswith(skipfile):
                    frame = frame.f_back
                    funcName = frame.f_code.co_name
                    lineNumber = frame.f_lineno
                    fileName = frame.f_code.co_filename
                    flag = False
                    break
            if flag:
                break
        else:
            show_funcName = False
            show_lineNumber = False
            show_fileName = False

        pre_format = []
        pre_format.append("[")
        if show_fileName:
            filename_str = os.path.split(fileName)[1]
            pre_format.append(f"{filename_str}")
        if show_fileName and show_funcName:
            pre_format.append("/")
        if show_funcName:
            pre_format.append(funcName)
        if show_lineNumber:
            pre_format.append(f":{lineNumber}")
        pre_format.append("]")
        if len(pre_format)==2:
            pre_format_str = ""
        else:
            pre_format_str = "".join(pre_format)
        if level == "debug" and not write_debug_to_log:
            print("DEBUG:",pre_format_str,message)
            return
        lev = level.lower()
        msg_format = f'{pre_format_str} [{lev}]-\t{message}'
        if lev == 'debug':
            self.norm_log.debug(msg=msg_format)
        elif lev == 'info':
            self.norm_log.info(msg=msg_format)
            self.server_bot(s_level=lev, message=message)
        elif lev == 'warning':
            self.norm_log.warning(msg=msg_format)
            self.server_bot(s_level=lev, message=message)
        elif lev == 'error':
            self.norm_log.error(msg=msg_format)
            pcr_log("__ERROR_LOG__").write_log("info", f"账号 {self.acc_name} ： {message}")
            self.server_bot(s_level=lev, message=message)
        else:
            self.norm_log.critical(msg=msg_format)


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
