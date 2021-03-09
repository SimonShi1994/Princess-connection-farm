from core.constant import MAIN_BTN
from scenes.root.seven_btn import SevenBTNMixin

class WoDeZhuYe(SevenBTNMixin):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name="WoDeZhuYe"
        def feature(screen):
            return self.is_exists(MAIN_BTN["liwu"],screen=screen)

        self.initFC = None
        self.feature = feature
