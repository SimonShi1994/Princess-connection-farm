import os
import time

from core.MoveRecord import movevar
from core.constant import HARD_COORD, NORMAL_COORD, FIGHT_BTN, MAOXIAN_BTN, MAX_MAP, ACTIVITY_COORD
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

    # 刷活动normal图(有bug，不可用）
    def do_activity_normal(self, buy_tili=0, activity_name="", mode=0):
        self.lock_home()
        if activity_name == "":
            raise Exception("请指定活动名")

        def enter_activity():
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

        def GetXYTD_activity(activity_name, mode, num):
            if mode == 0:
                D = ACTIVITY_COORD[activity_name]
                DR = D["right"]
                DL = D["left"]
                if num in DR:
                    return DR[num].x, DR[num].y, 1, "right"
                else:
                    return DL[num].x, DL[num].y, 1, "left"
            elif mode == 1:
                D = HARD_COORD[activity_name]
                return D[num].x, D[num].y, 1, None

        enter_activity()
        while True:
            screen_shot_ = self.getscreen()
            self.click(480, 380)
            time.sleep(0.5)
            self.click(480, 380)
            if UIMatcher.img_where(screen_shot_, 'img/home/zhuxian.bmp'):
                self.click(880, 80)
            if UIMatcher.img_where(screen_shot_, 'img/juqing/caidanyuan.bmp'):
                self.chulijiaocheng(turnback=None)
                enter_activity()
            if UIMatcher.img_where(screen_shot_, 'img/normal.jpg'):
                break
        for i in range(1,5):
            result = self.zhandouzuobiao(*GetXYTD_activity(activity_name=activity_name, mode=mode, num=i),
                                         buy_tili=buy_tili, duiwu=-2,
                                         bianzu=-2, juqing_in_fight=1, end_mode=1)
            if result < 3:
                raise Exception("你的练度不适合刷活动图，请提升练度后重试")
        result = self.zhandouzuobiao(*GetXYTD_activity(activity_name=activity_name, mode=mode, num=5),
                                     buy_tili=buy_tili, use_saodang=True, times="all",
                                     juqing_in_fight=1, end_mode=1)
        self.lock_home()

    @staticmethod
    def parse_tu_str(tustr: str):
        strs = tustr.split("-")
        assert len(strs) == 2, f"错误的编队信息：{tustr}"
        return int(strs[0]), int(strs[1])

    def tuitu(self, mode, to, from_="new", buy_tili=0, auto_upgrade=2, use_ub=2,
              force_three_star=False, clear_tili=True, var={}):
        """
        自动推图，目前仅支持使用以等级排序前五的角色进行推图。
        ！你使用的五个队员目前只能是等级最高的五位
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
        :param force_three_star: 强制三星
            如果某一关没打到三星，就认为这一关已经输了。
            False: 打输才算输
            True: 打赢但是没有三星，也判断为输
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

        var.setdefault("buy_tili", 0)
        if var["buy_tili"] < buy_tili:
            self.start_shuatu()
        if not self.check_shuatu():
            return
        enter()
        # 解析to与from
        toA, toB = self.parse_tu_str(to)
        if from_ == "new":
            if mode == 0:
                fromA, fromB = self.get_next_normal_id()
                Record(fromA, fromB, False)
            else:
                fromA, fromB = self.get_next_hard_id()
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
            if mode == 0:
                jq = (nowB == GetMax(nowA))
                em = 2 if jq else 1
            else:
                jq = (nowB == 1 and nowA == 1)
                em = 1
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
            if mode == 0:
                self.select_normal_id(nowA)
            elif mode == 1:
                self.select_hard_id(nowA)
            s = self.zhandouzuobiao(*GetXYTD(nowA, nowB), buy_tili=buy_tili, duiwu=duiwu, auto=ub,
                                    bianzu=bianzu, var=var, juqing_in_fight=jq, end_mode=em)
            if s > 0 and force_three_star and self.last_star < 3:
                s = 0  # 没达到三星就算输
            duiwu = 0
            bianzu = 0
            if s >= 0:
                retry_cnt = 0
            if s < 0 and not (s == -2 and self._zdzb_info == "nocishu"):
                if s == -3:
                    if mode == 1:
                        self.log.write_log("info", "无法点进关卡，可能当前关卡还未解锁，请先推Normal本。")
                        break
                    if retry_cnt == 1:
                        raise Exception("进入刷图失败！")
                    self.lock_home()
                    enter()
                    retry_cnt += 1
                    continue
                else:
                    if self._zdzb_info == "notili":
                        self.log.write_log("info", f"体力不足，终止推图。")
                    else:
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
                    self.auto_upgrade(buy_tili=buy_tili, do_shuatu=True if auto_upgrade == 2 else False, var=var)
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

        self.start_shuatu()
        a, b = getab()
        if a >= 3:
            return
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

        self.start_shuatu()
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
        if a == 1 and b < 8:
            self.tuitu(0, "1-8", buy_tili=3, auto_upgrade=1, use_ub=1, clear_tili=False, var=var)
            a, b = getab()
        if a == 1 and b == 8:
            self.auto_upgrade(0, True, False)
        if a < 3:
            self.tuitu(0, "3-2", buy_tili=3, auto_upgrade=1, use_ub=1, clear_tili=False, var=var)
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
        var.setdefault("buy_tili", 0)
        if var["buy_tili"] < buytili:
            self.start_shuatu()
        if not self.check_shuatu():
            return
        self.lock_home()
        self.enter_normal()
        self.select_normal_id(1)
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

    def zidongtuitu_normal(self, buy_tili=3, max_tu="max", var={},auto_upgrade = 1):
        """
        装备号自动推图，没达到三星自动强化。
        体力用光/强化后仍然失败 - 退出
        :param buy_tili: 购买体力的次数
        :param max_tu: 终点图号，"max"表示推到不能推为止
        :param auto_upgrade: 失败自动升级
            开启后，如果推图失败，则会进入升级逻辑
            如果升级之后仍然推图失败，则放弃推图
            0: 关闭自动升级
            1: 只自动强化，但是不另外打关拿装备
            2: 自动强化并且会补全一切装备
        """
        var.setdefault("cur_tili", 0)
        if var["cur_tili"] < buy_tili:
            self.start_shuatu()
        if not self.check_shuatu():
            return
        if max_tu == "max":
            max_tu = f"{MAX_MAP}-{max(NORMAL_COORD[MAX_MAP]['right'])}"
        self.tuitu(0, max_tu, buy_tili=buy_tili, force_three_star=True, var=var,auto_upgrade=auto_upgrade)

    def zidongtuitu_hard(self, buy_tili=3, max_tu="max", var={},auto_upgrade = 1):
        """
        装备号自动推HARD图，没达到三星自动强化。
        体力用光/强化后仍然失败 - 退出
        :param buy_tili: 购买体力的次数
        :param max_tu: 终点图号，"max"表示推到不能推为止
        :param auto_upgrade: 失败自动升级
            开启后，如果推图失败，则会进入升级逻辑
            如果升级之后仍然推图失败，则放弃推图
            0: 关闭自动升级
            1: 只自动强化，但是不另外打关拿装备
            2: 自动强化并且会补全一切装备
        """
        var.setdefault("cur_tili", 0)
        if var["cur_tili"] < buy_tili:
            self.start_shuatu()
        if not self.check_shuatu():
            return
        if max_tu == "max":
            max_tu = f"{MAX_MAP}-3"
        self.tuitu(1, max_tu, buy_tili=buy_tili, force_three_star=True, var=var,auto_upgrade = auto_upgrade)

    def shuatu_daily(self, tu_order: list, daily_tili=0, xianding=False, do_tuitu=False, var={}):
        """
        每日刷图（使用扫荡券）。每天重置一次刷图记录。
        气死我了，本来想做通用刷图的，可全是BUG，现在看来只能刷H本了。
            —— TheAutumnOfRice
        !!注:为了记录刷图次数，由于暂未使用OCR，
            刷图通过”一个一个刷“来确保计数准确。
            所以暂时不适合用于小号的刷图（还请用shuatuXX）
            该函数最适合大号推H图。
        :param tu_order: 刷图顺序表。
            tu_order为一个list，对每一个元素：
                "A-B-T"表示刷普通图A-B共T次
                "HA-B-T"表示刷困难图A-B共T次
            Example:
                tu_order=["3-4-10","H1-1-3"]
            注意：困难图如果刷超过3次，会自动购买次数。
            该刷图列表表示的刷图顺序为录入顺序。
        :param daily_tili: 每日买体力次数。
        :param xianding: 是否买空限定商店（如果出现的话）
        :param do_tuitu: 不能扫荡时，是否手刷
        """
        # 每日更新
        from core.utils import diffday
        ds = self.AR.get("daily_status", UDD["daily_status"])
        def new_day(ds):
            t1 = time.time()
            t2 = ds["last_time"]
            if diffday(t1, t2):
                # 新的一天，清空刷图记录
                self.log.write_log("info", "已经重置刷图记录。")
                ds["normal"] = {}
                ds["hard"] = {}
                ds["buy_tili"] = 0
            ds["last_time"] = t1
            self.AR.set("daily_status", ds)

        # 图号解析
        def parse_tu(ds):
            # 根据已经刷的图，制定接下来剩余要刷的图号
            def parse_str(s):
                mode = "N"
                if s[0] == "H":
                    mode = "H"
                    s = s[1:]
                lst = s.split("-")
                A, B, T = int(lst[0]), int(lst[1]), int(lst[2])
                return mode, A, B, T

            cur = []
            for i in tu_order:
                m, a, b, t = parse_str(i)
                target = ds["normal"] if m == "N" else ds["hard"]
                label = f"{a}-{b}"
                target.setdefault(label, 0)
                if target[label] < t:
                    cur += [(m, a, b, t - target[label])]
            return cur

        # 关卡分析
        def GetXYTD(mode, nowA, nowB):
            if mode == "N":
                D = NORMAL_COORD[nowA]
                DR = D["right"]
                DL = D["left"]
                if nowB in DR:
                    return DR[nowB].x, DR[nowB].y, 1, "right"
                else:
                    return DL[nowB].x, DL[nowB].y, 1, "left"
            elif mode == "H":
                D = HARD_COORD[nowA]
                return D[nowB].x, D[nowB].y, 1, None

        new_day(ds)
        cur = parse_tu(ds)
        var.setdefault("cur_tili", 0)
        if len(cur) == 0:
            self.log.write_log("info", "今天的刷图任务已经全部完成啦。")
            return
        if ds["buy_tili"] < daily_tili:
            self.start_shuatu()
        buy_tili = daily_tili - ds["buy_tili"]
        if buy_tili < 0:
            buy_tili = 0
        if not self.check_shuatu():
            return
        self.lock_home()
        self.enter_zhuxian()
        last_a = -1
        last_m = None
        for ind, (m, a, b, t) in enumerate(cur):
            x, y, _, d = GetXYTD(m, a, b)
            if m != last_m or a != last_a:
                if m == "N":
                    self.select_normal_id(a)
                else:
                    self.select_hard_id(a)

            now_time = 0
            retry_cnt = 0
            while now_time < t:
                last_tili = var["cur_tili"]
                self._zdzb_info = ""
                s = self.zhandouzuobiao(x, y, 1, d, use_saodang=True, buy_tili=buy_tili, buy_cishu=0, xianding=xianding,
                                        var=var)
                if s == -2 and self._zdzb_info == "nosaodang" and do_tuitu:
                    # 无扫荡，进推图
                    self._zdzb_info = ""
                    s = self.zhandouzuobiao(x, y, 1, d, use_saodang="auto", buy_tili=buy_tili, buy_cishu=0,
                                            xianding=xianding,
                                            end_mode=1, juqing_in_fight=True, var=var)
                    # 坐标重新确认
                    if m == "N":
                        self.select_normal_id(a)
                    else:
                        self.select_hard_id(a)
                new_tili = var["cur_tili"]
                if new_tili > last_tili:
                    # 之前的战斗中购买了体力
                    ds["buy_tili"] += last_tili - new_tili
                    self.AR.set("daily_status", ds)
                if s < 0 and self._zdzb_info == "notili":
                    # 扫荡失败了，结束吧。
                    self.log.write_log("info", f"体力不足，刷图终止，队列中还有{len(cur) - ind}个任务待完成。")
                    self.lock_home()
                    return
                elif s < 0 and self._zdzb_info == "nosaodang":
                    self.log.write_log("info", "无法扫荡，刷图终止。")
                    self.lock_home()
                    return
                elif s == -3:
                    if retry_cnt == 0:
                        self.log.write_log("error", f"无法进入刷图，刷图终止")
                        self.lock_home()
                        return
                    retry_cnt += 1
                    self.lock_home()
                    self.enter_zhuxian()
                    continue
                elif s > 0 or self._zdzb_info == "nocishu":
                    # 扫荡成功，记录一下~
                    if s == 1:
                        now_time += 1
                    else:
                        now_time += t
                    if m == "N":
                        if s == 1:
                            ds["normal"][f"{a}-{b}"] += 1
                        else:
                            ds["normal"][f"{a}-{b}"] += t
                    else:
                        if s == 1:
                            ds["hard"][f"{a}-{b}"] += 1
                        else:
                            ds["hard"][f"{a}-{b}"] += t
                    self.AR.set("daily_status", ds)
                    new_day(ds)
                elif self._zdzb_info == "noquan":
                    self.log.write_log("info", f"券不足，刷图终止，队列中还有{len(cur) - ind}个任务待完成。")
                    self.lock_home()
                    return
                else:
                    self.log.write_log("info", "战斗失败，刷图终止。")
                    self.lock_home()
                    return
            self.log.write_log("info", f"{a}-{b}刷图成功！")
        self.log.write_log("info", f"全部刷图任务已经完成。")
        self.lock_home()

    def shuatu_daily_new(self, tu_order: list, daily_tili=0, xianding=False, do_tuitu=False, var={}):
        """
        每日刷图（使用扫荡券）。每天重置一次刷图记录。
        气死我了，本来想做通用刷图的，可全是BUG，现在看来只能刷H本了。
            —— TheAutumnOfRice
        !!注:为了记录刷图次数，由于暂未使用OCR，
            刷图通过”一个一个刷“来确保计数准确。
            所以暂时不适合用于小号的刷图（还请用shuatuXX）
            该函数最适合大号推H图。
        :param tu_order: 刷图顺序表。
            tu_order为一个list，对每一个元素：
                "A-B-T"表示刷普通图A-B共T次
                "HA-B-T"表示刷困难图A-B共T次
            Example:
                tu_order=["3-4-10","H1-1-3"]
            注意：困难图如果刷超过3次，会自动购买次数。
            该刷图列表表示的刷图顺序为录入顺序。
        :param daily_tili: 每日买体力次数。
        :param xianding: 是否买空限定商店（如果出现的话）
        :param do_tuitu: 不能扫荡时，是否手刷
        """
        # 每日更新
        from core.utils import diffday
        ds = self.AR.get("daily_status", UDD["daily_status"])

        def new_day(ds):
            t1 = time.time()
            t2 = ds["last_time"]
            if diffday(t1, t2):
                # 新的一天，清空刷图记录
                self.log.write_log("info", "已经重置刷图记录。")
                ds["normal"] = {}
                ds["hard"] = {}
                ds["buy_tili"] = 0
            ds["last_time"] = t1
            self.AR.set("daily_status", ds)

        # 图号解析
        def parse_tu(ds):
            # 根据已经刷的图，制定接下来剩余要刷的图号
            def parse_str(s):
                mode = "N"
                if s[0] == "H":
                    mode = "H"
                    s = s[1:]
                lst = s.split("-")
                A, B, T = int(lst[0]), int(lst[1]), int(lst[2])
                return mode, A, B, T

            cur = []
            for i in tu_order:
                m, a, b, t = parse_str(i)
                target = ds["normal"] if m == "N" else ds["hard"]
                label = f"{a}-{b}"
                target.setdefault(label, 0)
                if target[label] < t:
                    cur += [(m, a, b, t - target[label])]
            return cur

        # 关卡分析
        def GetXYTD(mode, nowA, nowB):
            if mode == "N":
                D = NORMAL_COORD[nowA]
                DR = D["right"]
                DL = D["left"]
                if nowB in DR:
                    return DR[nowB].x, DR[nowB].y, 1, "right"
                else:
                    return DL[nowB].x, DL[nowB].y, 1, "left"
            elif mode == "H":
                D = HARD_COORD[nowA]
                return D[nowB].x, D[nowB].y, 1, None

        new_day(ds)
        cur = parse_tu(ds)
        var.setdefault("cur_tili", 0)
        if len(cur) == 0:
            self.log.write_log("info", "今天的刷图任务已经全部完成啦。")
            return
        if ds["buy_tili"] < daily_tili:
            self.start_shuatu()
        buy_tili = daily_tili - ds["buy_tili"]
        if buy_tili < 0:
            buy_tili = 0
        if not self.check_shuatu():
            return
        self.lock_home()
        self.enter_zhuxian()
        last_a = -1
        last_m = None
        for ind, (m, a, b, t) in enumerate(cur):
            x, y, _, d = GetXYTD(m, a, b)
            if m != last_m or a != last_a:
                if m == "N":
                    self.select_normal_id(a)
                else:
                    self.select_hard_id(a)

            now_time = 0
            retry_cnt = 0
            while now_time < t:
                last_tili = var["cur_tili"]
                self._zdzb_info = ""
                FS = self.GetFightSteps()
                FS.EnterMap(x, y, drag=d)
                FS.ShowInfo()
                s = self.zhandouzuobiao(x, y, 1, d, use_saodang=True, buy_tili=buy_tili, buy_cishu=0, xianding=xianding,
                                        var=var)
                if s == -2 and self._zdzb_info == "nosaodang" and do_tuitu:
                    # 无扫荡，进推图
                    self._zdzb_info = ""
                    s = self.zhandouzuobiao(x, y, 1, d, use_saodang="auto", buy_tili=buy_tili, buy_cishu=0,
                                            xianding=xianding,
                                            end_mode=1, juqing_in_fight=True, var=var)
                    # 坐标重新确认
                    if m == "N":
                        self.select_normal_id(a)
                    else:
                        self.select_hard_id(a)
                new_tili = var["cur_tili"]
                if new_tili > last_tili:
                    # 之前的战斗中购买了体力
                    ds["buy_tili"] += last_tili - new_tili
                    self.AR.set("daily_status", ds)
                if s < 0 and self._zdzb_info == "notili":
                    # 扫荡失败了，结束吧。
                    self.log.write_log("info", f"体力不足，刷图终止，队列中还有{len(cur) - ind}个任务待完成。")
                    self.lock_home()
                    return
                elif s < 0 and self._zdzb_info == "nosaodang":
                    self.log.write_log("info", "无法扫荡，刷图终止。")
                    self.lock_home()
                    return
                elif s == -3:
                    if retry_cnt == 0:
                        self.log.write_log("error", f"无法进入刷图，刷图终止")
                        self.lock_home()
                        return
                    retry_cnt += 1
                    self.lock_home()
                    self.enter_zhuxian()
                    continue
                elif s > 0 or self._zdzb_info == "nocishu":
                    # 扫荡成功，记录一下~
                    if s == 1:
                        now_time += 1
                    else:
                        now_time += t
                    if m == "N":
                        if s == 1:
                            ds["normal"][f"{a}-{b}"] += 1
                        else:
                            ds["normal"][f"{a}-{b}"] += t
                    else:
                        if s == 1:
                            ds["hard"][f"{a}-{b}"] += 1
                        else:
                            ds["hard"][f"{a}-{b}"] += t
                    self.AR.set("daily_status", ds)
                    new_day(ds)
                elif self._zdzb_info == "noquan":
                    self.log.write_log("info", f"券不足，刷图终止，队列中还有{len(cur) - ind}个任务待完成。")
                    self.lock_home()
                    return
                else:
                    self.log.write_log("info", "战斗失败，刷图终止。")
                    self.lock_home()
                    return
            self.log.write_log("info", f"{a}-{b}刷图成功！")
        self.log.write_log("info", f"全部刷图任务已经完成。")
        self.lock_home()

    def meiriHtu(self, H_list, daily_tili, xianding, do_tuitu, var={}):
        """
        每日H本。
        H_list：list["A-B"],刷什么H图
        daily_tili：购买体力次数
        xianding：是否买空限定商店
        do_tuitu 是否允许推图
        """
        lst = []
        for s in H_list:
            A, B = tuple(s.split("-"))
            lst += [f"H{A}-{B}-3"]
        self.shuatu_daily(lst, daily_tili, xianding, do_tuitu, var=var)

    def xiaohaoHtu(self, daily_tili, do_tuitu, var={}):
        """
        小号每日打H本。
        一个接一个打。
        :param daily_tili:购买体力次数
        :param do_tuitu: 是否允许推图
        """
        L = []
        for i in range(MAX_MAP):
            for j in [1, 2, 3]:
                L += [f"{i + 1}-{j}"]
        self.meiriHtu(L, daily_tili, False, do_tuitu, var)

    def shengjijuese(self, buy_tili=0, do_rank=True, do_shuatu=True):
        self.lock_home()
        self.auto_upgrade(buy_tili=buy_tili, do_rank=do_rank, do_shuatu=do_shuatu)
        self.lock_home()
