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
                if self.is_exists("img/ui/xinneirong.bmp"):
                    flag = True
                    break
                time.sleep(0.1)
            for _ in range(5):
                if self.is_exists("img/juqing/2_9_jiesuozhong.bmp"):
                    flag = True
                    break
                time.sleep(0.1)

            if flag:
                self.click_btn((JUQING_BTN["zhuxianjuqing"]), until_appear=(JUQING_BTN["wanfa"]))
                # 选择第几章
                time.sleep(1)
                r_list = self.img_where_all(img="img/juqing/new_content.bmp")
                # 检查剧情解锁中活动
                if not len(r_list):
                    r_list += self.img_where_all(img="img/juqing/2_9_jiesuozhong.bmp")
                if len(r_list):
                    x_arg = int(r_list[0])
                    y_arg = int(r_list[1]) + 50
                    time.sleep(1)
                    self.click_btn(p(x_arg, y_arg), until_disappear=(JUQING_BTN["wanfa"]))
                # 选择第几话（右上角玩法消失）
                time.sleep(1)
                # 先解锁
                if self.is_exists(JUQING_BTN["juqing_unlock"]):
                    time.sleep(1)
                    self.click_btn(JUQING_BTN["juqing_unlock"], until_appear=(JUQING_BTN["unlock_title"]))
                    time.sleep(1)
                    self.click_btn(JUQING_BTN["unlock_ok"], until_disappear=(JUQING_BTN["unlock_title"]))
                    time.sleep(0.5)
                    self.fclick(1, 1)

                r_list = self.img_where_all(img="img/juqing/new_content.bmp")
                if len(r_list):
                    x_arg = int(r_list[0]) + 200
                    y_arg = int(r_list[1]) + 50
                    time.sleep(1)
                    self.click_btn(p(x_arg, y_arg), retry=15, until_appear=[WZ_BTN["shujuxiazai"], JUQING_BTN["jiesuotiaojian"], JUQING_BTN["caidanyuan"]])
                    if self.is_exists(JUQING_BTN["jiesuotiaojian"]):
                        self.log.write_log("warning", "有尚未解锁的剧情，无法继续推进！")
                        break
                    self.guojuqing(story_type="zhuxian")
                else:
                    if self.handle_main_1_1():
                        self.log.write_log('info', "处理完第一章1-1剧情，返回")
                    elif self.handle_batong():
                        self.log.write_log('info', "处理完霸瞳皇帝，返回")
                    else:
                        self.log.write_log('info', "本章无新剧情")
                    self.lock_home()
                    continue
            else:
                self.log.write_log('info', "无新剧情")
                break
        self.lock_home()

    def handle_main_1_1(self):
        def scroll_down():
            time.sleep(1)
            obj = self.d.touch.down(934, 250)
            time.sleep(0.1)
            # 目前适配9+9 未来加page
            obj.move(934, 500)
            time.sleep(0.8)
            obj.up(934, 500)
            time.sleep(1)

        time.sleep(1)
        if self.is_exists("img/juqing/1_1_block.bmp"):
            scroll_down()
            r_list = self.img_where_all(img="img/juqing/new_content.bmp")
            # 特例
            if len(r_list):
                x_arg = int(r_list[0]) + 200
                y_arg = int(r_list[1]) + 50
                self.click_btn(p(x_arg, y_arg), retry=15, until_appear=[WZ_BTN["shujuxiazai"], JUQING_BTN["jiesuotiaojian"], JUQING_BTN["caidanyuan"]])

                if self.is_exists(WZ_BTN["shujuxiazai"].img, at=(435, 134, 523, 159)):
                    self.click_img(img=WZ_BTN["shujuxiazai_ok"].img, at=(557, 354, 620, 385))
                    time.sleep(2)

                # 选择快进剧情[选择支后再检测菜单圆]
                if self.is_exists(JUQING_BTN["caidanyuan"], method="sq"):
                    self.click_btn(JUQING_BTN["caidanyuan"], until_appear=(JUQING_BTN["auto"]))
                    if self.is_exists(JUQING_BTN["tiaoguo_1"], method="sq"):
                        # 快进确认弹出
                        self.click_btn(JUQING_BTN["tiaoguo_1"], until_appear=(JUQING_BTN["tiaoguo_2"]))
                        time.sleep(2)
                # 确认快进，包括视频和剧情
                if self.is_exists(JUQING_BTN["tiaoguo_2"]):
                    self.click_btn(JUQING_BTN["tiaoguo_2"])
                # 退出形式
                # 报酬确认 (好感度剧情)
                time.sleep(4)
                self.fclick(1, 1)
                return True

        return False

    def handle_batong(self):
        time.sleep(1)
        if self.is_exists("img/juqing/chap15_block.bmp"):
            self.click_btn(JUQING_BTN["chap15_block"])






