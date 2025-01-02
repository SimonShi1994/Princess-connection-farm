import time
from typing import TYPE_CHECKING, Union, Type

from core.constant import MAIN_BTN, DXC_ELEMENT, HAOYOU_BTN, MAOXIAN_BTN, FIGHT_BTN
from core.pcr_checker import LockTimeoutError
from scenes.fight.fighting_base import FightingBase, FightingWinBase, FightingLoseBase
from scenes.scene_base import PCRMsgBoxBase, PossibleSceneList


if TYPE_CHECKING:
    from scenes.zhuxian.zhuxian_normal import ZhuXianNormal
    from scenes.zhuxian.zhuxian_hard import ZhuXianHard


class FightingZhuXian(FightingBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightingZhuXian"

    def get_during(self) -> "DuringFightingZhuXian":
        return DuringFightingZhuXian(self._a)

    def auto_and_fast(self,max_speed=1):
        super().auto_and_fast(max_speed=max_speed)

    def wait_for_end_and_return(self,
                                zhuxian_type,
                                xianding=False,
                                max_fight_time = 300,):
        """
        :param zhuxian_type: 返回什么场景
        :param xianding: 是否买空限定商店
        :param max_fight_time: 最大战斗时间
        return: state dict{
            flag:  "win" / "lose"
            star: if win: 1~3
        }
        """
        dur = self.get_during()
        last_time = time.time()
        state = {"flag": None}

        while True:
            if time.time()-last_time > max_fight_time:
                raise LockTimeoutError(f"战斗超时！超过{max_fight_time}秒。")
            time.sleep(1)
            out = dur.check()
            if out is None:
                continue
            if isinstance(out,dur.LoveUpScene):
                out.skip()
            if isinstance(out,dur.FightingLoseZhuXian):
                state["flag"] = "lose"
                out.goto_zhuxian(zhuxian_type)
                break
            if isinstance(out,dur.FightingWinZhuXian):
                state["flag"] = "win"
                state["star"] = out.get_star()
                state["next"] = out.get_after()
                out.next()
                break
            if isinstance(out, dur.FightingDialog):
                out.skip()
            if isinstance(out,dur.HaoYouMsg):
                out.exit_with_off()

        if state["flag"] == "win":
            last_time = time.time()
            next = state["next"]
            while True:
                if time.time() - last_time > 120:
                    raise LockTimeoutError("在结算页面超时！")
                out = next.check()
                if out is None:
                    break
                if isinstance(out, next.XianDingShangDianBox):
                    # 限定商店
                    if xianding:
                        shop = out.Go()
                        shop.buy_all()
                        shop.back()
                        break
                    else:
                        out.Cancel()
                if isinstance(out, next.TuanDuiZhanBox):
                    out.OK()
                if isinstance(out, next.LevelUpBox):
                    out.OK()
                    self._a.start_shuatu()  # 体力又有了！
                if isinstance(out, next.ChaoChuShangXianBox):
                    out.OK()
                if isinstance(out, next.AfterFightKKR):
                    out.skip()
                    # 再次进图
                    self._a.get_zhuye().goto_maoxian().goto_zhuxian()
                    break
                if isinstance(out, next.FightingWinZhuXian2):
                    # 外出后可能还有Box，需要小心谨慎
                    out.next()
        return state

    def wait_for_end_and_return_normal(self,
                                xianding=False,
                                max_fight_time = 300,):
        from scenes.zhuxian.zhuxian_normal import ZhuXianNormal
        return self.wait_for_end_and_return(ZhuXianNormal,xianding=xianding,max_fight_time=max_fight_time)


class HaoYouMsg(PCRMsgBoxBase):
    def __init__(self,a):
        super().__init__(a)
        self.feature = self.fun_feature_exist(HAOYOU_BTN["hysqqr"])

    def exit_with_off(self):
        self.click(396,383,post_delay=2)
        self.exit(self.fun_click(369,476))


class LevelUpBox(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "LevelUpBox"
        self.feature = self.fun_feature_exist(FIGHT_BTN["dengjitisheng"])

    def OK(self):
        self.exit(self.fun_click(38, 24))  # Outside


class DuringFightingZhuXian(PossibleSceneList):
    from scenes.zhuxian.zhuxian_msg import KKRQianBao

    def __init__(self, a, *args, **kwargs):
        self.LoveUpScene = LoveUpScene
        self.LevelUpBox = LevelUpBox
        self.FightingWinZhuXian = FightingWinZhuXian
        self.FightingLoseZhuXian = FightingLoseZhuXian
        self.FightingDialog = FightingDialog
        self.HaoYouMsg = HaoYouMsg
        self.TuanDuiZhanBox = TuanDuiZhanBox
        self.AutoAdvanceStopBox = AutoAdvanceStopBox
        self.AutoAdvanceEndBox = AutoAdvanceEndBox

        scene_list = [
            self.KKRQianBao(a),
            LoveUpScene(a),
            LevelUpBox(a),
            FightingWinZhuXian(a),
            FightingLoseZhuXian(a),
            FightingDialog(a),
            HaoYouMsg(a),
            TuanDuiZhanBox(a),
            AutoAdvanceStopBox(a),
            AutoAdvanceEndBox(a)
        ]
        super().__init__(a, scene_list, double_check=0)


class TuanDuiZhanBox(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "TuanDuiZhanBox"
        self.feature = self.fun_feature_exist(MAOXIAN_BTN["tuanduizhan"])

    def OK(self):
        self.click_btn(MAOXIAN_BTN["tuanduizhan_quxiao"])  # 跳过团队站


class LoveUpScene(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "LoveUpScene"
        self.feature = self.fun_feature_exist(MAIN_BTN["tiaoguo"])

    def skip(self):
        self.exit(self.fun_click(MAIN_BTN["tiaoguo"]), interval=1)


class FightingDialog(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "LoveUpScene"
        self.feature = self.dialog_feature

    def dialog_feature(self, screen):
        return self._a.is_exists(MAIN_BTN["speaker_box"], screen=screen, method="sq", threshold=0.95)

    def skip(self):
        self.exit(self.fun_click(1, 1), interval=0.2)


class FightingWinZhuXian(FightingWinBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightingWinZhuXian"

    def get_star(self, screen=None):
        return self._a.get_fight_middle_stars(screen)

    def next(self):
        self.exit(self.fun_click(835, 499, post_delay=2))

    def get_after(self):
        return AfterFightingWin(self._a)


class AfterFightingWin(PossibleSceneList):
    from scenes.zhuxian.zhuxian_msg import XianDingShangDianBox, LevelUpBox, TuanDuiZhanBox, ChaoChuShangXianBox, \
        KKRQianBao

    def __init__(self, a, *args, **kwargs):
        self.AfterFightKKR = AfterFightKKR
        self.FightingWinZhuXian2 = FightingWinZhuXian2
        self.HaoYouMsg = HaoYouMsg
        self.LoveUpScene = LoveUpScene

        scene_list = [
            self.KKRQianBao(a),
            self.XianDingShangDianBox(a),
            self.LevelUpBox(a),
            self.TuanDuiZhanBox(a),
            self.ChaoChuShangXianBox(a),
            LoveUpScene(a),
            HaoYouMsg(a),
            FightingWinZhuXian2(a),
            AfterFightKKR(a),  # kkr剧情跳脸
        ]
        super().__init__(a, scene_list, double_check=3)


class AfterFightKKR(PCRMsgBoxBase):
    def __init__(self, a, *args, **kwargs):
        super().__init__(a)
        self.scene_name = "AfterFightKKR"
        self.feature = self.girls_feature

    def girls_feature(self, screen):
        return self.is_exists(DXC_ELEMENT["dxc_kkr"], screen=screen)

    def skip(self):
        self.chulijiaocheng(None)


class FightingWinZhuXian2(FightingWinBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightingWinZhuXian2"
        self.feature = self.win_feature

    def win_feature(self, screen):
        from core.constant import p
        huodedaoju = self.is_exists(p(img="img/fight/huodedaoju.bmp", at=(442, 135, 514, 160)), screen=screen)
        xiayibu = self.is_exists(p(img="img/fight/xiayibu.bmp", at=(794, 475, 865, 502)), screen=screen)
        jrtssy = self.is_exists(MAIN_BTN["jrtssy2"], screen=screen)
        return huodedaoju or (xiayibu or jrtssy)

    def next(self):
        time.sleep(5)
        self.click(829, 485, post_delay=1)


class FightingLoseZhuXian(FightingLoseBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightingLoseZhuXian2"

    def goto_zhuxian(self, zhuxian_type):
        return self.goto(zhuxian_type, self.fun_click(806, 489))  # 前往主线关卡
    
class AutoAdvanceStopBox(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "AutoAdvanceStopBox"
        self.feature = self.fun_feature_exist(MAOXIAN_BTN["auto_advance_stop"])

    def OK(self):
        self.click_btn(MAOXIAN_BTN["auto_advance_confirm"]) 

class AutoAdvanceEndBox(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "AutoAdvanceEndBox"
        self.feature = self.fun_feature_exist(MAOXIAN_BTN["auto_advance_end"])

    def OK(self):
        self.click_btn(MAOXIAN_BTN["auto_advance_confirm"]) 
        
    def next(self):
        time.sleep(5)
        self.click(829, 485, post_delay=1)     
