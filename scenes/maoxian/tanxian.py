import time
from core.constant import MAIN_BTN, DXC_ELEMENT, TANXIAN_BTN
from scenes.scene_base import PCRSceneBase, PossibleSceneList
from ..root.seven_btn import SevenBTNMixin

class AfterGotoTanXian(PossibleSceneList):
    def __init__(self, a):
        self.TanXianMenu = TanXianMenu
        self.TeamViewBack = TeamViewBack
        scene_list = [
            TanXianMenu(a),
            TeamViewBack(a)
        ]
        super().__init__(a, scene_list, double_check=0.)        

class TanXianMenu(SevenBTNMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "TanXianMenu"
        # self.feature = self.fun_feature_exist(TANXIAN_BTN["tanxian_logo"])
        self.feature = self.fun_feature_exist(TANXIAN_BTN["adventure_dest"])
        self.initFC = lambda FC: FC.getscreen().add_sidecheck(self._a.juqing_kkr)
    
    def handle_event(self):
        while True:
            time.sleep(5)
            counter = 0
            if self.is_exists(TANXIAN_BTN["event_notice"], threshold=0.7):     
                self.click(TANXIAN_BTN["event_notice"])
                counter += 1
                if counter >=4:
                    # 避免死循环
                    self.log.write_log("warning", "event识别有问题，跳出")
                    return
                time.sleep(1)
                r_list = self.img_where_all(TANXIAN_BTN["event_map"].img, method="sq")
                if len(r_list) == 0:
                    # 特殊事件,数量太少没怎么测过
                    self.log.write_log("info", "有特殊事件")
                    event_sp_pos = self.img_where_all(TANXIAN_BTN["event_map_sp"].img, method="sq")
                    if len(event_sp_pos) > 0:
                        self.fclick(event_sp_pos[0] - 10, event_sp_pos[1] - 55)
                        while True:
                            time.sleep(3)
                            # 有些特殊事件有跳过
                            if self.click_skip():
                                break 
                            # 没跳过的选第一个选项   
                            lst = self.img_where_all(img="img/juqing/xuanzezhi_1.bmp")
                            if len(lst) > 0:
                                self.click(int(lst[0]), int(lst[1]))
                                break
                    else:
                        # 以后会出的另一种事件
                        event_white_pos = self.img_where_all(TANXIAN_BTN["event_map_white"].img, method="sq")
                        if len(event_white_pos) > 0:
                            self.fclick(event_white_pos[0] - 10, event_white_pos[1] - 55)
                            while True:
                                time.sleep(3)
                                if self.click_skip():
                                    break 
                else:
                    self.fclick(r_list[0] - 10, r_list[1] - 55)
                    while True:
                        time.sleep(3)
                        if self.click_skip():
                            break
                self.lock_img(TANXIAN_BTN["adventure_dest"], elseclick=(1, 1), elsedelay=1)        
                continue
            else:
                self.log.write_log("info","无事件")  
                break 
        self.log.write_log("info","event处理完毕!") 

    def click_skip(self):
        if self.is_exists(TANXIAN_BTN["skip"]):
            self.click_btn(TANXIAN_BTN["skip"])
            return True
        elif self.is_exists(TANXIAN_BTN["skip2"]):
            # 某些事件的跳过位置偏下
            self.click_btn(TANXIAN_BTN["skip2"])  
            return True 
        else:
            return False                

    def goto_teamview(self) -> "AfterGotoTeamView":
        if self.is_exists(TANXIAN_BTN["team_view_off"], method="sq"):
            self.log.write_log("warning", "队伍可能未出发!")
            return None
        else:
            self.click_btn(TANXIAN_BTN["team_view"])
            return AfterGotoTeamView(self._a)        

        
        

class AfterGotoTeamView(PossibleSceneList):
    def __init__(self, a):
        self.TeamViewBack = TeamViewBack
        self.TeamViewNoBack = TeamViewNoBack
        scene_list = [
            TeamViewBack(a),
            TeamViewNoBack(a)
        ]
        super().__init__(a, scene_list, double_check=0.)   

class TeamViewBack(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "TeamViewBack"
        self.feature = self.fun_feature_exist(TANXIAN_BTN["have_team_back"])
    
    def confirm_back(self):
        self.click_btn(TANXIAN_BTN["confirm_back"], wait_self_before=True)
        while True:
            time.sleep(1)
            counter = 0
            if self.is_exists(TANXIAN_BTN["tiaoguowanbi"]):
                self.click_btn(TANXIAN_BTN["tiaoguowanbi"])
                continue
            if self.is_exists(TANXIAN_BTN["chongxinchufa"]):
                self.click_btn(TANXIAN_BTN["chongxinchufa"])
                continue
            if self.is_exists(TANXIAN_BTN["chufa"]):    
                self.click_btn(TANXIAN_BTN["chufa"])
                self.lock_img(TANXIAN_BTN["adventure_dest"], elseclick=(1, 1), elsedelay=1)
                break
            # 跳过时会偶尔出现特别事件,狂点左上角即可
            self.fclick(1, 1)
            counter += 1
            if counter >= 4:
                self.log.write_log("warning", "处理一键归来&出发有问题，跳出")
                return   
        self.log.write_log("info","一键归来&出发处理完毕!")    

class TeamViewNoBack(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "TeamViewNoBack"
        self.feature = self.fun_feature_exist(TANXIAN_BTN["no_team_back"])
    
    def close(self):
        self.click(483,475)
    