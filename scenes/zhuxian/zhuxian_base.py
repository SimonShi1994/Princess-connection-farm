import time
from typing import TYPE_CHECKING

from core.constant import MAOXIAN_BTN, ZHUXIAN_ID, ZHUXIAN_SECOND_ID
from core.pcr_checker import retry_run
from scenes.errors import MaoxianRecognizeError, ZhuxianIDRecognizeError
from scenes.fight.fightinfo_zhuxian import FightInfoZhuXian
from scenes.root.seven_btn import SevenBTNMixin

if TYPE_CHECKING:
    from scenes.zhuxian.zhuxian_normal import ZhuXianNormal
    from scenes.zhuxian.zhuxian_hard import ZhuXianHard


class ZhuXianBase(SevenBTNMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name="ZhuXianBase"
        self.maoxian_screen_state=None
        self.maoxian_id=None

    def goLeft(self):
        self.click(35, 275, post_delay=3)

    def goRight(self):
        self.click(925, 275, post_delay=3)

    def check_maoxian_screen(self, screen=None, is_raise=True):
        """
        获得冒险界面屏幕状态
        :return:
        1:  Normal图
        2： Hard图
        """
        sc = screen if screen is not None else self.getscreen()
        pn1 = self.img_prob(MAOXIAN_BTN["normal_on"], screen=sc)
        ph1 = self.img_prob(MAOXIAN_BTN["hard_on"], screen=sc)
        if pn1 > 0.9:
            self.maoxian_screen_state=1
            return 1
        elif ph1 > 0.9:
            self.maoxian_screen_state=2
            return 2
        else:
            if is_raise:
                self._raise(MaoxianRecognizeError, f"冒险识别失败！ Normal {pn1} Hard {ph1}")
            else:
                return -1

    def check_zhuxian_id(self, screen=None, max_retry=2):
        """
        识别主线图的图号
        2020-08-14 Add: By TheAutumnOfRice :
            只要截图截的小，普通困难都打倒！
        :param: screen:设置为None时，第一次重新截图
        :param max_retry: 找图失败最多尝试次数
        :return:
        1~ ：图号
        """

        # self.Drag_Left()  # 保证截图区域一致
        def fun():
            id = self.check_dict_id(ZHUXIAN_ID, screen, diff_threshold=0)
            for second in ZHUXIAN_SECOND_ID:
                if id in second:
                    id = self.check_dict_id(ZHUXIAN_SECOND_ID[second], screen, diff_threshold=0.1)
                    break
            if id is None:
                self._raise(ZhuxianIDRecognizeError)
            self.maoxian_id = id
            return id

        return retry_run(fun,max_retry)


    def Drag_Right(self):
        self._a.d.touch.down(600, 120).sleep(0.1).move(200, 120).sleep(0.2).up(200, 120)
        # self.d.drag(600, 270, 200, 270, 0.1)  # 拖拽到最右
        time.sleep(self._a.change_time)

    def Drag_Left(self):
        self._a.d.touch.down(200, 120).sleep(0.1).move(600, 120).sleep(0.2).up(600, 120)
        # self.d.drag(200, 270, 600, 270, 0.1)  # 拖拽到最左
        time.sleep(self._a.change_time)

    def click_xy_and_open_fightinfo(self, x, y) -> "FightInfoZhuXian":
        def gotofun():
            self.click(x, y)

        return self.goto(FightInfoZhuXian, gotofun)

    def goto_normal(self) -> "ZhuXianNormal":
        from scenes.zhuxian.zhuxian_normal import ZhuXianNormal
        def gotofun():
            self.click_img(self.last_screen, MAOXIAN_BTN["normal_on"])

        return self.goto(ZhuXianNormal, gotofun)  # Type:ZhuXianNormal

    def goto_hard(self) -> "ZhuXianHard":
        from scenes.zhuxian.zhuxian_hard import ZhuXianHard
        def gotofun():
            self.click_img(self.last_screen,MAOXIAN_BTN["hard_on"])
        return self.goto(ZhuXianHard,gotofun)  # Type:ZhuXianHard

