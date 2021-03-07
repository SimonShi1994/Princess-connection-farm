from core.constant import FIGHT_BTN
from scenes.fight.fighting_base import FightingBase,FightingWinBase


class FightingZhuXian(FightingBase):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name="FightingZhuXian"
        self.feature = self.fun_feature_exist(FIGHT_BTN["fighting_caidan"])

    def set_auto(self,auto,screen=None,max_retry=3):
        self._a.set_fight_auto(auto,screen,max_retry)

    def set_speed(self,level,max_level=1,screen=None,max_retry=3):
        self._a.set_fight_speed(level,max_level,screen,max_retry)


class FightingWinZhuXian(FightingWinBase):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name="FightingWinZhuXian"
        self.feature = self.win_feature

    def win_feature(self,screen):
        from core.constant import p
        duiwu_icon = p(img="img/fight/duiwu_icon.bmp", at=(896, 78, 924, 97))
        shbg = p(850,37,img="img/fight/shbg.bmp",at=(814, 26, 886, 48))
        return self.is_exists(duiwu_icon,screen=screen) and self.is_exists(shbg,screen=screen)

    def next(self):
        pass

    # TODO WinFeature2
    # TODO FailFeature