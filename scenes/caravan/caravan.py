from typing import Union
from core.constant import CARAVAN_BTN, MAIN_BTN
from core.pcr_checker import ContinueNow, PCRRetry, RetryNow
from scenes.caravan.caravan_event import *
from scenes.root.seven_btn import SevenBTNMixin
from scenes.scene_base import PCRSceneBase, PossibleSceneList

class FirstEnterCaravan(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FirstEnterCaravan"
        
        def feature(screen):
            return not self.is_exists(CARAVAN_BTN["peko_dice"], screen=screen) and not self.is_exists(CARAVAN_BTN["peko_dice_triple"], screen=screen)
        
        self.feature = feature
    
    def skip(self, buy_shop, gacha):
        dice = AfterThrowDice(self._a, buy_shop, gacha)
        dice.handle()
        return self.goto(CaravanMenu, gotofun=self.fun_click(1, 1), use_in_feature_only=True, interval=0.5)

class CaravanMenu(SevenBTNMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "CaravanMenu"
        self.throw_btn = CARAVAN_BTN["peko_dice"]
        
        def feature(screen):
            return self.is_exists(CARAVAN_BTN["peko_dice"], screen=screen) or self.is_exists(CARAVAN_BTN["peko_dice_triple"], screen=screen)
        
        self.feature = feature
    
    def get_dice_mode(self, screen=None, max_retry=3) -> int:
        """
        当前骰子模式，0为投掷一个，1为投掷三个，-1为检测失败
        """    
        MODE_DICT = {
            0: CARAVAN_BTN["dice_unselected"],
            1: CARAVAN_BTN["dice_selected"],
        }  
        out = self.check_dict_id(MODE_DICT, screen, max_retry=max_retry)
        if out is None:
            return -1
        else:
            self.throw_btn = CARAVAN_BTN["peko_dice"] if out == 0 else CARAVAN_BTN["peko_dice_triple"]
            return out      
        
    def set_dice_mode(self, mode, screen=None, max_retry=3) -> bool:
        """
        设置骰子模式，0为投掷一个，1为投掷三个
        """
        @PCRRetry(delay=0.5, max_retry=max_retry, raise_return=False)      
        def fun():
            nonlocal screen
            current_mode = self.get_dice_mode(screen, 3)
            if current_mode == -1:
                raise RetryNow()
            if current_mode == mode:
                return True
            else:
                self.click(CARAVAN_BTN["dice_unselected"], post_delay=1.5)  # 避免涟漪影响
                screen = self.getscreen()
                raise ContinueNow()                
        
        return fun()         
        
    def have_dice(self):
        black_threshold = 2000 if self.get_dice_mode() == 0 else 3000
        if self.is_exists(self.throw_btn, is_black=True, black_threshold=black_threshold):
            self.log.write_log("info", "没有骰子了！")
            return False
        return True

    def get_dice_number(self):
       try:
           num = self.ocr_int(902, 308, 927, 324)
           return num
       except Exception as e:
           return 0

    def goto_dishmenu(self) -> "CaravanDishMenu":
        return self.goto(CaravanDishMenu, gotofun=self.fun_click(CARAVAN_BTN["dish"]), use_in_feature_only=True)
    
    def throw_dice(self, buy_shop, gacha):
        self.lock_img(self.throw_btn, elseclick=(1, 1), elsedelay=1)
        self.click_btn(self.throw_btn)
        dice = AfterThrowDice(self._a, buy_shop, gacha)
        dice.handle()

class CaravanDishMenu(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "CaravanDishMenu"
        self.feature = self.fun_feature_exist(CARAVAN_BTN["dish_list"])

    def close(self):
        self.exit(self.fun_click(1, 1), interval=1)

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
        self.exit(self.fun_click(586, 478), interval=1)

class AfterThrowDice(PossibleSceneList):
    def __init__(self, a, buy_shop, gacha):
        self.ConfirmThrowDice = ConfirmThrowDice
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
        self.AddDiceEvent = AddDiceEvent
        self.SelectDiceEvent = SelectDiceEvent
        self.RerollDiceEvent = RerollDiceEvent
        self.GoalLottery = GoalLottery
        scene_list = [
            ConfirmThrowDice(a),
            Fork(a),
            Gacha(a, gacha),
            MileShop(a, buy_shop),
            Game(a),
            Gaming(a),
            GameResult(a),
            Event(a),
            Slot(a),       
            DishOverflow(a),
            GoalTreasure(a),
            GoalSummary(a),
            GoalLottery(a),
            CaravanMenu(a),
            AddDiceEvent(a),
            SelectDiceEvent(a),
            RerollDiceEvent(a)
        ]
        super().__init__(a, scene_list, double_check=0.)
        
    def check(self, double_check=None, check_double_scene=None, timeout=None, max_retry=None, no_scene_feature=None) -> Union["CaravanEvent", "CaravanMenu"]:
        return super().check(double_check, check_double_scene, timeout, max_retry, no_scene_feature)
    
    def handle(self):
        last_time = time.time()
        while True:
            time.sleep(1)
            if time.time() - last_time > 90:
                raise Exception("投骰子处理时间过长！")                
            out = self.check()
            if out is None:
                self.click(1, 1)
            if isinstance(out, CaravanEvent):
                out.handle() 
            if isinstance(out, CaravanMenu):
                break          

class AfterGoToCaravan(PossibleSceneList):
    def __init__(self, a):
        self.CaravanMenu = CaravanMenu(a)
        self.FirstEnterCaravan = FirstEnterCaravan(a)
        scene_list = [
            CaravanMenu(a),
            FirstEnterCaravan(a)
        ]
        super().__init__(a, scene_list, double_check=0.)