from DataCenter import LoadPCRData
from scenes.fight.fightinfo_base import FightInfoBase


class FightInfoZhuXian(FightInfoBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightInfoZhuXian"

    @staticmethod
    def get_map_tili(mode,a,b):
        # 获得图M a-b所需体力
        return LoadPCRData().get_map_tili(mode, a, b)

class FightInfoZhuXianNormal(FightInfoZhuXian):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightInfoZhuXianNormal"

    @staticmethod
    def get_Nmap_tili(a,b):
        # 获得图 N a-b所需体力
        return FightInfoZhuXian.get_map_tili("N",a,b)

    def can_fight(self,screen=None):
        # 是否可以直接挑战（对于N图来说，有体力就行）
        if screen is None:
            screen = self.getscreen()
        if self.no_tili_for_one_fight(screen):
            return False
        else:
            return True



