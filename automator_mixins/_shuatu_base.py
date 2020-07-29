import time

from automator_mixins._tools import ToolsMixin
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
                        self.d.click(876, 334)
                    self.click(758, 330, pre_delay=1, post_delay=1)  # 使用扫荡券的位置 也可以用OpenCV但是效率不够而且不能自由设定次数
                    screen_shot = self.getscreen()
                    if UIMatcher.img_where(screen_shot, 'img/ok.bmp'):
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    else:
                        time.sleep(0.5)
                        self.d.click(588, 370)
                    # screen_shot = a.d.screenshot(format="opencv")
                    # a.guochang(screen_shot,['img/shiyongsanzhang.jpg'])
                    screen_shot_ = self.getscreen()
                    if UIMatcher.img_where(screen_shot_, 'img/tilibuzu.jpg'):
                        pcr_log(self.account).write_log(level='info', message='>>>无扫荡券或者无体力！结束此次刷图任务！<<<\r\n')
                        self.switch = 1
                        self.d.click(677, 458)  # 取消
                        break
                    screen_shot = self.getscreen()
                    if UIMatcher.img_where(screen_shot, 'img/tiaoguo.jpg'):
                        self.guochang(screen_shot, ['img/tiaoguo.jpg'], suiji=0)
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    else:
                        time.sleep(1)
                        self.d.click(475, 481)  # 手动点击跳过
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    break
                else:
                    if tmp_cout < 3:
                        # 计时3次就失败
                        self.d.click(x, y)
                        time.sleep(0.5)
                        tmp_cout = tmp_cout + 1
                    else:
                        pcr_log(self.account).write_log(level='info', message='>>>无扫荡券或者无体力！结束此次刷图任务！<<<\r\n')
                        self.switch = 1
                        self.d.click(677, 458)  # 取消
                        break
        else:
            pcr_log(self.account).write_log(level='info', message='>>>无扫荡券或者无体力！结束刷图任务！<<<\r\n')
        while True:
            self.d.click(1, 1)
            time.sleep(0.3)
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/normal.jpg', at=(660, 72, 743, 94)):
                break
            if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                break

        # 进入hard图

    def enterHardMap(self):
        # 进入冒险
        time.sleep(2)
        self.d.click(480, 505)
        time.sleep(2)
        while True:
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
        # 点击进入主线关卡
        self.d.click(562, 253)
        time.sleep(2)
        while True:
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/normal.jpg'):
                self.d.click(880, 80)
            if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                break

    # 左移动

    def goLeft(self):
        self.click(35, 275, post_delay=3)

    # 右移动

    def goRight(self):
        self.click(925, 275, post_delay=3)

    def goHardMap(self):
        # 进入冒险
        from core.constant import MAX_MAP
        time.sleep(2)
        self.d.click(480, 505)
        time.sleep(2)
        while True:
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
        # 点击进入主线关卡
        self.click(562, 253)
        self.click(828, 85, pre_delay=5, post_delay=2)
        for _ in range(MAX_MAP):  # 设置大于当前进图数,让脚本能回归到1-1即可.
            # H图左移到1-1图
            self.click(27, 272, pre_delay=3)
        while True:
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/normal.jpg'):
                self.click(828, 85)
            else:
                UIMatcher.img_where(screen_shot_, 'img/hard.jpg')
                break

    def hard_shuatuzuobiao(self, x, y, times):  # 刷图函数，xy为该图的坐标，times为刷图次数,防止占用shuatuzuobiao用的
        if self.switch == 0:
            tmp_cout = 0
            self.d.click(x, y)
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
                        self.d.click(876, 334)
                    time.sleep(0.3)
                    self.d.click(758, 330)  # 使用扫荡券的位置 也可以用OpenCV但是效率不够而且不能自由设定次数
                    time.sleep(0.3)
                    screen_shot = self.getscreen()
                    if UIMatcher.img_where(screen_shot, 'img/ok.bmp'):
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    else:
                        time.sleep(0.5)
                        self.d.click(588, 370)
                    # screen_shot = a.d.screenshot(format="opencv")
                    # a.guochang(screen_shot,['img/shiyongsanzhang.jpg'])
                    screen_shot_ = self.getscreen()
                    if UIMatcher.img_where(screen_shot_, 'img/tilibuzu.jpg'):
                        pcr_log(self.account).write_log(level='info', message='>>>无扫荡券,无体力,无次数！结束此次刷图任务！<<<\r\n')
                        self.switch = 1
                        self.d.click(677, 458)  # 取消
                        break
                    screen_shot = self.getscreen()
                    if UIMatcher.img_where(screen_shot, 'img/tiaoguo.jpg'):
                        self.guochang(screen_shot, ['img/tiaoguo.jpg'], suiji=0)
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    else:
                        time.sleep(1)
                        self.d.click(475, 481)  # 手动点击跳过
                        self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    break
                else:
                    if tmp_cout < 3:
                        # 计时3次就失败
                        self.d.click(x, y)
                        time.sleep(0.5)
                        tmp_cout = tmp_cout + 1
                    else:
                        pcr_log(self.account).write_log(level='info', message='>>>无扫荡券,无体力,无次数！结束此次刷图任务！<<<\r\n')
                        self.switch = 1
                        self.d.click(677, 458)  # 取消
                        break
        else:
            pcr_log(self.account).write_log(level='info', message='>>>无扫荡券,无体力,无次数！结束刷图任务！<<<\r\n')
        while True:
            self.d.click(1, 1)
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
            self.d.click(1, 138)
            time.sleep(1)
        self.lockimg('img/tiaozhan.jpg', elseclick=[(x, y)], elsedelay=2)
        self.d.click(840, 454)
        time.sleep(0.7)

        while True:
            screen_shot_ = self.getscreen()
            if UIMatcher.imgs_where(screen_shot_, ['img/kuaijin.jpg', 'img/kuaijin_1.jpg']) != {}:
                break
            self.d.click(840, 454)  # 点到进入战斗画面
            time.sleep(0.7)
        while True:
            screen_shot_ = self.getscreen()
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
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, lockpic, at=screencut):
                    break
                elif UIMatcher.img_where(screen_shot_, 'img/xiayibu.jpg'):
                    self.d.click(832, 506)
                else:
                    self.d.click(1, 100)
            while True:  # 两次确认回到挑战界面
                self.d.click(1, 100)
                time.sleep(0.5)
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, lockpic, at=screencut):
                    break

    def qianghua(self):
        # 此处逻辑极为复杂，代码不好理解
        time.sleep(3)
        self.d.click(215, 513)  # 角色
        time.sleep(3)
        self.d.click(177, 145)  # First
        time.sleep(3)
        for i in range(5):
            print("Now: ", i)
            while True:
                screen_shot_ = self.d.screenshot(format='opencv')
                if UIMatcher.img_where(screen_shot_, 'img/keyihuode.jpg'):
                    # 存在可以获得，则一直获得到没有可以获得，或者没有三星
                    self.d.click(374, 435)
                    time.sleep(1)
                    screen_shot_ = self.d.screenshot(format='opencv')
                    if UIMatcher.img_where(screen_shot_, 'img/tuijianguanqia.jpg', at=(258, 87, 354, 107)):
                        # 已经强化到最大等级，开始获取装备
                        if not UIMatcher.img_where(screen_shot_, 'img/sanxingtongguan.jpg'):
                            # 装备不可刷，换人
                            self.d.click(501, 468)  # important
                            time.sleep(1)
                            break
                        while UIMatcher.img_where(screen_shot_, 'img/sanxingtongguan.jpg'):
                            # 一直刷到没有有推荐关卡但没有三星或者返回到角色列表
                            self.guochang(screen_shot_, ['img/sanxingtongguan.jpg'], suiji=0)
                            time.sleep(1)
                            # 使用扫荡券的数量：
                            for _ in range(4 - 1):
                                self.d.click(877, 333)
                                time.sleep(0.3)
                            self.d.click(752, 333)
                            time.sleep(0.7)
                            self.d.click(589, 371)
                            while True:
                                screen_shot_ = self.d.screenshot(format='opencv')
                                active_paths = UIMatcher.imgs_where(screen_shot_,
                                                                    ['img/tuijianguanqia.jpg', 'img/zidongqianghua.jpg',
                                                                     'img/tiaoguo.jpg'])
                                if 'img/tiaoguo.jpg' in active_paths:
                                    x, y = active_paths['img/tiaoguo.jpg']
                                    self.d.click(x, y)
                                if 'img/tuijianguanqia.jpg' in active_paths:
                                    flag = 'img/tuijianguanqia.jpg'
                                    break
                                elif 'img/zidongqianghua.jpg' in active_paths:
                                    flag = 'img/zidongqianghua.jpg'
                                    break
                                else:
                                    self.d.click(1, 100)
                                    time.sleep(1.3)
                            if flag == 'img/zidongqianghua.jpg':
                                # 装备获取完成，跳出小循环，重进大循环
                                self.d.click(371, 437)
                                time.sleep(0.7)
                                break
                            else:
                                # 装备未获取完毕，继续尝试获取
                                continue
                        self.d.click(501, 468)  # important
                        time.sleep(2)
                        continue
                    else:
                        # 未强化到最大等级，强化到最大登记
                        self.d.click(501, 468)  # important
                        time.sleep(3)
                        continue
                else:
                    # 没有可以获得
                    if UIMatcher.img_where(screen_shot_, 'img/ranktisheng.jpg', at=(206, 325, 292, 346)):
                        self.d.click(250, 338)
                        time.sleep(2)
                        screen_shot_ = self.d.screenshot(format='opencv')
                        active_list = UIMatcher.imgs_where(screen_shot_, ['img/queren.jpg', 'img/ok.bmp'])
                        if 'img/queren.jpg' in active_list:
                            x, y = active_list['img/queren.jpg']
                            self.d.click(x, y)
                        if 'img/ok.bmp' in active_list:
                            x, y = active_list['img/ok.bmp']
                            self.d.click(x, y)
                        time.sleep(8)
                        self.d.click(481, 369)
                        time.sleep(1)
                        continue
                    else:
                        self.d.click(371, 437)
                        time.sleep(0.7)
                        self.d.click(501, 468)  # important
                        time.sleep(2)
                        break
            self.d.click(933, 267)  # 下一位
            time.sleep(2)

        self.lock_home()
        self.lockimg('img/zhuxianguanqia.jpg', elseclick=[(480, 513)], elsedelay=3)
        self.d.click(562, 253)
        time.sleep(3)
        self.lockimg('img/normal.jpg', elseclick=[(704, 84)], elsedelay=0.5, alldelay=1, at=(660, 72, 743, 94))
        self.d.click(923, 272)
        time.sleep(3)

    def enter_normal(self, to_map: int = 7):
        """
        进入normal图，并且走到to_map图。
        :param to_map: 转到的地图位置
        :return: 是否成功进入。如果为False，则表示过于卡，停止刷图

        """
        self.click(480, 505, pre_delay=2, post_delay=2)
        while True:
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
        self.click(562, 253)
        # 此处很容易卡
        self.lockimg("img/normal.jpg", ifclick=(701, 83), elseclick=(701, 83), alldelay=2, ifbefore=3)
        self.duanyazuobiao()
        for _ in range(to_map - 7):
            # 以7图为基向右移动5图
            self.goRight()

    def Drag_Right(self):
        self.d.drag(600, 270, 200, 270, 0.1)  # 拖拽到最右
        time.sleep(2)

    def Drag_Left(self):
        self.d.drag(200, 270, 600, 270, 0.1)  # 拖拽到最左
        time.sleep(2)
