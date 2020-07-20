import time

from core.cv import UIMatcher
from ._shuatu_base import ShuatuBaseMixin


class RoutineMixin(ShuatuBaseMixin):
    """
    日常插片
    包含日常行动相关的脚本
    """

    def init_home(self):
        while True:
            screen = self.d.screenshot(format='opencv')
            if UIMatcher.img_where(screen, 'img/liwu.bmp', at=(891, 413, 930, 452)):
                break
            if UIMatcher.img_where(screen, 'img/niudan_jiasu.jpg', at=(700, 0, 960, 100)):
                self.d.click(893, 39)  # 跳过
                time.sleep(0.5)
                continue
            if UIMatcher.img_where(screen, 'img/jingsaikaishi.bmp', at=(755, 471, 922, 512)):
                self.d.click(786, 308)  # 选角色
                time.sleep(0.2)
                self.d.click(842, 491)  # 开始
                time.sleep(0.5)
                continue
            self.d.click(1, 1)
            time.sleep(0.3)

        self.lockimg('img/liwu.bmp', elseclick=[(1, 1)], elsedelay=0.2, at=(891, 413, 930, 452))  # 首页锁定
        time.sleep(0.5)
        # 这里防一波第二天可可萝跳脸教程
        screen_shot_ = self.d.screenshot(format='opencv')
        num_of_white, _, _ = UIMatcher.find_gaoliang(screen_shot_)
        if num_of_white < 50000:
            self.lockimg('img/renwu_1.bmp', elseclick=[(837, 433)], elsedelay=1)
            self.lockimg('img/liwu.bmp', elseclick=[(90, 514)], elsedelay=0.2, at=(891, 413, 930, 452))
            return
        if UIMatcher.img_where(screen_shot_, 'img/kekeluo.bmp'):
            self.lockimg('img/renwu_1.bmp', elseclick=[(837, 433)], elsedelay=1)
            self.lockimg('img/liwu.bmp', elseclick=[(90, 514)], elsedelay=0.2, at=(891, 413, 930, 452))

    def gonghuizhijia(self):  # 家园领取
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        self.lockimg('img/jyquanbushouqu.jpg', elseclick=[(622, 509)], elsedelay=1)
        self.lockimg('img/guanbi.jpg', elseclick=[(899, 429)], elsedelay=0.5, retry=3)
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=0.5, at=(891, 413, 930, 452))  # 回首页

    def mianfeiniudan(self):
        # 免费扭蛋
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        self.lockimg('img/liwu.bmp', ifclick=[(750, 510)], ifdelay=1, at=(891, 413, 930, 452))  # 点进扭蛋界面
        while True:
            # 跳过抽奖提示
            time.sleep(4)
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/niudan_sheding.jpg'):
                self.guochang(screen_shot_, ['img/niudan_sheding.jpg'], suiji=0)
                break
            else:
                time.sleep(1)
                self.d.click(473, 436)  # 手动点击
                time.sleep(2)
                break

        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/niudanputong.jpg'):
                self.guochang(screen_shot_, ['img/niudanputong.jpg'], suiji=0)
                time.sleep(1)
                self.d.click(722, 351)  # 点进扭蛋
                time.sleep(1)
                self.d.click(584, 384)
                break
            else:
                time.sleep(1)
                self.d.click(876, 75)  # 手动点击
                time.sleep(1)
                self.d.click(722, 351)  # 点进扭蛋
                time.sleep(1)
                self.d.click(584, 384)
                break
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    def mianfeishilian(self):
        # 免费十连
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        self.lockimg('img/liwu.bmp', ifclick=[(750, 510)], ifdelay=1, at=(891, 413, 930, 452))  # 点进扭蛋界面

        time.sleep(1)
        screen_shot_ = self.d.screenshot(format="opencv")
        if UIMatcher.img_where(screen_shot_, 'img/mianfeishilian.jpg'):  # 仅当有免费十连时抽取免费十连
            self.d.click(872, 355)  # 点击十连
            time.sleep(1)
            self.d.click(592, 369)  # 确认

        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/liwu.bmp', at=(891, 413, 930, 452)):
                break
            self.d.click(900, 40)
            time.sleep(0.5)
            self.d.click(100, 505)
            time.sleep(0.5)
            self.d.click(100, 505)
            time.sleep(1)  # 首页锁定，保证回到首页

    def shouqu(self):  # 收取全部礼物
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533), (1, 1)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        self.lockimg('img/shouqulvli.jpg', elseclick=[(910, 434)], at=(98, 458, 199, 496))
        self.lockimg('img/shouquliwu.bmp', elseclick=[(712, 477)], elsedelay=0.5, ifclick=[(588, 479)], ifbefore=0.5,
                     retry=3, at=(435, 30, 527, 58))
        self.lockimg('img/liwu.bmp', elseclick=[(1, 1)], elsedelay=0.3, at=(891, 413, 930, 452))  # 回首页

    def shouqurenwu(self):  # 收取任务报酬
        while True:
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/renwu.jpg'):
                self.guochang(screen_shot_, ['img/renwu.jpg'], suiji=0)
                break
            self.d.click(1, 1)
            time.sleep(1)
        time.sleep(3.5)
        self.d.click(846, 437)  # 全部收取
        time.sleep(1)
        self.d.click(100, 505)
        time.sleep(0.5)
        self.d.click(100, 505)
        time.sleep(1.5)
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    def goumaitili(self, times):  # 购买体力，注意此函数参数默认在首页执行，其他地方执行要调整参数
        for i in range(times):
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
            self.d.click(320, 31)
            time.sleep(1)
            screen_shot = self.d.screenshot(format="opencv")
            self.guochang(screen_shot, ['img/ok.bmp'], suiji=0)
            time.sleep(1)
            screen_shot = self.d.screenshot(format="opencv")
            self.guochang(screen_shot, ['img/zhandou_ok.jpg'], suiji=1)
            self.d.click(100, 505)  # 点击一下首页比较保险

    def goumaimana(self, times, mode=1):
        # mode 1: 购买times次10连
        # mode 0：购买times次1连
        if mode == 0:
            time.sleep(2)
            self.d.click(189, 62)
            for i in range(times):
                while True:  # 锁定取消2
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot_, 'img/quxiao2.jpg'):
                        break
                    self.d.click(189, 62)
                    time.sleep(2)
                self.d.click(596, 471)  # 第一次购买的位置
                while True:  # 锁定ok
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                        self.guochang(screen_shot_, ['img/ok.bmp'], suiji=0)
                        break
        else:
            time.sleep(2)
            self.d.click(189, 62)
            while True:  # 锁定取消2
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/quxiao2.jpg'):
                    break
                self.d.click(189, 62)
                time.sleep(2)
            self.d.click(596, 471)  # 第一次购买的位置
            while True:  # 锁定ok
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                    self.guochang(screen_shot_, ['img/ok.bmp'], suiji=0)
                    break
            for i in range(times):  # 购买剩下的times次
                while True:  # 锁定取消2
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot_, 'img/quxiao2.jpg'):
                        break
                time.sleep(3)
                self.d.click(816, 478)  # 购买10次
                while True:  # 锁定ok
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                        self.guochang(screen_shot_, ['img/ok.bmp'], suiji=0)
                        break

        self.lockimg('img/liwu.bmp', elseclick=[(1, 1)], elsedelay=0.5, at=(891, 413, 930, 452))  # 回首页

    def goumaijingyan(self):
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
        self.d.click(617, 435)
        time.sleep(2)
        self.lockimg('img/tongchang.jpg', elseclick=[(1, 100)], elsedelay=0.5, alldelay=1)
        self.d.click(387, 151)
        time.sleep(0.3)
        self.d.click(557, 151)
        time.sleep(0.3)
        self.d.click(729, 151)
        time.sleep(0.3)
        self.d.click(900, 151)
        time.sleep(0.3)
        self.d.click(785, 438)
        time.sleep(1.5)
        self.d.click(590, 476)
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

        # 买药

    def buyExp(self):
        # 进入商店
        count = 0
        self.d.click(616, 434)
        while True:
            self.d.click(82, 84)
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/exp.jpg'):
                break
            count += 1
            time.sleep(1)
            if count > 4:
                break
        if count <= 4:
            self.d.click(386, 148)
            self.d.click(556, 148)
            self.d.click(729, 148)
            self.d.click(897, 148)
            self.d.click(795, 437)
            time.sleep(1)
            self.d.click(596, 478)
            time.sleep(1)
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页

    def tansuo(self, mode=0):  # 探索函数
        """
        mode 0: 刷最上面的
        mode 1: 刷次上面的
        mode 2: 第一次手动过最上面的，再刷一次次上面的
        mode 3: 第一次手动过最上面的，再刷一次最上面的
        """
        is_used = 0
        self.d.click(480, 505)
        time.sleep(1)
        while True:  # 锁定地下城
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/dixiacheng.jpg'):
                break
            self.d.click(480, 505)
            time.sleep(1)
        self.d.click(734, 142)  # 探索
        time.sleep(3.5)
        while True:  # 锁定凯留头（划掉）返回按钮
            screen_shot_ = self.d.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot_, 'img/fanhui.bmp', at=(16, 12, 54, 48)):
                break
            self.d.click(1, 1)
            time.sleep(0.5)
        # 经验
        self.d.click(592, 255)  # 经验
        time.sleep(3)
        screen_shot_ = self.d.screenshot(format="opencv")
        if UIMatcher.img_where(screen_shot_, 'img/tansuo_used.jpg'):
            self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1)  # 回首页
        else:
            if mode >= 2:
                self.shoushuazuobiao(704, 152, lockpic='img/fanhui.bmp', screencut=(16, 12, 54, 48))
            if mode == 0 or mode == 3:
                self.d.click(704, 152)  # 5级
            else:
                self.d.click(707, 265)  # 倒数第二
            time.sleep(1)
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/tansuo_used2.jpg'):
                    is_used = 1
                    self.d.click(668, 452)  # 取消
                    break
                if UIMatcher.img_where(screen_shot_, 'img/tiaozhan.jpg'):
                    break
                time.sleep(0.5)
            if is_used == 0:
                self.d.drag(876, 329, 876, 329, 0.5)  # +号
                time.sleep(0.5)
                self.d.click(752, 327)  # 扫荡
                time.sleep(0.5)
                while True:
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                        self.d.click(590, 363)  # ok
                        time.sleep(0.5)
                        break
            if is_used == 1:
                self.d.click(36, 32)  # back
                time.sleep(1)
            is_used = 0
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/home.jpg'):
                    break
                self.d.click(1, 1)
                time.sleep(1)
            # mana
            self.d.click(802, 267)  # mana
            time.sleep(3)
            if mode >= 2:
                self.shoushuazuobiao(704, 152, lockpic='img/fanhui.bmp', screencut=(16, 12, 54, 48))
            if mode == 0 or mode == 3:
                self.d.click(704, 152)  # 5级
            else:
                self.d.click(707, 265)  # 倒数第二
            time.sleep(1.5)
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/tansuo_used2.jpg'):
                    is_used = 1
                    self.d.click(668, 452)  # 取消
                    break
                if UIMatcher.img_where(screen_shot_, 'img/tiaozhan.jpg'):
                    break
                time.sleep(0.5)
            if is_used == 0:
                self.d.drag(876, 329, 876, 329, 0.5)  # +号
                time.sleep(0.5)
                self.d.click(752, 327)  # 扫荡
                time.sleep(0.5)
                while True:
                    screen_shot_ = self.d.screenshot(format="opencv")
                    if UIMatcher.img_where(screen_shot_, 'img/ok.bmp'):
                        self.d.click(590, 363)  # ok
                        time.sleep(0.5)
                        break
            if is_used == 1:
                self.d.click(36, 32)  # back
                time.sleep(1)
            is_used = 0
            while True:
                screen_shot_ = self.d.screenshot(format="opencv")
                if UIMatcher.img_where(screen_shot_, 'img/home.jpg'):
                    break
                self.d.click(1, 1)
                time.sleep(1)
        # 完成战斗后
        self.lockimg('img/liwu.bmp', elseclick=[(131, 533)], elsedelay=1, at=(891, 413, 930, 452))  # 回首页
