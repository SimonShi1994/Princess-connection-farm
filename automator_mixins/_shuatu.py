import time
from typing import List

from core.cv import UIMatcher
from core.log_handler import pcr_log
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
            if UIMatcher.img_where(screen_shot_, 'img/normal.jpg', at=(660, 72, 743, 94)):
                break
        for i in range(map):
            time.sleep(3)
            self.d.click(27, 272)
        self.shuatuzuobiao(106, 279, 160)  # 1-1 刷7次体力为佳

        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

        # 刷11-3 hard图

    def shuatuNN(self, tu_list: List[List[int]]):
        """
        刷指定N图
        :param tu_list: 刷图列表
            一个包含了若干个List的List
            每一个List的格式如下：
                [大图号,小图号,刷图次数]
            例如[12,3,3]表示刷12-3图3次
            该List不必在意顺序，因为该函数内自动会调整顺序。
        """
        from core.constant import NORMAL_COORD
        # 进入冒险
        L = tu_list.copy()
        # 按照 A-B的顺序排序：A为主要依据，B为次要依据。
        L.sort(key=lambda x: (x[0], x[1]))
        self.enter_normal(7)
        cur_map = 7
        self.switch = 0
        for cur in L:
            A, B, Times = cur[0], cur[1], cur[2]
            if A not in NORMAL_COORD:
                pcr_log(self.account).write_log("error", f"坐标库中没有图号{A}-{B}的信息！跳过此图。")
                continue
            while cur_map < A:
                cur_map += 1
                self.goRight()

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
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    def shuatuHH(self, tu_list: List[List[int]]):
        """
        刷指定H图
        :param tu_list: 刷图列表
            一个包含了若干个List的List
            每一个List的格式如下：
                [大图号,小图号,刷图次数]
            例如[12,3,3]表示刷H12-3图3次
            该List不必在意顺序，因为该函数内自动会调整顺序。
        :return:
        """
        from core.constant import HARD_COORD
        self.goHardMap()  # 进入Hard本
        self.switch = 0
        L = tu_list.copy()
        # 按照 A-B的顺序排序：A为主要依据，B为次要依据。
        L.sort(key=lambda x: (x[0], x[1]))
        cur_map = 1
        for cur in L:
            A, B, Times = cur[0], cur[1], cur[2]
            if A not in HARD_COORD:
                pcr_log(self.account).write_log("error", f"坐标库中没有图号H{A}-{B}的信息！跳过此图。")
                continue
            while cur_map < A:
                cur_map += 1
                self.goRight()
            now_dict = HARD_COORD[A]
            if B in now_dict:
                xy = now_dict[B]
                self.shuatuzuobiao(*xy, Times)
            else:
                pcr_log(self.account).write_log("error", f"坐标库中没有图号H{A}-{B}的信息！跳过此图。")
                continue
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    # 刷活动hard图
    def doActivityHard(self):
        # 进入冒险
        time.sleep(2)
        self.d.click(480, 505)
        time.sleep(2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
        # 点击进入活动
        self.d.click(415, 430)
        time.sleep(3)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            self.d.click(480, 380)
            time.sleep(0.5)
            self.d.click(480, 380)
            if UIMatcher.img_where(screen_shot_, 'img/normal.jpg'):
                self.d.click(880, 80)
            if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                break
        self.shuatuzuobiao(689, 263, self.times)  # 1-5
        self.continueDo9(570, 354)  # 1-4
        self.continueDo9(440, 255)  # 1-3
        self.continueDo9(300, 339)  # 1-2
        self.continueDo9(142, 267)  # 1-1
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
