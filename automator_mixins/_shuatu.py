import os
import time

from core.MoveRecord import movevar
from core.constant import HARD_COORD, NORMAL_COORD, FIGHT_BTN, MAOXIAN_BTN
from core.constant import USER_DEFAULT_DICT as UDD
from core.cv import UIMatcher
from core.log_handler import pcr_log
from core.valid_task import ShuatuToTuple
from ._shuatu_base import ShuatuBaseMixin


class ShuatuMixin(ShuatuBaseMixin):
    """
    刷图插片
    包含登录相关操作的脚本
    """

    # 刷经验1-1
    def shuajingyan(self, map):
        """
        刷图刷1-1
        map为主图
        """
        # 进入冒险
        self.shuatuNN(["1-1-160"])

    # 刷经验3-1
    def shuajingyan3(self, map):
        """
        刷图刷3-1
        map为主图
        """
        # 进入冒险
        self.shuatuNN(["3-1-125"])

    def shuatuNN(self, tu_dict: list, var={}):
        """
        刷指定N图
        tu_dict: 其实应该叫tu_list，来不及改了
        ["A-B-Times",...,]
        :return:
        """
        # 进入冒险
        L = ShuatuToTuple(tu_dict)
        # 按照 A-B的顺序排序：A为主要依据，B为次要依据。
        self.enter_normal()
        self.switch = 0
        cur_map = self.check_normal_id()
        mv = movevar(var)
        if "curNN" in var:
            cur = var["curNN"]
            A, B, Times = L[cur]
            self.log.write_log("info", f"断点恢复：上次刷到了{A}-{B},继续执行。")
        else:
            cur = 0
            var["curNN"] = 0
        for cur in range(cur, len(L)):
            var["curNN"] = cur
            mv.save()
            A, B, Times = L[cur]
            if A not in NORMAL_COORD:
                pcr_log(self.account).write_log("error", f"坐标库中没有图号{A}-{B}的信息！跳过此图。")
                continue
            while cur_map != A:
                self.select_normal_id(A)
                cur_map = A
            now_dict = NORMAL_COORD[A]
            if B in now_dict["left"]:
                if A != 1:
                    self.Drag_Left()
                xy = now_dict["left"][B]
                self.shuatuzuobiao(*xy, Times)
            elif B in now_dict["right"]:
                if A != 1:
                    self.Drag_Right()
                xy = now_dict["right"][B]
                self.shuatuzuobiao(*xy, Times)
            else:
                pcr_log(self.account).write_log("error", f"坐标库中没有图号{A}-{B}的信息！跳过此图。")
                continue
        del var["curNN"]
        mv.save()
        self.lock_home()

    def shuatuHH(self, tu_dict: list, var={}):
        """
        刷指定H图
        :param tu_dict: 刷图列表
        tu_dict: 其实应该叫tu_list，来不及改了
        ["A-B-Times",...,]
        :return:
        """
        L = ShuatuToTuple(tu_dict)
        self.enter_hard()
        self.switch = 0
        cur_map = self.check_hard_id(self.last_screen)
        mv = movevar(var)
        if "curHH" in var:
            cur = var["curHH"]
            A, B, Times = L[cur]
            self.log.write_log("info", f"断点恢复：上次刷到了H{A}-{B},继续执行。")
        else:
            cur = 0
            var["curHH"] = 0
        for cur in range(cur, len(L)):
            var["curHH"] = cur
            mv.save()
            A, B, Times = L[cur]
            if A not in HARD_COORD:
                pcr_log(self.account).write_log("error", f"坐标库中没有图号H{A}-{B}的信息！跳过此图。")
                continue
            while cur_map != A:
                self.select_hard_id(A)
                cur_map = A
            now_dict = HARD_COORD[A]
            if B in now_dict:
                xy = now_dict[B]
                self.shuatuzuobiao(*xy, Times)
            else:
                pcr_log(self.account).write_log("error", f"坐标库中没有图号H{A}-{B}的信息！跳过此图。")
                continue
        del var["curHH"]
        mv.save()
        self.lock_home()

    # 刷活动hard图
    def doActivityHard(self):
        # 进入冒险
        time.sleep(2)
        self.click(480, 505)
        time.sleep(2)
        while True:
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
        # 点击进入活动
        self.click(415, 430)
        time.sleep(3)
        while True:
            screen_shot_ = self.getscreen()
            self.click(480, 380)
            time.sleep(0.5)
            self.click(480, 380)
            if UIMatcher.img_where(screen_shot_, 'img/zhuxian.jpg'):
                self.click(880, 80)
            if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                break
        self.shuatuzuobiao(689, 263, self.times)  # 1-5
        self.continueDo9(570, 354)  # 1-4
        self.continueDo9(440, 255)  # 1-3
        self.continueDo9(300, 339)  # 1-2
        self.continueDo9(142, 267)  # 1-1
        self.lock_home()

    @staticmethod
    def parse_tu_str(tustr: str):
        strs = tustr.split("-")
        assert len(strs) == 2, f"错误的编队信息：{tustr}"
        return int(strs[0]), int(strs[1])

    def tuitu(self, mode, to, from_="new", buy_tili=0, auto_upgrade=2, use_ub=2, clear_tili=True, var={}):
        """
        自动推图，目前仅支持使用以等级排序前五的角色进行推图。
        ！你使用的五个队员目前只能是等级最高的五位
        ! 必须先使用self.start_shuatu才能进行推图！
        :param mode:
            0: 推普通图
            1: 推困难本
        :param to: 字符串A-B,表示推图一直进行至A-B结束
            Example："3-1"
        :param from_:字符串 A-B，表示推图起点。
            若设置为"new"，则从最新图开始推图
            如果所推的图已经推过，则会重新手刷一遍。
        :param buy_tili: 一次推图任务内最多购买体力的次数
            该次数不仅包括推图所需的体力，也包括刷装备时所用的体力
        :param auto_upgrade: 失败自动升级
            开启后，如果推图失败，则会进入升级逻辑
            如果升级之后仍然推图失败，则放弃推图
            0: 关闭自动升级
            1: 只自动强化，但是不另外打关拿装备
            2: 自动强化并且会补全一切装备
        :param use_ub: 是否开大
            0：推图不开大
            1：非Boss图不开大，boss图开大
            2：全程开大
        :param clear_tili: 是否执行self.clear_tili_info
        注：推图的记录会被记录在users/tuitu中
        注：tuitu任务跳出的情况如下：
            1）to图已经刷玩，退出
            2）体力不够，且购买体力到达设定上限，退出
            3）未开启自动升级时，刷图失败
            4）开启自动升级，经过升级后，刷图仍然失败

        --By TheAutumnOfRice
        """

        def enter():
            self.lock_home()
            if mode == 0:
                self.enter_normal()
            elif mode == 1:
                self.enter_hard()

        def GetMax(nowA):
            D = NORMAL_COORD[nowA]
            DR = D["right"]
            DL = D["left"]
            return max(max(DR), max(DL))

        def AddNow(nowA, nowB):
            # 下一张图
            if mode == 0:
                Max = GetMax(nowA)
                nowB += 1
                if nowB > Max:
                    nowB = 1
                    nowA += 1
                    self.select_normal_id(nowA)
            elif mode == 1:
                nowB += 1
                if nowB > 3:
                    nowB = 1
                    nowA += 1
                    self.select_hard_id(nowA)
            return nowA, nowB

        def GetXYTD(nowA, nowB):
            if mode == 0:
                D = NORMAL_COORD[nowA]
                DR = D["right"]
                DL = D["left"]
                if nowB in DR:
                    return DR[nowB].x, DR[nowB].y, 1, "right"
                else:
                    return DL[nowB].x, DL[nowB].y, 1, "left"
            elif mode == 1:
                D = HARD_COORD[nowA]
                return D[nowB].x, D[nowB].y, 1, None

        def Record(nowA, nowB, last=True):
            data = self.AR.get("tuitu_status", UDD["tuitu_status"])
            if mode == 0:
                if last:
                    data["last"] = f"{nowA}-{nowB}"
                if data["max"] is None:
                    data["max"] = "1-1"
                a, b = self.parse_tu_str(data["max"])
                if nowA > a or (nowA == a and nowB > b):
                    data["max"] = f"{nowA}-{nowB}"
            elif mode == 1:
                if last:
                    data["Hlast"] = f"{nowA}-{nowB}"
                if data["Hmax"] is None:
                    data["Hmax"] = "1-1"
                a, b = self.parse_tu_str(data["Hmax"])
                if nowA > a or (nowA == a and nowB > b):
                    data["Hmax"] = f"{nowA}-{nowB}"

            self.AR.set("tuitu_status", data)

        # 解析to与from
        if not self.check_shuatu():
            return
        enter()
        toA, toB = self.parse_tu_str(to)
        if from_ == "new":
            fromA, fromB = self.get_next_normal_id()
            Record(fromA, fromB, False)
        else:
            fromA, fromB = self.parse_tu_str(from_)
        nowA, nowB = fromA, fromB
        bianzu = -2
        duiwu = -2
        last_lose = False
        retry_cnt = 0
        while nowA < toA or (nowA == toA and nowB <= toB):
            if not self.check_shuatu():
                break
            jq = (mode == 0) and (nowB == GetMax(nowA))
            if use_ub == 0:
                ub = 0
            elif use_ub == 1:
                ub = 1 if nowB == GetMax(nowA) else 0
            else:
                ub = 1
            # 剧情在普通关的关末触发
            # 删除之前的刷图记录避免冲突
            if "cur_times" in var:
                del var["cur_times"]
            if "cur_win" in var:
                del var["cur_win"]
            s = self.zhandouzuobiao(*GetXYTD(nowA, nowB), buy_tili=buy_tili, duiwu=duiwu, auto=ub,
                                    bianzu=bianzu, var=var, juqing_in_fight=jq, end_mode=2 if jq else 1)
            duiwu = 0
            bianzu = 0
            if s >= 0:
                retry_cnt = 0
            if s < 0:
                if s == -3:
                    if retry_cnt == 1:
                        raise Exception("进入刷图失败！")
                    self.lock_home()
                    enter()
                    retry_cnt += 1
                    continue
                self.log.write_log("error", f"推图过程中遇到未知的错误 :{s}，终止推图。")
                break  # 出现未知错误
            elif s == 0:
                if last_lose:
                    if mode == 0:
                        self.log.write_log("info", f"连续两次推图失败，推图终止于{nowA}-{nowB}")
                    elif mode == 1:
                        self.log.write_log("info", f"连续两次推图失败，推图终止于H{nowA}-{nowB}")
                    break
                last_lose = True
                if auto_upgrade > 0:
                    self.auto_upgrade(buy_tili=buy_tili, do_shuatu=True if auto_upgrade == 2 else 1, var=var)
                    # 还要回来
                    enter()
                    continue
            else:
                last_lose = False
                Record(nowA, nowB)
                if mode == 0:
                    self.log.write_log("info", f"推图{nowA}-{nowB}成功！")
                elif mode == 1:
                    self.log.write_log("info", f"推图H{nowA}-{nowB}成功！")
                nowA, nowB = AddNow(nowA, nowB)
        if clear_tili:
            self.clear_tili_info(var)
        self.lock_home()

    def chushihua(self, var={}):
        """
        初始化：从1-3到3-1。
        目前不能实现1-1~1-2，因为TheAutumnOfRice买不到这么早的初始号
        """

        def getab():
            data = self.AR.get("tuitu_status", UDD["tuitu_status"])
            a = 1
            b = 1
            if data['max'] is not None:
                a, b = self.parse_tu_str(data['max'])
                if a >= 3:
                    self.log.write_log("info", "该账号已经成功初始化。")
            return a, b

        a, b = getab()
        if a >= 3:
            return
        self.start_shuatu()
        mv = movevar(var)
        if not mv.flag("set"):
            self.lock_home()
            self.setting()
            mv.setflag("set")
        if a == 1 and b < 8:
            print("1")
            self.tuitu(0, "1-8", buy_tili=3, clear_tili=False, var=var)
            a, b = getab()
        if a == 1 and b == 8:
            self.auto_upgrade(buy_tili=3, var=var)
        if a == 1 or (a == 2 and b < 5):
            print("2")
            self.tuitu(0, "2-5", buy_tili=3, clear_tili=False, var=var)
            a, b = getab()
        if a == 2 and b == 5:
            self.auto_upgrade(buy_tili=3, var=var)
        if a == 1 or (a == 2 and b < 11):
            print("3")
            self.tuitu(0, "2-11", buy_tili=3, clear_tili=False, var=var)
            a, b = getab()
        if a == 2 and b == 11:
            self.auto_upgrade(buy_tili=3, var=var)
        if a < 3:
            print("4")
            self.tuitu(0, "3-1", buy_tili=3, clear_tili=False, var=var)
        self.clear_tili_info(var)
        mv.clearflags()

    def chushihua2(self, var={}):
        """
        另一个初始化的思路：全部体力投入1-1刷经验之后，等级拉上来了不需要装备都能秒关
        """

        def getab():
            data = self.AR.get("tuitu_status", UDD["tuitu_status"])
            a = 1
            b = 1
            if data['max'] is not None:
                a, b = self.parse_tu_str(data['max'])
                if a >= 3:
                    self.log.write_log("info", "该账号已经成功初始化。")
            return a, b

        a, b = getab()
        if a >= 3:
            return
        mv = movevar(var)
        self.lock_home()
        if not mv.flag("set"):
            self.setting()
            mv.setflag("set")
        if not mv.flag("liwu"):
            self.__getattribute__("shouqu")()
            mv.setflag("liwu")
        if not mv.flag("renwu"):
            self.__getattribute__("shouqurenwu")()
            mv.setflag("renwu")
        if not mv.flag("exp"):
            self.__getattribute__("buyExp")()
            mv.setflag("exp")
        if not mv.flag("jingyan"):
            self.shuajingyan_super(0, 0)
            mv.setflag("jingyan")
        if not mv.flag("shengji"):
            self.auto_upgrade(0, True, False)
            mv.setflag("shengji")
        self.start_shuatu()
        if a == 1 and b < 8:
            self.tuitu(0, "1-8", buy_tili=3, auto_upgrade=1, use_ub=1, clear_tili=False, var=var)
            a, b = getab()
        if a == 1 and b == 8:
            self.auto_upgrade(0, True, False)
        if a < 3:
            self.tuitu(0, "3-1", buy_tili=3, auto_upgrade=1, use_ub=1, clear_tili=False, var=var)
        self.clear_tili_info(var)
        mv.clearflags()

    def shuajingyan_super(self, mode=1, buytili=6, var={}):
        """
        超级刷经验1-1！
        扫荡券用完了就采用手刷，有扫荡券就再用扫荡券
        一直刷到倾家荡产，体力耗尽！
        :param mode: 模式
            0：纯扫荡券
            1：先扫荡券，无法扫荡时手刷
            2：纯手刷
        :param buytili: 购买体力次数
        """
        self.lock_home()
        self.enter_normal()
        self.select_normal_id(1)
        self.start_shuatu()
        P = NORMAL_COORD[1]['left'][1]
        T = 1
        while T > 0:
            if not self.check_shuatu():
                break

            if mode <= 1:
                T = self.zhandouzuobiao(P.x, P.y, "all", None, use_saodang=True, auto=0, speed=1, buy_tili=buytili,
                                        var=var)
                if T == -2:
                    if mode == 1:
                        T = self.zhandouzuobiao(P.x, P.y, 99999999, None, use_saodang=False, auto=0, speed=1,
                                                buy_tili=buytili, var=var)
            else:
                T = self.zhandouzuobiao(P.x, P.y, 99999999, None, use_saodang=False, auto=0, speed=1, buy_tili=buytili,
                                        var=var)

        self.clear_tili_info(var)
        self.lock_home()

    def save_box_screen(self, dir: str, sort: str = "xingshu"):
        """
        拍下自己的box并保存到dir文件夹中
        sort in [zhanli,xingshu,dengji]
        :return:
        """
        self.enter_normal()
        os.makedirs(dir, exist_ok=True)

        def do():
            nid = self.check_zhuxian_id(self.last_screen)
            if nid == -1:
                return
            drag = "left" if 1 in NORMAL_COORD[nid]["left"] else "right"
            if drag == "left":
                self.Drag_Left()
            elif drag == "right":
                self.Drag_Right()
            if not self.click_btn(NORMAL_COORD[nid][drag][1], until_appear=FIGHT_BTN["xuanguan_quxiao"],
                                  is_raise=False):
                return False
            if not self.is_exists(FIGHT_BTN["tiaozhan2"], method="sq"):  # 不能挑战
                return False
            out = self.click_btn(FIGHT_BTN["tiaozhan2"], until_appear={
                MAOXIAN_BTN["no_cishu"]: 1,
                MAOXIAN_BTN["no_tili"]: 2,
                FIGHT_BTN["zhandoukaishi"]: 3
            }, is_raise=False)
            if out != 3:
                return False
            self.set_fight_team_order(sort, 1)
            self.getscreen(os.path.join(dir, f"{self.account}.jpg"))
            return True

        if do():
            self.log.write_log("info", "前两行box拍摄成功！")
        else:
            self.log.write_log("error", "box拍摄失败！")
        self.lock_home()
