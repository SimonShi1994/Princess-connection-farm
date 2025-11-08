import time
from core.constant import CARAVAN_BTN, CARAVAN_GACHA_POS, CARAVAN_GACHA_COST, CARAVAN_SELL_DISH_POS, SHOP_BTN
from scenes.scene_base import PCRSceneBase

class CaravanEvent(PCRSceneBase):
    def __init__(self, a):
        super().__init__(a)
    
    def handle(self):
        pass

class ConfirmThrowDice(CaravanEvent):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "ConfirmThrowDice"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["throw_dice"])
    
    def handle(self):
        self.click(398, 290)
        self.click_btn(CARAVAN_BTN["throw_dice"])

class Fork(CaravanEvent):
    # 岔路
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "Fork"       

        def feature(screen):
           return self.is_exists(CARAVAN_BTN["goal_distance"], screen=screen)
                 
        self.feature = feature
        
    def handle(self):
        fork_pos = self.img_where_all(CARAVAN_BTN["goal_distance"].img, method="sq")
        self.click(fork_pos[0], fork_pos[1] + 70)


class MileShop(CaravanEvent):
    def __init__(self, a, buy_shop=False):
        super().__init__(a)
        self.scene_name = "MileShop"
        self.buy_shop = buy_shop
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
    
    def handle(self):
        if self.buy_shop:
            if self.select_all():         
                self.goto_confirm().confirm()
            self.select_dish()
            if self.select_all():
                self.goto_confirm().confirm()
        self.close()    
        
        
class MileShopConfirm(CaravanEvent):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "MileShopConfirm"
        self.feature = self.fun_feature_exist(SHOP_BTN["buy_confirm"])
    
    def confirm(self):
        self.lock_img(CARAVAN_BTN["finish_buying"], elseclick=(590, 478), elsedelay=1)
        self.lock_img(CARAVAN_BTN["mile_shop"], elseclick=(473, 477), elsedelay=1)

class Gacha(CaravanEvent):
    def __init__(self, a, gacha=1):
        super().__init__(a)
        self.scene_name = "Gacha"
        self.index = gacha
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
    
    def handle(self):
        if self.index > 3:
            self.goto_confirm(3).confirm()
        else:
            self.goto_confirm(self.index).confirm()

class GachaConfirm(PCRSceneBase):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "GachaConfirm"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["holding_mile"])
    
    def confirm(self):
        self.exit(self.fun_click(592, 367))

class Game(CaravanEvent):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "Game"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["game"])
    
    def handle(self):
        return self.goto(Gaming, gotofun=self.fun_click(CARAVAN_BTN["game_start"]), use_in_feature_only=False)
    
    
class Gaming(CaravanEvent):
    def __init__(self, a):
        super().__init__(a)
        self.duration = 30
        self.scene_name = "Gaming"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["pause"])
    
    def handle(self):
        start_time = time.time()
        end_time = start_time + self.duration
        while time.time() < end_time:
            self.d.touch.down(0, 270).sleep(1.5).up(0, 270)
            self.d.touch.down(959, 270).sleep(1.5).up(959, 270)

class GameResult(CaravanEvent):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "GameResult"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["game_result"])
    
    def handle(self):
        self.exit(self.fun_click(832, 489))   
        

class Event(CaravanEvent):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "Event"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["skip"])
    
    def handle(self):
        self.click_btn(CARAVAN_BTN["skip"])
        
class Slot(CaravanEvent):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "Slot"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["slot"])
    
    def handle(self):
        self.exit(self.fun_click(1, 1))
        
class DishOverflow(CaravanEvent):
    def __init__(self, a):
        super().__init__(a)
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
        
    def handle(self):
        num = self.get_sell_num()
        for i in range(1, num + 1):
            self.click(CARAVAN_SELL_DISH_POS[i])
        self.goto_confirm().confirm()

class SellConfirm(PCRSceneBase):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "SellConfirm"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["sell_confirm"])
    
    def confirm(self):
        self.lock_img(CARAVAN_BTN["finish_selling"], elseclick=(590, 478), elsedelay=1)
        self.lock_no_img(CARAVAN_BTN["finish_selling"], elseclick=(1, 1), elsedelay=1)

class GoalTreasure(CaravanEvent):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "Goal"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["result"])
    
    def handle(self):
        self.exit(self.fun_click(478, 476))

class GoalSummary(CaravanEvent):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "GoalSummary"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["summary"])
    
    def handle(self):
        self.exit(self.fun_click(478, 476))
        
class GoalLottery(CaravanEvent):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "GoalLottery"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["lottery"])
    
    def handle(self):
        self.exit(self.fun_click(478, 476))      

class AddDiceEvent(CaravanEvent):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "AddDiceEvent"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["add_dice"])
    
    def handle(self):
        self.click_btn(CARAVAN_BTN["add_dice"])
class SelectDiceEvent(CaravanEvent):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "SelectDiceEvent"
    
        def feature(screen):
           return self.is_exists(CARAVAN_BTN["or"], screen=screen) and not self.is_exists(CARAVAN_BTN["reroll"], screen=screen)
       
        self.feature = feature
    
    def handle(self):
        time.sleep(1)   
        left_point = self.ocr_int(304, 354, 373, 428)
        right_point = self.ocr_int(591, 352, 650, 426)
        if left_point >= right_point:
            self.click(338, 387)
        else:
            self.click(617, 395)

class RerollDiceEvent(CaravanEvent):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "RerollDiceEvent"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["reroll"])
    
    def handle(self):
        time.sleep(1)
        # 吃了料理锁定了点数没法重投
        if self.is_exists(CARAVAN_BTN["reroll"], is_black=True, black_threshold=2000):
            self.click(338, 387)
            return
        point = self.ocr_int(304, 354, 373, 428)
        if point <= 3:        
            self.click_btn(CARAVAN_BTN["reroll"])
        else:
            self.click(338, 387)