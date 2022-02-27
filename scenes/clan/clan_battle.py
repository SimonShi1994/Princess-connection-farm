import time

from core.constant import HANGHUI_BTN
from scenes.root.seven_btn import SevenBTNMixin
from core.pcr_checker import LockTimeoutError


class ClanBattleMAP(SevenBTNMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ClanBattleMAP"
        self.feature = self.fun_feature_exist(HANGHUI_BTN["rank_info"])
        self.initPC = self.gonghuizhan_precheck

    def gonghuizhan_precheck(self, screen):
        if self.is_exists(HANGHUI_BTN["queren"], screen=screen):  # 报酬确认
            self.click_btn(HANGHUI_BTN["queren"])
        if self.is_exists(HANGHUI_BTN["guanbi"], screen=screen):  # 公会战开始、排名公布
            self.click_btn(HANGHUI_BTN["guanbi"])
        if self.is_exists(HANGHUI_BTN["kkr_dialog"], screen=screen):
            self.click(160, 100)
            self.click(160, 100)
        if self.is_exists(HANGHUI_BTN["sudu"]):  # 战斗速度上限设定（关闭）
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
        self.feature = self.fun_feature_exist(HANGHUI_BTN["shbg"])
        self.initPC = self.zhandouzhunbei_precheck

    def zhandouzhunbei_precheck(self, screen):
        if self.is_exists(HANGHUI_BTN["kkr_dialog"], screen=screen):
            self.click(160, 100)
            self.click(160, 100)

    def make_formal(self):
        self.lock_img(HANGHUI_BTN["monizhan_unselected"], elseclick=(862, 104))

    def goto_battle(self):  # 点击挑战，进入队伍编组
        return self.goto(ClanBattleBianzu, self.fun_click(HANGHUI_BTN["tiaozhan"]))


class ClanBattleBianzu(ClanBattleMAP):  # 公会战编组
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ClanBattlePre"
        self.feature = self.fun_feature_exist(HANGHUI_BTN["rank_info"])
        self.initPC = self.duiwubianji_precheck

    def duiwubianji_precheck(self, screen):
        if self.is_exists(HANGHUI_BTN["kkr_dialog"], screen=screen):
            self.click(160, 100)
            self.click(160, 100)

