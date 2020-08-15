import time

from automator_mixins._fight_base import FightBaseMixin
from core.MoveRecord import movevar
from core.constant import MAOXIAN_BTN, MAIN_BTN, PCRelement, FIGHT_BTN, DXC_ELEMENT, SHOP_BTN, \
    ZHUXIAN_ID
from core.cv import UIMatcher
from core.log_handler import pcr_log


class ShuatuBaseMixin(FightBaseMixin):
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

    def zhuxian_kkr(self):
        """
        处理跳脸
        :return:
        """
        time.sleep(2)  # 等妈出现
        if self.is_exists(DXC_ELEMENT["dxc_kkr"]):
            self.chulijiaocheng(turnback=None)
            self.enter_zhuxian()
        self.lock_img(MAOXIAN_BTN["ditu"], elseclick=(80, 16), retry=5)  # 避免奇怪对话框

    def zhandouzuobiao(self, x, y, times, drag=None, use_saodang="auto", buy_tili=0, buy_cishu=0, xianding=False,
                       bianzu=0, duiwu=0, auto=1, speed=1, fastmode=True, fail_retry=False, var={}):
        """
        战斗坐标，新刷图函数（手刷+扫荡结合）
        内置剧情跳过、奇怪对话框跳过功能
        :param x: 点击图的x坐标
        :param y: 点击图的y坐标
        :param times: 刷图/手刷次数
        :param drag: 是否进行拖动校准
            设置为None时，点击坐标前不另外拖动给。
            "left"：进行左移动校准
            "right"：进行右移动校准
        :param use_saodang: 是否使用扫荡券
            True: 使用扫荡券，扫荡不成功则跳过
            False: 手打
            "auto“ (默认) 如果扫荡失败，则手打
        :param buy_tili: 是否自动购买体力。0不买，n表示最多买n次体力
        :param buy_cishu: 是否自动购买挑战次数（困难副本），0不买，1表示买1次。
        :param xianding: 是否买空限定商店
        :param auto: 是否开启自动
        :param speed: 是否开启加速
        :param bianzu: 使用编组号,为0时不切换，为-1时使用前五个角色
        :param duiwu: 使用队伍号，为0时不切换，为-1时使用前五个角色
        :param fastmode: 快速手刷模式：不退出重进而是通过“使用同一队伍再次挑战”来加速流程
        :param fail_retry: 失败是否重试。设置为True时手刷关卡，即使打败了也会重新再打。
                    重打的次数仍然算进总次数中。
        :return:
            -1: 出现未知的错误（场景判断失败）
            -2: 无法扫荡
            -3: 无法点进关卡
            >=0 整数：成功战胜的次数（非扫荡时）
            times：扫荡成功至少一次（扫荡时）
        """
        mv = movevar(var)
        var.setdefault("cur_tili", 0)  # 已经购买体力的次数
        var.setdefault("cur_times", 0)  # 已经战斗的次数
        var.setdefault("cur_win", 0)  # 已经胜利的次数

        def clear():
            del var["cur_tili"]
            del var["cur_times"]
            del var["cur_win"]

        def tili():
            if self.is_exists(MAOXIAN_BTN["no_tili"]):
                if var["cur_tili"] < buy_tili:
                    var["cur_tili"] += 1
                    self.log.write_log("info", f"体力不足，购买体力：{var['cur_tili']}/{buy_tili}！")
                    self.click_btn(MAOXIAN_BTN["buytili_ok"])
                    self.click_btn(MAOXIAN_BTN["buytili_ok"], wait_self_before=True)
                    click_ok = self.click_btn(MAOXIAN_BTN["buytili_ok2"], is_raise=False, wait_self_before=True)
                    if not click_ok:
                        self.log.write_log("warning", "购买体力可能失败。")
                    mv.save()
                    return click_ok
                else:
                    self.click_btn(MAOXIAN_BTN["buytili_quxiao"])
                    return False
            else:
                return True

        def cishu():
            if buy_cishu:
                if self.is_exists(MAOXIAN_BTN["no_cishu"]):
                    self.click_btn(MAOXIAN_BTN["buytili_ok"])
                    self.click_btn(MAOXIAN_BTN["buytili_ok"], wait_self_before=True)
                    click_ok = self.click_btn(MAOXIAN_BTN["buytili_ok2"], is_raise=False, wait_self_before=True)
                    if not click_ok:
                        self.log.write_log("warning", "购买次数可能失败。")
                    return click_ok
                else:
                    return False
            return True

        def buy(entered=False):
            # entered: 是否已经进入了商店，设置为True，则跳过“限定”的检测
            if not xianding:
                return False
            time.sleep(1.5)  # 等出现
            if entered or self.is_exists(MAOXIAN_BTN["xianding"]):
                if not entered:
                    self.click_btn(MAOXIAN_BTN["xianding"])
                self.wait_for_loading(delay=2)
                self.click(388, 148, post_delay=0.8)
                self.click(558, 149, post_delay=0.8)
                self.click(729, 149, post_delay=0.8)
                self.click(900, 148, post_delay=0.8)
                self.d.drag(613, 392, 613, 140, duration=0.1)
                self.click(388, 176, post_delay=0.8)
                self.click(559, 175, post_delay=0.8)
                self.click(729, 177, post_delay=0.8)
                self.click(899, 176, post_delay=0.8)
                # 点击购买
                self.click(794, 438)
                # 购买确认
                self.click_btn(SHOP_BTN["xianding_ok"], wait_self_before=True)
                for _ in range(5):
                    self.click(24, 84)
                # 立即关闭
                self.click_btn(SHOP_BTN["lijiguanbi"], until_appear=SHOP_BTN["querenchongzhi"])
                # 确认重制
                self.click_btn(SHOP_BTN["querenchongzhi"])
                # 返回
                for _ in range(5):
                    self.click(24, 84)
                self.click_btn(SHOP_BTN["fanhui"])
                self.wait_for_loading(delay=2)
            return True

        def shoushua(times):
            win_cnt = 0
            if not self.is_exists(FIGHT_BTN["tiaozhan2"], method="sq"):  # 不能挑战
                return 1
            self.click_btn(FIGHT_BTN["tiaozhan2"], method="sq")
            if not cishu():
                return 1
            # 换队
            if bianzu == -1 and duiwu == -1:
                self.set_fight_team_order()
            elif bianzu != 0 and duiwu != 0:
                self.set_fight_team(bianzu, duiwu)
            self.click_btn(FIGHT_BTN["zhandoukaishi"])
            while True:
                # 刷满times次
                self.wait_for_loading(delay=2)
                self.set_fight_auto(auto, screen=self.last_screen)
                self.set_fight_speed(speed, max_level=1, screen=self.last_screen)
                mode = 0
                while mode == 0:
                    # 等待战斗结束
                    mode = self.get_fight_state(max_retry=15, delay=3, check_hat=False, check_xd=True, go_xd=xianding)
                    time.sleep(3)
                if mode == -1:
                    raise Exception("战斗场景识别失败")
                elif mode == 1:
                    # 点击下一步：
                    var["cur_win"] += 1
                    var["cur_times"] += 1
                    win_cnt += 1
                    mv.save()
                    if win_cnt < times:
                        # 点击”再次挑战“
                        if not self.click_btn(MAOXIAN_BTN["zaicitiaozhan"], is_raise=False):
                            break
                        cishu()
                        if tili():
                            self.click_btn(MAOXIAN_BTN["chongshi_ok"])
                            # 点击了重试，继续刷！
                            continue
                        else:
                            # 不刷了，退出
                            pass
                    # 结束挑战
                    self.click_btn(FIGHT_BTN["xiayibu2"], wait_self_before=True)
                    self.wait_for_loading(delay=1)
                    self.zhuxian_kkr()  # 跳过剧情，跳过对话框
                    return 1
                elif mode == 2:
                    # 前往主线关卡
                    var["cur_times"] += 1
                    mv.save()
                    self.click(FIGHT_BTN["qwzxgq"], wait_self_before=True)
                    self.wait_for_loading(delay=1)
                    return 2
                elif mode == 3:
                    # 买东西
                    var["cur_times"] += 1
                    mv.save()
                    buy(True)
                    return 1

        def saodang(times):
            # 使用扫荡券
            sc = self.getscreen()
            p0 = self.img_prob(MAOXIAN_BTN["saodang_off"], screen=sc, method="sq")
            p1 = self.img_prob(MAOXIAN_BTN["saodang_on"], screen=sc, method="sq")
            if p1 > p0:
                # 可以扫荡
                for t in range(times - 1):  # 减一，本来就有一个了
                    self.click(MAOXIAN_BTN["saodang_plus"])
                click_ok = self.lock_img(MAOXIAN_BTN["saodang_ok"], elseclick=MAOXIAN_BTN["saodang_on"], elsedelay=5,
                                         is_raise=False, retry=2)
                if not click_ok or self.is_exists(MAOXIAN_BTN["no_cishu"], screen=self.last_screen):
                    # 可能不可扫荡
                    for _ in range(5):
                        self.click(45, 32)  # 瞎点点空一切对话框
                    self.click_btn(MAOXIAN_BTN["quxiao"])
                    return 0
                self.click_btn(MAOXIAN_BTN["saodang_ok"])
                self.lock_img([MAOXIAN_BTN["saodang_tiaoguo"], MAOXIAN_BTN["saodang_ok2"]])
                self.click_btn(MAOXIAN_BTN["saodang_tiaoguo"])
                self.click_btn(MAOXIAN_BTN["saodang_ok2"], wait_self_before=True)
                buy()
                self.click_btn(MAOXIAN_BTN["quxiao"])
                return 1
            else:
                # 不可扫荡
                self.click_btn(MAOXIAN_BTN["quxiao"])
                return 0

        def enter(mode=True):
            # mode=True时，如果点不进关卡会报错，否则只会返回false
            btn = PCRelement(x, y)
            if drag == "left":
                self.Drag_Left()
            elif drag == "right":
                self.Drag_Right()
            s = self.click_btn(btn, until_appear=FIGHT_BTN["xuanguan_quxiao"], is_raise=mode)
            return s

        if not enter(False):
            return -3
        stars = self.get_upperright_stars()
        if use_saodang in ["auto", True] and stars < 3:
            if use_saodang == "auto":
                use_saodang = False
            else:
                self.click_btn(MAOXIAN_BTN["quxiao"])
                return -2
        if use_saodang in ["auto", True]:
            state = saodang(times)
            if state == 1:
                # 扫荡成功
                clear()
                return times
            elif use_saodang == "auto":
                # 改手刷
                use_saodang = False
            else:
                clear()
                self.click_btn(MAOXIAN_BTN["quxiao"])
                return -2
        if use_saodang is False:
            while var["cur_times"] < times:
                # 手刷
                if fastmode:
                    s = shoushua(times - var["cur_times"])
                else:
                    s = shoushua(1)
                if s == 2:
                    if not fail_retry:
                        # 失败了不重试，结束
                        r = var["cur_win"]
                        clear()
                        return r
                if var["cur_times"] < times - 1:
                    enter()  # 再次进入
            r = var["cur_win"]
            clear()
            return r
        else:
            # 扫荡失败，还不是auto
            clear()
            self.click_btn(MAOXIAN_BTN["quxiao"])
            return -2

    def shuatuzuobiao(self, x, y, times):  # 刷图函数，xy为该图的坐标，times为刷图次数
        if self.switch == 0:
            tmp_cout = 0
            self.click(x, y, pre_delay=2, post_delay=2)
        else:
            pcr_log(self.account).write_log(level='info', message='>>>无扫荡券或者无体力，结束 全部 刷图任务！<<<')
            return
        if self.switch == 0:
            while True:  # 锁定加号
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/jiahao.bmp', at=(850, 305, 907, 358)):
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
                        pcr_log(self.account).write_log(level='info', message='>>>无扫荡券或者无体力！结束此次刷图任务！<<<')
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
                        pcr_log(self.account).write_log(level='info', message='>>>无扫荡券或者无体力！结束此次刷图任务！<<<')
                        self.switch = 1
                        self.click(677, 458)  # 取消
                        break
        else:
            pcr_log(self.account).write_log(level='info', message='>>>无扫荡券或者无体力！结束刷图任务！<<<')
        while True:
            self.click(1, 1)
            time.sleep(0.3)
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/zhuxian.jpg', at=(660, 72, 743, 94)):
                break
            if UIMatcher.img_where(screen_shot_, 'img/hard.jpg'):
                break

    def enter_zhuxian(self):
        # Fix: 2020-08-09 By TheAutumnOfRice: 未解锁地下城也可以使用了。
        # 进入主线
        self.lock_home()
        self.click_btn(MAIN_BTN["maoxian"], until_appear=MAIN_BTN["zhuxian"])
        # 进入地图
        self.click_btn(MAIN_BTN["zhuxian"], wait_self_before=True, until_appear=MAOXIAN_BTN["ditu"])

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
                self.click(MAOXIAN_BTN["hard_on"])
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
            pcr_log(self.account).write_log(level='info', message='>>>无扫荡券,无体力,无次数！结束 全部 刷图任务！<<<')
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
                        pcr_log(self.account).write_log(level='info', message='>>>无扫荡券,无体力,无次数！结束此次刷图任务！<<<')
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
                        pcr_log(self.account).write_log(level='info', message='>>>无扫荡券,无体力,无次数！结束此次刷图任务！<<<')
                        self.switch = 1
                        self.click(677, 458)  # 取消
                        break
        else:
            pcr_log(self.account).write_log(level='info', message='>>>无扫荡券,无体力,无次数！结束刷图任务！<<<')
        while True:
            self.click(1, 1)
            time.sleep(0.3)
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/zhuxian.jpg', at=(660, 72, 743, 94)):
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

    def check_zhuxian_id(self, screen=None):
        """
        识别主线图的图号
        2020-08-14 Add: By TheAutumnOfRice :
            只要截图截的小，普通困难都打倒！
        :param: screen:设置为None时，第一次重新截图
        :return:
        -1：识别失败
        1~ ：图号
        """
        # self.Drag_Left()  # 保证截图区域一致
        id = self.check_dict_id(ZHUXIAN_ID, screen)
        if id is None:
            return -1
        else:
            return id

    def check_normal_id(self, screen=None):
        return self.check_zhuxian_id(screen)

    def check_hard_id(self, screen=None):
        return self.check_zhuxian_id(screen)

    def shoushuazuobiao(self, x, y, jiaocheng=0, lockpic='img/zhuxian.jpg', screencut=None):
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
        self.lock_img('img/zhuxian.jpg', elseclick=[(704, 84)], elsedelay=0.5, alldelay=1, at=(660, 72, 743, 94))
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
                self.click(MAOXIAN_BTN["normal_on"])
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
                        self.click(MAOXIAN_BTN["normal_on"], post_delay=1)
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
                        self.click(MAOXIAN_BTN["hard_on"], post_delay=1)
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
        time.sleep(0.5)

    def Drag_Left(self):
        self.d.drag(200, 270, 600, 270, 0.1)  # 拖拽到最左
        time.sleep(0.5)
