import time

from core.constant import DXC_NUM
from core.cv import UIMatcher
from core.log_handler import pcr_log
from ._dxc_base import DXCBaseMixin
from ._tools import ToolsMixin


class DXCMixin(DXCBaseMixin, ToolsMixin):
    """
    地下城插片
    包含地下城脚本
    """

    def __init__(self):
        super().__init__()

    def dixiacheng_ocr(self, skip):
        """
        地下城函数已于2020/7/11日重写
        By:Cyice
        有任何问题 bug请反馈
        :param skip:
        :return:
        """
        # global dixiacheng_floor_times
        # 全局变量贯通两个场景的地下层次数识别
        while True:
            # 进入流程先锁上地下城执行函数
            self.dxc_switch = 1
            self.click(480, 505, pre_delay=0.5, post_delay=1)
            if self.is_exists('img/dixiacheng.jpg', at=(837, 92, 915, 140)):
                self.lock_no_img('img/dixiacheng.jpg', elseclick=(900, 138), elsedelay=1, retry=10)
                self.click(1, 1)
                # 防止一进去就是塔币教程
                # self.dxc_kkr()
                break
        tmp_cout = 0
        while tmp_cout <= 2:
            try:
                time.sleep(8)
                if self.is_exists('img/chetui.jpg'):
                    dixiacheng_floor = self.baidu_ocr(200, 410, 263, 458)
                    # print(dixiacheng_floor)
                    dixiacheng_floor = int(dixiacheng_floor['words_result'][0]['words'].split('/')[0])
                    time.sleep(2)
                    dixiacheng_floor_times = self.baidu_ocr(668, 421, 697, 445)
                    # print(dixiacheng_floor_times)
                    dixiacheng_floor_times = int(dixiacheng_floor_times['words_result'][0]['words'].split('/')[0])
                    tmp_cout = tmp_cout + 1
                    dixiacheng_times = dixiacheng_floor_times
                    # print(dixiacheng_floor, ' ', dixiacheng_floor_times)
                    if dixiacheng_floor > 1 and dixiacheng_floor_times <= 1:
                        pcr_log(self.account).write_log(level='info', message='%s 已经打过地下城，执行撤退' % self.account)
                        if self.is_exists('img/chetui.jpg'):
                            self.click(808, 435, pre_delay=1)
                            self.click(588, 371, pre_delay=2)
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
        while tmp_cout <= 2 and self.dxc_switch == 1:
            try:
                self.click(1, 1, post_delay=2)
                if self.is_exists('img/yunhai.bmp'):
                    time.sleep(2)
                    dixiacheng_times = self.baidu_ocr(868, 419, 928, 459)
                    dixiacheng_times = int(dixiacheng_times['words_result'][0]['words'].split('/')[0])
                    if dixiacheng_times <= 1:
                        break
                    tmp_cout = tmp_cout + 1
            except Exception as result:
                pcr_log(self.account).write_log(level='warning', message='2-检测出异常{},重试'.format(result))
                tmp_cout = tmp_cout + 1
        # 下面这段因为调试而注释了，实际使用时要加上
        while self.dxc_switch == 1:
            # print(dixiacheng_times, ' ', dixiacheng_floor_times)
            if dixiacheng_times == -1 and dixiacheng_floor_times == -1:
                pcr_log(self.account).write_log(level='warning', message='地下城次数为非法值！')
                pcr_log(self.account).write_log(level='warning', message='OCR无法识别！即将调用 非OCR版本地下城函数！\r\n')
                self.dixiacheng(skip)
                return False
            try:
                if self.is_exists('img/yunhai.bmp') and dixiacheng_times == 1:
                    self.dxc_switch = 0
                    # 识别到后满足条件，开锁
                    self.click(233, 311, post_delay=1)
                elif self.is_exists('img/yunhai.bmp') and dixiacheng_times == 0:
                    self.dxc_switch = 1
                    pcr_log(self.account).write_log(level='info', message='%s今天已经打过地下城' % self.account)
                    return False
                if self.dxc_switch == 0:
                    # 不加可能会导致卡顿找不到图片
                    self.lock_img('img/ok.bmp')
                    self.lock_no_img('img/ok.bmp', elseclick=[(592, 369)])  # 锁定OK
                else:
                    pcr_log(self.account).write_log(level='info', message='>>>今天无次数')
                    # LOG().Account_undergroundcity(self.account)
                    self.dxc_switch = 1
                    return False
                self.d.click(1, 1)
                # 这里防止卡可可萝
            except Exception as error:
                pcr_log(self.account).write_log(level='warning', message='3-检测出异常{}'.format(error))
                pcr_log(self.account).write_log(level='warning', message='OCR无法识别！即将调用 非OCR版本地下城函数！')
                self.dixiacheng(skip)
                return False
            try:
                if self.is_exists('img/chetui.jpg') and dixiacheng_times <= 1:
                    # print('>>>', dixiacheng_times)
                    break
            except:
                pcr_log(self.account).write_log(level='warning', message='地下城次数为非法值！')
                pcr_log(self.account).write_log(level='warning', message='OCR无法识别！即将调用 非OCR版本地下城函数！\r\n')
                self.dixiacheng(skip)
                return False

        while self.dxc_switch == 0:
            # 防止一进去就是塔币教程
            # self.dxc_kkr()
            while True:
                time.sleep(0.5)
                if self.is_exists('img/chetui.jpg'):
                    self.lock_img('img/tiaozhan.bmp', ifclick=[(833, 456)], elseclick=[(667, 360), (667, 330)])
                    # 锁定挑战和第一层
                    break
            while True:
                time.sleep(0.5)
                if self.is_exists('img/zhiyuan.jpg', at=(448, 78, 512, 102)):
                    time.sleep(1)
                    # self.click(100, 173)  # 第一个人
                    screen_shot = self.getscreen()
                    self.click_img(screen_shot, 'img/zhiyuan.jpg', pre_delay=2)
                    break

            if self.is_exists('img/dengjixianzhi.jpg', at=(45, 144, 163, 252)):
                self.click(213, 208, post_delay=1)  # 如果等级不足，就支援的第二个人
                # self.click(100, 173, post_delay=1)  # 支援的第一个人
            else:
                time.sleep(0.8)
                self.click(100, 173, post_delay=1)  # 支援的第一个人
                self.click(213, 208)  # 以防万一
            time.sleep(2)
            if self.is_exists('img/notzhandoukaishi.bmp', threshold=0.97):
                # 逻辑顺序改变
                # 当无法选支援一二位时，将会退出地下城
                pcr_log(self.account).write_log(level='info', message="%s无法出击!" % self.account)
                break
            else:
                self.click(98, 88, post_delay=1)  # 全部
                self.click(100, 173, post_delay=1)  # 第一个人
                self.click(833, 470)  # 战斗开始
            while True:
                if self.is_exists('img/notzhandoukaishi.bmp', threshold=0.97):
                    # 逻辑顺序改变
                    # 当无法选支援一二位时，将会退出地下城
                    pcr_log(self.account).write_log(level='info', message="%s无法出击!" % self.account)
                    break
                self.lock_img('img/ok.bmp', ifclick=[(588, 480)], elseclick=[(833, 470)], ifbefore=2, ifdelay=1)
                break

            if skip:  # 直接放弃战斗
                self.lock_img('img/caidan.jpg', ifclick=[(902, 33)], ifbefore=2, ifdelay=1)
                self.lock_img('img/fangqi.jpg', ifclick=[(625, 376)], ifbefore=2, ifdelay=3)
                self.lock_img('img/fangqi_2.bmp', ifclick=[(625, 376)], ifbefore=2, ifdelay=1)
                time.sleep(3)
                # 这里防一波打得太快导致来不及放弃
                if self.is_exists('img/shanghaibaogao.jpg') and self.is_exists('img/xiayibu.jpg'):
                    self.lock_no_img('img/xiayibu.jpg', elseclick=[(870, 503)])
                    break
                elif self.is_exists('img/shanghaibaogao.jpg') and self.is_exists('img/qianwangdixiacheng.jpg'):
                    self.lock_no_img('img/qianwangdixiacheng.jpg', elseclick=[(870, 503)])
                    break
            else:
                self.lock_img('img/auto_1.jpg', elseclick=[(914, 425)], retry=6)
                self.lock_img('img/kuaijin_3.bmp', elseclick=[(913, 494)], retry=6)
            while skip is False:  # 结束战斗返回
                time.sleep(1)
                if self.is_exists('img/shanghaibaogao.jpg') and self.is_exists('img/xiayibu.jpg'):
                    self.lock_no_img('img/xiayibu.jpg', elseclick=[(870, 503)])
                    break
                elif self.is_exists('img/shanghaibaogao.jpg') and self.is_exists('img/qianwangdixiacheng.jpg'):
                    self.lock_no_img('img/qianwangdixiacheng.jpg', elseclick=[(870, 503)])
                    break
                else:
                    if self.is_exists('img/chetui.jpg'):
                        break

            self.click(1, 1, pre_delay=1)  # 取消显示结算动画
            while True:  # 撤退地下城
                time.sleep(0.5)
                self.click(1, 1, pre_delay=1)  # 取消显示结算动画
                if self.is_exists('img/chetui.jpg'):
                    self.lock_img('img/ok.bmp', ifclick=[(588, 371)], elseclick=[(808, 435)], retry=20)
                    break
            # 执行完后再检测一轮后跳出大循环
            self.lock_no_img('img/chetui.jpg', elseclick=[(808, 435), (588, 371)], retry=20)
            self.lock_img('img/yunhai.bmp')
            break
        while True:  # 首页锁定
            if self.is_exists('img/liwu.bmp', at=(891, 413, 930, 452)):
                break
            self.click(131, 533, post_delay=1)  # 保证回到首页
            # 防卡死
            screen_shot_ = self.getscreen()
            # click_img 暂且无法传入list
            self.guochang(screen_shot_, ['img/xiayibu.jpg', 'img/qianwangdixiacheng.jpg'])
            screen_shot = self.getscreen()
            self.click_img(screen_shot, 'img/chetui.jpg')
            time.sleep(2)
            screen_shot = self.getscreen()
            self.click_img(screen_shot, 'img/ok.bmp')

    def dixiacheng(self, skip):
        """
        地下城函数于2020/7/14日修改
        By:Dr-Bluemond
        有任何问题 bug请反馈
        :param skip:
        :return:
        """
        # 首页 -> 地下城选章/（新号）地下城章内
        self.lock_img('img/dixiacheng.jpg', elseclick=[(480, 505)], elsedelay=0.5, at=(837, 92, 915, 140))  # 进入地下城
        self.lock_no_img('img/dixiacheng.jpg', elseclick=[(900, 138)], elsedelay=0.5, alldelay=5,
                         at=(837, 92, 915, 140))

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

        ok = self.lock_img('img/ok.bmp', elseclick=[(298, 213)], elsedelay=0.5, ifclick=[(596, 371)], ifbefore=1,
                           ifdelay=0, retry=3, at=(495, 353, 687, 388))
        if not ok:
            pcr_log(self.account).write_log(level='error', message="%s未能成功进入云海的山脉，跳过刷地下城" % self.account)
            self.lock_img('img/liwu.bmp', elseclick=[(131, 533)], at=(891, 413, 930, 452))
            return

        while True:
            # 锁定挑战和第一层
            self.lock_img('img/tiaozhan.bmp', elseclick=[(667, 360)], ifclick=[(833, 456)], at=(759, 428, 921, 483))
            time.sleep(2)
            self.click(480, 88)
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
                ok = self.lock_img('img/fangqi.jpg', elseclick=[(902, 33)], elsedelay=0.5, ifclick=[(625, 376)],
                                   ifbefore=0, ifdelay=0, retry=7, at=(567, 351, 686, 392))
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
                    self.click(250, 250)  # 云海
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

    def shuatuDD(self, dxc_id: int, mode: int, stop_criteria: int = 0, after_stop: int = 0, teams=None):  # 刷地下城
        """
        2020-07-29 Add By TheAutumnOfRice

        统一刷地下城函数，全Auto通关地下城
        三倍速通关！

        :param dxc_id: 地下城的ID
        :param mode: 模式
            mode 0：不打Boss，用队伍1只打小关
            mode 1：打Boss，用队伍1打小关，用队伍[1,2,3,4,5...]打Boss
            mode 2：打Boss，用队伍1打小关，用队伍[2,3,4,5...]打Boss
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
            若为"zhanli"，则按照战力排序，选择前五战力为当前队伍
            若为“a-b",其中a为1~5的整数，b为1~3的整数，则选择编组a队伍b。
        """
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
            # 人力OCR失败，一个一个尝试点击
            cur_layer = 1
        max_layer = max(DXC_NUM[dxc_id])
        set_bianzu, set_duiwu = parse_team_str(teams[0])
        if stop_criteria == 0:
            min_live = 5
        else:
            min_live = 1
        while cur_layer <= max_layer - 1:
            # 刷小怪
            cur_x, cur_y = DXC_COORD[dxc_id][cur_layer]
            state = self.dxczuobiao(cur_x, cur_y, 1, 2, set_bianzu, set_duiwu, min_live)
            set_bianzu = 0
            set_duiwu = 0
            if state == 0:
                # 伤亡惨重
                self.log.write_log("info", "在地下城伤亡惨重！")
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
