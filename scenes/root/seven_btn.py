from core.constant import MAIN_BTN
from scenes.scene_base import PCRSceneBase

class SevenBTNMixin(PCRSceneBase):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def goto_wodezhuye(self):
        from scenes.root.wodezhuye import WoDeZhuYe
        def gotofun():
            self.click(MAIN_BTN["zhuye"])
        return self.goto(WoDeZhuYe,gotofun)

    def goto_juese(self):
        from scenes.root.juese import JueSe
        def gotofun():
            self.click(MAIN_BTN["juese"])
        return self.goto(JueSe,gotofun)

    def goto_maoxian(self):
        from scenes.root.maoxian import MaoXian
        def gotofun():
            self.click(MAIN_BTN["maoxian"])
        return self.goto(MaoXian,gotofun)

    def goto_gonghuizhijia(self):
        from scenes.root.gonghuizhijia import GongHuiZhiJia
        def gotofun():
            self.click(MAIN_BTN["gonghuizhijia"])
        return self.goto(GongHuiZhiJia,gotofun)
