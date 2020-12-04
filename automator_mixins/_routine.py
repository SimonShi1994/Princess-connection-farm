import time

from core.MoveRecord import movevar
from core.constant import MAIN_BTN, JIAYUAN_BTN, NIUDAN_BTN, LIWU_BTN, RENWU_BTN, FIGHT_BTN
from core.constant import USER_DEFAULT_DICT as UDD
from core.cv import UIMatcher
from core.utils import diff_6hour, diff_5_12hour, diffday
from ._shuatu_base import ShuatuBaseMixin


class RoutineMixin(ShuatuBaseMixin):
    """
    日常插片
    包含日常行动相关的脚本
    """

    def gonghuizhijia(self, auto_update=False):  # 家园领取
        # 2020-07-31 TheAutumnOfRice: 检查完毕
        # 2020-09-09 CyiceK: 添加升级
        jiaju_list = ["saodangquan", "mana", "jingyan", "tili"]
        self.lock_home()
        self.lock_img(JIAYUAN_BTN["quanbushouqu"], elseclick=MAIN_BTN["gonghuizhijia"], elsedelay=1)

        if auto_update:
            screen_shot = self.getscreen()
            if self.click_img(img="img/jiayuan/jiayuan_shengji.bmp", screen=screen_shot):
                time.sleep(10)

        self.lock_img(JIAYUAN_BTN["guanbi"], elseclick=JIAYUAN_BTN["quanbushouqu"], elsedelay=0.5,
                      side_check=self.juqing_kkr, retry=5)

        if auto_update:
            i = 0
            while i <= 3:
                screen_shot = self.getscreen()
                if self.click_img(img="img/jiayuan/jiayuan_shengji.bmp", screen=screen_shot):
                    time.sleep(10)
                # 家具坐标
                self.lock_img(JIAYUAN_BTN["xinxi"], elseclick=JIAYUAN_BTN["jiaju"][jiaju_list[i]], elsedelay=2, retry=3)
                time.sleep(2)
                if self.is_exists(JIAYUAN_BTN["jy_dengjitisheng2"], is_black=True):
                    break
                elif not self.is_exists(JIAYUAN_BTN["zhuye"]):
                    self.click_btn(JIAYUAN_BTN["jy_dengjitisheng"],
                                   until_appear=JIAYUAN_BTN["quxiao"], elsedelay=2, retry=2)
                    time.sleep(3)
                    if self.is_exists(JIAYUAN_BTN["dengjitisheng"], is_black=True, black_threshold=1300):
                        self.lock_img(JIAYUAN_BTN["zhuye"], elseclick=[(1, 1)], retry=3)
                        i = i + 1
                        continue
                    elif self.is_exists(JIAYUAN_BTN["dengjitisheng"]):
                        self.click_btn(JIAYUAN_BTN["dengjitisheng"], until_disappear=JIAYUAN_BTN["dengjitisheng"],
                                       retry=2)
                i = i + 1
                continue

        self.lock_home()

    def mianfeiniudan(self):
        # 免费扭蛋
        # 2020-07-31 TheAutumnOfRice: 检查完毕
        ts = self.AR.get("time_status", UDD["time_status"])
        if not diff_5_12hour(time.time(), ts["niudan"]):
            self.log.write_log("info", "该时间段已经抽取过免费扭蛋！")
            return
        self.lock_home()
        self.lock_img(MAIN_BTN["liwu"], ifclick=MAIN_BTN["niudan"])
        while True:
            # 跳过抽奖提示
            time.sleep(4)
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/niudan_sheding.jpg'):
                self.guochang(screen_shot_, ['img/niudan_sheding.jpg'], suiji=0)
                break
            else:
                time.sleep(1)
                self.click(473, 436)  # 手动点击
                time.sleep(2)
                break
        state = self.lock_img({NIUDAN_BTN["putong_mianfei"]: 1, NIUDAN_BTN["putong_wancheng"]: 2},
                              elseclick=NIUDAN_BTN["putong"], retry=5, is_raise=False)
        if not state:
            self.log.write_log("error", "扭蛋检测失败。")
            self.lock_home()
            return
        if state == 1:
            self.lock_img(NIUDAN_BTN["putong_quxiao"], elseclick=NIUDAN_BTN["putong_mianfei"])
            self.lock_no_img(NIUDAN_BTN["putong_quxiao"], elseclick=NIUDAN_BTN["putong_ok"])
            self.lock_no_img(NIUDAN_BTN["niudanjieguo_ok"], elseclick=NIUDAN_BTN["niudanjieguo_ok"])
            # TODO 第一次扭蛋设置
        else:
            self.log.write_log("info", "可能已经领取过免费扭蛋了")
        ts["niudan"] = time.time()
        self.AR.set("time_status", ts)
        self.lock_home()

    def mianfeishilian(self):
        # 免费十连
        # 2020/9/20 CyiceK进行了稳定性修复
        self.lock_home()
        # self.lock_img(MAIN_BTN["liwu"], ifclick=MAIN_BTN["niudan"])
        # 点进扭蛋界面

        self.click_btn(MAIN_BTN["niudan"], until_disappear=MAIN_BTN["liwu"])
        while True:
            # 跳过抽奖提示
            time.sleep(4)
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/niudan_sheding.jpg'):
                self.guochang(screen_shot_, ['img/niudan_sheding.jpg'], suiji=0)
                break
            else:
                time.sleep(1)
                self.click(473, 436)  # 手动点击
                time.sleep(2)
                break

        screen_shot_ = self.getscreen()
        if self.is_exists(screen=screen_shot_, img=NIUDAN_BTN["mianfeishilian"]):  # 仅当有免费十连时抽取免费十连
            self.click_btn(NIUDAN_BTN["niudan_shilian"], until_appear=NIUDAN_BTN["putong_quxiao"])
            self.click_btn(NIUDAN_BTN["putong_ok"], until_disappear=NIUDAN_BTN["putong_ok"])
            time.sleep(1.5)
            self.lock_img(JIAYUAN_BTN["zhuye"], elseclick=[(900, 40)])
            # self.click(872, 355)  # 点击十连
            # time.sleep(1)
            # self.click(592, 369)  # 确认

        while True:
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/liwu.bmp', at=(891, 413, 930, 452)):
                break
            # if self.is_exists(screen=screen_shot_, img=JIAYUAN_BTN["zhuye"]):
            #   self.click(131, 533)
            # 首页锁定，保证回到首页
            self.lock_home()

    def shouqu(self):  # 收取全部礼物
        # 2020-08-06 TheAutumnOfRice: 检查完毕
        self.lock_home()
        self.click_btn(MAIN_BTN["liwu"], until_appear=LIWU_BTN["shouqulvli"])
        state = self.lock_img({LIWU_BTN["ok"]: True, LIWU_BTN["meiyouliwu"]: False},
                              elseclick=LIWU_BTN["quanbushouqu"], retry=2, elsedelay=8)
        if state:
            s = self.lock_img({LIWU_BTN["ok2"]: 1, LIWU_BTN["chiyoushangxian"]: 2},
                              elseclick=LIWU_BTN["ok"], elsedelay=8)
            if s == 1:
                self.click_btn(LIWU_BTN["ok2"])
                self.lock_home()
            else:
                self.log.write_log("warning", "收取体力达到上限！")
                self.lock_home()
                return
        else:
            self.lock_home()

    def shouqurenwu(self):  # 收取任务报酬
        # 2020-08-06 TheAutumnOfRice: 检查完毕
        self.lock_home()
        self.click_btn(MAIN_BTN["renwu"], until_appear=RENWU_BTN["renwutip"])
        state = self.lock_img({RENWU_BTN["quanbushouqu"]: True, RENWU_BTN["quanbushouqu_off"]: False},
                              alldelay=1, method="sq", threshold=0.90, is_raise=False, timeout=10)
        if state:
            # 全部收取亮着
            self.click_btn(RENWU_BTN["quanbushouqu"], until_appear=RENWU_BTN["guanbi"], elsedelay=5, timeout=10,
                           is_raise=False)
        self.lock_home()

    def goumaitili(self, times, var={}, limit_today=False):  # 购买体力
        # 稳定性保证
        # 2020-07-31 TheAutumnOfRice: 检查完毕

        mv = movevar(var)
        if "cur" in var:
            self.log.write_log("info", f"断点恢复：已经购买了{var['cur']}次体力，即将购买剩余{times - var['cur']}次。")
        else:
            var.setdefault("cur", 0)
        self.lock_home()
        while var["cur"] < times:
            if self.lock_img(img="img/ui/ok_btn_1.bmp", at=(488, 346, 692, 394), elseclick=MAIN_BTN["tili_plus"],
                             elsedelay=2, retry=3):
                # 这里限制了一天只能够购买多少次体力
                try:
                    if limit_today:
                        tili_time = self.ocr_center(530, 313, 583, 338, size=1.2).split('/')
                        tili_time = int(tili_time[1]) - int(tili_time[0])
                        if tili_time >= times:
                            return False
                except:
                    pass

            state = self.lock_img(MAIN_BTN["tili_ok"], elseclick=MAIN_BTN["tili_plus"], elsedelay=2, retry=3)
            if not state:
                self.log.write_log("warning", "体力达到上限，中断体力购买")
                break

            self.lock_no_img(MAIN_BTN["tili_ok"], elseclick=MAIN_BTN["tili_ok"], elsedelay=2)
            state = self.lock_img(MAIN_BTN["tili_ok2"], retry=3)
            # TODO 宝石不够时的判断
            var["cur"] += 1
            mv.save()
            self.lock_no_img(MAIN_BTN["tili_ok2"], elseclick=MAIN_BTN["tili_ok2"], elsedelay=1)
        del var["cur"]
        mv.save()

    def goumaimana(self, times, mode=1, var={}, limit_today=False):
        # mode 1: 购买times次10连
        # mode 0：购买times次1连

        self.lock_home()
        self.lock_img(MAIN_BTN["mana_title"], elseclick=MAIN_BTN["mana_plus"])

        # 这里限制了一天只能购买mana多少次，通过OCR判断
        try:
            if limit_today:
                time.sleep(0.5)
                self.lock_img(MAIN_BTN["mana_title"], elseclick=MAIN_BTN["mana_plus"])
                mana_time = self.ocr_center(422, 451, 480, 471, size=2.0).split('/')
                mana_time = int(mana_time[0])
                if mana_time >= times:
                    return False
        except:
            pass

        def BuyOne():
            self.lock_img(MAIN_BTN["mana_ok"], elseclick=MAIN_BTN["mana_one"])
            self.lock_no_img(MAIN_BTN["mana_ok"], elseclick=MAIN_BTN["mana_ok"])
            time.sleep(2)

        def BuyTen():
            self.lock_img(MAIN_BTN["mana_ok"], elseclick=MAIN_BTN["mana_ten"])
            self.lock_no_img(MAIN_BTN["mana_ok"], elseclick=MAIN_BTN["mana_ok"])
            time.sleep(16)

        if self.is_exists(MAIN_BTN["mana_blank"]):
            BuyOne()
        mv = movevar(var)
        if "cur" in var:
            self.log.write_log("info", f"断点恢复：已经购买了{var['cur']}次玛娜，即将购买剩余{times - var['cur']}次。")
        else:
            var.setdefault("cur", 0)
        while var["cur"] < times:
            if mode == 1:
                BuyTen()
            else:
                BuyOne()
            var["cur"] += 1
            mv.save()
        del var["cur"]
        mv.save()
        self.lock_home()

    def goumaijingyan(self):
        self.lock_home()
        self.click(617, 435)
        time.sleep(2)
        self.lock_img('img/tongchang.jpg', elseclick=[(1, 100)], elsedelay=0.5, alldelay=1)
        self.click(387, 151)
        time.sleep(0.3)
        self.click(557, 151)
        time.sleep(0.3)
        self.click(729, 151)
        time.sleep(0.3)
        self.click(900, 151)
        time.sleep(0.3)
        self.click(785, 438)
        time.sleep(1.5)
        self.click(590, 476)
        self.lock_home()

        # 买药

    def buyExp(self):
        # 进入商店
        ts = self.AR.get("time_status", UDD["time_status"])
        if not diff_6hour(time.time(), ts["buyexp"]):
            self.log.write_log("info", "该时间段内已经买过经验了！")
            return
        self.lock_home()
        count = 0
        self.click(616, 434)
        while True:
            self.click(82, 84)
            screen_shot_ = self.getscreen()
            if self.is_exists("img/exp.jpg", screen=screen_shot_) \
                    or self.is_exists("img/exp2.jpg", screen=screen_shot_) \
                    or self.is_exists("img/exp3.bmp", screen=screen_shot_):
                break
            count += 1
            time.sleep(1)
            if count > 5:
                break
        if count <= 5:
            self.click(386, 148)
            self.click(556, 148)
            self.click(729, 148)
            self.click(897, 148)
            self.click(795, 437)
            time.sleep(1)
            self.click(596, 478)
            time.sleep(1)
        ts["buyexp"] = time.time()
        self.AR.set("time_status", ts)
        self.lock_home()

    def tansuo(self, mode=0):  # 探索函数
        """
        mode 0: 刷最上面的
        mode 1: 刷次上面的
        mode 2: 第一次手动过最上面的，再刷一次次上面的
        mode 3: 第一次手动过最上面的，再刷一次最上面的
        """
        is_used = 0
        self.click(480, 505)
        time.sleep(1)
        while True:  # 锁定地下城
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
            self.click(480, 505)
            time.sleep(1)
        self.click(734, 142)  # 探索
        time.sleep(3.5)
        while True:  # 锁定凯留头（划掉）返回按钮
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/fanhui.bmp', at=(16, 12, 54, 48)):
                break
            self.click(1, 1)
            time.sleep(0.5)
        # 经验
        self.click(592, 255)  # 经验
        time.sleep(3)
        screen_shot_ = self.getscreen()
        if UIMatcher.img_where(screen_shot_, 'img/tansuo_used.jpg'):
            self.lock_img('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页
        else:
            if mode >= 2:
                self.shoushuazuobiao(704, 152, lockpic='img/fanhui.bmp', screencut=(16, 12, 54, 48))
            if mode == 0 or mode == 3:
                self.click(704, 152)  # 5级
            else:
                self.click(707, 265)  # 倒数第二
            time.sleep(1)
            while True:
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/tansuo_used2.jpg'):
                    is_used = 1
                    self.click(668, 452)  # 取消
                    break
                if UIMatcher.img_where(screen_shot_, 'img/tiaozhan.jpg'):
                    break
                time.sleep(0.5)
            if is_used == 0:
                self.d.drag(876, 329, 876, 329, 0.5)  # +号
                time.sleep(0.5)
                self.click(752, 327)  # 扫荡
                time.sleep(0.5)
                while True:
                    screen_shot_ = self.getscreen()
                    if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                        self.click(590, 363)  # ok
                        time.sleep(0.5)
                        break
            if is_used == 1:
                self.click(36, 32)  # back
                time.sleep(1)
            is_used = 0
            while True:
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/home.jpg'):
                    break
                self.click(1, 1)
                time.sleep(1)
            # mana
            self.click(802, 267)  # mana
            time.sleep(3)
            if mode >= 2:
                self.shoushuazuobiao(704, 152, lockpic='img/fanhui.bmp', screencut=(16, 12, 54, 48))
            if mode == 0 or mode == 3:
                self.click(704, 152)  # 5级
            else:
                self.click(707, 265)  # 倒数第二
            time.sleep(1.5)
            while True:
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/tansuo_used2.jpg'):
                    is_used = 1
                    self.click(668, 452)  # 取消
                    break
                if UIMatcher.img_where(screen_shot_, 'img/tiaozhan.jpg'):
                    break
                time.sleep(0.5)
            if is_used == 0:
                self.d.drag(876, 329, 876, 329, 0.5)  # +号
                time.sleep(0.5)
                self.click(752, 327)  # 扫荡
                time.sleep(0.5)
                while True:
                    screen_shot_ = self.getscreen()
                    if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                        self.click(590, 363)  # ok
                        time.sleep(0.5)
                        break
            if is_used == 1:
                self.click(36, 32)  # back
                time.sleep(1)
            is_used = 0
            while True:
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/home.jpg'):
                    break
                self.click(1, 1)
                time.sleep(1)
        # 完成战斗后
        self.lock_home()

    def tansuo_new(self, mode=0):
        """
        重写探索：刷/打最上可行的关卡
        mode=0 刷最上关卡（适合大号）
        mode=1 刷最上关卡，若无法点进则刷次上关卡（适合小号推探索图）
        mode=2 刷次上关卡，若无法点进则刷最上关卡（适合小号日常探索）
        """

        def tryfun():
            if mode == 0:
                ec = [(539, 146)]
            elif mode == 1:
                ec = [(539, 146), (541, 255)]
            else:
                ec = [(541, 255), (539, 146)]
            t = 0
            while t < 2:
                out = self.lock_img(FIGHT_BTN["xuanguan_quxiao"], elseclick=ec, elsedelay=8,
                                    is_raise=False, retry=2, elseafter=0.5)
                if out:
                    c = self.get_upperright_stars(self.last_screen)
                    if c == 3:
                        swc = self.switch
                        self.switch = 0
                        self.zhandouzuobiao(30, 30, 2, use_saodang=True, saodang_ok2=MAIN_BTN["tansuo_saodangok2"])
                        self.switch = swc
                        # 这样写非常糟糕的
                        t += 2
                    else:
                        self.log.write_log("info", "最上的关卡还没有三星通关，即将进入战斗。")
                        swc = self.switch
                        self.switch = 0
                        s = self.zhandouzuobiao(30, 30, 1, use_saodang=False, buy_tili=1)
                        self.switch = swc
                        if s == 0:
                            self.log.write_log("warning", "探索战斗失败！")
                        elif s == 1:
                            self.log.write_log("info", "探索战斗成功！")
                        else:
                            self.log.write_log("warning", f"探索战斗出现未知的错误：s={s}, info={self._zdzb_info}")
                        t += 1
                else:
                    self.log.write_log("warning", "无法进入探索！")
                    t += 2

        ts = self.AR.get("time_status", UDD["time_status"])
        if not diffday(time.time(), ts["tansuo"]):
            self.log.write_log("info", "今天已经探索过！")
            return

        self.lock_home()
        self.click_btn(MAIN_BTN["maoxian"], until_appear=MAIN_BTN["zhuxian"])
        self.click_btn(MAIN_BTN["tansuo"], until_appear=MAIN_BTN["jingyanzhiguanqia"])
        # 经验
        self.click_btn(MAIN_BTN["jingyanzhiguanqia"], until_appear=MAIN_BTN["tansuo_sytzcs"])
        if self.is_exists(MAIN_BTN["tansuo_zero"], screen=self.last_screen):
            self.log.write_log("info", "无经验挑战次数。")
        else:
            tryfun()
        self.click_btn(MAIN_BTN["tansuo_back"], until_appear=MAIN_BTN["jingyanzhiguanqia"])
        # mana
        self.click_btn(MAIN_BTN["managuanqia"], until_appear=MAIN_BTN["tansuo_sytzcs"])
        if self.is_exists(MAIN_BTN["tansuo_zero"], screen=self.last_screen):
            self.log.write_log("info", "无玛娜挑战次数。")
        else:
            tryfun()
        self.click_btn(MAIN_BTN["tansuo_back"], until_appear=MAIN_BTN["jingyanzhiguanqia"])
        ts["tansuo"] = time.time()
        self.AR.set("time_status", ts)
        self.lock_home()

    def shengji(self, mode=0, times=5, tili=False):
        """
            mode = 0 刷1+2（适合大号）
            mode = 1 只刷1（适合小号日常）
            mode = 2 只刷2（适合活动关）
        """

        def tryfun_shengji():
            def sj1():
                self.click(541, 260)
                time.sleep(3)
                self.zhandouzuobiao(30, 30, times, use_saodang=True, buy_tili=tili)
                time.sleep(0.5)

            def sj2():
                self.click(539, 146)
                time.sleep(3)
                self.zhandouzuobiao(30, 30, times, use_saodang=True, buy_tili=tili)
                time.sleep(0.5)

            if mode == 0:
                sj1()
                sj2()
            elif mode == 1:
                sj1()
            else:
                sj2()

        ts = self.AR.get("time_status", UDD["time_status"])
        if not diffday(time.time(), ts["shengji"]):
            self.log.write_log("info", "今天已经圣迹调查过了！")
            return

        if tili:
            self.start_shuatu()
        if not self.check_shuatu():
            return

        self.lock_home()
        self.click_btn(MAIN_BTN["maoxian"], elsedelay=4, until_appear=MAIN_BTN["zhuxian"])
        self.click_btn(MAIN_BTN["shengji"], elsedelay=4, until_appear=MAIN_BTN["shengjiguanqia"])
        tryfun_shengji()
        ts["shengji"] = time.time()
        self.AR.set("time_status", ts)
        self.lock_home()
