from core.constant import MAOXIAN_BTN
from core.pcr_checker import PCRRetry, RetryNow
from scenes.errors import ZhuxianIDRecognizeError
from scenes.zhuxian.zhuxian_base import ZhuXianBase


class ZhuXianVH(ZhuXianBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ZhuXianVH"

        def feature(screen):
            if not self.is_exists(MAOXIAN_BTN["ditu"], screen=screen):
                return False
            state = self.check_maoxian_screen(screen, is_raise=False)
            return state == 3

        self.feature = feature

    def check_vh_id(self, screen=None):
        return self.check_zhuxian_id(screen)

    @PCRRetry(None, 5, raise_return=False, delay=2)
    def select_vh_id(self, id):
        """
        走到vh的几图
        要求场景：已经在normal内
        :param id: 图号
        """
        sc = self.getscreen()
        try:
            cur_id = self.check_vh_id(sc)
        except ZhuxianIDRecognizeError as e:
            # 跳过大部分对话框
            # for _ in range(6):
            #     self.click(1,1)
            # 重进，防止不显示图号
            zhuye = self._a.get_zhuye()
            zhuye.goto_maoxian().goto_vh()
            # 防止未更新图的情况
            if self.is_exists(MAOXIAN_BTN["ditu"], screen=sc):
                for _ in range(3):
                    self.goLeft()
            else:
                raise e
            raise RetryNow()

        if cur_id < id:
            for i in range(id - cur_id):
                self.goRight()
        else:
            for i in range(cur_id - id):
                self.goLeft()
        cur_id = self.check_vh_id()
        if cur_id != id:
            raise RetryNow()
        return True
