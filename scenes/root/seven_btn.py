from typing import TYPE_CHECKING

from core.constant import MAIN_BTN
from scenes.scene_base import PCRSceneBase

if TYPE_CHECKING:
    from scenes.root.wodezhuye import WoDeZhuYe
    from scenes.root.juese import CharMenu
    from scenes.root.maoxian import MaoXian
    from scenes.root.gonghuizhijia import GongHuiZhiJia
    from scenes.root.zhucaidan import ZhuCaiDan
    from scenes.root.enhancement import EnhancementLevel

class SevenBTNMixin(PCRSceneBase):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name = "SevenBTN"

    def goto_wodezhuye(self)->"WoDeZhuYe":
        from scenes.root.wodezhuye import WoDeZhuYe
        def gotofun():
            self.click(MAIN_BTN["zhuye"])
        return self.goto(WoDeZhuYe,gotofun)  # Type:WoDeZhuYe

    def goto_juese(self)->"CharMenu":
        from scenes.root.juese import CharMenu
        def gotofun():
            self.click(MAIN_BTN["juese"])
            self.fclick(268, 20)
        return self.goto(CharMenu,gotofun)  # Type:JueSe
    
    def goto_enhancement(self)->"EnhancementLevel":
        from scenes.root.enhancement import EnhancementLevel
        def gotofun():
            self.click(MAIN_BTN["qianghua"])
        return self.goto(EnhancementLevel, gotofun)  

    def goto_maoxian(self)->"MaoXian":

        from scenes.root.maoxian import MaoXian
        def gotofun():
            self.click(MAIN_BTN["maoxian"])
        return self.goto(MaoXian,gotofun)  # Type:MaoXian

    def goto_gonghuizhijia(self)->"GongHuiZhiJia":

        from scenes.root.gonghuizhijia import GongHuiZhiJia
        def gotofun():
            self.click(MAIN_BTN["gonghuizhijia"])
        return self.goto(GongHuiZhiJia,gotofun)  # Type:GongHuiZhiJia

    def goto_zhucaidan(self)->"ZhuCaiDan":

        from scenes.root.zhucaidan import ZhuCaiDan
        def gotofun():
            self.click(MAIN_BTN["zhucaidan"])
        return self.goto(ZhuCaiDan,gotofun)  # Type:ZhuCaiDan
