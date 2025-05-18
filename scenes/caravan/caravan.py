'''
Description: 
Author: clm
Date: 2025-05-16 15:01:44
LastEditors: clm
LastEditTime: 2025-05-18 13:06:03
'''
'''
Description: 
Author: clm
Date: 2025-05-16 15:01:44
LastEditors: clm
LastEditTime: 2025-05-16 16:23:07
'''
from core.constant import CARAVAN_BTN, MAIN_BTN
from scenes.caravan.caravan_event import *
from scenes.root.seven_btn import SevenBTNMixin
from scenes.scene_base import PCRSceneBase, PossibleSceneList

class FirstEnterCaravan(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FirstEnterCaravan"
        
        def feature(screen):
            return not self.is_exists(CARAVAN_BTN["peko_dice"], screen=screen)
        
        self.feature = feature
    
    def skip(self):
        return self.goto(CaravanMenu, gotofun=self.fun_click(1, 1), use_in_feature_only=True, interval=0.5)

class CaravanMenu(SevenBTNMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "CaravanMenu"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["peko_dice"])
        
    def have_dice(self):
        if self.is_exists(CARAVAN_BTN["peko_dice"], is_black=True, black_threshold=2000):
            self.log.write_log("info", "没有骰子了！")
            return False
        return True

    def get_dice_number(self):
       try:
           num = self.ocr_int(906, 324, 943, 342)
           return num
       except Exception as e:
           return 0

    def goto_dishmenu(self) -> "CaravanDishMenu":
        return self.goto(CaravanDishMenu, gotofun=self.fun_click(CARAVAN_BTN["dish"]), use_in_feature_only=True)
    
    def throw_dice(self) -> "AfterThrowDice":
        self.click_btn(CARAVAN_BTN["peko_dice"])
        return AfterThrowDice(self._a)

class CaravanDishMenu(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "CaravanDishMenu"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["dish_list"])

    def close(self):
        self.lock_img(CARAVAN_BTN["peko_dice"], elseclick=(1, 1), elsedelay=1)

    def eat_first(self) -> "EatConfirm":
        if self.is_exists(CARAVAN_BTN["eat"],is_black=True, black_threshold=600):
            self.log.write_log("info", "似乎没法吃第一个,跳过")
            self.close()
            return None
        else:
            return self.goto(EatConfirm, gotofun=self.fun_click(394, 286), use_in_feature_only=True)

class EatConfirm(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "EatConfirm"
        
        def feature(screen):
            return self.is_exists(CARAVAN_BTN["eat_confirm"], screen=screen) or self.is_exists(CARAVAN_BTN["confirm_eat"], screen=screen)
        
        self.feature = feature

    def ok(self):
        self.click(586, 478)
        self.lock_img(CARAVAN_BTN["peko_dice"], elseclick=(1, 1), elsedelay=1)

class AfterThrowDice(PossibleSceneList):
    def __init__(self, a):
        self.ConfirmThrowDice = ConfirmThrowDice(a)
        self.Fork = Fork
        self.Gacha = Gacha
        self.MileShop = MileShop
        self.Game = Game
        self.Gaming = Gaming
        self.Gameresult = GameResult
        self.Event = Event
        self.Slot = Slot
        self.DishOverflow = DishOverflow
        self.GoalTreasure = GoalTreasure
        self.GoalSummary = GoalSummary
        self.CaravanMenu = CaravanMenu
        scene_list = [
            ConfirmThrowDice(a),
            Fork(a),
            Gacha(a),
            MileShop(a),
            Game(a),
            Gaming(a),
            GameResult(a),
            Event(a),
            Slot(a),       
            DishOverflow(a),
            GoalTreasure(a),
            GoalSummary(a),
            CaravanMenu(a),
        ]
        super().__init__(a, scene_list, double_check=0.)

class AfterGoToCaravan(PossibleSceneList):
    def __init__(self, a):
        self.CaravanMenu = CaravanMenu(a)
        self.FirstEnterCaravan = FirstEnterCaravan(a)
        scene_list = [
            CaravanMenu(a),
            FirstEnterCaravan(a)
        ]
        super().__init__(a, scene_list, double_check=0.)