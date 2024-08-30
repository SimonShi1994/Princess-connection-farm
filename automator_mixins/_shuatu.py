import os
import time
from math import floor, inf

from DataCenter import LoadPCRData
from core.MoveRecord import movevar
from core.constant import HARD_COORD, NORMAL_COORD, FIGHT_BTN, MAOXIAN_BTN, MAX_MAP, VH_COORD, \
    HANGHUI_BTN, HUODONG_BTN, JUQING_BTN, MAIN_BTN, WZ_BTN
from core.constant import USER_DEFAULT_DICT as UDD
from core.cv import UIMatcher
from core.log_handler import pcr_log
from core.pcr_checker import PCRRetry, LockTimeoutError, RetryNow, ContinueNow
from core.pcr_config import force_as_ocr_as_possible, debug
from core.valid_task import ShuatuToTuple
from scenes.fight.fightinfo_base import FightInfoBase
from scenes.fight.fightinfo_zhuxian import FightInfoZhuXian, FightInfoZhuXianNormal
from scenes.fight.fighting_zhuxian import AfterFightingWin
from scenes.huodong.huodong_base import HuodongMapBase, HuodongMenu, FightBianZuHuoDong
from scenes.waizhuan.wz_base import WZ_MapBase, WZ_Menu
from scenes.scene_base import PCRSceneBase

from ._shuatu_base import ShuatuBaseMixin


class ShuatuMixin(ShuatuBaseMixin):
    """
    刷图插片
    包含登录相关操作的脚本
    """

    # 刷经验1-1
    def shuajingyan(self, map=3):
        """
        刷图刷1-1
        map为主图
        """
        # 进入冒险
        self.shuatuNN(["1-1-160"])

    # 刷经验3-13
    def shuajingyan3(self, map=3):
        """
        刷图刷3-1
        map为主图
        """
        # 进入冒险
        self.shuatuNN(["3-1-125"])

    @staticmethod
    def GetXYTD(mode, nowA, nowB):
        """
        mode: N or H or VH
        返回MA-B的： X,Y,卵用没有参数，Drag方向
        """
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
        else:
            D = VH_COORD[nowA]
            return D[nowB].x, D[nowB].y, 1, None

    def kuaisujieren(self, max_do=2, max_map=999):
        """
        快速借人推图。
        进去主线Normal后，检测到N A-B则刷N A-1
        max_do:执行max_do次，或者并没有好友了。
        如果设置了max_map，则最多刷 N max_map-1
        """
        S = self.get_zhuye().goto_maoxian().goto_normal()
        now_id = S.check_normal_id(self.last_screen)
        if now_id > max_map:
            S.select_normal_id(max_map)
            now_id = max_map

        for now in range(max_do):
            SN = S.enter_NAB(now_id, 1)
            SN: FightInfoZhuXianNormal
            if SN is None:
                raise Exception(f"出现了进不了图{now_id}-1的蜜汁错误。")
            if not SN.can_fight():
                # 没体力
                self.log.write_log("info", "根本没有体力，借不了人！")
                self.lock_home()
                return
            tz = SN.goto_tiaozhan()
            out = tz.get_zhiyuan(1, force_haoyou=True)
            if out == 4:
                self.log.write_log("info", "没有好友了，借人结束。")
                break
            elif out > 0:
                self.log.write_log("warning", f"发生奇妙错误： CODE{out}，借人结束。")
                break
            ft = tz.goto_fight()
            ft.auto_and_fast()
            state = ft.wait_for_end_and_return_normal()
            if state["flag"] == "lose":
                self.log.write_log("info", "借人推图成功，可是没打过。")
            else:
                self.log.write_log("info", "借人推图成功，且打过了！")

        self.lock_home()

    def record_tuitu_state(self, mode, nowA, nowB, last=True):
        """
        记录推图状态
        mode:  0: Normal;   1: Hard
        nowA-nowB 关卡编号
        last：上次推图
        """
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

    def add_map_id(self, mode, nowA, nowB):
        """
        获得 mode下（0：普通 1：困难）， nowA-nowB关卡的下一关是什么
        """

        def GetMax(nowA):
            D = NORMAL_COORD[nowA]
            DR = D["right"]
            DL = D["left"]
            return max(max(DR), max(DL))
            # 下一张图

        if mode == 0:
            Max = GetMax(nowA)
            nowB += 1
            if nowB > Max:
                nowB = 1
                nowA += 1
        elif mode == 1:
            nowB += 1
            if nowB > 3:
                nowB = 1
                nowA += 1
        return nowA, nowB

    def jierentuitu(self, mode, to, from_="new", zhiyuan_mode=-1, max_do=2, var={}):
        """
        借人推图。
        没有自动升级功能所以上自己的人可能不能三星过关。
        确保你推的图大号能单吃。
        mode:  0 普通  1 困难
        to:  A-B 推到A-B结束
        from_:字符串 A-B，表示推图起点。
            若设置为"new"，则从最新图开始推图
            如果所推的图已经推过，则会重新手刷一遍。
        zhiyuan_mode: 见shuatu_daily_ocr
        max_do: 最多借几次。
        """
        # 解析to与from
        toA, toB = self.parse_tu_str(to)
        if from_ == "new":
            S = self.get_zhuye().goto_maoxian()
            if mode == 0:
                S.goto_normal()
            elif mode == 1:
                S.goto_hard()
            if mode == 0:
                fromA, fromB = self.get_next_normal_id()
                self.record_tuitu_state(mode, fromA, fromB, False)
            else:
                fromA, fromB = self.get_next_hard_id()
                self.record_tuitu_state(mode, fromA, fromB, False)
        else:
            fromA, fromB = self.parse_tu_str(from_)
        nowA, nowB = fromA, fromB
        # Make List.
        lst = []
        while nowA < toA or (nowA == toA and nowB <= toB):
            if mode == 0:
                lst.append(f"{nowA}-{nowB}-1")
            else:
                lst.append(f"H{nowA}-{nowB}-1")
            if len(lst) >= max_do:
                break
            nowA, nowB = self.add_map_id(mode, nowA, nowB)

        self.log.write_log("info", f"即将推图：{lst}")
        self.shuatu_daily_ocr(lst, zero_star_action="do", lose_action="exit", win_without_threestar_is_lose=False,
                              zhiyuan_mode=zhiyuan_mode, _use_daily=False, var=var)

    def jierentuitu_normal(self, max_tu, zhiyuan_mode=-1, max_do=2, var={}):
        if not self.check_shuatu():
            return
        if max_tu == "max":
            max_tu = f"{MAX_MAP}-{max(NORMAL_COORD[MAX_MAP]['right'])}"
        self.jierentuitu(0, max_tu, zhiyuan_mode=zhiyuan_mode, max_do=max_do, var=var)

    def jierentuitu_hard(self, max_tu, zhiyuan_mode=-1, max_do=2, var={}):
        if not self.check_shuatu():
            return
        if max_tu == "max":
            max_tu = f"{MAX_MAP}-3"
        self.jierentuitu(1, max_tu, zhiyuan_mode=zhiyuan_mode, max_do=max_do, var=var)

    def shuatuNN(self, tu_dict: list, use_ocr=False, var={}):
        """
        刷指定N图
        tu_dict: 其实应该叫tu_list，来不及改了
        ["A-B-Times",...,]
        :return:
        """
        # 进入冒险
        L = ShuatuToTuple(tu_dict)
        if use_ocr or force_as_ocr_as_possible:
            # L: List[Tuple[A,B,T]]
            new_L = []
            for l in L:
                A, B, T = l
                new_L += [f"{A}-{B}-{T}"]
            self.shuatu_daily_ocr(new_L, 0, False, "do", "do", "skip", "exit", False, "zhanli", False, var)
            return
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

    def shuatuHH(self, tu_dict: list, use_ocr: bool = False, var={}):
        """
        刷指定H图
        :param tu_dict: 刷图列表
        tu_dict: 其实应该叫tu_list，来不及改了
        ["A-B-Times",...,]
        :return:
        """
        L = ShuatuToTuple(tu_dict)
        if use_ocr or force_as_ocr_as_possible:
            # L: List[Tuple[A,B,T]]
            new_L = []
            for l in L:
                A, B, T = l
                new_L += [f"H{A}-{B}-{T}"]
            self.shuatu_daily_ocr(new_L, 0, False, "do", "do", "skip", "exit", False, "zhanli", False, var)
            return
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

    def tuitu_ocr(self, mode, from_="new", to="max", buy_tili=0, xianding=False, team_order="zhanli", zhiyuan_mode=0,
                  lose_action="exit", win_without_threestar_is_lose=True, upgrade_kwargs={}, var={}):
        """
        mode:   0 - Normal; 1 - Hard; 2 - VH （没测过）
        from_:  A-B 或者 new
        to:     A-B 或者 max
        buy_tili：所用体力
        其他参数见shuatu_dailt_ocr
        """
        # 使用shuatu_daily_ocr重写
        # Step 1: 寻找起点
        LST = []

        if mode == 0:
            if from_ == "new":
                self.get_zhuye().goto_maoxian().goto_normal().clear_initFC()
                A, B = self.get_next_normal_id()
                self.lock_home()
            else:
                A, B = [int(x) for x in from_.split("-")]
            D = NORMAL_COORD
            if to == "max":
                TA = max(D)
                TB = max(list(D[TA]['left']) + list(D[TA]['right']))
            else:
                TA, TB = [int(x) for x in to.split("-")]
            for aa in range(A, TA + 1):
                LST = []
                for bb in range(B if aa == A else 1,
                                max(list(D[aa]['left']) + list(D[aa]['right'])) + 1 if aa < TA else TB + 1):
                    LST.append(f"{aa}-{bb}-1")
                output = self.shuatu_daily_ocr(
                    tu_order=LST,
                    daily_tili=buy_tili,
                    xianding=xianding,
                    not_three_star_action="do",
                    zero_star_action="do",
                    lose_action=lose_action,
                    can_not_enter_action="exit",
                    win_without_threestar_is_lose=win_without_threestar_is_lose,
                    team_order=team_order,
                    zhiyuan_mode=zhiyuan_mode,
                    _use_daily=False,
                    upgrade_kwargs=upgrade_kwargs,
                    var=var,
                )
                if output == 1:
                    return
            return
        elif mode == 1:
            if from_ == "new":
                self.get_zhuye().goto_maoxian().goto_hard().clear_initFC()
                A, B = self.get_next_hard_id()
                self.lock_home()
            else:
                A, B = [int(x) for x in from_.split("-")]
            D = HARD_COORD
            if to == "max":
                TA = max(D)
                TB = 3
            else:
                TA, TB = [int(x) for x in to.split("-")]
            for aa in range(A, TA + 1):
                for bb in range(B if aa == A else 1,
                                4 if aa < TA else TB + 1):
                    LST.append(f"H{aa}-{bb}-1")
        elif mode == 2:
            if from_ == "new":
                self.get_zhuye().goto_maoxian().goto_vh().clear_initFC()
                A, B = self.get_next_hard_id(VH_COORD)
                self.lock_home()
            else:
                A, B = [int(x) for x in from_.split("-")]
            D = VH_COORD
            if to == "max":
                TA = max(D)
                TB = max(D[TA])
            else:
                TA, TB = [int(x) for x in to.split("-")]
            for aa in range(A, TA + 1):
                for bb in range(B if aa == A else 1,
                                4 if aa < TA else TB + 1):
                    LST.append(f"VH{aa}-{bb}-1")
        else:
            raise ValueError("mode can only be 0 or 1")

        # Step 2
        self.shuatu_daily_ocr(
            tu_order=LST,
            daily_tili=buy_tili,
            xianding=xianding,
            not_three_star_action="do",
            zero_star_action="do",
            lose_action=lose_action,
            can_not_enter_action="exit",
            win_without_threestar_is_lose=win_without_threestar_is_lose,
            team_order=team_order,
            zhiyuan_mode=zhiyuan_mode,
            _use_daily=False,
            upgrade_kwargs=upgrade_kwargs,
            var=var,
        )

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

        if force_as_ocr_as_possible:
            self.log.write_log("info", "该函数已经用OCR版本重写，自动跳转到tuitu_ocr函数。")
            self.tuitu_ocr(
                mode=mode,
                from_=from_,
                to=to,
                buy_tili=buy_tili,
                team_order="dengji",
                win_without_threestar_is_lose=force_as_ocr_as_possible,
                lose_action="exit" if auto_upgrade == 0 else "upgrade",
                upgrade_kwargs=dict(do_shuatu=False if auto_upgrade == 1 else True),
                var=var
            )
        else:
            self.log.write_log("error", "该函数的非OCR版本已经不再维护，估计不能用了。")

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
            self.record_tuitu_state(mode, nowA, nowB, last)

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
            self.log.write_log('info', "1")
            self.tuitu(0, "1-8", buy_tili=3, clear_tili=False, var=var)
            a, b = getab()
        if a == 1 and b == 8:
            self.auto_upgrade(buy_tili=3, var=var)
        if a == 1 or (a == 2 and b < 5):
            self.log.write_log('info', "2")
            self.tuitu(0, "2-5", buy_tili=3, clear_tili=False, var=var)
            a, b = getab()
        if a == 2 and b == 5:
            self.auto_upgrade(buy_tili=3, var=var)
        if a == 1 or (a == 2 and b < 11):
            self.log.write_log('info', "3")
            self.tuitu(0, "2-11", buy_tili=3, clear_tili=False, var=var)
            a, b = getab()
        if a == 2 and b == 11:
            self.auto_upgrade(buy_tili=3, var=var)
        if a < 3:
            self.log.write_log('info', "4")
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

    def zidongtuitu_normal(self, buy_tili=3, max_tu="max", var={}, auto_upgrade=1):
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
        self.tuitu(0, max_tu, buy_tili=buy_tili, force_three_star=True, var=var, auto_upgrade=auto_upgrade)

    def zidongtuitu_hard(self, buy_tili=3, max_tu="max", var={}, auto_upgrade=1):
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
        self.tuitu(1, max_tu, buy_tili=buy_tili, force_three_star=True, var=var, auto_upgrade=auto_upgrade)

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

    def shuatu_daily_ocr(self,
                         tu_order: list,
                         daily_tili=0,
                         xianding=False,
                         not_three_star_action="do",
                         zero_star_action="exit",
                         lose_action="skip",
                         can_not_enter_action="exit",
                         win_without_threestar_is_lose=True,
                         team_order="zhanli",
                         zhiyuan_mode=0,
                         _use_daily=True,
                         var={},
                         upgrade_kwargs={}):
        """
        OCR 刷图！！超快！！
        :param tu_order: 刷图顺序表。
            tu_order为一个list，对每一个元素：
                "A-B-T"表示刷普通图A-B共T次
                "HA-B-T"表示刷困难图A-B共T次
                "VHA-B-T"表示刷极难图A-B共T次
            Example:
                tu_order=["3-4-10","H1-1-3"]
              # 注意：困难图如果刷超过3次，并不会自动购买次数。
            20220303 NEW: Hard/VH允许输入大于3的值，此时会自动尝试进行购买次数了。

            该刷图列表表示的刷图顺序为录入顺序。

            20220206 NEW: 如果存在波浪线 ~，则表示H, VH的碎片数量达到波浪线后的值则停刷。若波浪线后为inf，则无限制。
                H图默认无限制。
                VH图默认为50。
                    "H3-3-3"  刷H3-3，无限制。
                    "H3-3-3~150"  刷H3-3到150个就停刷
                    "VH20-3-3~inf"  刷VH20-3到无限个
                    "VH20-3-3" 刷VH20-3到50个
        :param daily_tili: 每日买体力次数。
        :param xianding: 是否买空限定商店（如果出现的话）
        :param not_three_star_action: 遇到未满三星图如何操作
        :param zero_star_action: 遇到零星图如何操作
        :param lose_action: 推图失败如何操作
        :param can_not_enter_action: 无法进图时如何操作（不适用do）
            - action的种类
                "do" 手刷
                "exit" 终止刷图
                "skip" 跳过该图
                "upgrade" 开始自动升级角色，若仍然打不赢，终止刷图（仅对lose_action起作用，按照team_order的五个人，team_order不能为编组）
        :param win_without_threestar_is_lose: 如果没有三星过关就算输
        :param team_order:
            使用队伍 "A-B" 形式，表示编组A选择B。
            若为 order指令：则按以下order排序后取前5.
                - "zhanli" 按战力排序
                - "dengji" 按等级排序
                - "xingshu" 按星数排序
            若为"none"：不换人
        :param zhiyuan_mode:
            支援模式：
                0  - 不使用支援
                1  - 当有好友助战时使用好友支援+自己队伍，否则直接结束推图。
                -1 - 当有好友助战时仅使用好友支援一人推图，否则直接结束推图。
                2  - 当有好友助战时使用好友支援+自己队伍，否则不使用支援自己推图。
                -2 - 当有好友助战时仅使用好友支援一人推图，否则不使用支援自己推图。
                3  - 任意选择一个支援+自己队伍推图。
                -3 - 任意选择一个支援仅支援一人推图。
        :param _use_daily: 开启后，统计体力使用次数以及每个图刷过的次数（兼容shuatuNN）
        :return: 刷图状态
            0 - 正常结束（没有触发“终止刷图”）
            1 - 异常结束（触发“终止刷图”）
        """
        self.check_ocr_running()  # 必须要OCR！
        # 每日更新
        from core.utils import diffday
        mv = movevar(var)
        if _use_daily:
            ds = self.AR.get("daily_status", UDD["daily_status"])
            var['buy_tili'] = ds.setdefault('buy_tili', 0)
        else:
            mv.regflag("normal", {})
            mv.regflag("hard", {})
            mv.regflag("veryhard", {})
            mv.regflag("buy_tili", 0)
            ds = var
        mv.regflag("upgraded", False)

        def record_ds(ds):
            # 记录每日推图所用体力，推图记录之类。
            if _use_daily:
                t1 = time.time()
                t2 = ds["last_time"]
                if diffday(t1, t2):
                    # 新的一天，清空刷图记录
                    self.log.write_log("info", "已经重置刷图记录。")
                    ds["normal"] = {}
                    ds["hard"] = {}
                    ds["veryhard"] = {}
                    ds["buy_tili"] = 0
                ds["last_time"] = t1
                self.AR.set("daily_status", ds)
            else:
                mv.save()

        # 图号解析
        def parse_tu(ds):
            # 根据已经刷的图，制定接下来剩余要刷的图号
            def parse_str(s):
                mode = "N"
                if s[0] == "H":
                    mode = "H"
                    s = s[1:]
                elif s[0] == "V" and s[1] == "H":
                    mode = "VH"
                    s = s[2:]
                tg = None
                if '~' in s:
                    s, s_right = s.split('~')
                    if s_right == "inf":
                        tg = inf
                    else:
                        tg = int(s_right)
                lst = s.split("-")
                A, B, T = int(lst[0]), int(lst[1]), int(lst[2])
                if mode == "H" and tg is None:
                    tg = inf
                if mode == "VH" and tg is None:
                    tg = 50
                return mode, A, B, T, tg

            cur = []
            for i in tu_order:
                m, a, b, t, tg = parse_str(i)
                target = ds["normal"] if m == "N" else ds["hard"] if m == "H" else ds["veryhard"]
                label = f"{a}-{b}"
                target.setdefault(label, 0)
                if target[label] < t:
                    cur += [(m, a, b, t - target[label], t, tg)]
            new_cur = []
            # 分解任务：一次最多80扫荡(normal) 3次扫荡(hard,VH)
            for m, a, b, t, ori_t, tg in cur:
                tt = t
                while tt > 0:
                    if m == "N":
                        if tt > 80:
                            ttt = 80
                        else:
                            ttt = tt
                        tt -= ttt
                        new_cur += [(m, a, b, ttt, ori_t, tg)]
                    else:
                        if tt > 3:
                            ttt = 3
                        else:
                            ttt = tt
                        tt -= ttt
                        new_cur += [(m, a, b, ttt, ori_t, tg)]
            return new_cur

        # 关卡分析
        GetXYTD = self.GetXYTD

        record_ds(ds)
        cur = parse_tu(ds)
        ds.setdefault("buy_tili", 0)
        if len(cur) == 0:
            if _use_daily:
                self.log.write_log("info", "今天的刷图任务已经全部完成啦。")
            return 0
        if ds["buy_tili"] < daily_tili:
            self.start_shuatu()
        if not self.check_shuatu():
            return 1

        #   ======== 开始刷图 =========  #
        S = self.get_zhuye()
        S = S.goto_maoxian()
        last_a = -1
        last_m = None
        for ind, (m, a, b, t, ori_t, tg) in enumerate(cur):
            mode = "veryhard" if m == "VH" else "hard" if m == "H" else "normal"
            x, y, _, d = GetXYTD(m, a, b)
            # m: mode (VH,H,N)
            # a,b: a-b
            # t: **剩余** 要刷几次
            # x,y：坐标
            # d：拖动状态
            # Enter
            # ======== 进图 =========== #
            if m != last_m or a != last_a:
                if m == "N":
                    S = S.goto_normal()
                    res = S.select_normal_id(a)
                elif m == "H":
                    S = S.goto_hard()
                    res = S.select_hard_id(a)
                else:
                    S = S.goto_vh()
                    res = S.select_vh_id(a)
                if not res:
                    if can_not_enter_action == "exit":
                        self.log.write_log("info", f"无法进入图{m}{a}-{b}！结束刷图。")
                        self.save_last_screen(f"CanNotEnter1_{self.account}.bmp")
                        self.lock_home()
                        return 1
                    elif can_not_enter_action == "skip":
                        self.log.write_log("info", f"无法进入图{m}{a}-{b}！跳过该图。")
                        continue

            if d == "left":
                S.Drag_Left()
            elif d == "right":
                S.Drag_Right()

            @PCRRetry(name="DOIT")
            def DOIT():
                """
                进图大循环。此处PCRRetry相当于一个label，可以被goto。
                循环：
                    点 (x,y) ->
                    扫荡或者刷图
                遇到剧情或者商店，或者买体力，则回到一开始的位置重新进(x,y)：
                    raise ContinueNow("DOIT")  :回到开始，但是不计算重试次数。
                    raise RetryNow("DOIT")： 回到开始，但是重试计数器+1，如果再PCRRetry中增加max_retry，则可以控制结束次数。
                与外接的信息交换：
                    return "continue" ：跳过这关，不刷。
                    return "return"：结束刷图
                """
                nonlocal t  # 该关剩余次数
                if t == 0:
                    return "continue"  # 这关不用再刷了。
                M: FightInfoZhuXian = S.click_xy_and_open_fightinfo(x, y)
                if M is None:
                    if can_not_enter_action == "exit":
                        self.log.write_log("info", f"无法进入图{m}{a}-{b}！结束刷图。")
                        self.save_last_screen(f"CanNotEnter2_{self.account}.bmp")
                        self.lock_home()
                        return "return"
                    elif can_not_enter_action == "skip":
                        self.log.write_log("info", f"无法进入图{m}{a}-{b}！跳过该图。")
                        return "continue"
                S.clear_initFC()  # 清除可可罗的检测
                if m in ['H', 'VH']:
                    # 碎片目标检测
                    if tg != inf:
                        first_cnt = M.get_first_item_count()
                        if first_cnt >= tg:
                            self.log.write_log("info", f"图{m}{a}-{b}已经有{first_cnt}/{tg}个目标碎片，不刷啦！")
                            return "continue"
                sc = self.getscreen()
                stars = M.get_upperright_stars(sc)
                if debug: self.log.write_log("debug", f"星数：{stars}")
                if stars == 3:
                    # 可以扫荡
                    # 次数判断：对Hard图
                    max_cishu = t  # 目标：刷t次
                    if m in ["H", "VH"]:
                        cishu = M.get_cishu(sc)
                        if cishu == 0:
                            # 不能扫荡，没有次数
                            if ori_t > 3:
                                # 试图买次数
                                cishu_return = M.buy_cishu()
                                if cishu_return:
                                    # 购买成功
                                    cishu = 3
                                    ds[mode][f"{a}-{b}"] = 3
                                    record_ds(ds)
                                else:
                                    # 购买失败，可能已经买过了
                                    ds[mode][f"{a}-{b}"] = 6
                                    record_ds(ds)
                                    self.fclick(1, 1)
                                    self.log.write_log("info", f"{m}{a}-{b}已经买过次数，不能再刷更多了！")
                                    return "continue"
                            else:
                                ds[mode][f"{a}-{b}"] = 3
                                record_ds(ds)
                                self.fclick(1, 1)
                                self.log.write_log("info", f"{m}{a}-{b}已经不能再刷更多了！")
                                return "continue"
                        max_cishu = min(cishu, max_cishu)
                    self._zdzb_info = ""  # 记录失败原因
                    # 扫荡券判断：最多还能扫荡几次
                    quan = M.get_saodangquan(sc)
                    if quan < max_cishu:
                        self._zdzb_info = "noquan"
                        if quan == 0:
                            self.log.write_log("warning", "已经没有扫荡券了！终止刷图。")
                            self.lock_home()
                            return "return"
                        self.log.write_log("warning", f"扫荡券可能不足，只能支持刷{quan}次了。")
                        max_cishu = quan

                    # 体力判断：最多还能进行几次
                    left_tili = M.get_tili_left(sc)
                    one_tili = LoadPCRData().get_map_tili(mode, a, b)
                    max_cishu_tili = floor(left_tili / one_tili)
                    bought_tili = False
                    while max_cishu_tili < max_cishu:
                        # 体力不足：可以选择买体力倒是。
                        if ds["buy_tili"] < daily_tili:
                            # 可以！买体力！
                            self.fclick(1, 1)
                            bought_tili = True
                            S.goto_buytili().OK().OK()
                            ds["buy_tili"] += 1
                            record_ds(ds)
                            self.log.write_log("info", f"体力不足，购买体力{ds['buy_tili']}/{daily_tili}")
                            left_tili += 120
                            max_cishu_tili = floor(left_tili / one_tili)
                        else:
                            # 已经……买不动了
                            if daily_tili > 0:
                                self.log.write_log("info", f"已经消耗完全部的买体力次数了。")
                            self._zdzb_info = "notili"
                            if max_cishu_tili == 0:
                                self.log.write_log("info", "已经一点体力都不剩了！终止刷图。")
                                self.stop_shuatu()
                                self.lock_home()
                                return "return"
                            else:
                                self.log.write_log("info", f"剩下的体力只够刷{max_cishu_tili}次了！")
                            break
                    if bought_tili:
                        # 买过体力之后要重新进图
                        S.click_xy_and_open_fightinfo(x, y)
                    max_cishu = min(max_cishu, max_cishu_tili)
                    # 扫荡
                    true_cishu = max_cishu
                    M.set_saodang_cishu(true_cishu, one_tili=one_tili, left_tili=left_tili, sc=self.last_screen)
                    SD = M.goto_saodang()  # 扫荡确认
                    SD = SD.OK()  # 扫荡结果
                    # 记录
                    ds[mode][f"{a}-{b}"] += true_cishu
                    record_ds(ds)
                    MsgList = SD.OK()  # 扫荡后的一系列MsgBox
                    MsgList.exit_all(xianding)  # 退出全部
                    # 扫荡结束
                    # 保险起见
                    self.fclick(1, 1)
                    if true_cishu < t:
                        self.log.write_log("info", f"{m}{a}-{b}刷图剩余次数：{t - true_cishu}")
                        t -= true_cishu
                        raise ContinueNow("DOIT")
                    else:
                        self.log.write_log("info", f"{m}{a}-{b}刷图成功！")
                else:
                    # 特判
                    if stars == 0:
                        if zero_star_action == "exit":
                            self.log.write_log("info", f"{m}{a}-{b}尚未通关，终止刷图！")
                            self.lock_home()
                            return "return"
                        elif zero_star_action == "skip":
                            self.log.write_log("info", f"{m}{a}-{b}尚未通关，跳过刷图！")
                            for _ in range(6):
                                self.click(1, 1)
                            return "continue"
                    if stars < 3:
                        if not_three_star_action == "exit":
                            self.log.write_log("info", f"{m}{a}-{b}尚未三星，终止刷图！")
                            self.lock_home()
                            return "return"
                        elif not_three_star_action == "skip":
                            self.log.write_log("info", f"{m}{a}-{b}尚未三星，跳过刷图！")
                            for _ in range(6):
                                self.click(1, 1)
                            return "continue"
                    # 次数判断：对Hard图
                    if m in ["H", "VH"]:
                        cishu = M.get_cishu(sc)
                        if cishu == 0:
                            # 不能扫荡，没有次数
                            ds["hard"][f"{a}-{b}"] = 3
                            record_ds(ds)
                            for _ in range(6):
                                self.click(1, 1)
                            self.log.write_log("info", f"{m}{a}-{b}已经不能再刷更多了！")
                            return "continue"
                    # 体力判断：至少得有一次体力，否则就买
                    left_tili = M.get_tili_left(sc)
                    one_tili = LoadPCRData().get_map_tili(mode, a, b)
                    bought_tili = False
                    if left_tili < one_tili:
                        # 体力不足：可以选择买体力倒是。
                        if ds["buy_tili"] < daily_tili:
                            # 可以！买体力！
                            for _ in range(6):
                                self.click(1, 1)
                            bought_tili = True
                            S.goto_buytili().OK().OK()
                            ds["buy_tili"] += 1
                            record_ds(ds)
                            self.log.write_log("info", f"体力不足，购买体力{ds['buy_tili']}/{daily_tili}")
                        else:
                            # 已经……买不动了
                            self.log.write_log("info", "已经一点体力都不剩了！终止刷图。")
                            self.stop_shuatu()
                            self.lock_home()
                            return "return"
                    if bought_tili:
                        # 买过体力之后要重新进图
                        S.click_xy_and_open_fightinfo(x, y)
                    # 体力次数都够了，进入挑战
                    TZ = M.goto_tiaozhan()
                    # 设置支援
                    select_result = TZ.select_team_with_zhiyuan(team_order, zhiyuan_mode)
                    if (select_result == 'return'):
                        self.lock_home()
                        return 'return'
                    # 进入战斗
                    F = TZ.goto_fight()
                    During = F.get_during()
                    F.set_auto(1, screen=self.last_screen)
                    F.set_speed(2, max_level=2, screen=self.last_screen)
                    state = {"flag": None}
                    last_time = time.time()

                    def jiesuan(next: AfterFightingWin):
                        while True:
                            if time.time() - last_time > 120:
                                raise LockTimeoutError("在结算页面超时！")
                            out = next.check()
                            if out is None:
                                break
                            if isinstance(out, next.KKRQianBao):
                                out.set_and_ok()
                            if isinstance(out, next.XianDingShangDianBox):
                                # 限定商店
                                if xianding:
                                    out.buy_all()
                                else:
                                    out.Cancel()
                            if isinstance(out, next.TuanDuiZhanBox):
                                out.OK()
                            if isinstance(out, next.LevelUpBox):
                                out.OK()
                                self.start_shuatu()  # 体力又有了！
                            if isinstance(out, next.ChaoChuShangXianBox):
                                out.OK()
                            if isinstance(out, next.AfterFightKKR):
                                out.skip()
                                # 再次进图
                                self.get_zhuye().goto_maoxian().goto_zhuxian()
                                break
                            if isinstance(out, next.FightingWinZhuXian2):
                                # 外出后可能还有Box，需要小心谨慎
                                out.next()

                    while True:
                        if time.time() - last_time > 300:
                            # TOO LONG
                            raise LockTimeoutError("战斗超时！")
                        time.sleep(1)
                        out = During.check()
                        if out is None:
                            continue
                        if isinstance(out, During.KKRQianBao):
                            out.set_and_ok()
                        if isinstance(out, During.LoveUpScene):
                            out.skip()
                        if isinstance(out, During.LevelUpBox):
                            out.OK()
                        if isinstance(out, During.FightingLoseZhuXian):
                            state["flag"] = "lose"
                            out.goto_zhuxian(type(S))
                            break
                        if isinstance(out, During.FightingWinZhuXian):
                            state["flag"] = "win"
                            state["star"] = out.get_star()
                            state["next"] = out.get_after()
                            out.next()
                            break
                        if isinstance(out, During.TuanDuiZhanBox):
                            out.OK()
                        if isinstance(out, During.FightingDialog):
                            out.skip()
                        if isinstance(out, During.HaoYouMsg):
                            out.exit_with_off()
                    if state["flag"] == "win":
                        # 记录
                        ds[mode][f"{a}-{b}"] += 1
                        record_ds(ds)
                    if state["flag"] == "win" and state["star"] < 3 and win_without_threestar_is_lose:
                        self.log.write_log("info", f"没有三星通关（{state['star']}/3），算作失败！")
                        state["flag"] = "lose"
                        next = state["next"]
                        jiesuan(next)
                    if state["flag"] == "lose":
                        if lose_action == "exit":
                            self.log.write_log("info", f"战败于{m}{a}-{b}，结束刷图！")
                            self.lock_home()
                            return "return"
                        elif lose_action == "skip":
                            self.log.write_log("info", f"战败于{m}{a}-{b}，跳过该图！")
                            return "continue"
                        elif lose_action == "upgrade":
                            if var["upgraded"] is False:
                                self.log.write_log("info", f"战败于{m}{a}-{b}，尝试升级角色再次刷图！")
                                if team_order not in ['zhanli', 'dengji', 'xingshu', 'shoucang']:
                                    self.log.write_log("error",
                                                       f"战败自动升级中，team_order只能为zhanli/dengji/xingshu/shoucang！终止刷图。")
                                    self.lock_home()
                                    return "return"

                                self.auto_upgrade(buy_tili=upgrade_kwargs.setdefault("buy_tili", daily_tili),
                                                  buy_sucai=upgrade_kwargs.setdefault("buy_sucai", True),
                                                  do_rank=upgrade_kwargs.setdefault("do_rank", True),
                                                  do_shuatu=upgrade_kwargs.setdefault("do_shuatu", True),
                                                  do_kaihua=upgrade_kwargs.setdefault("do_kaihua", True),
                                                  do_zhuanwu=upgrade_kwargs.setdefault("do_zhuanwu", False),
                                                  count=upgrade_kwargs.setdefault("count", 5),
                                                  sortby=upgrade_kwargs.setdefault("sortby", team_order),
                                                  getzhiyuan=True if zhiyuan_mode != 0 else False, var=var)

                                var["upgraded"] = True
                                record_ds(ds)
                                mv.save()
                                self.log.write_log("info", "自动升级结束，重新尝试刷图。")
                                self.restart_this_task()
                            else:
                                self.log.write_log("info", f"战败于{m}{a}-{b}，已经升级过角色还打不过，放弃啦。")
                                self.lock_home()
                                return "return"

                        else:
                            self.log.write_log("info", f"战败于{m}{a}-{b}，重试该图！")
                            raise RetryNow("DOIT")
                    else:
                        # 战胜了！
                        self.log.write_log("info", f"战胜了{m}{a}-{b} ({state['star']}/3)！")
                        last_time = time.time()
                        next = state["next"]
                        jiesuan(next)
                        # 开init
                        S.set_initFC()
                        # 手刷结束
                        t -= 1
                    raise ContinueNow("DOIT")  # 把t次刷完

            self.fclick(1, 1)
            cmd = DOIT()
            self.fclick(1, 1)
            if cmd == "continue":
                continue
            elif cmd == "return":
                if not _use_daily:
                    mv.clearflags()
                return 1
        if not _use_daily:
            mv.clearflags()
        self.log.write_log("info", f"全部刷图任务已经完成。")
        self.lock_home()
        return 0

    def meiriHtu(self, H_list, daily_tili, xianding, do_tuitu, var={}):
        """
        每日H本。
        H_list：list["A-B"],刷什么H图
        daily_tili：购买体力次数
        xianding：是否买空限定商店
        do_tuitu 是否允许推图
        """
        if force_as_ocr_as_possible:
            self.meiriHtu_ocr(H_list, daily_tili, xianding, do_tuitu, var)
        lst = []
        for s in H_list:
            A, B = tuple(s.split("-"))
            lst += [f"H{A}-{B}-3"]
        self.shuatu_daily(lst, daily_tili, xianding, do_tuitu, var=var)

    def meiriHtu_ocr(self, H_list, daily_tili, xianding, do_tuitu, zhiyuan_mode=0, var={}):
        """
        每日H本OCR!!!。
        注：使用队伍为上一次的队伍。
        H_list：list["A-B"],刷什么H图
        daily_tili：购买体力次数
        xianding：是否买空限定商店
        do_tuitu 是否允许推图
        zhiyuan_mode 见shuatu_daily_ocr的相关介绍
        """
        lst = []
        for s in H_list:
            A, B = tuple(s.split("-"))
            lst += [f"H{A}-{B}-3"]
        self.shuatu_daily_ocr(lst,
                              daily_tili,
                              xianding=xianding,
                              not_three_star_action="do" if do_tuitu else "skip",
                              zero_star_action="do" if do_tuitu else "exit",
                              lose_action="exit",
                              win_without_threestar_is_lose=False,
                              team_order="none",
                              zhiyuan_mode=zhiyuan_mode,
                              var=var)

    def xiaohaoHtu(self, daily_tili, do_tuitu, var={}):
        """
        小号每日打H本。
        一个接一个打。
        :param daily_tili:购买体力次数
        :param do_tuitu: 是否允许推图
        """
        if force_as_ocr_as_possible:
            self.xiaohaoHtu_ocr(daily_tili, False, do_tuitu, var)
        L = []
        for i in range(MAX_MAP):
            for j in [1, 2, 3]:
                L += [f"{i + 1}-{j}"]
        self.meiriHtu(L, daily_tili, False, do_tuitu, var)

    def xiaohaoHtu_ocr(self, daily_tili, xianding, do_tuitu, zhiyuan_mode=0, var={}):
        """
        小号每日打H本OCR。
        一个接一个打。
        :param daily_tili:购买体力次数
        :aram xianding: 是否买空限定商店
        :param do_tuitu: 是否允许推图
        :param zhiyuan_mode: 见shuatu_daily_ocr
        """
        L = []
        for i in range(MAX_MAP):
            for j in [1, 2, 3]:
                L += [f"{i + 1}-{j}"]
        self.meiriHtu_ocr(L, daily_tili, xianding, do_tuitu, zhiyuan_mode, var)

    def shengjijuese(self, buy_tili=0, do_rank=True, do_shuatu=True):
        self.lock_home()
        self.auto_upgrade(buy_tili=buy_tili, do_rank=do_rank, do_shuatu=do_shuatu)
        self.lock_home()

    def daily_shuatu_auto(self, daily_tili=0, xianding=True,
                          do_kucunshibie=True, do_jueseshibie=True, n=1, max_tu="max", var={}):
        """
        每日刷图，但是基于角色识别和装备识别自动规划要刷的normal图！
        *你需要在data中事先设定角色的追踪*
        大号专用，默认所有图均三星可扫荡。
        :param daily_tili: 每日体力
        :param xianding: 是否刷空限定商店
        :param do_kucunshibie: 是否做库存识别
        :param do_jueseshibie: 是否做角色识别
        :param n: 当前为N几
        :param max_tu: 最多考虑到图几。设置为max时，为MAX_MAP
        """

        mv = movevar(var)
        if do_kucunshibie and mv.notflag("kucun"):
            self.log.write_log("info", "开始进行前置库存识别")
            self.kucunshibie(var=var)
            mv.setflag("kucun")
        if do_jueseshibie and mv.notflag("juese"):
            self.log.write_log("info", "开始进行前置角色识别")
            self.jueseshibie(var=var)
            mv.setflag("juese")
        import DataCenter
        DataCenter.AR = self.AR
        DataCenter.LoadPCRData()
        arg_strs = [f"--n={n}"]
        if max_tu != "max":
            arg_strs.append(f"--max-tu={max_tu}")
        # arg_str = " ".join(arg_strs)
        self.log.write_log("info", "正在规划最佳刷图方案……")
        out_sorted, out_map = DataCenter.ZB_ST_ADVICE(arg_strs, verbose=False)
        NMap = []
        for i in out_sorted:
            a, b = i.split("-")
            if int(a) < 11:
                continue
            c = out_map[i]
            if int(a) > MAX_MAP:
                self.log.write_log("warning",
                                   f"刷图规划中含有无法刷的图：{a}-{b}，跳过该图！你可以设置max_tu参数来避免这种情况。")
                continue
            NMap += [f"{a}-{b}-{c}"]
        # print("Will be shua:", NMap)
        self.log.write_log("info", f"即将按以下顺序进行刷图：{','.join(NMap)}")

        self.shuatu_daily_ocr(NMap, daily_tili=daily_tili, xianding=xianding, not_three_star_action="skip",
                              can_not_enter_action="skip", zero_star_action="skip", var=var)

    def auto_advance(self, mode=0, team_order="zhanli", buy_tili=0, lose_action="exit"):
        """
        自动推图推主线
        mode: 0-N, 1-H, 2-VH, 3-全推
        buy_tili：所用体力
        其他参数见shuatu_dailt_ocr
        """
        S = None
        if mode == 0:
            S = self.get_zhuye().goto_maoxian().goto_normal().clear_initFC()
        elif mode == 1:
            S = self.get_zhuye().goto_maoxian().goto_hard().clear_initFC()
        elif mode == 2:
            S = self.get_zhuye().goto_maoxian().goto_vh().clear_initFC()
        elif mode == 3:
            self.auto_advance(0, team_order, buy_tili, lose_action)
            self.auto_advance(1, team_order, buy_tili, lose_action)
            self.auto_advance(2, team_order, buy_tili, lose_action)

        self.check_ocr_running()  # 必须要OCR！
        self.select_most_right()

        next_level_pos = None
        for _ in range(5):
            next_level_pos = self.img_where(MAOXIAN_BTN["next_level"], threshold=0.965)
            if next_level_pos:
                x, y = next_level_pos
                # TODO: 这里的结构应该改成 shuatu base enter_next_level
                S = S.click_xy_and_open_fightinfo(x, y + 90)
                if not S:
                    S = S.click_xy_and_open_fightinfo(x, y + 50)
                if isinstance(S, FightInfoZhuXian):
                    # 找自动，打勾，
                    if S.can_auto_advance():
                        S.set_auto_advance()
                        BZ = S.goto_tiaozhan()
                        out = BZ.select_team_with_zhiyuan(team_order)
                        # if(select_result == 'return'):
                        #     self.lock_home()
                        #     return 'return'
                        F = BZ.goto_fight(buy_tili)
                        During = F.get_during()
                        F.set_auto(1, screen=self.last_screen)
                        F.set_speed(2, max_level=2, screen=self.last_screen)
                        state = {"flag": None}
                        last_time = time.time()
                        # TODO: 还没写完
                        # 999体 99次Normal 49次Hard 49次VH
                        # 从消耗体力推测需要推的关卡数量
                        time_max = 2400
                        time_wait = 0
                        while time_wait < time_max:
                            time.sleep(1)

                    else:
                        self.log.write_log("error", f"该关卡无法自动推进，放弃刷图")
                    # 

        if not next_level_pos:
            self.log.write_log("info", f"找不到下一关，放弃刷图")

        self.lock_home()

    ## 以下为活动和外传部分

    def dahaohuodong_hard(self, tu_order=[], code="current", entrance_ind="auto", var=None):
        """
        大号刷活动Hard图，要求已经手动通过关。
        tu_order: list of [1,2,3,4,5]
        code: 见scenes/huodng/huodong_manager.py
        entrance_ind：在冒险界面进入活动，设置为"auto"时，自动寻找剧情活动按钮；设置为int时，固定为从右往左数第几个按钮
        """
        self.lock_home()
        if not self.check_shuatu():
            return
        # List of str -> List of int
        tu_order = [int(s) for s in tu_order]
        MAP = self.get_zhuye().goto_maoxian().goto_huodong(code, entrance_ind)
        if MAP is False:
            self.log.write_log("warning", "无法找到活动入口，请确认是否活动期间")
            self.lock_home()
            return
        self.log.write_log("info", f"开始刷活动Hard：{MAP.NAME} - {tu_order}")
        out = MAP.shua_hard(tu_order)
        self.lock_home()

    def dahaohuodong_VHBoss(self, team_order="none", code="current", entrance_ind="auto", var=None):
        """
        大号打VHBoss，team_order见shuatu_daily_ocr。
        code: 见scenes/huodng/huodong_manager.py
        entrance_ind：在冒险界面进入活动，设置为"auto"时，自动寻找剧情活动按钮；设置为int时，固定为从右往左数第几个按钮
        """
        self.shua_hd_boss(team_order=team_order, code=code, entrance_ind=entrance_ind, once=True, boss_type="VH",
                          var=var, )
        # self.lock_home()
        # MAP = self.get_zhuye().goto_maoxian().goto_huodong(code, entrance_ind)
        # if MAP is False:
        #     self.log.write_log("warning", "无法找到活动入口，请确认是否活动期间")
        #     self.lock_home()
        #     return
        # self.log.write_log("info", f"开始刷活动VHBoss：{MAP.NAME}")
        # MAP.shua_VHBoss(team_order)
        # self.lock_home()

    def xiaohaohuodong_11(self, cishu="max", team_order="zhanli", get_zhiyuan=True, code="current", entrance_ind="auto",
                          var=None):
        """
        小号打活动1-1，没打过会推图。cishu可以为"max"或整数
        team_order见shuatu_daily_ocr。
        get_zhiyuan：设置为True，任意借支援。
        code: 见scenes/huodng/huodong_manager.py
        entrance_ind：在冒险界面进入活动，设置为"auto"时，自动寻找剧情活动按钮；设置为int时，固定为从右往左数第几个按钮
        """
        self.lock_home()
        if not self.check_shuatu():
            return
        if cishu != "max":
            cishu = int(cishu)
        MAP = self.get_zhuye().goto_maoxian().goto_huodong(code, entrance_ind)
        if MAP is False:
            self.log.write_log("warning", "无法找到活动入口，请确认是否活动期间")
            self.lock_home()
            return
        self.log.write_log("info", f"开始刷活动1-1：{MAP.NAME}")
        c, cishu_left = MAP.shua_11(cishu, team_order, get_zhiyuan)

        if c == 0 and (cishu_left == "max" or cishu_left > 0):
            # 再刷一次
            MAP = self.get_zhuye().goto_maoxian().goto_huodong(code, entrance_ind)
            if MAP is False:
                self.lock_home()
                return
            c, cishu_left = MAP.shua_11(cishu_left, team_order, get_zhiyuan)
        self.lock_home()

    def exchange_tfz(self, code="current", entrance_ind="auto", reset=False,
                     var=None):
        """
        code: 见scenes/huodng/huodong_manager.py
        entrance_ind：在冒险界面进入活动，设置为"auto"时，自动寻找剧情活动按钮；设置为int时，固定为从右往左数第几个按钮
        """
        self.lock_home()
        MAP = self.get_zhuye().goto_maoxian().goto_huodong(code, entrance_ind)
        if MAP is False:
            self.log.write_log("warning", "无法找到活动入口，请确认是否活动期间")
            self.lock_home()
            return
        MAP.exchange_tfz(reset=reset)
        self.lock_home()

    def shua_hd_boss(self, team_order="none", code="current", entrance_ind="auto", once=False, boss_type=None,
                     var=None):
        """
        打活动Boss，team_order见shuatu_daily_ocr。
        code: 见scenes/huodng/huodong_manager.py
        entrance_ind：在冒险界面进入活动，设置为"auto"时，自动寻找剧情活动按钮；设置为int时，固定为从右往左数第几个按钮
        """
        self.lock_home()
        act_map = self.get_zhuye().goto_maoxian().goto_huodong(code, entrance_ind)
        if act_map is False:
            self.log.write_log("warning", "无法找到活动入口，请确认是否活动期间")
            self.lock_home()
            return
        act_map.goto_hd_menu()
        self.log.write_log("info", f"开始刷活动Boss,难度{boss_type}")
        act_map.shua_hd_boss(team_order=team_order, once=once, boss_type=boss_type)
        self.lock_home()

    def tui_hd_map(self, diff="N", team_order="none", code="current", entrance_ind="auto", get_zhiyuan=False,
                   if_full=0, if_auto=True, var=None):

        self.lock_home()
        # 体力检查
        if not self.check_shuatu():
            return
        MAP: HuodongMapBase = self.get_zhuye().goto_maoxian().goto_huodong(code, entrance_ind)
        # 活动期间检查
        if MAP is False:
            self.log.write_log("warning", "无法找到活动入口，请确认是否活动期间")
            self.lock_home()
            return
        self.log.write_log("debug", f"类型：{type(MAP)}")
        MAP.tui_hd_map(diff=diff, team_order=team_order, get_zhiyuan=get_zhiyuan, if_full=if_full, if_auto=if_auto)
        self.fclick(1, 1)
        self.lock_home()

    def tui_hd_map_normal(self, team_order="none", code="current", entrance_ind="auto", get_zhiyuan=False,
                          if_full=0, if_auto=True, var=None):
        self.tui_hd_map(diff="N", team_order=team_order, code=code, entrance_ind=entrance_ind, get_zhiyuan=get_zhiyuan,
                        if_full=if_full, if_auto=if_auto)

    def tui_hd_map_hard(self, team_order="none", code="current", entrance_ind="auto", get_zhiyuan=False,
                        if_full=0, if_auto=True, var=None):
        self.tui_hd_map(diff="H", team_order=team_order, code=code, entrance_ind=entrance_ind, get_zhiyuan=get_zhiyuan,
                        if_full=if_full, if_auto=if_auto)

    def shua_hd_map_normal(self, code="current", entrance_ind="auto", map_id=1, cishu="max", var=None):

        self.lock_home()
        if not self.check_shuatu():
            return
        MAP = self.get_zhuye().goto_maoxian().goto_huodong(code=code, entrance_ind=entrance_ind)
        if MAP is False:
            self.log.write_log("warning", "无法找到活动入口，请确认是否活动期间")
            self.lock_home()
            return
        MAP.shua_hd_map_normal(map_id=map_id, cishu=cishu)
        self.lock_home()

    def huodong_getbonus(self, code="current", entrance_ind="auto", var=None):
        self.lock_home()
        MAP = self.get_zhuye().goto_maoxian().goto_huodong(code, entrance_ind)
        if MAP is False:
            self.log.write_log("warning", "无法找到活动入口，请确认是否活动期间")
            self.lock_home()
            return
        MAP.huodong_getbonus()
        self.lock_home()

    def huodong_read_juqing(self, code="current", entrance_ind="auto", var=None):
        self.lock_home()
        MAP = self.get_zhuye().goto_maoxian().goto_huodong(code, entrance_ind)
        if MAP is False:
            self.log.write_log("warning", "无法找到活动入口，请确认是否活动期间")
            self.lock_home()
            return
        MAP.huodong_read_juqing()
        self.lock_home()

    def huodong_read_xinlai(self, code="current", entrance_ind="auto", var=None):
        self.lock_home()
        MAP = self.get_zhuye().goto_maoxian().goto_huodong(code, entrance_ind)
        if MAP is False:
            self.log.write_log("warning", "无法找到活动入口，请确认是否活动期间")
            self.lock_home()
            return
        if MAP.XINLAI is False:
            self.log.write_log("warning", "该活动无信赖度章节")
            self.lock_home()
            return
        MAP.huodong_read_xinlai()
        self.lock_home()

    def tui_wz(self, code="01", team_order="none", if_full=2, get_zhiyuan=False):
        self.lock_home()

        if code == "08" or code == "12":
            self.log.write_log("error", f"由于场景限制，暂不支持外传08和外传12的自动推图！")
            return

        def check_wz_menu(code):
            sPossibleWZEnteringScene: PCRSceneBase = self.get_zhuye().goto_zhucaidan().goto_waizhuan()
            if (sPossibleWZEnteringScene.scene_name != "WZ_Gallery"):
                self.log.write_log("error", f"外传未解锁！请先通关主线3-2!")
                # todo：外层return
                self.lock_home()
                return False
            else:
                return sPossibleWZEnteringScene.goto_wz_menu(code)

        # 进图，前提：能进外传
        def tui_map(diff):
            Menu: WZ_Menu = self.get_zhuye().goto_zhucaidan().goto_waizhuan().goto_wz_menu(code)
            # 获取初始坐标及常数
            HXY1 = Menu._check_coord(Menu.HXY1)
            N_slice = Menu._check_constant(Menu.N_slice)
            NXY1 = Menu._check_coord(Menu.NXY1)
            if N_slice >= 2:
                NXY2 = Menu._check_coord(Menu.NXY2)
            if N_slice == 3:
                NXY3 = Menu._check_coord(Menu.NXY3)
            N1 = Menu._check_constant(Menu.N1)
            if N_slice >= 2:
                N2 = Menu._check_constant(Menu.N2)
            if N_slice == 3:
                N3 = Menu._check_constant(Menu.N3)
            # 函数内参数，第一次根据要求选编队，后续就不用选了，减少用时
            first_time = True

            # 推图大循环
            # 初始化Normal分片计数器,bool,T代表完成，F代表未完成
            if N_slice == 3:
                n3 = False
            if N_slice >= 2:
                n2 = False
            n1 = False
            while True:
                now = 0
                if self.check_shuatu() is False:
                    break
                MAP = Menu.goto_map()
                if diff == "N":
                    # 先到最左
                    MAP.goto_wz_normal()
                    MAP.go_left(N_slice - 1)
                    # 分段计数器
                    now = 1
                    if N_slice >= 2:
                        # 第一分片已完成，向右到第二分片
                        if n1 is True:
                            MAP.go_right(1)
                            now = 2
                        # 第二分片已完成，向右到第三分片
                        if n2 is True:
                            MAP.go_right(1)
                            now = 3
                else:
                    MAP.goto_wz_hard()
                MAP.to_leftdown()
                MAP.to_leftdown()
                if diff == "N":
                    # Normal 难度
                    if now is 2:
                        fi = MAP.click_xy_and_open_fightinfo(*NXY2, typ=FightInfoBase)
                        max_tu = N2 - N1
                    # 第二分片已完成，向右到第三分片
                    elif now is 3:
                        fi = MAP.click_xy_and_open_fightinfo(*NXY3, typ=FightInfoBase)
                        max_tu = N3 - N2
                    else:
                        max_tu = N1
                        fi = MAP.click_xy_and_open_fightinfo(*NXY1, typ=FightInfoBase)
                    if fi:
                        a = fi.to_last_map(max_tu=max_tu)
                    else:
                        raise RuntimeError(f"出现了进不了外传{code}[{Menu.NAME}]Normal图分段{now}" +
                                           "的错误，可能坐标存在偏移！")
                else:
                    # Hard难度
                    fi = MAP.click_xy_and_open_fightinfo(*HXY1, typ=FightInfoBase)
                    if fi:
                        a = fi.to_last_map(max_tu=5)
                    else:
                        raise RuntimeError(f"出现了进不了外传{code}[{Menu.NAME}]Hard图" +
                                           "的错误，可能坐标存在偏移！")

                if a == "finish" and fi.get_upperright_stars() == 3:
                    if diff == "N":
                        self.fclick(1, 1)
                        if now is 1:
                            n1 = True
                            if N_slice == 1:
                                break
                            else:
                                continue
                        elif now is 2:
                            n2 = True
                            if N_slice == 2:
                                break
                            else:
                                continue
                        else:
                            # now is 3:
                            n3 = True
                            if N_slice == 3:
                                break
                            else:
                                continue
                    if diff == "H":
                        break

                else:
                    st = fi.easy_shoushua(team_order=team_order, one_tili=10, max_speed=2, get_zhiyuan=get_zhiyuan,
                                          if_full=if_full)  # 打完默认回fi
                    if st == 1 or st == 3:
                        self.stop_shuatu()
                        self.fclick(1, 1)
                        WZ_MapBase(self).enter().goto_menu()
                    if first_time:
                        first_time = False
                        continue

                    time.sleep(3)
                    self.fclick(1, 1)
                    time.sleep(1)
                    out = self.lock_img({
                        HUODONG_BTN["shadow_return"]: 1,  # 可以看到return的情况
                        HUODONG_BTN["shadow_help"]: 1,  # 信赖度
                        HUODONG_BTN["NORMAL_ON"]: 2,  # Normal，在map了
                        HUODONG_BTN["HARD_ON"]: 2,  # Hard，在map了
                        JUQING_BTN["caidanyuan"]: 3,  # 剧情菜单
                        HUODONG_BTN["speaker_box"]: 1,
                        WZ_BTN["help"]: 4,

                    }, elseclick=(1, 1), timeout=20, is_raise=False, threshold=0.9)

                    if out == 1:
                        self.lock_img(WZ_BTN["help"], elseclick=(31, 30), elsedelay=1, timeout=120)
                        continue
                    elif out == 2:
                        continue
                    elif out == 3:
                        self.guojuqing(story_type="huodong")
                        continue
                    elif out == 4:
                        continue
                    else:
                        self.fclick(1, 1)
                        continue
            self.fclick(1, 1)
            WZ_MapBase(self).enter().goto_menu()

        def tui_nboss():
            # 开始Nboss
            Menu = WZ_Menu(self).enter().goto_nboss()
            fb: FightBianZuHuoDong = Menu.goto(FightBianZuHuoDong,
                                               Menu.fun_click(HUODONG_BTN["tiaozhan2_on"]))
            fb.select_team(team_order=team_order)
            zd = fb.goto_zhandou()
            zd.auto_and_fast(1)
            time.sleep(1)
            while True:
                out = self.lock_img({
                    HUODONG_BTN["NORMAL_ON"]: 1,  # Normal，在map了
                    HUODONG_BTN["HARD_ON"]: 1,  # Hard，在map了
                    WZ_BTN["help"]: 3,
                    HUODONG_BTN["long_next"]: 4,
                    HUODONG_BTN["short_next"]: 5,
                    HUODONG_BTN["short_next2"]: 5,
                    FIGHT_BTN["menu"]: 6,

                }, elseclick=(1, 1), timeout=20, is_raise=False, threshold=0.85)

                if out == 1:
                    self.lock_img(WZ_BTN["help"], elseclick=(31, 30), elsedelay=1, timeout=120)
                    break
                elif out == 3:
                    break
                elif out == 4:
                    self.click_btn(HUODONG_BTN["long_next"])
                    continue
                elif out == 5:
                    self.click(838, 489)
                    time.sleep(3)
                    continue
                elif out == 6:
                    time.sleep(6)
                    continue
                else:
                    self.fclick(1, 1)
                    continue

        def tui_hboss():
            # 开始hboss
            Menu = WZ_Menu(self).enter().goto_hboss()
            fb: FightBianZuHuoDong = Menu.goto(FightBianZuHuoDong,
                                               Menu.fun_click(HUODONG_BTN["tiaozhan2_on"]))
            fb.select_team(team_order="1-1")
            zd = fb.goto_zhandou()
            zd.auto_and_fast(1)
            time.sleep(1)
            while True:
                out = self.lock_img({
                    HUODONG_BTN["NORMAL_ON"]: 1,  # Normal，在map了
                    HUODONG_BTN["HARD_ON"]: 1,  # Hard，在map了
                    WZ_BTN["help"]: 3,
                    HUODONG_BTN["long_next"]: 4,
                    HUODONG_BTN["short_next"]: 5,
                    HUODONG_BTN["short_next2"]: 5,
                    FIGHT_BTN["menu"]: 6,

                }, elseclick=(1, 1), timeout=20, is_raise=False, threshold=0.85)

                if out == 1:
                    self.lock_img(WZ_BTN["help"], elseclick=(31, 30), elsedelay=1, timeout=120)
                    break
                elif out == 3:
                    break
                elif out == 4:
                    self.click_btn(HUODONG_BTN["long_next"])
                    continue
                elif out == 5:
                    self.click(838, 489)
                    time.sleep(3)
                    continue
                elif out == 6:
                    time.sleep(6)
                    continue
                else:
                    self.fclick(1, 1)
                    continue

        def tui_vhboss():
            # 开始vhboss
            Menu = HuodongMenu(self).goto_vhboss()
            fb: FightBianZuHuoDong = Menu.goto(FightBianZuHuoDong,
                                               Menu.fun_click(HUODONG_BTN["tiaozhan2_on"]))
            fb.select_team(team_order=team_order)
            zd = fb.goto_zhandou()
            zd.auto_and_fast(1)
            time.sleep(1)
            while True:
                out = self.lock_img({
                    HUODONG_BTN["NORMAL_ON"]: 1,  # Normal，在map了
                    HUODONG_BTN["HARD_ON"]: 1,  # Hard，在map了
                    WZ_BTN["help"]: 3,
                    HUODONG_BTN["long_next"]: 4,
                    HUODONG_BTN["short_next"]: 5,
                    HUODONG_BTN["short_next2"]: 5,
                    FIGHT_BTN["menu"]: 6,

                }, elseclick=(1, 1), timeout=20, is_raise=False, threshold=0.85)

                if out == 1:
                    self.lock_img(WZ_BTN["help"], elseclick=(31, 30), elsedelay=2, timeout=120)
                    break
                elif out == 3:
                    break
                elif out == 4:
                    self.click_btn(HUODONG_BTN["long_next"])
                    continue
                elif out == 5:
                    self.click(838, 489)
                    continue
                elif out == 6:
                    time.sleep(6)
                    continue
                else:
                    self.fclick(1, 1)
                    continue

        def get_liwu():
            self.lock_img(WZ_BTN["help"], elseclick=(1, 1), elsedelay=1)
            self.click_btn(HUODONG_BTN["liwu"], until_appear=HUODONG_BTN["wanchengqingkuang"])
            time.sleep(0.2)
            self.click(781, 433)  # 收取
            time.sleep(1)
            self.click(478, 468)  # 关闭
            time.sleep(1)

        if not check_wz_menu(code):
            return

        self.fclick(1, 1)
        time.sleep(1)
        boss_count = self.img_where_all(img=WZ_BTN["boss_pass"].img, at=(673, 78, 806, 376), threshold=0.8)
        passes = len(boss_count) / 3
        self.log.write_log("info", f"已通关{passes}个boss")

        if passes < 1:
            tui_map("N")
            time.sleep(5)
            tui_nboss()
            time.sleep(5)
        if passes < 2:
            tui_map("H")
            time.sleep(5)
            tui_hboss()
            time.sleep(5)
        if passes < 3:
            tui_vhboss()
        else:
            self.log.write_log("info", f"该外传已全部通关，前往领取任务奖励")
        self.lock_home()
        self.get_zhuye().goto_zhucaidan().goto_waizhuan().goto_wz_menu(code)
        get_liwu()
        self.lock_home()

    def yijiansaodang(self, times=3):
        self.lock_home()
        self.get_zhuye().goto_maoxian().goto_zhuxian()
        self.lock_img(MAOXIAN_BTN["saodangquan"])
        self.click_btn(MAOXIAN_BTN["saodangquan"], until_appear=MAOXIAN_BTN["guankayilan"])
        if times != 3:
            self.fclick(731, 410)
            self.fclick(731, 410)
            i = 1
            while True:
                if i < times:

                    if self.is_exists(FIGHT_BTN["tilibuzu"]):
                        break
                    self.click(882, 410)
                    time.sleep(0.2)
                    i += 1
                    continue
                else:
                    break
        if self.is_exists(FIGHT_BTN["no_tili_2"], threshold=0.9):
            self.log.write_log("warning", "扫荡体力不足，跳过")
            self.skip_this_task()
        self.click_btn(FIGHT_BTN["yijiansaodang"], until_disappear=FIGHT_BTN["quxiao"])
        self.lock_no_img(FIGHT_BTN["quxiao"])
        time.sleep(0.5)

        while True:
            sc = self.getscreen()
            # 挑战次数不足
            if self.is_exists(FIGHT_BTN["yijianhuifu"]):
                self.click_btn(FIGHT_BTN["buhuifu"])
                print("111")
                continue

            if self.is_exists(FIGHT_BTN["yijiansaodangqueren"]):
                self.click_img(screen=sc, img="img/queren.jpg")
                print("222")
                break
            # 体力不足，部分关卡不能进行
            if self.is_exists(FIGHT_BTN["yijiansaodangqueren2"]):
                self.click_img(screen=sc, img="img/queren.jpg")

                print("333")
                continue
        self.click_btn(FIGHT_BTN["tiaozhan_saodang"], until_appear=FIGHT_BTN["saodangjieguo"])
        time.sleep(5)
        self.lock_home()
