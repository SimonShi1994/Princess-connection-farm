import time

from core.constant import HANGHUI_BTN
from scenes.root.seven_btn import SevenBTNMixin
from core.pcr_checker import LockTimeoutError


class ClanBase(SevenBTNMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ClanBase"
        self.feature = self.fun_feature_exist(HANGHUI_BTN["chengyuanxinxi"])

    def goto_clanmember(self) -> "ClanMember":
        return self.goto(ClanMember, self.fun_click(HANGHUI_BTN["chengyuanxinxi"]))


class ClanMember(ClanBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ClanMember"
        self.feature = self.fun_feature_exist(HANGHUI_BTN["jiangxu_chengyuan"])

    def goto_exitclan(self) -> "NoClan":
        return self.goto(NoClan, self.fun_click(HANGHUI_BTN["exit_clan"]))

    '''
    sortflag:0 默认值; 1 按战力; 2 按职务
    '''

    def sortmember(self, sortflag):
        self.click_btn(HANGHUI_BTN["chengyuanpaixu"], elsedelay=5, until_appear=HANGHUI_BTN["paixuqueren"])
        if sortflag == 1:
            self.fclick(287, 295)
            self.click_btn(HANGHUI_BTN["paixuqueren"], elsedelay=5, until_disappear=HANGHUI_BTN["paixuqueren"])

        return

    def like(self, sortflag):
        if sortflag == 0 or sortflag == 1:
            if self.is_exists('img/dianzan.bmp'):
                click_list = [(826, 198), (826, 316), (826, 428)]
                for i in click_list:
                    if self.lock_img('img/dianzan.bmp', ifclick=[i], elseclick=[(480, 374)], retry=10):
                        if self.lock_img('img/queren.bmp', retry=8):
                            self.lock_no_img('img/queren.bmp', elseclick=[(480, 374)], retry=10)
                            continue
                        else:
                            self.log.write_log("warning", "已经没有点赞次数了")
                            self.lock_home()
                            break
                    else:
                        self.log.write_log("error", "找不到点赞按钮")
                        self.lock_home()
                        break
        if sortflag == 2:
            if self.is_exists('img/dianzan.bmp'):
                click_list = [(826, 198), (826, 316), (826, 428)]
                for i in click_list:
                    if self.lock_img('img/dianzan.bmp', ifclick=[i], elseclick=[(480, 374)], retry=10):
                        if self.lock_img('img/queren.bmp', retry=8):
                            self.lock_no_img('img/queren.bmp', elseclick=[(480, 374)], retry=10)
                            continue
                        else:
                            self.log.write_log("warning", "已经没有点赞次数了")
                            self.lock_home()
                            break
                    else:
                        self.log.write_log("error", "找不到点赞按钮")
                        self.lock_home()
                        break


class NoClan(SevenBTNMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "NoClan"
        self.feature = self.fun_feature_exist(HANGHUI_BTN["sheding_join"])


class ClanBattleMAP(SevenBTNMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ClanBattleMAP"
        self.feature = self.fun_feature_exist(HANGHUI_BTN["rank_info"])
        self.initPC = self.gonghuizhan_precheck

    def gonghuizhan_precheck(self, screen):
        if self.is_exists(HANGHUI_BTN["baochouqueren"], screen=screen):
            self.click_btn(HANGHUI_BTN["baochouqueren"])
        if self.is_exists(HANGHUI_BTN["guanbi"], screen=screen):
            self.click_btn(HANGHUI_BTN["guanbi"])
        if self.is_exists(HANGHUI_BTN["sudu"]):
            self.click(349, 282)
            time.sleep(1)
            self.click(479, 365)
        return screen

    def click_boss(self):
        r = self.img_where_all(img="img/hanghui/battle/boss_lp.bmp", at=(13, 133, 916, 379), threshold=0.6)
        if r is []:
            self.log.write_log("info", "未识别到BOSS，可能不在公会战期间")
            return False
        else:
            x = r[0]
            y = r[1]
            x1 = int(x) + 77
            y1 = int(y) - 43
            self.click(x1, y1)
            self.lock_no_img(HANGHUI_BTN["rank_info"])

    def get_cishu(self):
        a = self.ocr_int(549, 395, 569, 415)
        if a == 0:
            if self.is_exists(HANGHUI_BTN["fanhuanshijian"]):
                return 1
            else:
                return 0
        else:
            return a


class ClanBattlePre(ClanBattleMAP):
    # 公会战准备
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ClanBattlePre"
        self.feature = self.fun_feature_exist(HANGHUI_BTN["rank_info"])

    def make_formal(self):
        self.lock_img(HANGHUI_BTN["monizhan_unselected"], elseclick=(862, 104))

    def goto_battle(self):  # 点击挑战，进入队伍编组
        from scenes.fight.fightbianzu_base import FightBianZuBase
        return self.goto(FightBianZuBase, self.fun_click(HANGHUI_BTN["tiaozhan"]))
