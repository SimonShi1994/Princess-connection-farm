import time

from core.cv import UIMatcher
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

    # 不安全，建议删除
    def shuatu(self, opcode):
        for i in range(0, len(opcode), 3):
            if opcode[i] != 'h':
                eval(operation_dic[opcode[i:i+3]])

    # 不安全，建议删除
    def shuatu_hard(self, opcode):
        for i in range(0, len(opcode), 3):
            if opcode[i] == 'h':
                eval(operation_dic[opcode[i:i+3]])

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

    def do11to3Hard(self):
        # 进入冒险
        self.enterHardMap()
        self.continueDo9(767, 327)  # 11-3
        self.continueDo9(479, 241)  # 11-2
        self.continueDo9(217, 360)  # 11-1
        self.goLeft()
        self.continueDo9(764, 334)  # 10-3
        self.goLeft()
        self.goLeft()
        self.continueDo9(218, 386)  # 8-1
        self.goLeft()
        self.continueDo9(749, 285)  # 7-3
        self.continueDo9(476, 335)  # 7-2
        self.goLeft()
        self.goLeft()
        self.continueDo9(696, 270)  # 5-3
        self.goLeft()
        self.continueDo9(247, 270)  # 4-1

        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

        # 刷1-3 hard图

    def do1to3Hard(self):
        # 进入冒险
        self.enterHardMap()
        self.shuatuzuobiao(250, 280, self.times)  # 4-1
        self.goLeft()
        self.continueDo9(715, 280)  # 3-3
        self.continueDo9(470, 365)  # 3-2
        self.continueDo9(255, 260)  # 3-1
        self.goLeft()
        self.continueDo9(729, 340)  # 2-3
        self.continueDo9(473, 368)  # 2-2
        self.continueDo9(280, 275)  # 2-1
        self.goLeft()
        self.continueDo9(251, 340)  # 1-1
        self.continueDo9(465, 266)  # 1-2
        self.continueDo9(695, 318)  # 1-3
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    def ziduan00(self):
        print('>>>识别到00参数该字段不刷图,要刷图请更改zhanghao.txt！结束刷图任务！<<<\r\n')
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    # 刷1-11 Hard图,分账号刷hard
    def do1_11Hard(self):
        self.goHardMap()  # 进入Hard本
        self.hard_shuatuzuobiao(250, 340, self.times)  # 1-1妈
        # self.hard_shuatuzuobiao(465, 270, self.times)  # 1-2铃铛
        # self.hard_shuatuzuobiao(695, 325, self.times)  # 1-3香菜弓
        self.goRight()
        # self.hard_shuatuzuobiao(286, 270, self.times)  # 2-1剑圣怜
        self.hard_shuatuzuobiao(474, 370, self.times)  # 2-2优衣
        self.hard_shuatuzuobiao(730, 340, self.times)  # 2-3充电宝
        self.goRight()
        self.hard_shuatuzuobiao(255, 260, self.times)  # 3-1佩可
        self.hard_shuatuzuobiao(470, 365, self.times)  # 3-2羊驼
        self.hard_shuatuzuobiao(715, 280, self.times)  # 3-3兔子
        self.goRight()
        self.hard_shuatuzuobiao(250, 275, self.times)  # 4-1妈
        # self.hard_shuatuzuobiao(485, 240, self.times)  # 4-2大眼
        # self.hard_shuatuzuobiao(765, 260, self.times)  # 4-3扇子
        self.goRight()
        # self.hard_shuatuzuobiao(245, 325, self.times)  # 5-1铃铛
        # self.hard_shuatuzuobiao(450, 245, self.times)  # 5-2美东
        self.hard_shuatuzuobiao(700, 270, self.times)  # 5-3tp弓栞
        self.goRight()
        self.hard_shuatuzuobiao(265, 305, self.times)  # 6-1优衣
        # self.hard_shuatuzuobiao(500, 310, self.times)  # 6-2牛
        self.hard_shuatuzuobiao(715, 260, self.times)  # 6-3姐姐
        self.goRight()
        self.hard_shuatuzuobiao(275, 245, self.times)  # 7-1佩可
        # self.hard_shuatuzuobiao(475, 345, self.times)  # 7-2病娇
        # self.hard_shuatuzuobiao(745, 290, self.times)  # 7-3忍
        self.goRight()
        # self.hard_shuatuzuobiao(215, 390, self.times)  # 8-1剑圣怜
        # self.hard_shuatuzuobiao(480, 355, self.times)  # 8-2镜子
        # self.hard_shuatuzuobiao(715, 295, self.times)  # 8-3哈哈剑
        self.goRight()
        # self.hard_shuatuzuobiao(220, 270, self.times)  # 9-1香菜弓
        self.hard_shuatuzuobiao(480, 355, self.times)  # 9-2兔子
        self.hard_shuatuzuobiao(765, 295, self.times)  # 9-3充电宝
        self.goRight()
        # self.hard_shuatuzuobiao(220, 365, self.times)  # 10-1大眼
        # self.hard_shuatuzuobiao(480, 250, self.times)  # 10-2美东
        self.hard_shuatuzuobiao(765, 330, self.times)  # 10-3扇子
        self.goRight()
        self.hard_shuatuzuobiao(215, 360, self.times)  # 11-1羊驼
        self.hard_shuatuzuobiao(480, 250, self.times)  # 11-2病娇
        self.hard_shuatuzuobiao(765, 330, self.times)  # 11-3姐姐
        self.goRight()
        # self.hard_shuatuzuobiao(215, 255, self.times)  # 11-1牛
        # self.hard_shuatuzuobiao(480, 355, self.times)  # 11-2栞
        # self.hard_shuatuzuobiao(765, 240, self.times)  # 11-3哈哈剑
        self.goRight()

        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    # 刷7图
    def shuatu7(self):
        # 进入冒险
        self.click(480, 505, pre_delay=2, post_delay=2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
        self.d.click(562, 253)
        time.sleep(3)
        self.d.click(701, 83)
        time.sleep(2)
        self.duanyazuobiao()
        if self.tag < 22:  # 暂时先按各11次来判定
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/normal.jpg', at=(660, 72, 743, 94)):
                    break
                if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                    self.d.click(701, 83)
                    break
            self.switch = 0
            self.d.drag(600, 270, 200, 270, 0.1)  # 拖拽到最右
            time.sleep(2)
            self.shuatuzuobiao(760, 240, self.times)  # 7-14
            self.shuatuzuobiao(630, 257, self.times)  # 7-13
            self.shuatuzuobiao(755, 350, self.times)  # 7-12
            self.shuatuzuobiao(664, 410, self.times)  # 7-11
            self.shuatuzuobiao(544, 400, self.times)  # 7-10
            self.shuatuzuobiao(505, 300, self.times)  # 7-9
            self.shuatuzuobiao(410, 240, self.times)  # 7-8
            self.d.drag(200, 270, 600, 270, 0.1)  # 拖拽到最左
            time.sleep(2)
            self.shuatuzuobiao(625, 230, self.times)  # 7-7
            self.shuatuzuobiao(680, 365, self.times)  # 7-6
            self.shuatuzuobiao(585, 425, self.times)  # 7-5
            self.shuatuzuobiao(500, 330, self.times)  # 7-4
            self.shuatuzuobiao(450, 240, self.times)  # 7-3
            self.shuatuzuobiao(353, 285, self.times)  # 7-2
            self.shuatuzuobiao(275, 200, self.times)  # 7-1
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        else:
            print('>>>高延迟模式刷图失败,放弃刷图<<<\r\n')
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    def shuatu8(self):
        # 进入冒险
        self.click(480, 505, pre_delay=2, post_delay=2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
        self.click(562, 253, )
        self.click(701, 83, pre_delay=4, post_delay=2)
        self.duanyazuobiao()
        if self.tag < 22:  # 暂时先按各11次来判定
            for _ in range(1):
                # 以7图为基向右移动3图
                self.click(925, 275, post_delay=3)
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/normal.jpg', at=(660, 72, 743, 94)):
                    break
                if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                    self.click(701, 83, pre_delay=0, post_delay=2)
                    break
            self.switch = 0
            self.d.drag(600, 270, 200, 270, 0.1)
            time.sleep(2)
            self.shuatuzuobiao(584, 260, self.times)  # 8-14
            self.shuatuzuobiao(715, 319, self.times)  # 8-13
            self.shuatuzuobiao(605, 398, self.times)  # 8-12
            self.shuatuzuobiao(478, 374, self.times)  # 8-11
            self.shuatuzuobiao(357, 405, self.times)  # 8-10
            self.shuatuzuobiao(263, 324, self.times)  # 8-9
            self.shuatuzuobiao(130, 352, self.times)  # 8-8
            self.d.drag(200, 270, 600, 270, 0.1)  # 拖拽到最左
            time.sleep(2)
            self.shuatuzuobiao(580, 401, self.times)  # 8-7
            self.shuatuzuobiao(546, 263, self.times)  # 8-6
            self.shuatuzuobiao(457, 334, self.times)  # 8-5
            self.shuatuzuobiao(388, 240, self.times)  # 8-4
            self.shuatuzuobiao(336, 314, self.times)  # 8-3
            self.shuatuzuobiao(230, 371, self.times)  # 8-2
            self.shuatuzuobiao(193, 255, self.times)  # 8-1
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        else:
            print('>>>高延迟模式刷图失败,放弃刷图<<<\r\n')
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    # 10图
    def shuatu10(self):
        # 进入冒险
        self.click(480, 505, pre_delay=2, post_delay=2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
        self.click(562, 253,)
        self.click(701, 83, pre_delay=4, post_delay=2)
        self.duanyazuobiao()
        if self.tag < 22:  # 暂时先按各11次来判定
            for _ in range(3):
                # 以7图为基向右移动3图
                self.click(925, 275, post_delay=3)
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/normal.jpg', at=(660, 72, 743, 94)):
                    break
                if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                    self.click(701, 83, pre_delay=0, post_delay=2)
                    break
            self.switch = 0
            self.d.drag(600, 270, 200, 270, 0.1)
            time.sleep(2)
            self.shuatuzuobiao(821, 299, self.times)  # 10-17
            self.shuatuzuobiao(703, 328, self.times)  # 10-16
            self.shuatuzuobiao(608, 391, self.times)  # 10-15
            self.shuatuzuobiao(485, 373, self.times)  # 10-14
            self.shuatuzuobiao(372, 281, self.times)  # 10-13
            self.shuatuzuobiao(320, 421, self.times)  # 10-12
            self.shuatuzuobiao(172, 378, self.times)  # 10-11
            self.shuatuzuobiao(251, 235, self.times)  # 10-10
            self.shuatuzuobiao(111, 274, self.times)  # 10-9
            self.d.drag(200, 270, 600, 270, 0.1)  # 拖拽到最左
            time.sleep(2)
            self.shuatuzuobiao(690, 362, self.times)  # 10-8
            self.shuatuzuobiao(594, 429, self.times)  # 10-7
            self.shuatuzuobiao(411, 408, self.times)  # 10-6
            self.shuatuzuobiao(518, 332, self.times)  # 10-5
            self.shuatuzuobiao(603, 238, self.times)  # 10-4
            self.shuatuzuobiao(430, 239, self.times)  # 10-3
            self.shuatuzuobiao(287, 206, self.times)  # 10-2
            self.shuatuzuobiao(146, 197, self.times)  # 10-1
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        else:
            print('>>>高延迟模式刷图失败,放弃刷图<<<\r\n')
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    # 11图
    def shuatu11(self):
        # 进入冒险
        self.click(480, 505, pre_delay=2, post_delay=2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
        self.click(562, 253, )
        self.click(701, 83, pre_delay=4, post_delay=2)
        self.duanyazuobiao()
        if self.tag < 22:  # 暂时先按各11次来判定
            for _ in range(4):
                # 以7图为基向右移动4图
                self.click(925, 275, post_delay=3)
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/normal.jpg', at=(660, 72, 743, 94)):
                    break
                if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                    self.click(701, 83, pre_delay=0, post_delay=2)
                    break
            self.switch = 0
            self.d.drag(600, 270, 200, 270, 0.1)    # 拖拽到最右
            time.sleep(2)
            self.shuatuzuobiao(663, 408, self.times)  # 11-17
            self.shuatuzuobiao(542, 338, self.times)  # 11-16
            self.shuatuzuobiao(468, 429, self.times)  # 11-15
            self.shuatuzuobiao(398, 312, self.times)  # 11-14
            self.shuatuzuobiao(302, 428, self.times)  # 11-13
            self.shuatuzuobiao(182, 362, self.times)  # 11-12
            self.shuatuzuobiao(253, 237, self.times)  # 11-11
            self.shuatuzuobiao(107, 247, self.times)  # 11-10
            self.d.drag(200, 270, 600, 270, 0.1)  # 拖拽到最左
            time.sleep(2)
            self.shuatuzuobiao(648, 316, self.times)  # 11-9
            self.shuatuzuobiao(594, 420, self.times)  # 11-8
            self.shuatuzuobiao(400, 432, self.times)  # 11-7
            self.shuatuzuobiao(497, 337, self.times)  # 11-6
            self.shuatuzuobiao(558, 240, self.times)  # 11-5
            self.shuatuzuobiao(424, 242, self.times)  # 11-4
            self.shuatuzuobiao(290, 285, self.times)  # 11-3
            self.shuatuzuobiao(244, 412, self.times)  # 11-2
            self.shuatuzuobiao(161, 325, self.times)  # 11-1
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        else:
            print('>>>高延迟模式刷图失败,放弃刷图<<<\r\n')
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    # 12图
    def shuatu12(self):
        # 进入冒险
        self.click(480, 505, pre_delay=2, post_delay=2)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
        self.click(562, 253, )
        self.click(701, 83, pre_delay=4, post_delay=2)
        self.duanyazuobiao()
        if self.tag < 22:  # 暂时先按各11次来判定
            for _ in range(5):
                # 以7图为基向右移动5图
                self.click(925, 275, post_delay=3)
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/normal.jpg', at=(660, 72, 743, 94)):
                    break
                if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                    self.click(701, 83, pre_delay=0, post_delay=2)
                    break
            self.switch = 0
            self.d.drag(600, 270, 200, 270, 0.1)  # 拖拽到最右
            time.sleep(2)
            self.shuatuzuobiao(760, 255, self.times)  # 12-17
            self.shuatuzuobiao(610, 245, self.times)  # 12-16
            self.shuatuzuobiao(450, 270, self.times)  # 12-15
            self.shuatuzuobiao(565, 415, self.times)  # 12-14
            self.shuatuzuobiao(400, 425, self.times)  # 12-13
            self.shuatuzuobiao(280, 365, self.times)  # 12-12
            self.shuatuzuobiao(265, 245, self.times)  # 12-11
            self.shuatuzuobiao(130, 265, self.times)  # 12-10
            self.d.drag(200, 270, 600, 270, 0.1)  # 拖拽到最左
            time.sleep(2)
            self.shuatuzuobiao(675, 380, self.times)  # 12-9
            self.shuatuzuobiao(550, 440, self.times)  # 12-8
            self.shuatuzuobiao(445, 365, self.times)  # 12-7
            self.shuatuzuobiao(575, 245, self.times)  # 12-6
            self.shuatuzuobiao(435, 250, self.times)  # 12-5
            self.shuatuzuobiao(310, 285, self.times)  # 12-4
            self.shuatuzuobiao(265, 395, self.times)  # 12-3
            self.shuatuzuobiao(155, 315, self.times)  # 12-2
            self.shuatuzuobiao(185, 210, self.times)  # 12-1
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        else:
            print('>>>高延迟模式刷图失败,放弃刷图<<<\r\n')
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    def shoushuazuobiao(self, x, y, jiaocheng=0, lockpic='img/normal.jpg', screencut=None):
        """
        不使用挑战券挑战，xy为该图坐标
        jiaocheng=0 只处理简单的下一步和解锁内容
        jiaocheng=1 要处理复杂的教程
        lockpic: 返回时锁定的图
        screencut: 返回时锁定的图的搜索范围
        :return:
        """
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, lockpic, at=screencut):
                break
            self.d.click(1, 138)
            time.sleep(1)
        self.lockimg('img/tiaozhan.jpg', elseclick=[(x, y)], elsedelay=2)
        self.d.click(840, 454)
        time.sleep(0.7)

        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.imgs_where(screen_shot_, ['img/kuaijin.jpg', 'img/kuaijin_1.jpg']) != {}:
                break
            self.d.click(840, 454)  # 点到进入战斗画面
            time.sleep(0.7)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if self.click_img(screen_shot_, 'img/kuaijin.jpg', at=(891, 478, 936, 517)):
                time.sleep(1)
            if self.click_img(screen_shot_, 'img/auto.jpg', at=(891, 410, 936, 438)):
                time.sleep(1)
            if UIMatcher.img_where(screen_shot_, 'img/wanjiadengji.jpg', at=(233, 168, 340, 194)):
                break
            self.d.click(1, 138)
            time.sleep(0.5)
        if jiaocheng == 1:  # 有复杂的教程，交给教程函数处理
            self.chulijiaocheng()
        else:  # 无复杂的教程，自己处理掉“下一步”
            for _ in range(7):
                self.d.click(832, 506)
                time.sleep(0.2)
            while True:
                time.sleep(2)
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, lockpic, at=screencut):
                    break
                elif UIMatcher.img_where(screen_shot_, 'img/xiayibu.jpg'):
                    self.d.click(832, 506)
                else:
                    self.d.click(1, 100)
            while True:  # 两次确认回到挑战界面
                self.d.click(1, 100)
                time.sleep(0.5)
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, lockpic, at=screencut):
                    break
