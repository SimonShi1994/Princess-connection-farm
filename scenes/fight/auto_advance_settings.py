from scenes.scene_base import PCRMsgBoxBase
from scenes.fight.fighting_zhuxian import FightingZhuXian
from scenes.fight.buy_ap import BuyAPMsgBox
from core.constant import MAOXIAN_BTN
import time

class AutoAdvanceSettings(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "AutoAdvanceSettings"
        # todo: add feature "ZidongTuijinSheding"
        self.feature = self.fun_feature_exist(MAOXIAN_BTN["auto_advance_settings_title"])


    def need_buy_ap(self):
        return self.is_exists(MAOXIAN_BTN["without_buy_ap"])
 

    def ok(self):
        # 回复体力后会重新弹出窗口，若还不够，还会提示回复体力
        # 剩下的工作是确认FightingZhuxian
        return self.goto(FightingZhuXian, self.click_btn(MAOXIAN_BTN["auto_advance_fight"]))

    def ok_without_buy_ap(self):
        return self.goto(FightingZhuXian, self.click_btn(MAOXIAN_BTN["without_buy_ap"]))

    def goto_fight(self, buy_ap=False, ub_on=True):
        """
        buy_ap: 体力不足时是否买体力
        ub_on: 过图是否开启UB (活动图初音)
        """

        if self.is_exists(MAOXIAN_BTN["auto_advance_mainline_feature"]):
            self.click(114, 283, post_delay=0.3) # 推到体力不足  首领出现(425,280)
            self.click(727, 392, post_delay=0.3) # 非3星不停止  停止(425,390)
            self.dragdown()
            self.click(423, 283, post_delay=0.3) # 跳过boss对话, 不跳过(724, 290)
            self.click(113 if ub_on else 724, 392, post_delay=0.3)  # 是否开UB

        elif self.is_exists(MAOXIAN_BTN["auto_advance_event_feature"]):
            self.click(505, 293, post_delay=0.3) # 跳过剧情, 不跳过(724, 290)
            self.click(288 if ub_on else 724, 392, post_delay=0.3) # 是否开启UB
        else:
            # 未知状况 退出
            return False
        
        while self.need_buy_ap():
            if buy_ap:
                # click 
                out = self.goto(BuyAPMsgBox, self.click_btn(MAOXIAN_BTN["auto_advance_buy_ap"]))
                # go to buy ap
                # out.buy AP 弹两个窗，买体力，买体力-确认
                # 购买失败，那就不干了？
                if not out:
                    return False
                continue
            else:
                out = self.ok_without_buy_ap()
                break
        else:
            out = self.ok()
        return out
    
    def dragdown(self):
        time.sleep(1)
        obj = self.d.touch.down(855, 400)
        time.sleep(0.1)
        obj.move(855, 80)
        time.sleep(0.8)
        obj.up(855, 80)
        time.sleep(1)


