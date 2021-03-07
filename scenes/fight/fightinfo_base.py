from scenes.scene_base import PCRMsgBoxBase

class FightInfoBase(PCRMsgBoxBase):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name="FightInfo"

