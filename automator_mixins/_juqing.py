import time
from core.constant import MAIN_BTN,  JUQING_BTN, p
from automator_mixins._tools import ToolsMixin


class JuQingMixin(ToolsMixin):

    def guozhuxianjuqing(self, type="zhuxian"):
        while True:
            self.click_btn(MAIN_BTN["juqing"], until_appear=(JUQING_BTN["zhuxianjuqing"]))
            if self.is_exists("img/ui/xinneirong.bmp", at=(462, 70, 495, 87)):
                self.click_btn((JUQING_BTN["zhuxianjuqing"]), until_appear=(JUQING_BTN["wanfa"]))
                self.click(765, 125)
                time.sleep(3)
                r_list = self.img_where_all(img="img/juqing/new_content.bmp")
                x_arg = int(r_list[0])+200
                y_arg = int(r_list[1])+50
                self.click_btn(p(x_arg, y_arg), until_appear=(JUQING_BTN["quxiao"]))
                self.guojuqing()
            else:
                print("无新剧情")
                break

