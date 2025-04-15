from core.constant import FIGHT_BTN
from scenes.scene_base import PCRSceneBase
import threading


class FightingBase(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "Fighting"
        self.feature = self.fun_feature_exist(FIGHT_BTN["fighting_caidan"])

    def set_auto(self, auto, screen=None, max_retry=3):
        if screen is None:
            screen = self.getscreen()
        self._a.set_fight_auto(auto, screen, max_retry)

    def set_speed(self, level, max_level=1, screen=None, max_retry=3):
        if screen is None:
            screen = self.getscreen()
        self._a.set_fight_speed(level, max_level, screen, max_retry)

    def set_set(self, set, screen=None, max_retry=3):
        if screen is None:
            screen = self.getscreen()
        self._a.set_fight_set(set, screen, max_retry)        

    def auto_and_fast(self, max_speed):
        self.set_auto(1, self.last_screen)
        self.set_speed(max_speed, max_speed, self.last_screen)

    def fighting_action(self, action_str=""):
        """
        action_str:
            仅应该包含12345这5种字符之一。
            连点控制：12345分别表示从左到右的5个位置是否需要在战斗中连点
            空字符串：什么都不会发生

        e.g.:
            with self.fighting_action("12"):
                # 其它命令，但是在执行的同时会并行执行连点操作
                ...
            # 结束连点
        """
        liandian_list = []
        for i in '12345':
            if i in action_str:
                liandian_list.append(int(i))
        parent = self

        class FightingAction:
            def __init__(self):
                self.thread_flag = True

            def action_thread(self):
                while self.thread_flag:
                    for ld in liandian_list:
                        parent.click(FIGHT_BTN["fighting_five_char"][ld])

            def __enter__(self):
                if action_str != "":
                    self.thread_flag = True
                    T = threading.Thread(target=self.action_thread, name="ActionThread", daemon=True)
                    T.start()

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.thread_flag = False

        return FightingAction()

class FightingWinBase(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightingWin"
        self.feature = self.win_feature

    def win_feature(self, screen):
        from core.constant import p
        duiwu_icon = p(909,88,img="img/fight/duiwu_icon.bmp",at=(895, 78, 923, 97))
        shbg = p(850,38,img="img/fight/shbg.bmp",at=(814, 27, 886, 49))
        return self.is_exists(duiwu_icon, screen=screen) and self.is_exists(shbg, screen=screen)


class FightingLoseBase(PCRSceneBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightingLose"
        self.feature = self.lose_feature

    def lose_feature(self, screen):
        from core.constant import p
        duiwu_icon = p(851, 36, img="img/fight/duiwu_icon.bmp", at=(828, 17, 871, 52))
        shbg = p(731, 37, img="img/fight/shbg.bmp", at=(684, 23, 778, 51))
        # 伤害报告在上，队伍图标在下，主线失败
        lose_feature_1 = self.is_exists(duiwu_icon, screen=screen) and self.is_exists(shbg, screen=screen)
        duiwu_icon = p(910, 35, img="img/fight/duiwu_icon.bmp", at=(896, 25, 924, 44))
        shbg = p(790, 37, img="img/fight/shbg.bmp", at=(754, 26, 826, 48))
        # 伤害报告在左，队伍图标在右，活动失败
        lose_feature_2 = self.is_exists(duiwu_icon, screen=screen) and self.is_exists(shbg, screen=screen)
        return lose_feature_1 or lose_feature_2
