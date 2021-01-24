from scenes.scene_base import PCRSceneBase

class FightInfoBase(PCRSceneBase):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name="FightInfo"

