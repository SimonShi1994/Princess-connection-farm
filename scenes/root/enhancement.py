from core.constant import ENHANCEMENT_BTN, MAIN_BTN
from scenes.root.seven_btn import SevenBTNMixin


class EnhancementBase(SevenBTNMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "Enhancement"
        self.initFC = self.getFC(False).getscreen().add_sidecheck(self._a.juqing_kkr)
    
    def goto_level(self) -> "EnhancementLevel":
        return self.goto(EnhancementLevel, gotofun=self.fun_click(ENHANCEMENT_BTN["level_unselected"]))
    
    def goto_skill(self) -> "EnhancementSkill":
        return self.goto(EnhancementSkill, gotofun=self.fun_click(ENHANCEMENT_BTN["skill_unselected"]))
    
    def goto_masterskill(self) -> "EnhancementMasterSkill":
        return self.goto(EnhancementMasterSkill, gotofun=self.fun_click(ENHANCEMENT_BTN["masterskill_unselected"]))
    
class EnhancementLevel(EnhancementBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "EnhancementLevel"
        self.feature = self.fun_feature_exist(ENHANCEMENT_BTN["fire"])
    
    def enhance_one_click(self):
        if self.is_exists(ENHANCEMENT_BTN["enhance_oneclick"], is_black=True, black_threshold=1400):
            self.log.write_log("info", "属性等级无法强化")
            return
        self.click_btn(ENHANCEMENT_BTN["enhance_oneclick"])
        self.click_btn(ENHANCEMENT_BTN["confirm"])
                
        
class EnhancementSkill(EnhancementBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "EnhancementSkill"
        self.feature = self.fun_feature_exist(ENHANCEMENT_BTN["shard"])
        
    def enhance_one_click(self):
        if self.is_exists(ENHANCEMENT_BTN["enhance_oneclick_icon"], is_black=True, black_threshold=700):
            self.log.write_log("info", "属性技能无法强化")
            return
        self.click_btn(ENHANCEMENT_BTN["enhance_oneclick_icon"])
        self.click_btn(ENHANCEMENT_BTN["confirm"])        
        
class EnhancementMasterSkill(EnhancementBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "EnhancementMasterSkill"
        self.feature = self.fun_feature_exist(ENHANCEMENT_BTN["masterskill_shard"])
        
    def enhance_one_click(self):
        if self.is_exists(ENHANCEMENT_BTN["enhance_oneclick_icon"], is_black=True, black_threshold=700):
            self.log.write_log("info", "大师技能无法强化")
            return
        self.click_btn(ENHANCEMENT_BTN["enhance_oneclick_icon"])
        self.click_btn(ENHANCEMENT_BTN["confirm"])             
    