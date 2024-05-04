from scenes.scene_base import PCRMsgBoxBase, PossibleSceneList
from core.constant import MAOXIAN_BTN

# buy ap box
# todo: 现在只能一次一次买，加入OCR买多管
class BuyAPMsgBox(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "BuyAPMsgBox"
        self.feature = self.fun_feature_exist(MAOXIAN_BTN["buy_ap_title"])

    def buy_ap(self):
        out = self.goto("BuyAPResultMsgBox", self.fun_click(MAOXIAN_BTN["buy_ap_confirm"]))
        if isinstance(out, BuyAPSuccessMsgBox):
            return out.ok()
        else:
            return False
        
class BuyAPSuccessMsgBox(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "BuyAPSuccessMsgBox"
        self.feature = self.fun_feature_exist(MAOXIAN_BTN["buy_ap_success_title"])

    def ok(self):
        return self.lock_no_img(self.feature, elseclick=MAOXIAN_BTN["buy_ap_success_confirm"])

# 没见过 没素材
# class BuyAPFailedMsgBox(PCRMsgBoxBase):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.scene_name = "BuyAPFailedMsgBox"

class BuyAPResultMsgBox(PossibleSceneList):
    def __init__(self, a):
        scene_list = [
            BuyAPSuccessMsgBox(a),
            # BuyAPFailedMsgBox(a),
        ]
        super().__init__(a, scene_list, double_check=1.)


    def ok(self):
        return 