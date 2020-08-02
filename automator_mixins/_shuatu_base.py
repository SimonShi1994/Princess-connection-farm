import time

from automator_mixins._tools import ToolsMixin
from core.constant import MAOXIAN_BTN, NORMAL_ID, MAIN_BTN, HARD_ID
from core.cv import UIMatcher
from core.log_handler import pcr_log


class ShuatuBaseMixin(ToolsMixin):
    """
    刷图基础插片
    包含刷图基本操作和基本变量存储
    """

    def __init__(self):
        super().__init__()
        self.switch = 0
        self.times = 3  # 总刷图次数

    def sw_init(self):
        self.switch = 0

    def saodangzuobiao(self, x, y, times, auto_tili=False):
        pass

    def shuatuzuobiao(self, x, y, times):  # 刷图函数，xy为该图的坐标，times为刷图次数
        if self.switch == 0:
            tmp_cout = 0
            self.click(x, y, pre_delay=2, post_delay=2)
        else:
            pcr_log(self.account).write_log(level='info', message='>>>无扫荡券或者无体力，结束 全部 刷图任务！<<<\r\n')
            return
        if self.switch == 0:
            while True:  # 锁定加号
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/jiahao.bmp'):
                    # screen_shot = a.d.screenshot(format="opencv")
                    for i in range(times - 1):  # 基础1次
                        # 扫荡券不必使用opencv来识别，降低效率
                        self.click(876, 334)
                    self.click(758, 330, pre_delay=1, post_delay=1)  # 使用扫荡券的位置 也可以用OpenCV但是效率不够而且不能自由设定次数
                    screen_shot = self.getscreen()
                    if UIMatcher.img_where(screen_shot, 'img/ok.bmp'):
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    else:
                        time.sleep(0.5)
                        self.click(588, 370)
                    # screen_shot = a.d.screenshot(format="opencv")
                    # a.guochang(screen_shot,['img/shiyongsanzhang.jpg'])
                    screen_shot_ = self.getscreen()
                    if UIMatcher.img_where(screen_shot_, 'img/tilibuzu.jpg'):
                        pcr_log(self.account).write_log(level='info', message='>>>无扫荡券或者无体力！结束此次刷图任务！<<<\r\n')
                        self.switch = 1
                        self.click(677, 458)  # 取消
                        break
                    screen_shot = self.getscreen()
                    if UIMatcher.img_where(screen_shot, 'img/tiaoguo.jpg'):
                        self.guochang(screen_shot, ['img/tiaoguo.jpg'], suiji=0)
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    else:
                        time.sleep(1)
                        self.click(475, 481)  # 手动点击跳过
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    break
                else:
                    if tmp_cout < 3:
                        # 计时3次就失败
                        self.click(x, y)
                        time.sleep(0.5)
                        tmp_cout = tmp_cout + 1
                    else:
                        pcr_log(self.account).write_log(level='info', message='>>>无扫荡券或者无体力！结束此次刷图任务！<<<\r\n')
                        self.switch = 1
                        self.click(677, 458)  # 取消
                        break
        else:
            pcr_log(self.account).write_log(level='info', message='>>>无扫荡券或者无体力！结束刷图任务！<<<\r\n')
        while True:
            self.click(1, 1)
            time.sleep(0.3)
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/normal.jpg', at=(660, 72, 743, 94)):
                break
            if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                break

    def enter_zhuxian(self):
        # 进入主线
        self.lock_home()
        self.click(*MAIN_BTN["maoxian"])
        # 进入地图（此处写500，90是为了防止误触到关卡）
        self.lock_img(MAIN_BTN["dxc"], ifclick=MAIN_BTN["zhuxian"], elseclick=MAIN_BTN["maoxian"], ifbefore=2)
        # 判断是否进入地图
        self.lock_img(MAOXIAN_BTN["ditu"], ifclick=MAOXIAN_BTN["normal_on"], elseclick=MAIN_BTN["zhuxian"], ifbefore=2)

    def enter_hard(self, max_retry=3):
        self.enter_zhuxian()
        for retry in range(max_retry):
            time.sleep(1)
            state = self.check_maoxian_screen()
            if state == -1:
                raise Exception("进入冒险失败！")
            elif state == 0:
                self.enter_zhuxian()
            elif state == 1:
                self.click(*MAOXIAN_BTN["hard_on"])
            elif state == 2:
                return
        raise Exception("进入困难图超过最大尝试次数！")

    # 左移动
    def goLeft(self):
        self.click(35, 275, post_delay=3)

    # 右移动

    def goRight(self):
        self.click(925, 275, post_delay=3)

    def check_maoxian_screen(self):
        """
        获得冒险界面屏幕状态
        :return:
        -1: 未知状态
        0： 找到了“冒险”，但不清楚是Normal还是Hard
        1:  Normal图
        2： Hard图
        """
        sc = self.getscreen()
        pn1 = self.img_prob(MAOXIAN_BTN["normal_on"], screen=sc)
        ph1 = self.img_prob(MAOXIAN_BTN["hard_on"], screen=sc)
        if pn1 > 0.9:
            return 1
        elif ph1 > 0.9:
            return 2
        elif self.is_exists(MAOXIAN_BTN["ditu"], screen=sc):
            return 0
        else:
            return -1

    def hard_shuatuzuobiao(self, x, y, times):  # 刷图函数，xy为该图的坐标，times为刷图次数,防止占用shuatuzuobiao用的
        if self.switch == 0:
            tmp_cout = 0
            self.click(x, y)
            time.sleep(0.5)
        else:
            pcr_log(self.account).write_log(level='info', message='>>>无扫荡券,无体力,无次数！结束 全部 刷图任务！<<<\r\n')
            return
        if self.switch == 0:
            while True:  # 锁定加号
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/jiahao.bmp'):
                    # screen_shot = a.d.screenshot(format="opencv")
                    for i in range(times - 1):  # 基础1次
                        # 扫荡券不必使用opencv来识别，降低效率
                        self.click(876, 334)
                    time.sleep(0.3)
                    self.click(758, 330)  # 使用扫荡券的位置 也可以用OpenCV但是效率不够而且不能自由设定次数
                    time.sleep(0.3)
                    screen_shot = self.getscreen()
                    if UIMatcher.img_where(screen_shot, 'img/ok.bmp'):
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    else:
                        time.sleep(0.5)
                        self.click(588, 370)
                    # screen_shot = a.d.screenshot(format="opencv")
                    # a.guochang(screen_shot,['img/shiyongsanzhang.jpg'])
                    screen_shot_ = self.getscreen()
                    if UIMatcher.img_where(screen_shot_, 'img/tilibuzu.jpg'):
                        pcr_log(self.account).write_log(level='info', message='>>>无扫荡券,无体力,无次数！结束此次刷图任务！<<<\r\n')
                        self.switch = 1
                        self.click(677, 458)  # 取消
                        break
                    screen_shot = self.getscreen()
                    if UIMatcher.img_where(screen_shot, 'img/tiaoguo.jpg'):
                        self.guochang(screen_shot, ['img/tiaoguo.jpg'], suiji=0)
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    else:
                        time.sleep(1)
                        self.click(475, 481)  # 手动点击跳过
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    break
                else:
                    if tmp_cout < 3:
                        # 计时3次就失败
                        self.click(x, y)
                        time.sleep(0.5)
                        tmp_cout = tmp_cout + 1
                    else:
                        pcr_log(self.account).write_log(level='info', message='>>>无扫荡券,无体力,无次数！结束此次刷图任务！<<<\r\n')
                        self.switch = 1
                        self.click(677, 458)  # 取消
                        break
        else:
            pcr_log(self.account).write_log(level='info', message='>>>无扫荡券,无体力,无次数！结束刷图任务！<<<\r\n')
        while True:
            self.click(1, 1)
            time.sleep(0.3)
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/normal.jpg', at=(660, 72, 743, 94)):
                break
            if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                break

    # 继续执行函数
    def continueDo9(self, x, y):
        self.switch = 0
        self.shuatuzuobiao(x, y, self.times)  # 3-3

    # 识别7村断崖
    def duanyazuobiao(self):
        """
        识别断崖的坐标
        """
        from core.constant import MAX_MAP
        tag = 0
        time.sleep(2)
        while True:
            if tag > MAX_MAP:  # 超过MAX_MAP次点击则不刷图
                for _ in range(6):
                    self.click(925, 275)
                    time.sleep(1.5)  # 这是高延迟识别时间,模拟器卡顿请加时
                break
            else:
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/duanyazuobiao.jpg'):
                    pcr_log(self.account).write_log(level='info', message='>>>成功识别标记,开始刷图.<<<\r\n')
                    break
                self.click(27, 272)
                tag += 1
                time.sleep(1.5)

    def check_normal_id(self, screen=None):
        """
        识别normal图的图号
        :param: screen:设置为None时，第一次重新截图
        :return:
        -1：识别失败
        1~ ：图号
        """
        self.Drag_Left()  # 保证截图区域一致
        id = self.check_dict_id(MAOXIAN_BTN["title_box"], NORMAL_ID, screen)
        if id is None:
            return -1
        else:
            return id

    def check_hard_id(self, screen=None):
        """
        识别hard图的图号
        :param: screen:设置为None时，第一次重新截图
        :return:
        -1：识别失败
        1~ ：图号
        """
        id = self.check_dict_id(MAOXIAN_BTN["title_box"], HARD_ID, screen)
        if id is None:
            return -1
        else:
            return id

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
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, lockpic, at=screencut):
                break
            self.click(1, 138)
            time.sleep(1)
        self.lock_img('img/tiaozhan.jpg', elseclick=[(x, y)], elsedelay=2)
        self.click(840, 454)
        time.sleep(0.7)

        while True:
            screen_shot_ = self.getscreen()
            if UIMatcher.imgs_where(screen_shot_, ['img/kuaijin.jpg', 'img/kuaijin_1.jpg']) != {}:
                break
            self.click(840, 454)  # 点到进入战斗画面
            time.sleep(0.7)
        while True:
            screen_shot_ = self.getscreen()
            if self.click_img(screen_shot_, 'img/kuaijin.jpg', at=(891, 478, 936, 517)):
                time.sleep(1)
            if self.click_img(screen_shot_, 'img/auto.jpg', at=(891, 410, 936, 438)):
                time.sleep(1)
            if UIMatcher.img_where(screen_shot_, 'img/wanjiadengji.jpg', at=(233, 168, 340, 194)):
                break
            self.click(1, 138)
            time.sleep(0.5)
        if jiaocheng == 1:  # 有复杂的教程，交给教程函数处理
            self.chulijiaocheng()
        else:  # 无复杂的教程，自己处理掉“下一步”
            for _ in range(7):
                self.click(832, 506)
                time.sleep(0.2)
            while True:
                time.sleep(2)
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, lockpic, at=screencut):
                    break
                elif UIMatcher.img_where(screen_shot_, 'img/xiayibu.jpg'):
                    self.click(832, 506)
                else:
                    self.click(1, 100)
            while True:  # 两次确认回到挑战界面
                self.click(1, 100)
                time.sleep(0.5)
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, lockpic, at=screencut):
                    break

    def qianghua(self):
        # 此处逻辑极为复杂，代码不好理解
        time.sleep(3)
        self.click(215, 513)  # 角色
        time.sleep(3)
        self.click(177, 145)  # First
        time.sleep(3)
        for i in range(5):
            print("Now: ", i)
            while True:
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/keyihuode.jpg'):
                    # 存在可以获得，则一直获得到没有可以获得，或者没有三星
                    self.click(374, 435)
                    time.sleep(1)
                    screen_shot_ = self.getscreen()
                    if UIMatcher.img_where(screen_shot_, 'img/tuijianguanqia.jpg', at=(258, 87, 354, 107)):
                        # 已经强化到最大等级，开始获取装备
                        if not UIMatcher.img_where(screen_shot_, 'img/sanxingtongguan.jpg'):
                            # 装备不可刷，换人
                            self.click(501, 468)  # important
                            time.sleep(1)
                            break
                        while UIMatcher.img_where(screen_shot_, 'img/sanxingtongguan.jpg'):
                            # 一直刷到没有有推荐关卡但没有三星或者返回到角色列表
                            self.guochang(screen_shot_, ['img/sanxingtongguan.jpg'], suiji=0)
                            time.sleep(1)
                            # 使用扫荡券的数量：
                            for _ in range(4 - 1):
                                self.click(877, 333)
                                time.sleep(0.3)
                            self.click(752, 333)
                            time.sleep(0.7)
                            self.click(589, 371)
                            while True:
                                screen_shot_ = self.getscreen()
                                active_paths = UIMatcher.imgs_where(screen_shot_,
                                                                    ['img/tuijianguanqia.jpg', 'img/zidongqianghua.jpg',
                                                                     'img/tiaoguo.jpg'])
                                if 'img/tiaoguo.jpg' in active_paths:
                                    x, y = active_paths['img/tiaoguo.jpg']
                                    self.click(x, y)
                                if 'img/tuijianguanqia.jpg' in active_paths:
                                    flag = 'img/tuijianguanqia.jpg'
                                    break
                                elif 'img/zidongqianghua.jpg' in active_paths:
                                    flag = 'img/zidongqianghua.jpg'
                                    break
                                else:
                                    self.click(1, 100)
                                    time.sleep(1.3)
                            if flag == 'img/zidongqianghua.jpg':
                                # 装备获取完成，跳出小循环，重进大循环
                                self.click(371, 437)
                                time.sleep(0.7)
                                break
                            else:
                                # 装备未获取完毕，继续尝试获取
                                continue
                        self.click(501, 468)  # important
                        time.sleep(2)
                        continue
                    else:
                        # 未强化到最大等级，强化到最大登记
                        self.click(501, 468)  # important
                        time.sleep(3)
                        continue
                else:
                    # 没有可以获得
                    if UIMatcher.img_where(screen_shot_, 'img/ranktisheng.jpg', at=(206, 325, 292, 346)):
                        self.click(250, 338)
                        time.sleep(2)
                        screen_shot_ = self.getscreen()
                        active_list = UIMatcher.imgs_where(screen_shot_, ['img/queren.jpg', 'img/ok.bmp'])
                        if 'img/queren.jpg' in active_list:
                            x, y = active_list['img/queren.jpg']
                            self.click(x, y)
                        if 'img/ok.bmp' in active_list:
                            x, y = active_list['img/ok.bmp']
                            self.click(x, y)
                        time.sleep(8)
                        self.click(481, 369)
                        time.sleep(1)
                        continue
                    else:
                        self.click(371, 437)
                        time.sleep(0.7)
                        self.click(501, 468)  # important
                        time.sleep(2)
                        break
            self.click(933, 267)  # 下一位
            time.sleep(2)

        self.lock_home()
        self.lock_img('img/zhuxianguanqia.jpg', elseclick=[(480, 513)], elsedelay=3)
        self.click(562, 253)
        time.sleep(3)
        self.lock_img('img/normal.jpg', elseclick=[(704, 84)], elsedelay=0.5, alldelay=1, at=(660, 72, 743, 94))
        self.click(923, 272)
        time.sleep(3)

    def enter_normal(self, max_retry=3):
        """
        进入normal图
        """
        self.enter_zhuxian()
        for retry in range(max_retry):
            time.sleep(1)
            state = self.check_maoxian_screen()
            if state == -1:
                raise Exception("进入冒险失败！")
            elif state == 0:
                self.enter_zhuxian()
            elif state == 2:
                self.click(*MAOXIAN_BTN["normal_on"])
            elif state == 1:
                return

        raise Exception("进入普通图超过最大尝试次数！")

    def select_normal_id(self, id):
        """
        走到normal的几图
        要求场景：已经在normal内
        :param id: 图号
        """
        while True:
            sc = self.getscreen()
            cur_id = self.check_normal_id(sc)
            if cur_id == -1:
                self.wait_for_loading(sc)
                if self.is_exists(MAOXIAN_BTN["ditu"]):
                    if self.check_maoxian_screen() == 2:
                        self.click(*MAOXIAN_BTN["normal_on"], post_delay=1)
                    # 重试一次
                    continue
                else:
                    raise Exception("Normal 图号识别失败！")
            if cur_id == id:
                return
            elif cur_id < id:
                for i in range(id - cur_id):
                    self.goRight()
            elif cur_id > id:
                for i in range(cur_id - id):
                    self.goLeft()

    def select_hard_id(self, id):
        """
        走到hard的几图
        要求场景：已经在hard内
        :param id: 图号
        """
        while True:
            sc = self.getscreen()
            cur_id = self.check_hard_id(sc)
            if cur_id == -1:
                self.wait_for_loading(sc)
                if self.is_exists(MAOXIAN_BTN["ditu"]):
                    # 重试一次
                    if self.check_maoxian_screen() == 1:
                        self.click(*MAOXIAN_BTN["hard_on"], post_delay=1)
                    continue
                else:
                    raise Exception("Hard 图号识别失败！")
            if cur_id == id:
                return
            elif cur_id < id:
                for i in range(id - cur_id):
                    self.goRight()
            elif cur_id > id:
                for i in range(cur_id - id):
                    self.goLeft()

    def Drag_Right(self):
        self.d.drag(600, 270, 200, 270, 0.1)  # 拖拽到最右
        time.sleep(2)

    def Drag_Left(self):
        self.d.drag(200, 270, 600, 270, 0.1)  # 拖拽到最左
        time.sleep(2)
