import time
from core.constant import MAIN_BTN,  JUQING_BTN, WZ_BTN, p
from automator_mixins._tools import ToolsMixin


class JuQingMixin(ToolsMixin):

    def guozhuxianjuqing(self, type="zhuxian"):
        self.lock_home()
        while True:
            self.click_btn(MAIN_BTN["juqing"], until_appear=(JUQING_BTN["zhuxianjuqing"]))

            flag = False
            for _ in range(5):
                if self.is_exists("img/ui/xinneirong.bmp", at=(462, 70, 495, 87)):
                    flag = True
                    break
                time.sleep(0.1)

            if flag:
                self.click_btn((JUQING_BTN["zhuxianjuqing"]), until_appear=(JUQING_BTN["wanfa"]))
                # 选择第几章
                r_list = self.img_where_all(img="img/juqing/new_content.bmp")
                if len(r_list):
                    x_arg = int(r_list[0]) + 200
                    y_arg = int(r_list[1]) + 50
                    self.click_btn(p(x_arg, y_arg), until_disappear=(JUQING_BTN["wanfa"]))
                # 选择第几话（右上角玩法消失）
                time.sleep(1)
                r_list = self.img_where_all(img="img/juqing/new_content.bmp")
                if len(r_list):
                    x_arg = int(r_list[0]) + 200
                    y_arg = int(r_list[1]) + 50

                    self.click_btn(p(x_arg, y_arg), retry=15, until_appear=[WZ_BTN["shujuxiazai"], JUQING_BTN["jiesuotiaojian"]])
                    if self.is_exists(JUQING_BTN["jiesuotiaojian"]):
                        self.log.write_log("warning", "有尚未解锁的剧情，无法继续推进！")
                        break

                self.guojuqing(story_type="zhuxian")
            else:
                self.log.write_log('info', "无新剧情")
                break
        self.lock_home()
