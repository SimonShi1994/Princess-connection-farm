from scenes.fight.fightinfo_base import FightInfoBase


class FightInfoZhuXian(FightInfoBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightInfoZhuXian"
