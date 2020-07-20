import time

from core.Automator import *
from core.MoveRecord import moveset
from core.cv import UIMatcher
from core.utils import random_name, CreatIDnum


def OneFun(ms: moveset, fun, *args, **kwargs):
    ms.startw(None, start=True)
    ms.exitw(fun, *args, kwargs=kwargs)


class PCRMoves:
    def __init__(self, a: Automator):
        self.a = a

    def ms_menu_home(self):
        # 回到主页
        ms = moveset("menu_home")

        def f(self: Automator):
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=0.5)  # 回首页

        OneFun(ms, f, self.a)
        return ms

    def ms_menu_hanghui(self, first=False):
        # 点击行会按钮，如果还未加入行会，则first=True
        ms = moveset("menu_hanghui")

        def f(self: Automator):
            self.lockimg('img/hanghui.bmp', elseclick=[(693, 436)], elsedelay=1)  # 锁定进入行会
            time.sleep(1)
            if first:
                self.lockimg('img/zujianhanghui.bmp', elseclick=[(1, 1)])  # 锁定行会界面
            else:
                self.lockimg('img/zhiyuansheding.bmp', elseclick=[(1, 1)])

        OneFun(ms, f, self.a)
        return ms

    def ms_tichuhanghui(self):
        ms = moveset("tichuhanghui")
        OneFun(ms, self.a.tichuhanghui)
        return ms

    def ms_yaoqinghanghui(self, inviteUID):
        ms = moveset("yaoqinghanghui")

        return ms

    def ms_jieshouhanghui(self):
        ms = moveset("jieshouhanghui")

        def Part1(self: Automator):
            self.d.click(687, 35)  # 点击邀请列表
            time.sleep(1)
            self.d.click(704, 170)  # 点击邀请列表
            self.lockimg('img/jiaru.bmp', ifclick=[(839, 443)], ifdelay=1)  # 点击加入
            self.lockimg('img/ok.bmp', ifclick=[(597, 372)], ifdelay=1)  # 点击ok
            time.sleep(1)

        def Part2(self: Automator):
            self.lockimg('img/ok.jpg')  # 锁定ok
            screen_shot_ = self.d.screenshot(format="opencv")
            self.guochang(screen_shot_, ['img/ok.jpg'], suiji=0)

        def Part3(self: Automator):
            self.lockimg('img/zhiyuansheding.bmp', ifclick=[(85, 350)], alldelay=0.5)  # 点击支援设定
            self.lockimg('img/zhiyuanjiemian.bmp', elseclick=[(1, 1)], alldelay=0.5)  # 锁定支援界面
            self.d.click(109, 234)  # 点击支援
            time.sleep(1)

        def Part4A(self: Automator):
            self.lockimg('img/quxiao3.bmp', ifclick=[(739, 91)], ifdelay=1)  # 点击排序设定
            self.lockimg('img/ok.bmp', ifclick=[(291, 142), (588, 483)], ifdelay=1)  # 点击战力和ok
            self.lockimg('img/quxiao3.bmp', ifclick=[(109, 175)], ifdelay=1)  # 点击第一个人
            time.sleep(1)
            self.d.click(833, 456)  # 点击设定

        def Part5(self: Automator):
            self.lockimg('img/ok.bmp', ifclick=[(591, 440)], ifdelay=1)  # 点击ok

        def Part4B(self: Automator):
            self.lockimg('img/zhiyuanjiemian.bmp', ifclick=[(105, 356)], ifdelay=1)  # 点击第二个+号
            self.lockimg('img/quxiao3.bmp', ifclick=[(109, 175)], ifdelay=1)  # 点击第一个人
            time.sleep(1)
            self.d.click(833, 456)  # 点击设定

        ENT = ms.startw(None)
        ms.T_forcestart(ENT)  # 强制从开头执行
        ms.T_ifnotflag("JRHH")  # 如果没有加入行会
        ms.nextset(self.ms_menu_hanghui(True))  # 点击行会
        ms.nextw(Part1, self.a)  # 接受邀请
        ms.T_nextflag("JRHH")
        ms.nextw(Part2, self.a)  # 点确定
        ms.T_else()  # 如果已经接受过邀请
        ms.nextset(self.ms_menu_hanghui(False))  # 点击行会
        ms.T_end()
        ms.nextw(Part3, self.a)  # 点击支援设定
        ms.T_ifnotflag("ZY1")  # 支援第一人
        ms.nextw(Part4A, self.a)
        ms.T_nextflag("ZY1")
        ms.nextw(Part5, self.a)  # 点确认
        ms.T_end()
        ms.T_ifnotflag("ZY2")  # 支援第二人
        ms.nextw(Part4B, self.a)
        ms.T_nextflag("ZY2")
        ms.nextw(Part5, self.a)
        ms.T_end()
        ms.nextset(self.ms_menu_home())  # 回主页
        ms.T_clearflags()
        return ms

    def ms_joinhanghui(self, clubname):
        def Part1(self: Automator):
            print('>>>>>>>即将加入公会名为：', clubname, '<<<<<<<')
            self.d.click(860, 81)  # 点击设定
            self.lockimg('img/quxiao2.jpg', ifclick=[(477, 177)], ifdelay=1)  # 点击输入框
            self.d.send_keys(clubname)
            time.sleep(1)
            self.d.click(1, 1)
            time.sleep(1)
            self.d.click(587, 432)
            time.sleep(5)
            self.d.click(720, 172)
            time.sleep(1)
            self.lockimg('img/jiaru.bmp', ifclick=[(839, 443)], ifdelay=1)  # 点击加入

        def Part2(self: Automator):
            self.lockimg('img/ok.jpg', ifclick=[(597, 372)], ifdelay=1)  # 点击ok

        ms = moveset("joinhanghui")
        ms.T_forcestart(ms.startw(None))
        ms.T_ifnotflag("FIN")
        ms.nextset(self.ms_menu_hanghui(True))
        ms.nextw(Part1, self.a)
        ms.T_nextflag("FIN")
        ms.nextw(Part2, self.a)
        ms.nextset(self.ms_menu_home())  # 回主页
        ms.T_end()
        ms.T_clearflags()
        return ms

    def ms_login_auth(self, ac, pwd):
        def Part(self: Automator):
            need_auth = self.login(ac=ac, pwd=pwd)
            if need_auth:
                auth_name, auth_id = random_name(), CreatIDnum()
                self.auth(auth_name=auth_name, auth_id=auth_id)

        ms = moveset("login_auth")
        OneFun(ms, Part, self.a)

    def ms_init_home(self):
        ms = moveset("init_home")
        OneFun(ms, self.a.init_home)
        return ms

    def ms_sw_init(self):
        ms = moveset("sw_init")
        OneFun(ms, self.a.sw_init)
        return ms

    def ms_gonghuizhijia(self):
        ms = moveset("gonghuizhijia")
        OneFun(ms, self.a.gonghuizhijia)
        return ms

    def ms_mianfeiniudan(self):
        ms = moveset("mianfeiniudan")
        OneFun(ms, self.a.mianfeiniudan)
        return ms

    def ms_mianfeishilian(self):
        ms = moveset("mianfeishilian")
        OneFun(ms, self.a.mianfeishilian)
        return ms

    def ms_dianzan(self, sortflag=0):
        ms = moveset("dianzan")
        OneFun(ms, self.a.dianzan, sortflag=sortflag)
        return ms

    def ms_shouqu(self):
        ms = moveset("shouqu")
        OneFun(ms, self.a.shouqu)
        return ms

    def ms_shouqurenwu(self):
        ms = moveset("shouqurenwu")
        OneFun(ms, self.a.shouqurenwu)
        return ms

    def ms_change_acc(self):
        ms = moveset("change_acc")
        OneFun(ms, self.a.change_acc)
        return ms

    def ms_goumaitili(self, times):
        ms = moveset("goumaitili")
        ms.addvar("now", 0)  # 当前购买次数
        A = ms.startw(self.a.goumaitili, kwargs=dict(times=1), start=True)
        ms.nextwv("var['now']+=1")
        ms.endif(lambda var: var['now'] < times, A, "__exit__")
        return ms

    def ms_goumaimana(self, times, mode=1):
        ms = moveset("goumaimana")

        def Part1(self: Automator):
            time.sleep(2)
            self.d.click(189, 62)

        def Part2A(self: Automator):
            self.lockimg('img/quxiao2.jpg', elseclick=(189, 62), alldelay=2)
            self.d.click(596, 471)  # 第一次购买的位置

        def Part2B(self: Automator):
            self.lockimg('img/quxiao2.jpg', alldelay=3)
            self.d.click(816, 478)  # 购买10次

        def PartOK(self: Automator):
            while True:  # 锁定ok
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                    self.guochang(screen_shot_, ['img/ok.bmp'], suiji=0)
                    break

        if mode == 1:
            times += 1  # 十连多算之前抽的一次
        ENT = ms.startset(self.ms_menu_home())
        ms.T_forcestart(ENT)  # 强制回到主页
        ms.addvar("now", 0)  # 购买次数统计
        ms.nextw(Part1, self.a)  # 进入购买页面
        ms.T_ifflag("now", 0)
        ms.nextw(Part2A, self.a)  # 购买一次一连
        ms.nextwv("var['now']+=1")
        ms.nextw(PartOK, self.a)
        A = ms.T_end()
        ms.T_ifflag("now", times, "<")
        if mode == 0:
            ms.nextw(Part2A, self.a)  # 抽取1连
        else:
            ms.nextw(Part2B, self.a)  # 抽取10连
        ms.nextwv("var['now']+=1")  # 计数器+1
        ms.nextw(PartOK, self.a)  # 点确定
        ms.endw(None, next_id=A)
        ms.T_end()
        ms.exitset(self.ms_menu_home())
        return ms

    def ms_goumaijingyan(self):
        ms = moveset("goumaijingyan")
        OneFun(ms, self.a.goumaijingyan)
        return ms

    def ms_hanghui(self):
        ms = moveset("hanghui")
        OneFun(ms, self.a.hanghui)
        return ms

    def ms_shuatuzuobiao(self, x, y, times):
        # 这一段逻辑太复杂了，暂时原样照抄
        ms = moveset("shuatuzuobiao")
        OneFun(ms, self.a.shuatuzuobiao, x, y, times)
        return ms

    def ms_shuajingyan(self, map):
        ms = moveset("shuajingyan")
        OneFun(ms, self.a.shuajingyan, map)
        return ms

    def ms_shuatu8(self):
        def PartIN(self: Automator):
            # 进入冒险
            time.sleep(2)
            self.d.click(480, 505)
            time.sleep(2)
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                    break
            self.d.click(562, 253)
            time.sleep(2)
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/normal.jpg'):
                    break

        def PartDragRight(self: Automator):
            self.d.drag(600, 270, 200, 270, 0.1)
            time.sleep(2)

        def PartDragLeft(self: Automator):
            self.d.drag(200, 270, 600, 270, 0.1)  # 拖拽到最左
            time.sleep(2)

        def AddShua(ms, x, y):
            ms.nextset(self.ms_shuatuzuobiao, x, y, self.a.times)

        msl = moveset("subleft")  # 左半边
        msl.onstart(9999)
        msl.startw(PartDragRight, self.a, start_id=9999)  # 进去先拖拽
        msl.endw(None, next_id="__last__")
        msl.startw(None, start=True)
        AddShua(msl, 584, 260)
        AddShua(msl, 715, 319)
        AddShua(msl, 605, 398)
        AddShua(msl, 478, 374)
        AddShua(msl, 357, 405)
        AddShua(msl, 263, 324)
        AddShua(msl, 130, 352)
        msl.exitw(None)
        msr = moveset("subright")  # 右半边
        msr.onstart(9999)
        msr.startw(PartDragLeft, self.a, start_id=9999)  # 进去先拖拽
        msr.endw(None, next_id="__last__")
        msr.startw(None, start=True)
        AddShua(msr, 580, 401)
        AddShua(msr, 546, 263)
        AddShua(msr, 457, 334)
        AddShua(msr, 388, 240)
        AddShua(msr, 336, 314)
        AddShua(msr, 230, 371)
        AddShua(msr, 193, 255)
        msr.exitw(None)
        ms = moveset("shuatu8")
        ENT = ms.startw(PartIN, self.a)
        ms.T_forcestart(ENT)
        ms.T_ifnotflag("FINL")
        ms.nextset(msl)
        ms.T_nextflag("FINL")
        ms.T_end()
        ms.T_ifnotflag("FINR")
        ms.nextset(msr)
        ms.T_nextflag("FINR")
        ms.T_end()
        ms.exitset(self.ms_menu_home())
        return ms

    def ms_shuatu10(self):
        def PartIN(self: Automator):
            # 进入冒险
            time.sleep(2)
            self.d.click(480, 505)
            time.sleep(2)
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                    break
            self.d.click(562, 253)
            time.sleep(5)
            for _ in range(1):
                # 左移到10图
                self.d.click(27, 272)
                time.sleep(3)
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/normal.jpg'):
                    break

        def PartDragRight(self: Automator):
            self.d.drag(600, 270, 200, 270, 0.1)
            time.sleep(2)

        def PartDragLeft(self: Automator):
            self.d.drag(200, 270, 600, 270, 0.1)  # 拖拽到最左
            time.sleep(2)

        def AddShua(ms, x, y):
            ms.nextset(self.ms_shuatuzuobiao, x, y, self.a.times)

        msl = moveset("subleft")  # 左半边
        msl.onstart(9999)
        msl.startw(PartDragRight, self.a, start_id=9999)  # 进去先拖拽
        msl.endw(None, next_id="__last__")
        msl.startw(None, start=True)
        AddShua(msl, 821, 299)
        AddShua(msl, 703, 328)
        AddShua(msl, 608, 391)
        AddShua(msl, 485, 373)
        AddShua(msl, 372, 281)
        AddShua(msl, 320, 421)
        AddShua(msl, 172, 378)
        AddShua(msl, 251, 235)
        AddShua(msl, 111, 274)
        msl.exitw(None)
        msr = moveset("subright")  # 右半边
        msr.onstart(9999)
        msr.startw(PartDragLeft, self.a, start_id=9999)  # 进去先拖拽
        msr.endw(None, next_id="__last__")
        msr.startw(None, start=True)
        AddShua(msr, 690, 362)
        AddShua(msr, 594, 429)
        AddShua(msr, 411, 408)
        AddShua(msr, 518, 332)
        AddShua(msr, 603, 238)
        AddShua(msr, 430, 239)
        AddShua(msr, 287, 206)
        AddShua(msr, 146, 197)
        msr.exitw(None)
        ms = moveset("shuatu10")
        ENT = ms.startw(PartIN, self.a)
        ms.T_forcestart(ENT)
        ms.T_ifnotflag("FINL")
        ms.nextset(msl)
        ms.T_nextflag("FINL")
        ms.T_end()
        ms.T_ifnotflag("FINR")
        ms.nextset(msr)
        ms.T_nextflag("FINR")
        ms.T_end()
        ms.exitset(self.ms_menu_home())
        return ms

    def ms_shuatu11(self):
        def PartIN(self: Automator):
            # 进入冒险
            time.sleep(2)
            self.d.click(480, 505)
            time.sleep(2)
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                    break
            self.d.click(562, 253)
            time.sleep(2)
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/normal.jpg'):
                    break

        def PartDragRight(self: Automator):
            self.d.drag(600, 270, 200, 270, 0.1)
            time.sleep(2)

        def PartDragLeft(self: Automator):
            self.d.drag(200, 270, 600, 270, 0.1)  # 拖拽到最左
            time.sleep(2)

        def AddShua(ms, x, y):
            ms.nextset(self.ms_shuatuzuobiao, x, y, self.a.times)

        msl = moveset("subleft")  # 左半边
        msl.onstart(9999)
        msl.startw(PartDragRight, self.a, start_id=9999)  # 进去先拖拽
        msl.endw(None, next_id="__last__")
        msl.startw(None, start=True)
        AddShua(msl, 663, 408)
        AddShua(msl, 542, 338)
        AddShua(msl, 468, 429)
        AddShua(msl, 398, 312)
        AddShua(msl, 302, 428)
        AddShua(msl, 182, 362)
        AddShua(msl, 253, 237)
        AddShua(msl, 107, 247)
        msl.exitw(None)
        msr = moveset("subright")  # 右半边
        msr.onstart(9999)
        msr.startw(PartDragLeft, self.a, start_id=9999)  # 进去先拖拽
        msr.endw(None, next_id="__last__")
        msr.startw(None, start=True)
        AddShua(msr, 648, 316)
        AddShua(msr, 594, 420)
        AddShua(msr, 400, 432)
        AddShua(msr, 497, 337)
        AddShua(msr, 558, 240)
        AddShua(msr, 424, 242)
        AddShua(msr, 290, 285)
        AddShua(msr, 244, 412)
        msr.exitw(None)
        ms = moveset("shuatu8")
        ENT = ms.startw(PartIN, self.a)
        ms.T_forcestart(ENT)
        ms.T_ifnotflag("FINL")
        ms.nextset(msl)
        ms.T_nextflag("FINL")
        ms.T_end()
        ms.T_ifnotflag("FINR")
        ms.nextset(msr)
        ms.T_nextflag("FINR")
        ms.T_end()
        ms.exitset(self.ms_menu_home())
        return ms

    def ms_dixiacheng(self, skip):
        # 逻辑太复杂，暂时不细写
        ms = moveset("dixiacheng")
        OneFun(ms, self.a.dixiacheng, skip)
        return ms

    def ms_dixiachengzuobiao(self, x, y, auto, team=0):
        # 逻辑太复杂，暂时不细写
        ms = moveset("dixiachengzuobiao")
        OneFun(ms, self.a.dixiachengzuobiao, x, y, auto, team)
        return ms

    def ms_tansuo(self, mode=0):
        # 逻辑太复杂，暂时不细写
        ms = moveset("tansuo")
        OneFun(ms, self.a.tansuo, mode)
        return ms

    def ms_dixiachengDuanya(self):
        # 逻辑太复杂，暂时不细写
        ms = moveset("dixiachengDuanya")
        OneFun(ms, self.a.dixiachengDuanya)
        return ms

    def ms_shoushuazuobiao(self, x, y, jiaocheng=0, lockpic="img/normal.jpg", screencut=None):
        ms = moveset("shoushuazuobiao")
        OneFun(ms, self.a.shoushuazuobiao, x, y, jiaocheng, lockpic, screencut)
        return ms

    def ms_chulijiaocheng(self):
        ms = moveset("chulijiaocheng")
        OneFun(ms, self.a.chulijiaocheng)
        return ms

    def ms_qianghua(self):
        ms = moveset("qianghua")
        OneFun(ms, self.a.qianghua)
        return ms

    def ms_setting(self):
        ms = moveset("setting")
        OneFun(ms, self.a.setting)
        return ms
