from typing import TYPE_CHECKING, Union
from core.cv import UIMatcher
from core.constant import MAIN_BTN, MAOXIAN_BTN, ZHUCAIDAN_BTN,HAOYOU_BTN
from core.pcr_checker import LockTimeoutError
from scenes.root.seven_btn import SevenBTNMixin

class HaoYouRoot(SevenBTNMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "HaoYouRoot"
        self.initFC = None
        self.feature = self.fun_feature_exist(HAOYOU_BTN["hualin_root"])

    def goto_haoyouguanli(self)->"HaoYouGuanLi":
        return self.goto(HaoYouGuanLi, self.fun_click(HAOYOU_BTN["haoyouguanli_w"]))


class HaoYouGuanLi(SevenBTNMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "HaoYouGuanLi"
        self.initFC = None
        self.feature = self.fun_feature_exist(HAOYOU_BTN["hualin_guanli"])

    def search_friend(self,friend_id:str):
        """
        按照ID添加好友
        """
        self.click_btn(HAOYOU_BTN["xunzhaohaoyou"],until_appear=HAOYOU_BTN["sousuosheding"])
        self.click_btn(HAOYOU_BTN["sousuosheding"],until_appear=HAOYOU_BTN["wanjiaidsousuo"])
        self.fclick(281,220,post_delay=1)  # 玩家ID
        self.click(491,238,post_delay=1)  # 输入框
        self._a.d.send_keys(friend_id,clear=True)
        self.fclick(698, 141, pre_delay=1,post_delay=1)  # 关闭窗口
        self.lock_no_img(HAOYOU_BTN["wanjiaidsousuo"],elseclick=(580,370))
        self.lock_img(HAOYOU_BTN["hysqqr_gl"],elseclick=(829,196))
        self.lock_no_img(HAOYOU_BTN["hysqqr_gl"],elseclick=(587,368))
        self.fclick(1,1,times=10,pre_delay=1)  # OK
        self.lock_no_img(HAOYOU_BTN["sqhy"],elseclick=(479,368))  # 已经添加了好友


    def accept_friend(self,
                      name_prefix_valid:str=None,
                      gonghui_prefix_valid:str=None,
                      all_reject=False,
                      ):
        """
        通过好友申请
        可以增加验证前缀：要求所属工会或者名称的前缀为指定值。
        开启all_reject时，清空全部申请列表
        """
        # 先寻找好友，再检测搜索设定按钮的消失
        self.click_btn(HAOYOU_BTN["xunzhaohaoyou"],until_appear=HAOYOU_BTN["sousuosheding"])
        self.lock_no_img(HAOYOU_BTN["sousuosheding"],elseclick=(553,27))

        def CheckExist(screen=None):
            # 是否还有申请？检测最上面是不是一片空白（方差过小）
            if screen is None:
                screen = self.getscreen()
            at = (363, 134, 902, 195)
            bd = UIMatcher.img_cut(screen,at)
            s = bd.std()
            return s>10

        def DoOne():
            # 进行一次选择
            accept = not all_reject
            if accept and name_prefix_valid is not None or gonghui_prefix_valid is not None:
                self.check_ocr_running()
                # 验证名称
                self.click_btn(HAOYOU_BTN["info_btn"],until_appear=HAOYOU_BTN["jianjie"])
                sc = self.getscreen()
                if name_prefix_valid is not None:
                    nam = self.ocr_center(*HAOYOU_BTN["name_box"].at,screen_shot=sc)
                    if nam == -1:
                        self.log.write_log("error","OCR识别错误：无法识别好友名称，跳过该验证！")
                    else:
                        if nam.startswith(name_prefix_valid):
                            self.log.write_log("info",f"【√】识别到好友：{nam} 以 {name_prefix_valid} 为前缀，验证通过。")
                        else:
                            self.log.write_log("info", f"【×】好友申请 {nam} 不以 {name_prefix_valid} 为前缀，验证失败！")
                            accept = False

                if accept and gonghui_prefix_valid is not None:
                    nam = self.ocr_center(*HAOYOU_BTN["hanghui_box"].at, screen_shot=sc)
                    if nam == -1:
                        self.log.write_log("error", "OCR识别错误：无法识别好友公会，跳过该验证！")
                    else:
                        if nam.startswith(gonghui_prefix_valid):
                            self.log.write_log("info", f"【√】识别到公会{nam} 以 {gonghui_prefix_valid} 为前缀，验证通过。")
                        else:
                            self.log.write_log("info", f"【×】公会 {nam} 不以 {gonghui_prefix_valid} 为前缀，验证失败！")
                            accept = False
            self.fclick(1,1,post_delay=1)
            if accept:
                self.click_btn(HAOYOU_BTN["accept_btn"],until_appear=HAOYOU_BTN["hysqtgqr"])
                self.lock_no_img(HAOYOU_BTN["hysqtgqr"],elseclick=(587,364)),
                self.fclick(1, 1, times=10, pre_delay=1)  # OK
            else:
                self.click_btn(HAOYOU_BTN["reject_btn"],until_appear=HAOYOU_BTN["hysqjjqr"])
                self.lock_no_img(HAOYOU_BTN["hysqjjqr"],elseclick=(587,364)),
                self.fclick(1, 1, times=10, pre_delay=1)  # OK

        while CheckExist():
            DoOne()













