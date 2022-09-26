import time
from typing import Union

from core.constant import HANGHUI_BTN, FIGHT_BTN, DXC_ELEMENT
from scenes.fight.fightbianzu_base import FightBianZuBase
from scenes.fight.fighting_zhuxian import FightingZhuXian
from scenes.root.seven_btn import SevenBTNMixin
from scenes.scene_base import PCRMsgBoxBase, PossibleSceneList


class ClanBattleMAP(SevenBTNMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ClanBattleMAP"
        self.feature = self.fun_feature_exist(HANGHUI_BTN["rank_info"])
        self.initPC = self.gonghuizhan_precheck

    def gonghuizhan_precheck(self, screen):
        if self.is_exists(HANGHUI_BTN["queren"], screen=screen):  # 报酬确认
            self.click(HANGHUI_BTN["queren"])
            time.sleep(2)
        elif self.is_exists(HANGHUI_BTN["guanbi"], screen=screen):  # 公会战开始、排名公布
            self.click(HANGHUI_BTN["guanbi"])
            time.sleep(2)
        elif self.is_exists(HANGHUI_BTN["kkr_dialog"], screen=screen):
            self.click(160, 100)
            self.click(160, 100)
            time.sleep(2)
        elif self.is_exists(img="img/duiwu.jpg", screen=screen, is_black=True, black_threshold=800):
            time.sleep(4)
            self.fclick(1, 1)
        elif self.is_exists(HANGHUI_BTN["kkr_dialog2"], screen=screen):
            self.click(160, 100)
            self.click(160, 100)
            time.sleep(2)
        elif self.is_exists(HANGHUI_BTN["sudu"], screen=screen):  # 战斗速度上限设定（关闭）
            self.click(349, 282)
            time.sleep(2)
            self.click(479, 365)
            time.sleep(2)
        return screen

    def goto_battlepre(self) -> Union[int, "ClanBattlePre"]:  # 点击进入BOSS
        time.sleep(5)
        r = self.img_where_all(img="img/hanghui/battle/boss_arrow.bmp", threshold=0.5, at=(45, 1, 908, 367))
        if not r:
            self.log.write_log("warning", "未识别到BOSS，可能不在公会战期间")
            return -1
        else:
            x = r[0]
            y = r[1]
            x1 = int(x)
            y1 = int(y) + 115
            return self.goto(ClanBattlePre, self.fun_click(x1, y1))

    def get_cishu(self):
        self.lock_img(HANGHUI_BTN["sytzcs"], elseclick=(1, 1), elsedelay=0.1)  # 确保画面稳定的
        time.sleep(0.5)
        screen = self.getscreen()
        a = self.ocr_int(555, 396, 567, 414, screen_shot=screen)
        if a == 0:
            if self.is_exists(HANGHUI_BTN["fanhuanshijian"], screen=screen):
                return -1
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
        # if self.is_exists(HANGHUI_BTN["kkr_dialog2"], screen=screen):
        #     self.click(160, 100)
        #     self.click(160, 100)
        return screen

    def make_formal(self):
        self.lock_img(HANGHUI_BTN["monizhan_unselected"], elseclick=(862, 104))

    def goto_bianzu(self) -> "FightBianZuBase":  # 点击挑战，进入队伍编组
        return self.goto(FightBianZuBase, self.fun_click(HANGHUI_BTN["tiaozhan"]))


class TuanDuiZhanQueRen(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "TuanDuiZhanQueRen"
        self.feature = self.fun_feature_exist(HANGHUI_BTN["tdzksqr"])

    def ok(self):
        return self.goto(FightingZhuXian, self.fun_click(HANGHUI_BTN["zhandou_confirm"]))


class FanHuanQueRen(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FanHuanQueRen"
        self.feature = self.fun_feature_exist(HANGHUI_BTN["fhsjqr"])

    def ok(self):
        return self.goto(FightingZhuXian, self.fun_click(HANGHUI_BTN["zhandou_confirm2"]))


class ZhiYuanQueRen(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ZhiYuanQueRen"
        self.feature = self.fun_feature_exist(DXC_ELEMENT["zyjsqr"])

    def ok(self):
        return self.goto(FightingZhuXian, self.fun_click(DXC_ELEMENT["zyjsqr_ok"]))


class AfterEnterTiaoZhan(PossibleSceneList):
    def __init__(self, a):
        self.TuanDuiZhanQueRen = TuanDuiZhanQueRen
        self.ZhiYuanQueRen = ZhiYuanQueRen
        self.next_scene = FightingZhuXian
        scene_list = [
            TuanDuiZhanQueRen(a),
            FightingZhuXian(a),
            FanHuanQueRen(a),
            ZhiYuanQueRen(a),
        ]
        super().__init__(a, scene_list, double_check=1.)


class FightBianZuHangHui(FightBianZuBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightBianZuZhuXian"

    def goto_fight(self):
        # 前往战斗开始！
        while True:
            time.sleep(2)
            out = self.goto(AfterEnterTiaoZhan, self.fun_click(FIGHT_BTN["zhandoukaishi"]))
            if isinstance(out, TuanDuiZhanQueRen):
                self.click(HANGHUI_BTN["zhandou_confirm"])
                continue
            elif isinstance(out, FanHuanQueRen):
                self.click_img(HANGHUI_BTN["zhandou_confirm"].img)
                continue
            elif isinstance(out, ZhiYuanQueRen):
                self.click(DXC_ELEMENT["zyjsqr_ok"])
                continue
            else:
                break
        return out
