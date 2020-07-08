import datetime
class LOG:
    path = ""

    def __init__(self, logfile='AccountRecord.txt'):
        with open(logfile, 'w', encoding='utf-8') as fp:  # 打开日志文件，不存在则创建；存在则清空
            pass
        self.path = logfile  # 日志文件路径

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
