import time

from core.constant import DXC_NUM, FIGHT_BTN, DXC_ELEMENT
from core.cv import UIMatcher
from core.log_handler import pcr_log
from core.pcr_config import force_as_ocr_as_possible
from scenes.dxc.dxc_select import DXCSelectA, DXCSelectB, PossibleDXCMenu
from ._dxc_base import DXCBaseMixin
from ._tools import ToolsMixin


class DXCMixin(DXCBaseMixin, ToolsMixin):
    """
    地下城插片
    包含地下城脚本
    """

    def __init__(self):
        super().__init__()

    def dixiacheng_ocr(self, skip, assist_num=1, stuck_today=False, stuck_notzhandoukaishi=False):
        """
        地下城函数已于2020/7/11日重写
        By:Cyice
        有任何问题 bug请反馈
        :param assist_num: 选支援第一行的第n个，等级限制会自动选择第n+1个
        :param stuck_notzhandoukaishi: 卡住等级不足
        :param stuck_today: 今天卡住地下城
        :param skip: 跳过战斗
        :return:
        """
        # global dixiacheng_floor_times
        # 全局变量贯通两个场景的地下层次数识别

        # 数据纠正
        if assist_num > 8 or assist_num < 1:
            assist_num = 1

        self.lock_home()

        for _ in range(3):
            self.click(10, 242)

        out = self.enter_dxc(1)
        if not out:
            pcr_log(self.account).write_log("info", f"{self.account}-已经刷过地下城！")
            self.lock_home()
            return
        while True:
            # 塔币教程处理
            time.sleep(3)
            if not self.is_exists('img/dxc/chetui.bmp', at=(830, 407, 929, 448), is_black=True, black_threshold=200):
                self.lock_img('img/dxc/chetui.bmp', side_check=self.dxc_kkr, at=(830, 407, 929, 448),
                              threshold=0.98)
                break
            else:
                if self.is_exists('img/dxc/chetui.bmp', at=(830, 407, 929, 448), is_black=True,
                                  black_threshold=4000):
                    # raise (Exception, "卡教程了")
                    self.chulijiaocheng(turnback=None)
                    if self.is_exists(DXC_ELEMENT["dxc_in_shop"]):
                        self.click(DXC_ELEMENT["dxc_in_shop"])
                    else:
                        # 应急处理：从主页返回
                        self.lock_home()  # 回首页
                        self.click(480, 505, post_delay=1)
                        self.lock_img('img/dixiacheng.jpg', elseclick=(480, 505), elsedelay=1, alldelay=1)
                        self.click(900, 138, post_delay=3)
                        self.lock_img(DXC_ELEMENT["chetui"])  # 锁定撤退
                elif self.is_exists('img/dxc/chetui.bmp', at=(830, 407, 929, 448), is_black=True,
                                    black_threshold=2000):
                    self.lock_img('img/dxc/chetui.bmp', side_check=self.juqing_kkr, at=(830, 407, 929, 448),
                                  threshold=0.98, retry=3)
                # 过剧情
                self.lock_img('img/dxc/chetui.bmp', side_check=self.juqing_kkr, at=(830, 407, 929, 448),
                              threshold=0.98, retry=3)

        tmp_cout = 0
        while tmp_cout <= 2:
            try:
                if self.is_exists('img/dxc/chetui.bmp', at=(830, 407, 929, 448)):
                    self.lock_img('img/dxc/chetui.bmp', side_check=self.dxc_kkr, at=(830, 407, 929, 448),
                                  threshold=0.98)
                    dixiacheng_floor = self.ocr_center(586, 421, 614, 438, size=1.5)
                    # print(dixiacheng_floor)
                    dixiacheng_floor = int(dixiacheng_floor.split('/')[0])
                    dixiacheng_floor_times = self.ocr_center(789, 422, 820, 438, size=1.5)
                    # print(dixiacheng_floor_times)

                    # 本地OCR会把0识别成字母O。。。
                    dixiacheng_floor_times = dixiacheng_floor_times.replace('O', '0')

                    dixiacheng_floor_times = int(dixiacheng_floor_times.split('/')[0])
                    tmp_cout = tmp_cout + 1
                    dixiacheng_times = dixiacheng_floor_times
                    # print(dixiacheng_floor, ' ', dixiacheng_floor_times)
                    if dixiacheng_floor > 1 and dixiacheng_floor_times <= 1:
                        pcr_log(self.account).write_log(level='info', message='%s 已经打过地下城，执行撤退' % self.account)
                        while True:  # 撤退地下城
                            time.sleep(self.change_time)
                            self.click(1, 1)  # 跳过结算
                            screen_shot_ = self.getscreen()
                            if self.is_exists('img/dxc/chetui.bmp', screen=screen_shot_, at=(830, 407, 929, 448)):
                                self.lock_img('img/ui/queren_blue.bmp', elseclick=[(876, 427)], elsedelay=2.8)
                                self.click_btn(DXC_ELEMENT["d1_queren_blue"],
                                               until_disappear=DXC_ELEMENT["d1_queren_blue"])
                                continue
                            elif self.is_exists(DXC_ELEMENT["sytzcs"], screen=screen_shot_):
                                break
                            elif self.is_exists("img/yunhai.bmp", screen=screen_shot_, threshold=0.975):
                                self.enter_dxc(1)
                                break
                            else:
                                self.click(1, 1, pre_delay=self.change_time)  # 取消显示结算动画
                                self.click(10, 242)  # 左点
                        # if self.is_exists('img/dxc/chetui.bmp'):
                        #     self.click(878, 432, pre_delay=self.change_time)
                        #     self.click(588, 371, pre_delay=1 + self.change_time)
                            # self.lock_home()
                            # self.dixiacheng_ocr(skip, assist_num, stuck_today, stuck_notzhandoukaishi)
                            break
                    elif dixiacheng_floor >= 1 and dixiacheng_floor_times <= 1:
                        pcr_log(self.account).write_log(level='info', message='%s 不知是否打过地下城，开始执行地下城流程' % self.account)
                        self.dxc_switch = 0
                        # 开锁
                        break
                    elif dixiacheng_floor == 1 and skip is True:
                        pcr_log(self.account).write_log(level='info',
                                                        message='%s 由于跳过战斗的开启，不知是否打过地下城，开始执行地下城流程' % self.account)
                        self.dxc_switch = 0
                        # 开锁
                        break
                else:
                    dixiacheng_floor_times = -1
                    break
            except Exception as result:
                pcr_log(self.account).write_log(level='warning', message='1-检测出异常{},重试'.format(result))
                tmp_cout = tmp_cout + 1
        tmp_cout = 0
        while tmp_cout <= 3 and self.dxc_switch == 1:
            try:
                # 防可可萝
                self.lock_img('img/yunhai.bmp', side_check=self.juqing_kkr, retry=3)
                if self.is_exists('img/yunhai.bmp'):
                    dixiacheng_times = self.ocr_center(879, 430, 917, 448, size=2.0)

                    # 本地OCR会把0识别成字母O。。。
                    dixiacheng_times = dixiacheng_times.replace('O', '0')

                    # {'log_id': ***, 'words_result_num': 1, 'words_result': [{'words': '0/1'}]}
                    # print(dixiacheng_times)
                    dixiacheng_times = int(dixiacheng_times.split('/')[0])
                    if dixiacheng_times <= 1:
                        break
                    tmp_cout = tmp_cout + 1
            except Exception as result:
                pcr_log(self.account).write_log(level='warning', message='2-检测出异常{},重试'.format(result))
                # 休息3s，等解锁动画
                time.sleep(3)
                tmp_cout = tmp_cout + 1
        while self.dxc_switch == 1:
            # print(dixiacheng_times, ' ', dixiacheng_floor_times)
            if dixiacheng_times == -1 and dixiacheng_floor_times == -1:
                pcr_log(self.account).write_log(level='warning', message='地下城次数为非法值！')
                pcr_log(self.account).write_log(level='warning', message='OCR无法识别！即将调用 非OCR版本地下城函数！\r\n')
                self.dixiacheng(skip)
                return
            try:
                if self.is_exists('img/yunhai.bmp') and dixiacheng_times == 1:
                    self.click(130, 259, post_delay=self.change_time)
                    # 保险
                    self.lock_no_img('img/yunhai.bmp', elseclick=[(130, 259)], threshold=0.975)
                    self.dxc_switch = 0
                    # 识别到后满足条件，开锁
                elif self.is_exists('img/yunhai.bmp') and dixiacheng_times == 0:
                    self.dxc_switch = 1
                    pcr_log(self.account).write_log(level='info', message='%s今天已经打过地下城' % self.account)
                    return
                if self.dxc_switch == 0:
                    # 不加可能会导致卡顿找不到图片
                    self.lock_img('img/ui/queren_blue.bmp', elseclick=[(130, 259)])
                    self.lock_no_img('img/ui/queren_blue.bmp', elseclick=[(592, 369)])  # 锁定OK
                else:
                    pcr_log(self.account).write_log(level='warning', message='识别不到次数！')
                    # LOG().Account_undergroundcity(self.account)
                    self.dxc_switch = 1
                    return
                self.d.click(1, 1)
                # 这里防止卡可可萝
            except Exception as error:
                pcr_log(self.account).write_log(level='warning', message='3-检测出异常{}'.format(error))
                pcr_log(self.account).write_log(level='warning', message='OCR无法识别！即将调用 非OCR版本地下城函数！')
                self.dixiacheng(skip)
                return
            try:
                if self.is_exists('img/dxc/chetui.bmp', at=(830, 407, 929, 448) and dixiacheng_times <= 1):
                    # print('>>>', dixiacheng_times)
                    break
            except:
                pcr_log(self.account).write_log(level='warning', message='地下城次数为非法值！')
                pcr_log(self.account).write_log(level='warning', message='OCR无法识别！即将调用 非OCR版本地下城函数！\r\n')
                self.dixiacheng(skip)
                return

        while self.dxc_switch == 0:
            if stuck_today:
                pcr_log(self.account).write_log(level='info', message="%s今天选择了卡住地下城哦~" % self.account)
                break

            # 防止一进去就是塔币教程
            self.lock_img('img/dxc/chetui.bmp', side_check=self.dxc_kkr, at=(830, 407, 929, 448))
            # 又一防御措施，防止没进去地下城
            self.lock_no_img('img/yunhai.bmp', elseclick=[(130, 259), (592, 369)], threshold=0.97)
            while True:
                time.sleep(0.5)
                self.lock_img('img/dxc/chetui.bmp', side_check=self.dxc_kkr, at=(830, 407, 929, 448))
                self.lock_img('img/dxc/chetui.bmp', side_check=self.juqing_kkr, at=(830, 407, 929, 448))
                if self.is_exists('img/dxc/chetui.bmp', at=(830, 407, 929, 448)):
                    self.lock_img('img/tiaozhan.bmp', ifclick=[(833, 456)], elseclick=[(667, 360), (667, 330)],
                                  side_check=self.dxc_kkr)
                    time.sleep(2)
                    self.lock_no_img('img/tiaozhan.bmp', ifclick=[(667, 360), (667, 330)], elseclick=[(833, 456)],
                                     side_check=self.dxc_kkr)
                    # 锁定挑战和第一层
                    break
            time.sleep(self.change_time)
            self.lock_img(DXC_ELEMENT["sheding"], ifclick=(478, 443), retry=4)
            if self.click_btn(DXC_ELEMENT["zhiyuan_white"], until_appear=DXC_ELEMENT["zhiyuan_blue"],
                              retry=3, wait_self_before=True):
                if assist_num >= 3:
                    print("开发者没有写大于支援位置3的暗点检测，需要到再在群里提吧（有点小麻烦")
                pass
            # if self.lock_no_img(DXC_ELEMENT["zhiyuan_blue"], retry=1):
            else:
                pcr_log(self.account).write_log(level='info', message="%s 无支援人物!" % self.account)
                self.dxc_switch = 1
                break

            time.sleep(self.change_time + 1)
            if self.is_exists(DXC_ELEMENT["zhiyuan_gouxuan"]):
                pass
            elif self.is_exists('img/dengjixianzhi.jpg', threshold=0.1, is_black=True, black_threshold=5900,
                                at=(45, 144, 163, 252)) and assist_num <= 2:
                # 如果第二个也等级不足就退出
                if self.is_exists('img/dengjixianzhi.jpg', threshold=0.1, is_black=True, black_threshold=5900,
                                  at=(160, 126, 270, 232)):
                    pcr_log(self.account).write_log(level='info', message="%s 的等级无法达到两个支援要求的最低等级!" % self.account)
                    self.dxc_switch = 1
                    break
                # 如果等级不足，就支援的第二个人
                self.click_btn(DXC_ELEMENT["zhiyuan_dianren"][assist_num + 1],
                               until_appear=DXC_ELEMENT["zhiyuan_gouxuan"])
                # self.click(100, 173, post_delay=1)  # 支援的第一个人
            else:
                time.sleep(self.change_time)
                self.click_btn(DXC_ELEMENT["zhiyuan_dianren"][assist_num], until_appear=DXC_ELEMENT["zhiyuan_gouxuan"])

            # click_btn 的retry无法覆盖到until_appear
            # if self.click_btn(DXC_ELEMENT["zhiyuan_dianren"][assist_num], until_appear=DXC_ELEMENT["zhiyuan_gouxuan"], retry=4):
            #     pass
            # elif self.click_btn(DXC_ELEMENT["zhiyuan_dianren"][assist_num + 1], until_appear=DXC_ELEMENT["zhiyuan_gouxuan"] , retry=4):
            #     pass
            # else:
            #     pcr_log(self.account).write_log(level='info', message="%s 的等级无法达到两个支援要求的最低等级!" % self.account)
            #     self.dxc_switch = 1
            #     break

            time.sleep(self.change_time)
            if self.is_exists('img/notzhandoukaishi.bmp', at=(758, 423, 915, 473), is_black=True, black_threshold=1500):
                # 逻辑顺序改变
                # 当无法选支援一二位时，将会退出地下城
                pcr_log(self.account).write_log(level='info', message="%s无法出击!" % self.account)
                break
            else:
                # 全部
                self.click_btn(DXC_ELEMENT["quanbu_white"], until_appear=DXC_ELEMENT["quanbu_blue"], elsedelay=0.1)
                for i in range(1, 9):
                    self.click(DXC_ELEMENT["zhiyuan_dianren"][i])
                self.click_btn(DXC_ELEMENT["zhandoukaishi"], until_disappear=DXC_ELEMENT["zhandoukaishi"]
                               , elsedelay=0.1)  # 战斗开始
            while True:
                if self.is_exists(FIGHT_BTN["caidan"]):
                    break
                self.lock_img('img/ui/queren_blue.bmp', elseclick=[(833, 470)], ifbefore=self.change_time + 1,
                              ifdelay=self.change_time, retry=10)
                self.lock_no_img('img/ui/queren_blue.bmp', elseclick=[(588, 480)])
                break

            if skip:  # 直接放弃战斗
                self.lock_img(FIGHT_BTN["caidan"], elseclick=[(1, 1)], retry=5)
                self.click_btn(FIGHT_BTN["caidan"], wait_self_before=True, until_appear=FIGHT_BTN["fangqi_1"],
                               elsedelay=0.1)
                self.click_btn(FIGHT_BTN["fangqi_1"], until_appear=FIGHT_BTN["fangqi_2"])
                self.click_btn(FIGHT_BTN["fangqi_2"], until_disappear=FIGHT_BTN["fangqi_2"])
                time.sleep(3 + self.change_time)
                # 这里防一波打得太快导致来不及放弃
                if self.is_exists('img/shanghaibaogao.jpg', at=(663, 6, 958, 120)) and \
                        self.is_exists('img/xiayibu.jpg', at=(457, 421, 955, 535)):
                    self.lock_no_img('img/xiayibu.jpg', elseclick=[(870, 503)])
                elif self.is_exists('img/shanghaibaogao.jpg', at=(663, 6, 958, 120)) and \
                        self.is_exists('img/qianwangdixiacheng.jpg', at=(457, 421, 955, 535)):
                    self.lock_no_img('img/qianwangdixiacheng.jpg', elseclick=[(870, 503)])
            else:
                # 防止奇奇怪怪的飞到主菜单
                if self.lock_img('img/caidan.jpg', elseclick=[(1, 1)], retry=6):
                    self.lock_img('img/auto_1.jpg', elseclick=[(914, 425)], elsedelay=0.2, retry=3)
                    self.lock_img('img/kuaijin_3.bmp', elseclick=[(913, 494)], elsedelay=0.2, retry=3)
            while skip is False:  # 结束战斗返回
                time.sleep(self.change_time)
                if self.is_exists('img/shanghaibaogao.jpg', at=(663, 6, 958, 120)) and \
                        self.is_exists('img/xiayibu.jpg', at=(457, 421, 955, 535)):
                    self.lock_no_img('img/xiayibu.jpg', elseclick=[(870, 503)])
                    break
                elif self.is_exists('img/shanghaibaogao.jpg', at=(663, 6, 958, 120)) and \
                        self.is_exists('img/qianwangdixiacheng.jpg', at=(457, 421, 955, 535)):
                    self.lock_no_img('img/qianwangdixiacheng.jpg', elseclick=[(870, 503)])
                    break
                else:
                    self.click(1, 1, pre_delay=self.change_time)  # 取消显示结算动画
                    if self.is_exists('img/shanghaibaogao.jpg', threshold=0.8, at=(663, 6, 958, 120)):
                        self.click(870, 503)
                    if self.is_exists('img/dxc/chetui.bmp'):
                        break

            while True:  # 撤退地下城
                if self.dxc_switch == 1:
                    break
                time.sleep(self.change_time)
                self.click(1, 1)  # 跳过结算
                screen_shot_ = self.getscreen()
                if self.is_exists('img/dxc/chetui.bmp', screen=screen_shot_, at=(830, 407, 929, 448)):
                    self.lock_img('img/ui/queren_blue.bmp', elseclick=[(876, 427)], elsedelay=2.8)
                    self.click_btn(DXC_ELEMENT["d1_queren_blue"], until_disappear=DXC_ELEMENT["d1_queren_blue"])
                    continue
                elif self.is_exists(DXC_ELEMENT["sytzcs"], screen=screen_shot_):
                    break
                elif self.is_exists("img/yunhai.bmp", screen=screen_shot_, threshold=0.975):
                    break
                else:
                    self.click(1, 1, pre_delay=self.change_time)  # 取消显示结算动画
                    self.click(10, 242)  # 左点
            # 执行完后再检测一轮后跳出大循环 self.lock_no_img('img/dxc/chetui.bmp', elseclick=[(808, 435), (588, 371)], retry=20,
            # at=(779, 421, 833, 440)) self.lock_img('img/yunhai.bmp')
            break

        while True:
            # 防卡死
            if self.is_exists(img="img/home/liwu.bmp", at=(891, 417, 927, 448)):
                break
            screen_shot_ = self.getscreen()
            # click_img 暂且无法传入list
            self.click_img(screen=screen_shot_, img='img/xiayibu.jpg')
            self.click_img(screen=screen_shot_, img='img/qianwangdixiacheng.jpg')

            if stuck_today or stuck_notzhandoukaishi or self.dxc_switch == 1:
                self.lock_home()
                continue

            screen_shot = self.getscreen()
            self.click_img(screen_shot, 'img/dxc/chetui.bmp', at=(830, 407, 929, 448))
            time.sleep(2 + self.change_time)
            screen_shot = self.getscreen()
            self.click_img(screen_shot, 'img/ui/queren_blue.bmp')
            self.lock_home()

    def dixiacheng(self, skip):
        """
        地下城函数于2020/7/14日修改
        地下城函数再于2020/8/13日修改
        By:Dr-Bluemond
        有任何问题 bug请反馈
        :param skip:
        :return:
        """
        if force_as_ocr_as_possible:
            pcr_log(self.account).write_log("info", f"{self.account}-即将调用OCR版地下城！")
            self.dixiacheng_ocr(skip)
            return

        out = self.enter_dxc(1)
        if not out:
            pcr_log(self.account).write_log("info", f"{self.account}-已经刷过地下城！")
            self.lock_home()
            return
        # # 首页 -> 地下城选章/（新号）地下城章内
        # self.lock_img('img/dixiacheng.jpg', elseclick=[(480, 505)], elsedelay=0.5, at=(837, 92, 915, 140))  # 进入地下城
        # self.lock_no_img('img/dixiacheng.jpg', elseclick=[(900, 138)], elsedelay=0.5, alldelay=5,
        #                  at=(837, 92, 915, 140))
        # # 防止一进去就是塔币教程
        # self.lock_img('img/chetui.jpg', elseclick=[(1, 1)], side_check=self.dxc_kkr, retry=3, at=(738, 420, 872, 442))
        # # 防止教程
        # self.lock_img('img/chetui.jpg', elseclick=[(1, 1)], side_check=self.juqing_kkr, at=(738, 420, 872, 442),
        #               retry=3)

        # 撤退 如果 已经进入
        while True:
            screen = self.getscreen()
            if UIMatcher.img_where(screen, 'img/yunhai.bmp'):
                break
            if UIMatcher.img_where(screen, 'img/chetui.jpg', at=(738, 420, 872, 442)):
                self.lock_img('img/ok.bmp', elseclick=[(810, 433)], elsedelay=1, ifclick=[(592, 370)], ifbefore=0.5,
                              at=(495, 353, 687, 388))
                continue
            self.click(1, 100)
            time.sleep(0.3)

        ok = self.lock_img('img/ok.bmp', elseclick=[(131, 159)], elsedelay=2, ifclick=[(596, 371)], ifbefore=0.5,
                           ifdelay=0, retry=3)
        if not ok:
            pcr_log(self.account).write_log(level='error', message="%s未能成功进入云海的山脉，跳过刷地下城" % self.account)
            self.lock_img('img/liwu.bmp', elseclick=[(131, 533)], at=(891, 413, 930, 452))
            return
        # 防止教程
        self.lock_img('img/chetui.jpg', side_check=self.juqing_kkr, at=(738, 420, 872, 442), retry=3, threshold=0.97)

        while True:
            # 防止塔币教程
            self.lock_img('img/chetui.jpg', elseclick=[(1, 1)], side_check=self.dxc_kkr, at=(738, 420, 872, 442),
                          retry=10, threshold=0.97)
            # 锁定挑战和第一层
            time.sleep(1.5)
            self.lock_img('img/tiaozhan.bmp', elseclick=[(667, 360)], elsedelay=1, ifclick=[(833, 456)],
                          at=(759, 428, 921, 483))
            self.lock_img('img/dxc/quanbu.bmp', ifclick=[(480, 88)], ifbefore=1, at=(78, 80, 114, 102))
            time.sleep(0.5)
            poses = [(106, 172), (216, 172), (323, 172), (425, 172)]
            for pos in poses:
                self.click(*pos)
                time.sleep(0.2)
            self.click(98, 92)
            time.sleep(0.5)
            for pos in poses:
                self.click(*pos)
                time.sleep(0.2)
            screen = self.getscreen()
            if UIMatcher.img_where(screen, 'img/notzhandoukaishi.bmp', threshold=0.98):
                # 当无法出击时将会退出地下城
                time.sleep(0.5)
                self.click(1, 100)
                pcr_log(self.account).write_log(level='info', message="%s无法出击!" % self.account)
                break
            while True:
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/zhandoukaishi.jpg', at=(758, 427, 917, 479)):
                    time.sleep(1)
                    self.click(833, 470)  # 战斗开始
                    self.lock_img('img/ok.bmp', ifclick=[(588, 479)], ifdelay=0.5, retry=5)
                    break
                time.sleep(1)

            time.sleep(4)  # 这里填写你预估的进入战斗加载所花费的时间
            if skip:  # 直接放弃战斗
                ok = self.lock_img('img/fangqi.jpg', elseclick=[(902, 33)], elsedelay=1, ifclick=[(625, 376)],
                                   ifbefore=0.5, ifdelay=0, retry=10, at=(567, 351, 686, 392))
                if ok:
                    ok2 = self.lock_img('img/fangqi_2.bmp', ifclick=[(625, 376)], ifbefore=0.5, ifdelay=0, retry=3,
                                        at=(486, 344, 693, 396))
                    if not ok2:
                        skip = False
                else:
                    skip = False
            else:
                self.lock_img('img/kuaijin_2.bmp', elseclick=[(913, 494)], ifbefore=0, ifdelay=0.5, retry=10)
                screen = self.getscreen()
                if UIMatcher.img_where(screen, 'img/auto.jpg'):
                    time.sleep(0.2)
                    self.click(914, 425)

            if skip is False:
                self.lock_img('img/shanghaibaogao.jpg', elseclick=[(1, 100)], ifclick=[(820, 492)], ifdelay=3)
                self.lock_no_img('img/shanghaibaogao.jpg', elseclick=[(820, 492)], elsedelay=3)

            self.click(1, 1)  # 取消显示结算动画
            self.lock_img('img/chetui.jpg', elseclick=[(1, 1)], at=(738, 420, 872, 442))
            self.lock_img('img/ok.bmp', elseclick=[(809, 433)], elsedelay=1, at=(495, 353, 687, 388))
            self.lock_no_img('img/ok.bmp', elseclick=[(592, 373)], elsedelay=0.5, at=(495, 353, 687, 388))
            break

        self.lock_img('img/liwu.bmp', elseclick=[(131, 533)], at=(891, 413, 930, 452))

    def dixiachengYunhai(self):  # 地下城 云海 （第一个）
        self.click(480, 505)
        time.sleep(1)
        while True:
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
            self.click(480, 505)
            time.sleep(1)
        self.click(900, 138)
        time.sleep(3)

        screen_shot_ = self.getscreen()
        if UIMatcher.img_where(screen_shot_, 'img/dixiacheng_used.jpg'):  # 避免某些农场号刚买回来已经进了地下城
            self.lock_img('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页
        else:
            # 下面这段因为调试而注释了，实际使用时要加上
            while True:
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):  # 避免某些农场号刚买回来已经进了地下城
                    break
                if UIMatcher.img_where(screen_shot_, 'img/yunhai.bmp'):
                    self.click(130, 259)  # 云海
                    time.sleep(1)
                    while True:
                        screen_shot_ = self.getscreen()
                        if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                            break
                    self.click(592, 369)  # 点击ok
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
            self.lock_img('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页

    def dixiachengDuanya(self):  # 地下城 断崖（第三个）
        self.click(480, 505)
        time.sleep(1)
        while True:
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
            self.click(480, 505)
            time.sleep(1)
        self.click(900, 138)
        time.sleep(3)
        screen_shot_ = self.getscreen()
        if UIMatcher.img_where(screen_shot_, 'img/dixiacheng_used.jpg'):  # 避免某些农场号刚买回来已经进了地下城
            self.lock_img('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页
        else:
            # 下面这段因为调试而注释了，实际使用时要加上
            while True:
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):  # 避免某些农场号刚买回来已经进了地下城
                    break
                if UIMatcher.img_where(screen_shot_, 'img/yunhai.bmp'):
                    self.click(712, 267)  # 断崖
                    time.sleep(1)
                    while True:
                        screen_shot_ = self.getscreen()
                        if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                            break
                    self.click(592, 369)  # 点击ok
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
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/10.jpg'):  # 地下城10层失败重试1次，使低练度号能2刀通关boss
                    self.is_dixiacheng_end = 0
                    self.dixiachengzuobiao(654, 321, 0)  # 10层
                self.click(780, 430)
                time.sleep(1)
                self.click(576, 364)

        # 完成战斗后
        self.lock_home()

    def shuatuDD(self, dxc_id: int, mode: int, stop_criteria: int = 0, after_stop: int = 0, teams=None,
                 safety_stop=1):  # 刷地下城

        return self.shuatuDD_OCR(dxc_id, mode, stop_criteria, after_stop, teams, safety_stop, 0)
        # 2020-08-01 Fix By TheAutumnOfRice 对快速截屏的兼容性
        from core.constant import DXC_COORD
        def parse_team_str(teamstr: str):
            if teamstr == "":
                return 0, 0
            elif teamstr == "zhanli":
                return -1, -1
            strs = teamstr.split("-")
            assert len(strs) == 2, f"错误的编队信息：{teamstr}"
            return int(strs[0]), int(strs[1])

        def stop_fun():
            if after_stop == 0:
                self.log.write_log("info", "触发停止条件，回到主页。")
                self.lock_home()
            else:
                self.log.write_log("info", "触发停止条件，撤退。")
                self.dxc_chetui()
                self.lock_home()

        if teams is None:
            teams = [""]
        assert len(teams) > 0, "至少设置一个队伍！"
        if mode == 2:
            assert len(teams) > 1, "模式2下，至少设置两个队伍！"
        if dxc_id not in DXC_COORD:
            self.log.write_log("error", "坐标库中没有{dxc_id}号地下城的信息！")
            return
        self.lock_home()
        if not self.enter_dxc(dxc_id):
            # 进入地下城失败，次数不足
            self.lock_home()
            return
        # 已经进入地下城
        cur_layer = self.check_dxc_level(dxc_id)  # 获取层数
        if cur_layer == -1:
            # 人力OCR失败，一个一个尝试bian点击
            cur_layer = 1
        max_layer = max(DXC_NUM[dxc_id])
        set_bianzu, set_duiwu = parse_team_str(teams[0])
        if stop_criteria == 0:
            min_live = 5
        else:
            min_live = 1
        while cur_layer <= max_layer - 1:
            # 刷小怪
            if mode == 3 and cur_layer >= 2:
                stop_fun()
                return
            cur_x, cur_y = DXC_COORD[dxc_id][cur_layer]
            state = self.dxczuobiao(cur_x, cur_y, 1, 2, set_bianzu, set_duiwu, min_live)
            set_bianzu = 0
            set_duiwu = 0
            if state == 0:
                # 伤亡惨重
                if safety_stop:
                    self.log.write_log("warning", "安全保护启动，可能在小关中阵亡，跳过地下城。")
                    self.save_last_screen("安全保护Debug.bmp")
                    for _ in range(10):
                        self.click(1, 1)
                    self.lock_home()
                else:
                    self.log.write_log("warning", "在地下城伤亡惨重！")
                    for _ in range(10):
                        self.click(1, 1)
                    stop_fun()
                return
            elif state == -2:
                # 没有点中图，试试下一个
                cur_layer += 1
                continue
            elif state == -1:
                # 发生未知错误
                raise Exception("在执行地下城时发生了未知的错误，场景识别失败！")
            elif state == 1:
                # 打赢了
                self.log.write_log("info", f"战胜了地下城{dxc_id}-{cur_layer}!")
                cur_layer += 1
            elif state == 2:
                # 打输了，看看有没有机会再打一次
                self.log.write_log("info", f"战败于地下城{dxc_id}-{cur_layer}!")
        if mode == 0:
            self.log.write_log("info", "不打Boss。")
            stop_fun()
            return

        cur_team = 0
        if mode == 2:
            cur_team = 1
            set_bianzu, set_duiwu = parse_team_str(teams[cur_team])
        all_team = len(teams)
        cur_x, cur_y = DXC_COORD[dxc_id][max_layer]
        while True:
            # 用剩余的队伍一个接一个打Boss
            state = self.dxczuobiao(cur_x, cur_y, 1, 2, set_bianzu, set_duiwu, min_live)
            set_bianzu = 0
            set_duiwu = 0
            if state == 0:
                # 伤亡惨重
                self.log.write_log("info", "在地下城打Boss伤亡惨重！")
                cur_team += 1
                if cur_team < all_team:
                    set_bianzu, set_duiwu = parse_team_str(teams[cur_team])
                    self.log.write_log("info", f"更换队伍：{teams[cur_team]}")
                    continue
                else:
                    self.log.write_log("info", "你的队伍都死光啦！")
                    stop_fun()
                    return
            elif state == -2:
                # 没有点中图，试试下一个
                self.log.write_log("error", "没有找到Boss坐标，中止任务")
                stop_fun()
                return
            elif state == -1:
                # 发生未知错误
                raise Exception("在执行地下城时发生了未知的错误，场景识别失败！")
            elif state == 1:
                # 打赢了
                cur_layer += 1
                self.log.write_log("info", f"战胜了地下城{dxc_id}-BOSS!")
                break
            elif state == 2:
                # 打输了，看看有没有机会再打一次
                self.log.write_log("info", f"战败于地下城{dxc_id}-BOSS!")
                continue
        # 打赢了
        self.lock_home()

    def shuatuDD_OCR(self, dxc_id: int, mode: int, stop_criteria: int = 0, after_stop: int = 0, teams=None,
                     safety_stop=1, assist=0):  # 刷地下城
        """
        2021-04-22 Add By TheAutumnOfRice

        统一刷地下城函数，全Auto通关地下城
        三倍速通关！
        修复周年庆UIBUG，采用scenes框架

        :param dxc_id: 地下城的ID
        :param mode: 模式
            mode 0：不打Boss，用队伍1只打小关
            mode 1：打Boss，用队伍1打小关，用队伍[1,2,3,4,5...]打Boss
            mode 2：打Boss，用队伍1打小关，用队伍[2,3,4,5...]打Boss
            mode 3：用只打第一小关，无论怎样都退出
            mode 4：（攒TP）用队伍[1,2,3,...,N-1]攒TP，N为总层数；用队伍[N,N+1,...]打Boss （不支持借人）
        :param stop_criteria: 终止条件
            设置为0时，只要战斗中出现人员伤亡，直接结束
            设置为1时，一直战斗到当前队伍无人幸存，才结束
                注：如果在小关遇到停止条件，则直接结束
                打Boss时，如果选用mode 2，则当一个队触发停止条件后会更换下一个队伍
                直到队伍列表全部被遍历完毕才结束。
        :param after_stop: 停止之后做什么
            设置为0时，直接回到主页
            设置为1时，撤退并回到主页
                注：如果mode==1（不打Boss），则打完小关之后是否撤退仍然受到该参数的影响
        :param teams:
            编队列表，参战地下城所使用的编队
            按照列表顺序分别表示编队1号，2号，3号……
            每一个元素为一个字符串
            若为空字符串，则表示不进行队伍更改，沿用上次队伍
            若为"zhanli/dengji/xingshu"，则按照相关排序，选择前五最高为当前队伍
            若为“a-b",其中a为1~5的整数，b为1~3的整数，则选择编组a队伍b。
        :param safety_stop: 安全措施（防止过早退出）
            设置为0时，如果在小关触发停止条件，则不管
            设置为1时，如果在小关触发停止条件，则跳过本脚本，不撤退，防止大号误撤退（默认）
        :param assist: 借人模式
            设置为0时，不借人。
            设置为1~16时，借第n个人（若设置为1，则借左上角的，以此类推）
            注：若指定了具体编队，则借人在编队后进行；否则借人将先进行。
        """
        # 2020-08-01 Fix By TheAutumnOfRice 对快速截屏的兼容性
        from core.constant import DXC_COORD

        def stop_fun():
            if after_stop == 0:
                self.log.write_log("info", "触发停止条件，回到主页。")
                self.lock_home()
            else:
                self.log.write_log("info", "触发停止条件，撤退。")
                S = DXCSelectB(self)
                S.goto_chetui().ok()
                self.lock_home()

        if teams is None:
            teams = [""]
        assert len(teams) > 0, "至少设置一个队伍！"
        if mode == 2:
            assert len(teams) > 1, "模式2下，至少设置两个队伍！"
        if dxc_id not in DXC_COORD:
            self.log.write_log("error", f"坐标库中没有{dxc_id}号地下城的信息！")
            return

        # Start
        S = self.get_zhuye()
        S = S.goto_maoxian()
        S = S.goto_dxc()
        if isinstance(S, DXCSelectA):
            cishu = S.get_cishu()
            if cishu == 0:
                self.log.write_log("info", "地下城次数已经耗尽。")
                self.lock_home()
                return
            S = S.enter_dxc(dxc_id)

        # 已经进入地下城
        cur_layer = S.get_jieshu()
        max_layer = max(DXC_NUM[dxc_id])

        if stop_criteria == 0:
            min_live = 5
        else:
            min_live = 1

        cur_team = -1

        while cur_layer <= max_layer:
            if mode == 3 and cur_layer >= 2:
                self.log.write_log("info", "只打第一层")
                stop_fun()
                return
            if mode == 0 and cur_layer == max_layer:
                self.log.write_log("info", "不打Boss。")
                stop_fun()
                return
            cur_x, cur_y = DXC_COORD[dxc_id][cur_layer]

            # 尝试点图
            self.wait_for_stable(at=DXC_ELEMENT["map"], delay=1, threshold=0.1, max_retry=5)  # 等待小人走完
            out = S.click_xy_and_open_fightinfo_xy(cur_x, cur_y)
            if out is None:
                # 点图失败，跳过下一层
                self.log.write_log("warning", "进图失败，尝试下一层。")
                cur_layer += 1
                continue
            out = out.goto_tiaozhan()
            _team_init = False
            # 进入编组，这个循环控制：换人 - 检查存活 - 如果存活满足要求，跳出循环
            while True:
                if cur_layer < max_layer:
                    # 打小怪的配置
                    cur_team = 0
                else:
                    if not _team_init:
                        # 初始化打Boss队伍配置
                        _team_init = True
                        if mode == 1:
                            cur_team = 0
                        elif mode == 2:
                            cur_team = 1
                        elif mode == 4:
                            cur_team = max_layer - 1
                        else:
                            cur_team = 0  # 错误的配置
                        if cur_team >= len(teams):
                            cur_team = len(teams) - 1
                if mode < 4:
                    # 非攒TP模式，只在第一层进行选人
                    if assist > 0:
                        if teams[cur_team] in ['zhanli', 'xingshu', 'dengji']:
                            # 先支援，再选满
                            out.select_by_sort(order=teams[0], change=1)  # 先把人全下了 (change=1)
                            out.get_zhiyuan(assist)  # 上支援
                            out.select_by_sort(order=teams[0], change=3)  # 不下人，尽量上人 (change=3)
                        elif teams[cur_team] == "":
                            # 不动。
                            pass
                        else:
                            # 先选队伍，再支援
                            out.select_team(teams[cur_team])
                            out.get_zhiyuan(assist)
                    else:
                        # 没有支援就很简单了：直接上人。
                        out.select_team(teams[cur_team])

                    # 仅第一次进入时借人和选人。
                    assist = 0
                    teams[cur_team] = ""
                else:
                    # 攒TP模式，根据层数选人，不支持借人
                    out.select_team(teams[cur_layer - 1])

                # 检查死亡情况
                if out.get_fight_current_member_count() < min_live:
                    # 伤亡惨重
                    if cur_layer < max_layer:
                        # 小关阵亡，直接结束
                        if safety_stop:
                            self.log.write_log("warning", "安全保护启动，可能在小关中阵亡，跳过地下城。")
                            self.save_last_screen("安全保护Debug.bmp")
                            for _ in range(10):
                                self.click(1, 1)
                            self.lock_home()
                        else:
                            self.log.write_log("warning", "在地下城小关伤亡惨重！")
                            for _ in range(10):
                                self.click(1, 1)
                            stop_fun()
                        return
                    else:
                        # Boss阵亡，换队伍直到不能换位置。
                        cur_team += 1
                        if cur_team >= len(teams):
                            self.log.write_log("info", "你的队伍都死光啦！")
                            stop_fun()
                            return
                        else:
                            self.log.write_log("info", f"伤亡惨重，更换队伍：{teams[cur_team]}")
                            continue
                else:
                    # 找到满足要求的队伍，出战！
                    break

            # 开始战斗
            out = out.goto_zhandou()
            screen = self.getscreen()
            if cur_layer < max_layer:
                if mode == 4:
                    # 攒TP
                    out.set_auto(0, screen)
                else:
                    # 不攒TP
                    out.set_auto(1, screen)
            else:
                out.set_auto(1, screen)
            screen = self.last_screen
            out.set_speed(2, 2, screen)  # 三倍速
            state = out.wait_for_end()
            if state == 1:
                # 战斗胜利
                self.log.write_log("info", f"战胜了地下城{dxc_id}-{cur_layer}!")
                cur_layer += 1
            else:
                # 战斗失败
                self.log.write_log("info", f"战败于地下城{dxc_id}-{cur_layer}!")

            # 战斗结束的一系列处理
            PS = PossibleDXCMenu(self)
            out = PS.check(double_check=3, check_double_scene=True, timeout=60, no_scene_feature=False)
            if isinstance(out, PS.DXCSelectA):
                # 打完了地下城，通关了。
                self.log.write_log("info", "通关地下城！")
                self.lock_home()
                return
            elif isinstance(out, (PS.DXCKKR, PS.DXCJuQing)):
                # 跳过KKR和剧情
                out.skip()
                self.get_zhuye().goto_maoxian().goto_dxc()
                # continue再次检查处于A还是B
                continue
            elif isinstance(out, PS.ShouQuBaoChou):
                out.ok()
                continue
            elif isinstance(out, PS.DXCSelectB):
                # 回到选图界面，轮询结束。
                continue

        # 打赢了
        self.lock_home()
