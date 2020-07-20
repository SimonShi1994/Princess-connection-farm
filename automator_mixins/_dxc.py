import time

from core.cv import UIMatcher
from ._dxc_base import DXCBaseMixin
from ._tools import ToolsMixin


class DXCMixin(DXCBaseMixin, ToolsMixin):
    """
    地下城插片
    包含地下城脚本
    """

    def dixiacheng_to_fix(self, skip):
        """
        地下城函数已于2020/7/11日重写
        By:Cyice
        有任何问题 bug请反馈
        :param skip:
        :return:
        """
        while True:
            time.sleep(3)
            self.d.click(480, 505)
            time.sleep(1)
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                self.d.click(900, 138)
                time.sleep(15)
                # 我太怕妈妈了QAQ,这上面是防可可萝骑脸，按需求调配
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/kekeluo.bmp'):
                    time.sleep(10)
                    # 跳过可可萝
                    self.d.click(1, 1)
                    time.sleep(1)
                    break
                else:
                    break
        while True:
            try:
                time.sleep(5)
                dixiacheng_floor = self.baidu_ocr(200, 410, 263, 458)
                dixiacheng_floor = int(dixiacheng_floor['words_result'][0]['words'].split('/')[0])
                if dixiacheng_floor > 1:
                    print('%s 已经打过地下城，执行撤退' % self.account)
                    time.sleep(3)
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):
                        self.d.click(808, 435)
                        time.sleep(1)
                        self.d.click(588, 371)
                        time.sleep(3)
                        break
                else:
                    break
            except Exception as result:
                print('检测出异常{}'.format(result))
            break
        try:
            time.sleep(5)
            dixiacheng_times = self.baidu_ocr(868, 419, 928, 459)
            dixiacheng_times = int(dixiacheng_times['words_result'][0]['words'].split('/')[0])
        except Exception as result:
            print('检测出异常{}'.format(result))
        # 下面这段因为调试而注释了，实际使用时要加上
        while True:
            try:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/yunhai.bmp') and dixiacheng_times == 1:
                    self.d.click(233, 311)
                    time.sleep(1)
                elif UIMatcher.img_where(screen_shot_, 'img/yunhai.bmp') and dixiacheng_times == 0:
                    self.dxc_switch = 1
                    # LOG().Account_undergroundcity(self.account)
                if self.dxc_switch == 0:
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                        self.d.click(592, 369)
                    # self.lockimg('img/ok.bmp', ifclick=[(592, 369)], elseclick=[(592, 369)])
                    # 锁定OK
                else:
                    print('>>>今天无次数\r\n')
                    # LOG().Account_undergroundcity(self.account)
                    break
            except Exception as error:
                print('检测出异常{}'.format(error))
                print('OCR无法识别！\r\n')
                break
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):
                break
        while self.dxc_switch == 0:
            while True:
                time.sleep(2)
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):
                    self.lockimg('img/tiaozhan.bmp', ifclick=[(833, 456)], elseclick=[(667, 360)])
                    # 锁定挑战和第一层
                    break
            while True:
                time.sleep(2)
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/zhiyuan.jpg'):
                    time.sleep(1)
                    # self.d.click(100, 173)  # 第一个人
                    screen_shot = self.d.screenshot(format="opencv")
                    self.guochang(screen_shot, ['img/zhiyuan.jpg'], suiji=0)
                    break

            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dengjixianzhi.jpg'):
                self.d.click(213, 208)  # 如果等级不足，就支援的第二个人
                time.sleep(1)
            else:
                self.d.click(100, 173)  # 支援的第一个人
                time.sleep(1)
                self.d.click(213, 208)  # 以防万一
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/notzhandoukaishi.bmp', threshold=1.0):
                # 逻辑顺序改变
                # 当无法选支援一二位时，将会退出地下城
                print("无法出击!")
                break
            else:
                self.d.click(98, 88)  # 全部
                time.sleep(1)
                self.d.click(100, 173)  # 第一个人
                time.sleep(1)
                self.d.click(833, 470)  # 战斗开始
            while True:
                time.sleep(2)
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                    self.guochang(screen_shot_, ['img/ok.bmp'], suiji=0)
                    break
                if UIMatcher.img_where(screen_shot_, 'img/zhandoukaishi.jpg'):
                    time.sleep(1.5)
                    self.d.click(833, 470)  # 战斗开始
                    break

            if skip:  # 直接放弃战斗
                self.lockimg('img/caidan.jpg', ifclick=[(902, 33)], ifbefore=2, ifdelay=1)
                self.lockimg('img/fangqi.jpg', ifclick=[(625, 376)], ifbefore=2, ifdelay=3)
                self.lockimg('img/fangqi_2.bmp', ifclick=[(625, 376)], ifbefore=2, ifdelay=1)
            else:
                self.lockimg('img/kuaijin_1.jpg', ifclick=[(913, 494)], elseclick=[(913, 494)], ifbefore=2, ifdelay=1)
            while skip is False:  # 结束战斗返回
                time.sleep(2)
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/shanghaibaogao.jpg'):
                    time.sleep(3)
                    self.guochang(screen_shot_, ['img/xiayibu.jpg', 'img/qianwangdixiacheng.jpg'], suiji=0)
                    if UIMatcher.img_where(screen_shot_, 'img/duiwu.jpg'):
                        self.guochang(screen_shot_, ['img/xiayibu.jpg', 'img/qianwangdixiacheng.jpg'], suiji=0)
                        break
                    else:
                        print('>>>无法识别到图像，坐标点击\r\n')
                        time.sleep(3)
                        self.d.click(828, 502)
                        break
                elif UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):
                    time.sleep(3)
                    # 撤退
                    self.d.click(808, 435)
                    time.sleep(1)
                    self.d.click(588, 371)
                    break

            time.sleep(1)
            self.d.click(1, 1)  # 取消显示结算动画
            while True:  # 撤退地下城
                time.sleep(2)
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):
                    # for i in range(3):
                    # 保险措施
                    # self.d.click(808, 435)
                    # time.sleep(1)
                    # self.d.click(588, 371)
                    self.guochang(screen_shot_, ['img/chetui.jpg'], suiji=0)
                    time.sleep(1)
                    screen_shot = self.d.screenshot(format="opencv")
                    self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
                    # LOG().Account_undergroundcity(self.account)
                    break
                self.d.click(1, 1)  #
                time.sleep(1)
            break
        while True:  # 首页锁定
            if UIMatcher.img_where(screen_shot_, 'img/liwu.bmp', at=(891, 413, 930, 452)):
                break
            self.d.click(131, 533)
            time.sleep(1)  # 保证回到首页
            # 防卡死
            screen_shot_ = self.d.screenshot(format="opencv")
            self.guochang(screen_shot_, ['img/xiayibu.jpg', 'img/qianwangdixiacheng.jpg'], suiji=0)
            screen_shot = self.d.screenshot(format="opencv")
            self.guochang(screen_shot, ['img/chetui.jpg'], suiji=0)
            screen_shot = self.d.screenshot(format="opencv")
            self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)

    def dixiacheng(self, skip):
        """
        地下城函数于2020/7/14日修改
        By:Dr-Bluemond
        有任何问题 bug请反馈
        :param skip:
        :return:
        """
        # 首页 -> 地下城选章/（新号）地下城章内
        self.lockimg('img/dixiacheng.jpg', elseclick=[(480, 505)], elsedelay=0.5, at=(837, 92, 915, 140))  # 进入地下城
        self.lock_no_img('img/dixiacheng.jpg', elseclick=[(900, 138)], elsedelay=0.5, alldelay=5,
                         at=(837, 92, 915, 140))

        # 撤退 如果 已经进入
        while True:
            screen = self.d.screenshot(format='opencv')
            if UIMatcher.img_where(screen, 'img/yunhai.bmp'):
                break
            if UIMatcher.img_where(screen, 'img/chetui.jpg', at=(738, 420, 872, 442)):
                self.lockimg('img/ok.bmp', elseclick=[(810, 433)], elsedelay=1, ifclick=[(592, 370)], ifbefore=0.5,
                             at=(495, 353, 687, 388))
                continue
            self.d.click(1, 100)
            time.sleep(0.3)

        ok = self.lockimg('img/ok.bmp', elseclick=[(298, 213)], elsedelay=0.5, ifclick=[(596, 371)], ifbefore=1,
                          ifdelay=0, retry=3)
        if not ok:
            print("未能成功进入云海的山脉，跳过刷地下城")
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], at=(891, 413, 930, 452))
            return

        while True:
            # 锁定挑战和第一层
            self.lockimg('img/tiaozhan.bmp', elseclick=[(667, 360)], ifclick=[(833, 456)], at=(759, 428, 921, 483))
            time.sleep(2)
            self.d.click(480, 88)
            time.sleep(0.5)
            poses = [(106, 172), (216, 172), (323, 172), (425, 172)]
            for pos in poses:
                self.d.click(*pos)
                time.sleep(0.2)
            self.d.click(98, 92)
            time.sleep(0.5)
            for pos in poses:
                self.d.click(*pos)
                time.sleep(0.2)
            screen = self.d.screenshot(format='opencv')
            if UIMatcher.img_where(screen, 'img/notzhandoukaishi.bmp', threshold=0.98):
                # 当无法出击时将会退出地下城
                time.sleep(0.5)
                self.d.click(1, 100)
                print("无法出击!")
                break
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/zhandoukaishi.jpg', at=(758, 427, 917, 479)):
                    time.sleep(1)
                    self.d.click(833, 470)  # 战斗开始
                    self.lockimg('img/ok.bmp', ifclick=[(588, 479)], ifdelay=0.5, retry=5)
                    break
                time.sleep(1)

            time.sleep(4)  # 这里填写你预估的进入战斗加载所花费的时间
            if skip:  # 直接放弃战斗
                ok = self.lockimg('img/fangqi.jpg', elseclick=[(902, 33)], elsedelay=0.5, ifclick=[(625, 376)],
                                  ifbefore=0, ifdelay=0, retry=7, at=(567, 351, 686, 392))
                if ok:
                    ok2 = self.lockimg('img/fangqi_2.bmp', ifclick=[(625, 376)], ifbefore=0.5, ifdelay=0, retry=3,
                                       at=(486, 344, 693, 396))
                    if not ok2:
                        skip = False
                else:
                    skip = False
            else:
                self.lockimg('img/kuaijin_2.bmp', elseclick=[(913, 494)], ifbefore=0, ifdelay=0.5, retry=10)
                screen = self.d.screenshot(format='opencv')
                if UIMatcher.img_where(screen, 'img/auto.jpg'):
                    time.sleep(0.2)
                    self.d.click(914, 425)

            if skip is False:
                self.lockimg('img/shanghaibaogao.jpg', elseclick=[(1, 100)], ifclick=[(820, 492)], ifdelay=3)
                self.lock_no_img('img/shanghaibaogao.jpg', elseclick=[(820, 492)], elsedelay=3)

            self.d.click(1, 1)  # 取消显示结算动画
            self.lockimg('img/chetui.jpg', elseclick=[(1, 1)], at=(738, 420, 872, 442))
            self.lockimg('img/ok.bmp', elseclick=[(809, 433)], elsedelay=1, at=(495, 353, 687, 388))
            self.lock_no_img('img/ok.bmp', elseclick=[(592, 373)], elsedelay=0.5, at=(495, 353, 687, 388))
            break

        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], at=(891, 413, 930, 452))

    def dixiachengYunhai(self):  # 地下城 云海 （第一个）
        self.d.click(480, 505)
        time.sleep(1)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
            self.d.click(480, 505)
            time.sleep(1)
        self.d.click(900, 138)
        time.sleep(3)

        screen_shot_ = self.d.screenshot(format="opencv")
        if UIMatcher.img_where(screen_shot_, 'img/dixiacheng_used.jpg'):  # 避免某些农场号刚买回来已经进了地下城
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页
        else:
            # 下面这段因为调试而注释了，实际使用时要加上
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):  # 避免某些农场号刚买回来已经进了地下城
                    break
                if UIMatcher.img_where(screen_shot_, 'img/yunhai.bmp'):
                    self.d.click(250, 250)  # 云海
                    time.sleep(1)
                    while True:
                        screen_shot_ = self.d.screenshot(format="opencv")
                        if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                            break
                    self.d.click(592, 369)  # 点击ok
                    time.sleep(1)
                    break
            # 刷地下城
            self.dixiachengzuobiao(666, 340, 0, 1)  # 1层
            self.dixiachengzuobiao(477, 296, 0)  # 2层
            self.dixiachengzuobiao(311, 306, 0)  # 3层
            self.dixiachengzuobiao(532, 301, 0)  # 4层
            self.dixiachengzuobiao(428, 315, 0)  # 5层
            self.dixiachengzuobiao(600, 313, 0)  # 6层
            self.dixiachengzuobiao(447, 275, 0)  # 7层

            # 完成战斗后
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页

    def dixiachengDuanya(self):  # 地下城 断崖（第三个）
        self.d.click(480, 505)
        time.sleep(1)
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
            self.d.click(480, 505)
            time.sleep(1)
        self.d.click(900, 138)
        time.sleep(3)
        screen_shot_ = self.d.screenshot(format="opencv")
        if UIMatcher.img_where(screen_shot_, 'img/dixiacheng_used.jpg'):  # 避免某些农场号刚买回来已经进了地下城
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页
        else:
            # 下面这段因为调试而注释了，实际使用时要加上
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):  # 避免某些农场号刚买回来已经进了地下城
                    break
                if UIMatcher.img_where(screen_shot_, 'img/yunhai.bmp'):
                    self.d.click(712, 267)  # 断崖
                    time.sleep(1)
                    while True:
                        screen_shot_ = self.d.screenshot(format="opencv")
                        if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                            break
                    self.d.click(592, 369)  # 点击ok
                    time.sleep(1)
                    break
            # 刷地下城
            self.dixiachengzuobiao(642, 371, 0, 1)  # 1层
            self.dixiachengzuobiao(368, 276, 0, 2)  # 2层
            self.dixiachengzuobiao(627, 263, 0)  # 3层
            self.dixiachengzuobiao(427, 274, 0)  # 4层
            self.dixiachengzuobiao(199, 275, 0)  # 5层
            self.dixiachengzuobiao(495, 288, 0)  # 6层
            self.dixiachengzuobiao(736, 291, 0)  # 7层
            self.dixiachengzuobiao(460, 269, 0)  # 8层
            self.dixiachengzuobiao(243, 274, 0)  # 9层
            self.dixiachengzuobiao(654, 321, 0, 1)  # 10层

            # 点击撤退
            if self.is_dixiacheng_end == 1:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/10.jpg'):  # 地下城10层失败重试1次，使低练度号能2刀通关boss
                    self.is_dixiacheng_end = 0
                    self.dixiachengzuobiao(654, 321, 0)  # 10层
                self.d.click(780, 430)
                time.sleep(1)
                self.d.click(576, 364)

        # 完成战斗后
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
