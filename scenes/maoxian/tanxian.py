import time
from core.constant import MAIN_BTN, DXC_ELEMENT, TANXIAN_BTN
from core.pcr_checker import LockTimeoutError
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
        counter = 0
        while True:
            time.sleep(5)       
            if self.is_exists(TANXIAN_BTN["event_notice"], threshold=0.7):     
                self.click(TANXIAN_BTN["event_notice"])
                counter += 1
                if counter > 6:
                    # 避免死循环
                    self.log.write_log("warning", "event识别有问题，跳出")
                    return
                time.sleep(2)
                self.lock_no_img(TANXIAN_BTN["adventure_dest"], elseclick=(480, 270), elsedelay=1)
                last_time = time.time()
                while True:
                    if time.time() - last_time > 90:
                        raise LockTimeoutError("事件处理超时！")
                    time.sleep(1)
                    if self.click_skip():
                        break
                self.lock_img(TANXIAN_BTN["adventure_dest"], elseclick=(1, 1), elsedelay=1)        
                continue
            else:
                self.log.write_log("info","无事件")  
                break 
        self.log.write_log("info","event处理完毕!") 

    def click_skip(self):
        lst = self.img_where_all(img="img/juqing/xuanzezhi_1.bmp")
        if len(lst) > 0:
            self.click(int(lst[0]), int(lst[1]))
            return True
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
    