from scenes.scene_base import PCRSceneBase


class FightingBase(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "Fighting"


class FightingWinBase(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightingWin"


class FightingLoseBase(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightingLose"
