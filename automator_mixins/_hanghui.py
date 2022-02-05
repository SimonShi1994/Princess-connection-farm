import time

from core.constant import MAIN_BTN, HANGHUI_BTN, PCRelement, TUANDUIZHAN_BTN, DXC_ELEMENT
from core.constant import USER_DEFAULT_DICT as UDD
from core.cv import UIMatcher
from core.log_handler import pcr_log
from core.safe_u2 import timeout
from core.utils import diffday
from automator_mixins._tools import ToolsMixin


class HanghuiMixin(ToolsMixin):
    """
    行会插片。
    包含行会相关的脚本。
    """

    @timeout(300, "行会捐赠用时过长，可能卡住！")
    def hanghui(self, once_times):
        """
        行会自动捐赠装备
        2020/8/6 By:CyiceK 检查完毕
        """
        self.lock_home()
        # self.find_img('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=self.change_time,
        #               at=(891, 413, 930, 452))  # 回首页
        # self.d.click(693, 436)
        self.find_img('img/hanghui.bmp', elseclick=[(693, 436)], elsedelay=2)  # 锁定进入行会
        self.lock_no_img('img/zhandou_ok.jpg', elseclick=[(239, 351)], retry=5, side_check=self.juqing_kkr)
        while True:  # 6-17修改：减少opencv使用量提高稳定性
            if self.is_exists('img/zhiyuansheding.bmp'):
                time.sleep(3)  # 加载行会聊天界面会有延迟
                self.lock_no_img('img/juanzengqingqiu.jpg', elseclick=[(367, 39)], retry=1)
                for _ in range(once_times):
                    time.sleep(0.8)
                    if self.is_exists('img/juanzeng.jpg', threshold=0.865):
                        screen_shot = self.getscreen()
                        self.click_img(screen_shot, 'img/juanzeng.jpg')
                        # 点击max 后 ok
                        time.sleep(2)
                        self.lock_no_img('img/max.jpg', elseclick=[(644, 385), (552, 470)], elsedelay=self.change_time,
                                         retry=20)
                        time.sleep(0.8)
                        if self.is_exists('img/ok.bmp', threshold=0.90):
                            self.lock_no_img('img/ok.bmp', elseclick=[(494, 368)], retry=4)
                        self.lock_no_img('img/zhandou_ok.jpg', elseclick=[(536, 361)], retry=3)
                        self.lock_no_img('img/juanzengqingqiu.jpg', elseclick=[(367, 39)], retry=1)
                    else:
                        self.lock_no_img('img/juanzengqingqiu.jpg', elseclick=[(367, 39)], elsedelay=self.change_time,
                                         retry=1)
                while True:
                    self.click(1, 1, post_delay=self.change_time)
                    # 防止ok卡住了
                    if self.is_exists('img/ok.bmp', threshold=0.90):
                        self.lock_no_img('img/ok.bmp', elseclick=[(494, 368)], retry=4)
                    if self.is_exists('img/zhiyuansheding.bmp'):
                        break
                break
            time.sleep(2)
            # 处理多开捐赠失败的情况
            screen_shot = self.getscreen()
            self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
            self.click(1, 1, post_delay=self.change_time)  # 处理被点赞的情况

        # self.click(100, 505, post_delay=self.change_time)  # 回到首页
        self.lock_home()
        # self.find_img('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=self.change_time,
        #               at=(891, 413, 930, 452))  # 回首页

    def tichuhanghui(self):  # 踢出行会
        self.lock_home()
        # 进入
        self.click_btn(MAIN_BTN["hanghui"], elsedelay=1, until_appear=HANGHUI_BTN["hanghui_title"])
        # 管理界面
        self.click_btn(HANGHUI_BTN["chengyuanxinxi"], elsedelay=1,
                       until_appear=HANGHUI_BTN["shaixuantiaojian_chengyuan"])
        # 筛选全角色战力
        self.click_btn(HANGHUI_BTN["shaixuantiaojian_chengyuan"], elsedelay=1, until_appear=HANGHUI_BTN["fenlei"])
        self.click_btn(HANGHUI_BTN["zhanli_chengyuan"], elsedelay=1, until_appear=HANGHUI_BTN["zhanli_chengyuan"])
        self.click_btn(HANGHUI_BTN["hanghui_ok"], elsedelay=1)
        # 降序排列
        self.lock_img(HANGHUI_BTN["jiangxu_chengyuan"], elseclick=HANGHUI_BTN["jiangxu_chengyuan"])
        # 踢出第一
        self.click_btn(HANGHUI_BTN["chengyuanguanli_first"], elsedelay=1, until_appear=HANGHUI_BTN["kaichu"])
        self.click_btn(HANGHUI_BTN["kaichu"], elsedelay=1, until_appear=HANGHUI_BTN["hanghui_ok"])
        self.click_btn(HANGHUI_BTN["hanghui_ok"])
        # 返回
        self.lock_home()

    def yaoqinghanghui(self, inviteUID):  # 邀请行会
        self.click(693, 430)  # 点击行会
        self.lock_img('img/zhiyuansheding.bmp', elseclick=[(1, 1)], alldelay=0.5)  # 锁定行会界面
        self.click(241, 350)  # 点击成员
        self.lock_img('img/chengyuanliebiao.bmp', ifclick=[(717, 33)], ifdelay=1)  # 点击搜索成员
        self.lock_img('img/sousuochengyuan.bmp', ifclick=[(845, 90)], ifdelay=1)  # 点击搜索设定
        self.lock_img('img/ok.bmp', ifclick=[(487, 236)], ifdelay=1)  # 点击输入框
        self.d.send_keys(inviteUID)
        time.sleep(1)
        self.click(1, 1)
        self.lock_img('img/ok.bmp', ifclick=[(585, 366)], ifdelay=1)  # 点击ok
        self.lock_img('img/sousuochengyuan.bmp', ifclick=[(844, 181)], ifdelay=1)  # 点击邀请
        self.lock_img('img/ok.bmp', ifclick=[(588, 439)], ifdelay=1)  # 点击ok
        self.lock_img('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=0.5, at=(891, 413, 930, 452))  # 回首页

    def jieshouhanghui(self):
        self.click(693, 430)  # 点击行会
        self.lock_img('img/zujianhanghui.bmp', elseclick=[(1, 1)], alldelay=0.5)  # 锁定行会界面
        self.click(687, 35)  # 点击邀请列表
        time.sleep(1)
        self.click(704, 170)  # 点击邀请列表
        self.lock_img('img/jiaru.bmp', ifclick=[(839, 443)], ifdelay=1)  # 点击加入
        self.lock_img('img/ok.bmp', ifclick=[(597, 372)], ifdelay=1)  # 点击ok
        time.sleep(1)
        self.lock_img('img/ok.jpg')  # 锁定ok
        screen_shot_ = self.getscreen()
        self.guochang(screen_shot_, ['img/ok.jpg'], suiji=0)
        self.lock_img('img/zhiyuansheding.bmp', ifclick=[(85, 350)], alldelay=0.5)  # 点击支援设定
        self.lock_img('img/zhiyuanjiemian.bmp', elseclick=[(1, 1)], alldelay=0.5)  # 锁定支援界面
        self.click(109, 234)  # 点击支援
        time.sleep(1)
        self.lock_img('img/quxiao3.bmp', ifclick=[(739, 91)], ifdelay=1)  # 点击排序设定
        self.lock_img('img/ok.bmp', ifclick=[(291, 142), (588, 483)], ifdelay=1)  # 点击战力和ok
        self.lock_img('img/quxiao3.bmp', ifclick=[(109, 175)], ifdelay=1)  # 点击第一个人
        time.sleep(1)
        self.click(833, 456)  # 点击设定
        self.lock_img('img/ok.bmp', ifclick=[(591, 440)], ifdelay=1)  # 点击ok

        self.lock_img('img/zhiyuanjiemian.bmp', ifclick=[(105, 356)], ifdelay=1)  # 点击第二个+号
        self.lock_img('img/quxiao3.bmp', ifclick=[(109, 175)], ifdelay=1)  # 点击第一个人
        time.sleep(1)
        self.click(833, 456)  # 点击设定
        self.lock_img('img/ok.bmp', ifclick=[(591, 440)], ifdelay=1)  # 点击ok
        self.lock_img('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=0.5, at=(891, 413, 930, 452))  # 回首页

    def joinhanghui(self, clubname):  # 小号加入行会
        # 应该废弃了
        self.log.write_log('waring',"此功能或许已经废弃，转另一个版本")
        self.log.write_log('info','>>>>>>>即将加入公会名为：', clubname, '<<<<<<<')
        self.click(693, 430)  # 点击行会
        self.lock_img('img/zujianhanghui.bmp', elseclick=[(1, 1)], alldelay=0.5)  # 锁定行会界面
        time.sleep(1)
        self.lock_img('img/zujianhanghui.bmp', elseclick=[(1, 1)], alldelay=0.5)  # 锁定行会界面
        self.click(860, 79)  # 点击设定
        self.lock_img('img/quxiao2.jpg', ifclick=[(477, 177)], ifdelay=1)  # 点击输入框
        self.d.send_keys(clubname)
        time.sleep(1)
        self.click(1, 1)
        time.sleep(1)
        self.click(587, 432)
        time.sleep(5)
        self.click(720, 172)
        time.sleep(1)
        self.lock_img('img/jiaru.bmp', ifclick=[(839, 443)], ifdelay=1)  # 点击加入
        self.lock_img('img/ok.jpg', ifclick=[(597, 372)], ifdelay=1)  # 点击ok
        self.lock_img('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=0.5, at=(891, 413, 930, 452))  # 回首页

    def join_hanghui(self, clubname):
        # 2021-8-11 CyiceK修了点bug
        self.log.write_log('info','>>>>>>>即将加入公会名为：' + clubname + '<<<<<<<')
        self.lock_home()
        # 进入
        self.click_btn(MAIN_BTN["hanghui"])
        while True:
            if self.is_exists(HANGHUI_BTN["zujianhanghui"]):
                break
            if self.is_exists(HANGHUI_BTN["chengyuanxinxi"]):
                self.log.write_log('info',"已加入行会")
                return
            self.fclick(689, 460)
            time.sleep(0.5)
        # 过剧情
        self.lock_img(img=HANGHUI_BTN["zujianhanghui"], side_check=self.juqing_kkr)
        # 点击设定
        self.click_btn(HANGHUI_BTN["sheding_join"], elsedelay=1, until_appear=HANGHUI_BTN["input_join"])
        time.sleep(1)
        while True:
            # 点搜索文本框
            self.click_btn(HANGHUI_BTN["input_join"], until_disappear=None)
            time.sleep(1)
            self.d.send_keys(clubname)
            time.sleep(1)
            self.fclick(470, 80)
            # 此处必须为0.99
            time.sleep(1)
            if self.is_exists(HANGHUI_BTN["sousuo_join"], threshold=0.98, method="sq"):
                # 搜索按钮点亮，点击搜索
                self.click_btn(HANGHUI_BTN["sousuo_join"], elsedelay=1)
                break
        # 进入行会
        self.click_btn(HANGHUI_BTN["in_join"], until_appear=HANGHUI_BTN["join_btn"], elsedelay=1)
        # 点击加入 加入行会！不是申请加入！
        self.click_btn(HANGHUI_BTN["join_btn"], until_appear=HANGHUI_BTN["hanghui_ok"], elsedelay=1)
        # 确认
        self.click_btn(HANGHUI_BTN["hanghui_ok"], elsedelay=1)
        self.lock_home()

    def zhiyuan(self, zhiyuanjieshu=False):
        # Add: By TheAutumnOfRice 考虑了无法撤下支援的情况
        """
        :param zhiyuanjieshu: 是否尝试点击”支援结束“按钮
        """
        self.lock_home()
        # 进入
        self.click_btn(MAIN_BTN["hanghui"], until_appear=HANGHUI_BTN["zhiyuansheding"])
        # 设置支援
        self.click_btn(HANGHUI_BTN["zhiyuansheding"])

        def zhiyuansheding():
            # 战力排列
            if self.is_exists(HANGHUI_BTN["zhanlipaixu"]) is False:
                self.click_btn(HANGHUI_BTN["shaixuantiaojian_juese"])
                self.click_btn(HANGHUI_BTN["zhanli_juese"], until_appear=HANGHUI_BTN["zhanli_juese"])
                self.click_btn(HANGHUI_BTN["hanghui_ok_juese"])
            # 降序排列
            self.lock_img(HANGHUI_BTN["jiangxu_juese"], elseclick=HANGHUI_BTN["jiangxu_juese"])
            while 1:
                self.click(HANGHUI_BTN["juese2"], post_delay=0.5)
                self.click(HANGHUI_BTN["juese1"], post_delay=0.5)
                # 此处必须为0.99
                if self.is_exists(HANGHUI_BTN["juesesheding"], threshold=0.99):
                    self.click_btn(HANGHUI_BTN["juesesheding"], until_appear=HANGHUI_BTN["hanghui_ok_double"])
                    self.click_btn(HANGHUI_BTN["hanghui_ok_double"])
                    break
                # 支援1

        def shouqubaochou():
            self.click_btn(HANGHUI_BTN["zyjsqr_ok"], until_appear=HANGHUI_BTN["sqbc"])
            for _ in range(5):
                self.click(40, 82)

        if zhiyuanjieshu:
            if self.click_btn(HANGHUI_BTN["zyjs_1"], until_appear=HANGHUI_BTN["zyjsqr"], elsedelay=3, retry=3,
                              is_raise=False):
                shouqubaochou()

            if self.click_btn(HANGHUI_BTN["zyjs_2"], until_appear=HANGHUI_BTN["zyjsqr"], elsedelay=3, retry=3,
                              is_raise=False):
                shouqubaochou()
        if self.click_btn(HANGHUI_BTN["zhiyuan_dxc1"], until_appear=HANGHUI_BTN["zhiyuanquxiao"], elsedelay=1,
                          timeout=6, is_raise=False):
            zhiyuansheding()
        # 支援2
        if self.click_btn(HANGHUI_BTN["zhiyuan_dxc2"], until_appear=HANGHUI_BTN["zhiyuanquxiao"], elsedelay=1,
                          timeout=6, is_raise=False):
            zhiyuansheding()
        self.lock_home()

    def dianzan(self, sortflag=0):
        """
        2020/8/6 By:CyiceK 检查完毕
        2020/8/18 TheAutumnOfRice：加了一点点at。
            ↑@CyiceK真的，加了at之后的运算速度飞升，不能为了图方便而不加at的。
        :param sortflag:
        :return:
        """
        # 行会点赞
        # 一天只能点一次
        ts = self.AR.get("time_status", UDD["time_status"])
        cur = time.time()
        if not diffday(cur, ts["dianzan"]):
            self.log.write_log("info", "今日已经点过赞！")
            return
        self.lock_home()
        # 进入行会
        out = self.lock_img(PCRelement(img='img/zhiyuansheding.bmp', at=(16, 338, 159, 380)),
                            ifclick=[(230, 351), (1, 1)],
                            elseclick=[(1, 1), (688, 432)],
                            elsedelay=8, retry=6, is_raise=False)
        if not out:
            self.log.write_log("error", "无法进入行会")
            self.lock_home()
            return
        self.lock_no_img('img/zhandou_ok.jpg', elseclick=[(239, 351)], retry=5)
        self.click_btn(HANGHUI_BTN["chengyuanxinxi"], elsedelay=5, timeout=20)
        if sortflag == 1:
            self.lock_img('img/queren.jpg', elseclick=[(720, 97)], retry=3)  # 点击排序
            self.lock_no_img('img/queren.jpg', elseclick=[(289, 303), (587, 372)],
                             elsedelay=self.change_time, retry=3)  # 按战力降序 这里可以加一步调降序
            if self.is_exists('img/dianzan.bmp'):
                click_list = [(826, 198), (826, 316), (826, 428)]
                for i in click_list:
                    if self.lock_img('img/dianzan.bmp', ifclick=[i], elseclick=[(480, 374)], retry=10):
                        if self.lock_img('img/queren.jpg', retry=8):
                            self.lock_no_img('img/queren.jpg', elseclick=[(480, 374)], retry=10)
                            continue
                        else:
                            self.log.write_log("warning", "已经没有点赞次数了")
                            self.lock_home()
                            break
                    else:
                        self.log.write_log("error", "找不到点赞按钮")
                        self.lock_home()
                        break

            # 点赞 战力降序第一/第二/第三个人
            # (480, 374) 是ok的坐标
        else:
            if self.is_exists('img/dianzan.bmp'):
                click_list = [(818, 198), (826, 316), (826, 428)]
                for i in click_list:
                    if self.lock_img('img/dianzan.bmp', ifclick=[i], elseclick=[(480, 374)], retry=10):
                        if self.lock_img('img/queren.jpg', retry=8):
                            self.lock_no_img('img/queren.jpg', elseclick=[(480, 374)], retry=10)
                            continue
                        else:
                            self.log.write_log("warning", "已经没有点赞次数了")
                            self.lock_home()
                            break
                    else:
                        self.log.write_log("error", "找不到点赞按钮")
                        self.lock_home()
                        break
            # 点赞 职务降序（默认） 第二/第三个人，副会长
        self.click(479, 381)
        screen_shot_ = self.getscreen()
        self.click_img(screen_shot_, 'img/queren.jpg')
        # 保存点赞时间
        ts["dianzan"] = time.time()
        self.AR.set("time_status", ts)
        # self.lock_img('img/liwu.bmp', elseclick=[(131, 533), (1, 1), (480, 374)], elsedelay=self.change_time,
        #               at=(891, 413, 930, 452))  # 回首页
        self.lock_home()

    def faqijuanzeng(self, equip_img: str, wait_time: int = 300):
        """
        发起装备捐赠。
        :param equip_img: 装备图片路径
        :param wait_time: 等待时间（如果上次已经使用faqijuanzeng捐赠但是还没有过8小时零1分钟，
            若等待时间不超过wait_time秒则等待，否则跳过该任务
        :return:
        """

        def get_equ_at(r, c):
            EQU_X = [53, 160, 268, 377, 484]
            EQU_Y = [128, 236, 345]
            EQU_A = 93
            return (EQU_X[c], EQU_Y[r], EQU_X[c] + EQU_A, EQU_Y[r] + EQU_A)

        def check_current():
            sc = self.getscreen()
            for r in range(3):
                for c in range(5):
                    at = get_equ_at(r, c)
                    # print(at)
                    if self.is_exists(img=equip_img, at=at, screen=sc):
                        return (at[0] + 37, at[1] + 37)
            return None

        def dragdown():
            obj = self.d.touch.down(55, 347)
            time.sleep(0.1)
            obj.move(55, 130.5)
            time.sleep(0.8)
            sc = self.getscreen()
            r1c0 = UIMatcher.img_cut(sc, get_equ_at(1, 0))
            flag = False
            if r1c0.std() < 15:
                # 拖到底了
                flag = True
            obj.up(55, 130)
            time.sleep(1)
            return flag

        def get_equ_xy():
            while True:
                c = check_current()
                if c is not None:
                    return PCRelement(*c)
                if dragdown():
                    return None

        def sort_down():
            if not self.is_exists(HANGHUI_BTN["sort_down"]):
                self.click_btn(HANGHUI_BTN["sort_down"], until_appear=HANGHUI_BTN["sort_down"])

        def sort_xiyou():
            if not self.is_exists(HANGHUI_BTN["sort_xiyou"]):
                self.click_btn(HANGHUI_BTN["sort_xiyou"], until_appear=HANGHUI_BTN["sort_ok"])
                self.click(291, 305, post_delay=0.8)
                self.click_btn(HANGHUI_BTN["sort_ok"])

        def get_last_record():
            ts = self.AR.get("time_status", UDD["time_status"])
            return ts["juanzeng"]

        def set_last_record():
            ts = self.AR.get("time_status", UDD["time_status"])
            ts["juanzeng"] = time.time()
            self.AR.set("time_status", ts)

        tm = get_last_record()
        min_time = 8 * 3600 + 60
        diff = time.time() - tm
        if diff < min_time:
            wait = min_time - diff
            if wait <= wait_time:
                self.log.write_log("info", f"离下次捐赠还有{int(wait)}秒，进入等待。")
                time.sleep(wait)
                self.log.write_log("info", "脚本继续执行。")
            else:
                self.log.write_log("warning", f"离下次捐赠还有{int(wait)}秒，跳过该脚本。")
                return

        self.lock_home()
        # 进入
        self.click_btn(MAIN_BTN["hanghui"], until_appear=HANGHUI_BTN["zhiyuansheding"])
        # 请求捐赠装备
        if self.is_exists(HANGHUI_BTN["jzqqqk"], screen=self.last_screen):
            # 不敢确定是不是捐赠结束后还会出现“捐赠请求情况”。
            self.click_btn(HANGHUI_BTN["jzqqqk"])
            for _ in range(5):
                self.click(16, 92)
            if self.is_exists(HANGHUI_BTN["jzqqqk"]):
                self.log.write_log("warning", "捐赠失败，可能上次捐赠请求仍未结束")
                self.lock_home()
                return

        if self.is_exists(HANGHUI_BTN["jzqqjg"], screen=self.last_screen):
            self.click_btn(HANGHUI_BTN["jzqqjg"])
            for _ in range(5):
                self.click(16, 92)

        if not self.click_btn(HANGHUI_BTN["qqjzzb"], until_appear=HANGHUI_BTN["fqjzqq"], is_raise=False):
            self.log.write_log("warning", "捐赠失败，可能捐赠仍在冷却")
            self.lock_home()
            return

        sort_down()
        sort_xiyou()
        btn = get_equ_xy()
        if btn is None:
            self.log.write_log("error", "没有找到要捐赠的装备！")
        else:
            self.click(btn, post_delay=1)
            self.click_btn(HANGHUI_BTN["fqjzqq"], until_appear=HANGHUI_BTN["jzqq_ok"])
            self.click_btn(HANGHUI_BTN["jzqq_ok"])
            set_last_record()
        self.lock_home()

    def tuanduizhan(self):
        """
        自动摸会战 By：CyiceK
        2021/2/5
        :return:
        """
        self.lock_home()
        if not self.lock_img(img=TUANDUIZHAN_BTN["tuanduizhan"], ifclick=(875, 272),
                             elseclick=(478, 519), elsedelay=5, side_check=self.juqing_kkr, retry=3):
            pcr_log(self.account).write_log("info", f"{self.account}该用户未解锁行会战哦")
            return
        while True:
            if self.lock_img(img=TUANDUIZHAN_BTN["taofaxinxi"], elsedelay=2, elseclick=(1, 1),
                             side_check=self.juqing_kkr):
                time.sleep(5 + self.change_time)
                try:
                    self.lock_img(img=TUANDUIZHAN_BTN["taofaxinxi"], elsedelay=2, elseclick=(1, 1),
                                  side_check=self.juqing_kkr)
                    screen = self.getscreen()
                    r_list = self.img_where_all(img=TUANDUIZHAN_BTN["shangbiao"], screen=screen)
                    if self.lock_img(img=TUANDUIZHAN_BTN["tiaozhan"], elseclick=(int(r_list[0]), int(r_list[1])),
                                     side_check=self.juqing_kkr, retry=5):
                        if self.is_exists(TUANDUIZHAN_BTN["tiaozhan"]):
                            break
                    else:
                        # if看看是不是延迟太高导致的
                        if not self.is_exists(img=TUANDUIZHAN_BTN["tiaozhan"]):
                            self.click(1, 1)
                except Exception as e:
                    pcr_log(self.account).write_log("info", f"识别不到boss信息，已退出本任务")
                    return
            else:
                continue

        def tiaozhan() -> bool:
            # 非主流写法，内部方法
            while True:
                self.lock_img(TUANDUIZHAN_BTN["tiaozhan"], ifclick=[(833, 462)], side_check=self.juqing_kkr, retry=3)
                self.lock_img(DXC_ELEMENT["sheding"], ifclick=(478, 443), retry=3)
                if self.is_exists(TUANDUIZHAN_BTN["guanbi"]):
                    self.click(TUANDUIZHAN_BTN["guanbi"])
                if self.is_exists(TUANDUIZHAN_BTN["qianwangguanqia"]):
                    # self.lock_no_img(TUANDUIZHAN_BTN["qianwangguanqia"], elseclick=(592, 436))
                    # 刷 1-1获取次数？
                    pcr_log(self.account).write_log("info", f"没有挑战次数")
                    self.lock_home()
                    return False
                if self.is_exists('img/notzhandoukaishi.bmp', at=(758, 423, 915, 473), is_black=True,
                                  black_threshold=1400):
                    # 全部
                    self.click_btn(DXC_ELEMENT["quanbu_white"], until_appear=DXC_ELEMENT["quanbu_blue"], elsedelay=0.1)
                    if not self.is_exists(DXC_ELEMENT["zhiyuan_gouxuan"]):
                        for i in range(1, 9):
                            self.click(DXC_ELEMENT["zhiyuan_dianren"][i])

                        # 点完人后确认一遍
                        if self.is_exists('img/notzhandoukaishi.bmp', at=(758, 423, 915, 473), is_black=True,
                                          black_threshold=1400):
                            pcr_log(self.account).write_log(level='info', message="%s没有合适的人物打公会战!" % self.account)
                            self.lock_home()
                            return False
                        break
                elif self.is_exists('img/dxc/zhandoukaishi.bmp', at=(758, 423, 915, 473)):
                    return True

        while True:
            # 战斗检测
            state = tiaozhan()
            if not state:
                return
            # 战斗开始
            self.click_btn(DXC_ELEMENT["zhandoukaishi"], until_disappear=DXC_ELEMENT["zhandoukaishi"], elsedelay=0.1,
                           retry=4)

            if self.lock_img(TUANDUIZHAN_BTN["zhandou"], retry=7):
                # 战斗
                self.lock_no_img(TUANDUIZHAN_BTN["zhandou"], elseclick=(587, 374))
                break
            if self.is_exists('img/caidan.jpg'):
                break
            if self.is_exists(TUANDUIZHAN_BTN["tiaozhan"]):
                tiaozhan()

        while True:
            if self.lock_img('img/caidan.jpg', elseclick=[(1, 1)], retry=3):
                self.lock_img('img/auto_1.jpg', elseclick=[(914, 425)], elsedelay=0.2, retry=3)
                self.lock_img('img/kuaijin_1.jpg', elseclick=[(913, 494)], elsedelay=0.2, retry=3)
            if self.is_exists('img/shanghaibaogao.jpg', at=(767, 18, 948, 65)) and \
                    self.is_exists('img/xiayibu.jpg', at=(694, 474, 920, 535)):
                self.lock_no_img('img/xiayibu.jpg', elseclick=[(806, 508)])
                break
        self.lock_home()
