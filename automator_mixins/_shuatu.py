import time

from core.constant import HARD_COORD, NORMAL_COORD
from core.cv import UIMatcher
from core.log_handler import pcr_log
from core.valid_task import ShuatuToTuple
from ._shuatu_base import ShuatuBaseMixin

# 已支持刷图选项
operation_dic = {
    'h00': 'self.ziduan00()',  # h00为不刷任何hard图
    'h01': 'self.do1_11Hard()',  # 刷hard 1-11图,默认购买3次体力,不想刷的图去注释掉即可
    'tsk': 'self.tansuo()',  # 探索开,注意mana号没开探索可能会卡死
    'n07': 'self.shuatu7()',  # 刷7图
    'n08': 'self.shuatu8()',  # 刷8图
    'n10': 'self.shuatu10()',  # 刷10图
    'n11': 'self.shuatu11()',  # 刷11图
    'n12': 'self.shuatu12()',  # 刷12图
}


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
        #进入冒险选项卡
        self.click(480,505)
        time.sleep(2)
        # 进入地图（此处写500，90是为了防止误触到关卡）
        self.lockimg("img/dixiacheng.jpg",ifclick=(500, 90),elseclick=(480,505),alldelay=2,ifbefore=0.5)
        #判断是否进入地图
        self.lockimg("img/ditu.jpg",ifclick=(701, 83),elseclick=(500, 90),alldelay=2,ifbefore=0.5)
        # 进入normal图（此处很容易卡）
        self.lockimg("img/normal.jpg", elseclick=(701, 83), alldelay=2, ifbefore=3)
        # 进入1图
        for i in range(map):
            time.sleep(3)
            self.click(27, 272)
        self.shuatuzuobiao(106, 279, 160)  # 1-1 刷7次体力为佳
        self.lock_home()

    # 刷经验3-1
    def shuajingyan3(self, map):
        """
        刷图刷3-1
        map为主图
        """
        # 进入冒险
        #进入冒险选项卡
        self.click(480,505)
        time.sleep(2)
        # 进入地图（此处写500，90是为了防止误触到关卡）
        self.lockimg("img/dixiacheng.jpg",ifclick=(500, 90),elseclick=(480,505),alldelay=2,ifbefore=0.5)
        #判断是否进入地图
        self.lockimg("img/ditu.jpg",ifclick=(701, 83),elseclick=(500, 90),alldelay=2,ifbefore=0.5)
        # 进入normal图（此处很容易卡）
        self.lockimg("img/normal.jpg", elseclick=(701, 83), alldelay=2, ifbefore=3)
        # 进入3图
        for i in range(map-3):
            time.sleep(3)
            self.click(27, 272)
        self.shuatuzuobiao(138, 188, 125)  # 3-1
        self.lock_home()


    def shuatuNN(self, tu_dict: list):
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
        for cur in L:
            A, B, Times = cur
            if A not in NORMAL_COORD:
                pcr_log(self.account).write_log("error", f"坐标库中没有图号{A}-{B}的信息！跳过此图。")
                continue
            while cur_map != A:
                self.select_normal_id(A)
                cur_map = A
            now_dict = NORMAL_COORD[A]
            if B in now_dict["left"]:
                self.Drag_Left()
                xy = now_dict["left"][B]
                self.shuatuzuobiao(*xy, Times)
            elif B in now_dict["right"]:
                self.Drag_Right()
                xy = now_dict["right"][B]
                self.shuatuzuobiao(*xy, Times)
            else:
                pcr_log(self.account).write_log("error", f"坐标库中没有图号{A}-{B}的信息！跳过此图。")
                continue
        self.lock_home()

    def shuatuHH(self, tu_dict: list):
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
        for cur in L:
            A, B, Times = cur
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
            if UIMatcher.img_where(screen_shot_, 'img/normal.jpg'):
                self.click(880, 80)
            if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                break
        self.shuatuzuobiao(689, 263, self.times)  # 1-5
        self.continueDo9(570, 354)  # 1-4
        self.continueDo9(440, 255)  # 1-3
        self.continueDo9(300, 339)  # 1-2
        self.continueDo9(142, 267)  # 1-1
        self.lock_home()
