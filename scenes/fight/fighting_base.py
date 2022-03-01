from core.constant import FIGHT_BTN
from scenes.scene_base import PCRSceneBase


class FightingBase(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "Fighting"
        self.feature = self.fun_feature_exist(FIGHT_BTN["fighting_caidan"])

    def set_auto(self, auto, screen=None, max_retry=3):
        if screen is None:
            screen = self.getscreen()
        self._a.set_fight_auto(auto, screen, max_retry)

    def set_speed(self, level, max_level=1, screen=None, max_retry=3):
        if screen is None:
            screen = self.getscreen()
        self._a.set_fight_speed(level, max_level, screen, max_retry)

    def auto_and_fast(self,max_speed):
        self.set_auto(1,self.last_screen)
        self.set_speed(max_speed,max_speed,self.last_screen)


class FightingWinBase(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightingWin"
        self.feature = self.win_feature

    def win_feature(self, screen):
        from core.constant import p
        duiwu_icon = p(909,88,img="img/fight/duiwu_icon.bmp",at=(895, 78, 923, 97))
        shbg = p(850,38,img="img/fight/shbg.bmp",at=(814, 27, 886, 49))
        return self.is_exists(duiwu_icon, screen=screen) and self.is_exists(shbg, screen=screen)


class FightingLoseBase(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightingLose"
        self.feature = self.lose_feature

    def lose_feature(self, screen):
        from core.constant import p
        duiwu_icon = p(851, 36, img="img/fight/duiwu_icon.bmp", at=(828, 17, 871, 52))
        shbg = p(731, 37, img="img/fight/shbg.bmp", at=(684, 23, 778, 51))
        return self.is_exists(duiwu_icon, screen=screen) and self.is_exists(shbg, screen=screen)
