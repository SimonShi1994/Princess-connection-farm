import datetime


class LOG:
    path = ""

    def __init__(self, logfile='AccountRecord.log'):
        self.path = logfile  # 日志文件路径

    def log_init(self):
        with open(self.path, 'w', encoding='utf-8') as fp:  # 打开日志文件，不存在则创建；存在则清空
            pass

    def Account_Logout(self, ac):  # 帐号登出记录
        now_time = datetime.datetime.now()
        now_time_str = datetime.datetime.strftime(now_time, '[%Y-%m-%d %H:%M:%S]')
        with open(self.path, 'a+', encoding='utf-8') as fp:  # append
            fp.write(now_time_str + '\t' + '帐号：' + ac + ' 成功登出.\n')

    def Account_Login(self, ac):  # 帐号登陆记录
        now_time = datetime.datetime.now()
        now_time_str = datetime.datetime.strftime(now_time, '[%Y-%m-%d %H:%M:%S]')
        with open(self.path, 'a+', encoding='utf-8') as fp:  # append
            fp.write(now_time_str + '\t' + '帐号：' + ac + ' 成功登陆.\n')

    def Account_undergroundcity(self, ac):  # 地下城完成记录
        now_time = datetime.datetime.now()
        now_time_str = datetime.datetime.strftime(now_time, '[%Y-%m-%d %H:%M:%S]')
        with open(self.path, 'a+', encoding='utf-8') as fp:  # append
            fp.write(now_time_str + '\t' + '帐号：' + ac + ' 已完成地下城.\n')

    def Account_bad_connecting(self, ac):  # 连接失败记录
        now_time = datetime.datetime.now()
        now_time_str = datetime.datetime.strftime(now_time, '[%Y-%m-%d %H:%M:%S]')
        with open(self.path, 'a+', encoding='utf-8') as fp:  # append
            fp.write(now_time_str + '\t' + '帐号：' + ac + ' connecting/loading失败啦qwq（已重启app）.\n')
