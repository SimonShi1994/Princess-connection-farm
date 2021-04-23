from core.constant import FIGHT_BTN
from scenes.scene_base import PCRSceneBase


class FightingBase(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "Fighting"
        self.feature = self.fun_feature_exist(FIGHT_BTN["fighting_caidan"])

    def set_auto(self, auto, screen=None, max_retry=3):
        self._a.set_fight_auto(auto, screen, max_retry)

    def set_speed(self, level, max_level=1, screen=None, max_retry=3):
        self._a.set_fight_speed(level, max_level, screen, max_retry)


class FightingWinBase(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightingWin"
        self.feature = self.win_feature

    def win_feature(self, screen):
        from core.constant import p
        duiwu_icon = p(img="img/fight/duiwu_icon.bmp", at=(896, 78, 924, 97))
        shbg = p(850, 37, img="img/fight/shbg.bmp", at=(814, 26, 886, 48))
        return self.is_exists(duiwu_icon, screen=screen) and self.is_exists(shbg, screen=screen)


class FightingLoseBase(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightingLose"
        self.feature = self.lose_feature

    def lose_feature(self, screen):
        from core.constant import p
        duiwu_icon = p(910, 35, img="img/fight/duiwu_icon.bmp", at=(896, 25, 924, 44))
        shbg = p(790, 37, img="img/fight/shbg.bmp", at=(754, 26, 826, 48))
        return self.is_exists(duiwu_icon, screen=screen) and self.is_exists(shbg, screen=screen)
