from PCRMoves import PCRMoves
from Automator import *
from MoveRecord import moveset


class AutomatorS:
    """
    稳定执行的Automator
    当程序出现异常强制退出时，再次进入会从上次未执行的地方继续
    含有部分回复逻辑，但
    """

    def __init__(self, a: Automator):
        self.a = a
        self.ms = moveset("moveset")
        # self.ms.seterr("runerr")
        self.ms.startw(None, start=True)
        self.p = PCRMoves(a)

    def start(self):
        return self.ms.nextset(self.p.ms_start())

    def login(self, ac, pwd):
        return self.ms.nextset(self.p.ms_login(ac, pwd))

    def auth(self, auth_name, auth_id):
        return self.ms.nextset(self.p.ms_auth(auth_name, auth_id))

    def tichuhanghui(self):
        return self.ms.nextset(self.p.ms_tichuhanghui())

    def yaoqinghanghui(self, inviteUID):
        return self.ms.nextset(self.p.ms_yaoqinghanghui(inviteUID))

    def jieshouhanghui(self):
        return self.ms.nextset(self.p.ms_jieshouhanghui())

    def joinhanghui(self, clubname):
        return self.ms.nextset(self.p.ms_joinhanghui(clubname))

    def login_auth(self, ac, pwd):
        return self.ms.nextset(self.p.ms_login_auth, ac, pwd)

    def init_home(self):
        return self.ms.nextset(self.p.ms_init_home())

    def sw_init(self):
        return self.ms.nextset(self.p.ms_sw_init())

    def gonghuizhijia(self):
        return self.ms.nextset(self.p.ms_gonghuizhijia())

    def mianfeiniudan(self):
        return self.ms.nextset(self.p.ms_mianfeiniudan())

    def mianfeishilian(self):
        return self.ms.nextset(self.p.ms_mianfeishilian())

    def dianzan(self, sortflag=0):
        return self.ms.nextset(self.p.ms_dianzan(sortflag))

    def shouqu(self):
        return self.ms.nextset(self.p.ms_shouqu())

    def shouqurenwu(self):
        return self.ms.nextset(self.p.ms_shouqurenwu())

    def change_acc(self):
        return self.ms.nextset(self.p.ms_change_acc())

    def goumaitili(self, times):
        return self.ms.nextset(self.p.ms_goumaitili(times))

    def goumaimana(self, times, mode=1):
        return self.ms.nextset(self.p.ms_goumaimana(times, mode))

    def goumaijingyan(self):
        return self.ms.nextset(self.p.ms_goumaijingyan())

    def hanghui(self):
        return self.ms.nextset(self.p.ms_hanghui())

    def shuatuzuobiao(self, x, y, times):
        return self.ms.nextset(self.p.ms_shuatuzuobiao(x, y, times))

    def shuajingyan(self, map):
        return self.ms.nextset(self.p.ms_shuajingyan(map))

    def shuatu8(self):
        return self.ms.nextset(self.p.ms_shuatu8())

    def shuatu10(self):
        return self.ms.nextset(self.p.ms_shuatu10())

    def shuatu11(self):
        return self.ms.nextset(self.p.ms_shuatu11())

    def dixiacheng(self, skip):
        return self.ms.nextset(self.p.ms_dixiacheng(skip))

    def dixiachengzuobiao(self, x, y, auto, team=0):
        return self.ms.nextset(self.p.ms_dixiachengzuobiao(x, y, auto, team))

    def tansuo(self, mode=0):
        return self.ms.nextset(self.p.ms_tansuo(mode))

    def dixiachengDuanya(self):
        return self.ms.nextset(self.p.ms_dixiachengDuanya())

    def shoushuazuobiao(self, x, y, jiaocheng, lockpic, screencut):
        return self.ms.nextset(self.p.ms_shoushuazuobiao(x, y, jiaocheng, lockpic, screencut))

    def chulijiaocheng(self):
        return self.ms.nextset(self.p.ms_chulijiaocheng())

    def qianghua(self):
        return self.ms.nextset(self.p.ms_qianghua())

    def setting(self):
        return self.ms.nextset(self.p.ms_setting())

    def run(self, addr="rec"):
        """
        运行设置好的脚本。
        :param addr: 运行信息存储目录
        """
        self.ms.exitw(None)
        outms = moveset(self.a.account)  # 以账户名称创建记录文件
        # outms.addcatch("runerr",999)  # 异常处理
        outms.startw(None, start=True, start_id=0)
        outms.exitset(self.ms)
        outms.run(addr)
