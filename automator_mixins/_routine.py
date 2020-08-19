import time

from core.MoveRecord import movevar
from core.constant import MAIN_BTN, JIAYUAN_BTN, NIUDAN_BTN, LIWU_BTN, RENWU_BTN
from core.cv import UIMatcher
from ._shuatu_base import ShuatuBaseMixin


class RoutineMixin(ShuatuBaseMixin):
    """
    日常插片
    包含日常行动相关的脚本
    """

    def init_home(self):
        # 2020-07-31 TheAutumnOfRice: 检查完毕
        while True:
            screen_shot_ = self.getscreen()
            if self.is_exists(MAIN_BTN["liwu"], screen=screen_shot_):
                break
            if self.is_exists(MAIN_BTN["tiaoguo"], screen=screen_shot_):
                self.click(893, 39, post_delay=0.5)  # 跳过
                continue
            if self.is_exists(MAIN_BTN["jingsaikaishi"], screen=screen_shot_):
                self.click(786, 308, post_delay=0.2)  # 选角色
                self.click(842, 491)  # 开始
                continue
            num_of_white, x, y = UIMatcher.find_gaoliang(screen_shot_)
            if num_of_white < 77000:
                break

            self.click(1, 1, post_delay=0.5)
            self.click(330, 270, post_delay=1)
            # 跳过特别庆典

        self.lock_home()
        time.sleep(0.5)
        # 这里防一波第二天可可萝跳脸教程
        screen_shot_ = self.getscreen()
        num_of_white, _, _ = UIMatcher.find_gaoliang(screen_shot_)
        if num_of_white < 50000:
            self.lock_img('img/renwu_1.bmp', elseclick=[(837, 433)], elsedelay=1)
            self.lock_home()
            return
        if UIMatcher.img_where(screen_shot_, 'img/kekeluo.bmp'):
            self.lock_img('img/renwu_1.bmp', elseclick=[(837, 433)], elsedelay=1)
            self.lock_home()
        time.sleep(1)
        self.lock_home()  # 追加检测

    def gonghuizhijia(self):  # 家园领取
        # 2020-07-31 TheAutumnOfRice: 检查完毕
        self.lock_home()
        self.lock_img(JIAYUAN_BTN["quanbushouqu"], elseclick=MAIN_BTN["gonghuizhijia"], elsedelay=1)
        self.lock_img(JIAYUAN_BTN["guanbi"], elseclick=JIAYUAN_BTN["quanbushouqu"], elsedelay=0.5,
                      side_check=self.juqing_kkr, retry=3)
        self.lock_home()

    def mianfeiniudan(self):
        # 免费扭蛋
        # 2020-07-31 TheAutumnOfRice: 检查完毕
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
                              elseclick=NIUDAN_BTN["putong"])
        if state == 1:
            self.lock_img(NIUDAN_BTN["putong_quxiao"], elseclick=NIUDAN_BTN["putong_mianfei"])
            self.lock_no_img(NIUDAN_BTN["putong_quxiao"], elseclick=NIUDAN_BTN["putong_ok"])
            self.lock_no_img(NIUDAN_BTN["niudanjieguo_ok"], elseclick=NIUDAN_BTN["niudanjieguo_ok"])
            # TODO 第一次扭蛋设置
        else:
            self.log.write_log("info", "可能已经领取过免费扭蛋了")
        self.lock_home()

    def mianfeishilian(self):
        # 免费十连
        self.lock_home()
        self.lock_img('img/liwu.bmp', ifclick=[(750, 510)], ifdelay=1, at=(891, 413, 930, 452))  # 点进扭蛋界面

        time.sleep(1)
        screen_shot_ = self.getscreen()
        if UIMatcher.img_where(screen_shot_, 'img/mianfeishilian.jpg'):  # 仅当有免费十连时抽取免费十连
            self.click(872, 355)  # 点击十连
            time.sleep(1)
            self.click(592, 369)  # 确认

        while True:
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/liwu.bmp', at=(891, 413, 930, 452)):
                break
            self.click(900, 40)
            time.sleep(0.5)
            self.click(100, 505)
            time.sleep(0.5)
            self.click(100, 505)
            time.sleep(1)  # 首页锁定，保证回到首页

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

    def goumaitili(self, times, var={}):  # 购买体力
        # 稳定性保证
        # 2020-07-31 TheAutumnOfRice: 检查完毕
        mv = movevar(var)
        if "cur" in var:
            self.log.write_log("info", f"断点恢复：已经购买了{var['cur']}次体力，即将购买剩余{times - var['cur']}次。")
        else:
            var.setdefault("cur", 0)
        self.lock_home()
        while var["cur"] < times:
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

    def goumaimana(self, times, mode=1, var={}):
        # mode 1: 购买times次10连
        # mode 0：购买times次1连

        self.lock_home()
        self.lock_img(MAIN_BTN["mana_title"], elseclick=MAIN_BTN["mana_plus"])

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
        self.lock_home()
        count = 0
        self.click(616, 434)
        while True:
            self.click(82, 84)
            screen_shot_ = self.getscreen()
            if self.is_exists("img/exp.jpg", screen=screen_shot_) or self.is_exists("img/exp2.jpg",
                                                                                    screen=screen_shot_):
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
