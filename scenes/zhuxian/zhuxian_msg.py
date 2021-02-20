from core.constant import FIGHT_BTN, MAOXIAN_BTN

from typing import TYPE_CHECKING

from core.constant import FIGHT_BTN, MAOXIAN_BTN
from core.pcr_checker import GotoException
from scenes.scene_base import PCRMsgBoxBase

if TYPE_CHECKING:
    from core.Automator import Automator


class AfterFightException:
    def __init__(self, a: "Automator"):
        self._a = a
        self.info = {}

    def do_xianding(self):
        # TODO !!!
        pass

    def make_FC(self):
        FC = self._a.getFC(False)
        FC.getscreen()
        # 限定商店
        FC.exist(MAOXIAN_BTN["xianding"], raise_=GotoException("xianding"))
        # 超出物品上限
        FC.exist(MAOXIAN_BTN["chaochushangxian"], raise_=GotoException("chaochushangxian"))
        # 等级提升
        FC.exist(FIGHT_BTN["dengjitisheng"], raise_=GotoException("dengjitisheng"))
        # 公会战
        FC.exist(MAOXIAN_BTN["tuanduizhan"], raise_=GotoException("tuanduizhan"))


class SaoDangQueRen(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "SaoDangQueRen"

        def feature(screen):
            return self.is_exists(MAOXIAN_BTN["saodang_query"], screen=screen)

        self.initFC = None
        self.feature = feature

    def OK(self) -> "SaoDangJieGuo":
        def gotofun():
            self.click(591, 369)

        return self.goto(SaoDangJieGuo, gotofun)


class SaoDangJieGuo(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "SaoDangJieGuo"

        def feature(screen):
            a1 = self.is_exists(MAOXIAN_BTN["saodang_tiaoguo"], screen=screen)
            a2 = self.is_exists(MAOXIAN_BTN["saodang_ok2"], screen=screen)
            a3 = self.is_exists(MAOXIAN_BTN["saodang_tiaoguo"], is_black=True, screen=screen)
            return a1 or a2 or a3

        self.initFC = None
        self.feature = feature

    def OK(self):
        def gotofun():
            self.click(473, 475)
