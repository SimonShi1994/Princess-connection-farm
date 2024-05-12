from automator_mixins._fight_base import FightBaseMixin
from core.constant import MAIN_BTN, JJC_BTN


class JJCMixin(FightBaseMixin):
    """
    竞技场插片
    包含日常行动相关的脚本
    """

    # 进入jjc
    # 做jjc任务
    def doJJC(self):
        # 进入jjc
        self.lock_home()
        self.click_btn(MAIN_BTN["maoxian"], until_appear=MAIN_BTN["zhuxian"])
        self.lock_img(JJC_BTN["arena"], elseclick=[MAIN_BTN["arena"], (1, 290)], elsedelay=1)
        self.lock_img(JJC_BTN["list"], elseclick=[JJC_BTN["arena_pos"], (1, 290)], elsedelay=1)
        self.click_btn(JJC_BTN["shouqu"], until_appear=JJC_BTN["shouqu_ok"],
                       elsedelay=4, retry=2, side_check=self.right_kkr)
        for _ in range(5):
            self.click(24, 84)

        # 小心编组设定
        with self.ES(self.bianzusheding_initFC()):
            out = self.lock_img({
                JJC_BTN["zdks"]: 1,
                JJC_BTN["tzcs"]: 2,
            }, is_raise=False, elseclick=JJC_BTN["player"], elsedelay=4, timeout=30)
            if not out:
                self.log.write_log("error", "无法进入战斗竞技场！")
                self.lock_home()
                return
            if out == 2:
                self.log.write_log("info", "战斗竞技场次数不足！")
                self.lock_home()
                return
            self.click_btn(JJC_BTN["zdks"])
            # 803 496
            self.wait_for_loading(delay=2)
            self.set_fight_speed(2, 2)
        self.lock_img(JJC_BTN["list"], timeout=180, elseclick=[(803, 496), (1, 1),(914,353)], elsedelay=8)
        self.lock_home()
        # 做pjjc任务

    def doPJJC(self):
        self.lock_home()
        self.click_btn(MAIN_BTN["maoxian"], until_appear=MAIN_BTN["zhuxian"])
        self.lock_img(JJC_BTN["arena"], elseclick=[MAIN_BTN["arena"], (1, 290)], elsedelay=1)
        self.lock_img(JJC_BTN["plist"], elseclick=[JJC_BTN["p_arena_pos"], (1, 290)], elsedelay=1)
        self.click_btn(JJC_BTN["shouqu"], until_appear=JJC_BTN["shouqu_ok"],
                       elsedelay=4, retry=2, side_check=self.right_kkr)
        for _ in range(5):
            self.click(24, 84)

        # 小心编组设定
        with self.ES(self.bianzusheding_initFC()):
            out = self.lock_img({
                JJC_BTN["dwbz"]: 1,
                JJC_BTN["tzcs"]: 2,
            }, is_raise=False, elseclick=JJC_BTN["player"], elsedelay=4, timeout=30)
            if not out:
                self.log.write_log("error", "无法进入公主竞技场！")
                self.lock_home()
                return
            if out == 2:
                self.log.write_log("info", "公主竞技场次数不足！")
                self.lock_home()
                return
            for _ in range(10):
                self.click(843, 452, post_delay=0.5)
            # 843, 452
            self.wait_for_loading(delay=2)
            self.set_fight_speed(2, 2)
        self.lock_img(JJC_BTN["plist"], timeout=180 * 3, elseclick=[(803, 506), (1, 1),(914,353)], elsedelay=8)
        self.lock_home()
