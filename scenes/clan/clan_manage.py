import time

from core.constant import HANGHUI_BTN
from scenes.root.seven_btn import SevenBTNMixin
from core.pcr_checker import LockTimeoutError


class ClanBase(SevenBTNMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ClanBase"
        self.feature = self.fun_feature_exist(HANGHUI_BTN["chengyuanxinxi"])

    def goto_clanmember(self) -> "ClanMember":
        return self.goto(ClanMember, self.fun_click(HANGHUI_BTN["chengyuanxinxi"]))


class ClanMember(ClanBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ClanMember"
        self.feature = self.fun_feature_exist(HANGHUI_BTN["jiangxu_chengyuan"])

    def goto_exitclan(self) -> "NoClan":
        return self.goto(NoClan, self.fun_click(HANGHUI_BTN["exit_clan"]))

    '''
    sortflag:0 默认值; 1 按战力; 2 按职务
    '''
    def sortmember(self, sortflag):
        self.click_btn(HANGHUI_BTN["chengyuanpaixu"], elsedelay=5, until_appear=HANGHUI_BTN["paixuqueren"])
        if sortflag == 1:
            self.fclick(287, 295)
            self.click_btn(HANGHUI_BTN["paixuqueren"], elsedelay=5, until_disappear=HANGHUI_BTN["paixuqueren"])

        return

    def like(self, sortflag):
        if sortflag == 0 or sortflag == 1:
            if self.is_exists('img/dianzan.bmp'):
                click_list = [(826, 198), (826, 316), (826, 428)]
                for i in click_list:
                    if self.lock_img('img/dianzan.bmp', ifclick=[i], elseclick=[(480, 374)], retry=10):
                        if self.lock_img('img/queren.bmp', retry=8):
                            self.lock_no_img('img/queren.bmp', elseclick=[(480, 374)], retry=10)
                            continue
                        else:
                            self.log.write_log("warning", "已经没有点赞次数了")
                            self.lock_home()
                            break
                    else:
                        self.log.write_log("error", "找不到点赞按钮")
                        self.lock_home()
                        break
        if sortflag == 2:
            if self.is_exists('img/dianzan.bmp'):
                click_list = [(826, 198), (826, 316), (826, 428)]
                for i in click_list:
                    if self.lock_img('img/dianzan.bmp', ifclick=[i], elseclick=[(480, 374)], retry=10):
                        if self.lock_img('img/queren.bmp', retry=8):
                            self.lock_no_img('img/queren.bmp', elseclick=[(480, 374)], retry=10)
                            continue
                        else:
                            self.log.write_log("warning", "已经没有点赞次数了")
                            self.lock_home()
                            break
                    else:
                        self.log.write_log("error", "找不到点赞按钮")
                        self.lock_home()
                        break



class NoClan(SevenBTNMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "NoClan"
        self.feature = self.fun_feature_exist(HANGHUI_BTN["sheding_join"])



