import time
from core.constant import CARAVAN_BTN, CARAVAN_GACHA_POS, CARAVAN_GACHA_COST, CARAVAN_SELL_DISH_POS, SHOP_BTN
from scenes.scene_base import PCRSceneBase

class ConfirmThrowDice(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ConfirmThrowDice"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["throw_dice"])
    
    def confirm(self):
        self.click(398, 290)
        self.click_btn(CARAVAN_BTN["throw_dice"])

class Fork(PCRSceneBase):
    # 岔路
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "Fork"       

        def feature(screen):
           return self.is_exists(CARAVAN_BTN["goal_distance"], screen=screen)
                 
        self.feature = feature
        
    def select_fork(self):
        fork_pos = self.img_where_all(CARAVAN_BTN["goal_distance"].img, method="sq")
        self.click(fork_pos[0], fork_pos[1] + 70)


class MileShop(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "MileShop"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["mile_shop"])

    def select_dish(self):
        self.lock_img(CARAVAN_BTN["mile_shop"])
        time.sleep(1)
        self.click(516,122)
    
    def select_all(self):
        self.click_btn(CARAVAN_BTN["select_all"], until_disappear=None)
        if self.is_exists(CARAVAN_BTN["buy_all"], is_black=True, black_threshold=1400):
            self.log.write_log("info", "没有里程了！")
            return False
        return True
                    
    def close(self):
        self.exit(self.fun_click(1, 1), interval=2)
    
    def goto_confirm(self) -> "MileShopConfirm":
        return self.goto(MileShopConfirm, gotofun=self.fun_click(CARAVAN_BTN["buy_all"]), use_in_feature_only=True)
    
    def buy_all(self):
        if self.select_all():         
            self.goto_confirm().confirm()
        self.select_dish()
        if self.select_all():
            self.goto_confirm().confirm()    
        
        
class MileShopConfirm(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "MileShopConfirm"
        self.feature = self.fun_feature_exist(SHOP_BTN["buy_confirm"])
    
    def confirm(self):
        self.lock_img(CARAVAN_BTN["finish_buying"], elseclick=(590, 478), elsedelay=1)
        self.lock_img(CARAVAN_BTN["mile_shop"], elseclick=(473, 477), elsedelay=1)

class Gacha(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "Gacha"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["gacha"])
    
    def get_holding_mile(self):
        return self.ocr_int(265, 482, 345, 500)      
    
    def goto_confirm(self, index)-> "GachaConfirm":
        cost = CARAVAN_GACHA_COST[index]
        holding_mile = self.get_holding_mile()
        if holding_mile < cost:
            for i in range(index - 1, 0, -1):
                required_mile = CARAVAN_GACHA_COST[i]
                if holding_mile >= required_mile:
                    pos = CARAVAN_GACHA_POS[i]
                    return self.goto(GachaConfirm, gotofun=self.fun_click(pos), use_in_feature_only=True)
        pos = CARAVAN_GACHA_POS[index]           
        return self.goto(GachaConfirm, gotofun=self.fun_click(pos), use_in_feature_only=True)
    
    def do_gacha(self, index):
        if index > 3:
            self.goto_confirm(3).confirm()
        else:
            self.goto_confirm(index).confirm()

class GachaConfirm(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "GachaConfirm"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["holding_mile"])
    
    def confirm(self):
        self.exit(self.fun_click(592, 367))

class Game(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "Game"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["game"])
    
    def start(self):
        self.click_btn(CARAVAN_BTN["game_start"])
    
    def goto_gaming(self):
        return self.goto(Gaming, gotofun=self.fun_click(CARAVAN_BTN["game_start"]), use_in_feature_only=False)
    
    
class Gaming(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.duration = 30
        self.scene_name = "Gaming"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["pause"])
    
    def play(self):
        start_time = time.time()
        end_time = start_time + self.duration
        while time.time() < end_time:
            self.d.touch.down(0, 270).sleep(1.5).up(0, 270)
            self.d.touch.down(959, 270).sleep(1.5).up(959, 270)

class GameResult(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "GameResult"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["game_result"])
    
    def next(self):
        self.exit(self.fun_click(832, 489))   
        

class Event(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "Event"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["skip"])
    
    def skip(self):
        self.click_btn(CARAVAN_BTN["skip"])
        
class Slot(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "Slot"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["slot"])
    
    def next(self):
        self.exit(self.fun_click(1, 1))
        
class DishOverflow(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "DishOverflow"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["sell_all"])
    
    def get_sell_num(self):
        num_at = (503, 100, 549, 120)
        result = self.ocr_center(*num_at)
        if result == -1:
            raise Exception("识别卖出料理数量失败！")
        left, right = map(int, result.split('/')) 
        return left - right
    
    def goto_confirm(self) -> "SellConfirm":
        return self.goto(SellConfirm, gotofun=self.fun_click(CARAVAN_BTN["sell_all"]), use_in_feature_only=True)
        
    def sell_all(self):
        num = self.get_sell_num()
        for i in range(1, num + 1):
            self.click(CARAVAN_SELL_DISH_POS[i])
        self.goto_confirm().confirm()

class SellConfirm(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "SellConfirm"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["sell_confirm"])
    
    def confirm(self):
        self.lock_img(CARAVAN_BTN["finish_selling"], elseclick=(590, 478), elsedelay=1)
        self.lock_no_img(CARAVAN_BTN["finish_selling"], elseclick=(1, 1), elsedelay=1)

class GoalTreasure(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "Goal"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["result"])
    
    def next(self):
        self.click(478, 476)

class GoalSummary(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "GoalSummary"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["summary"])
    
    def close(self):
        self.click(478, 476)