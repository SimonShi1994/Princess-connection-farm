import time

from core.constant import MAIN_BTN, HANGHUI_BTN, PCRelement, TUANDUIZHAN_BTN, DXC_ELEMENT
from core.constant import USER_DEFAULT_DICT as UDD
from core.cv import UIMatcher
from core.log_handler import pcr_log
from core.safe_u2 import timeout
from core.utils import diffday
from ._tools import ToolsMixin


class HaoYouMixin(ToolsMixin):
    """
    好友插片。
    包含好友相关操作。
    """
    def tianjiahaoyou(self,friend_id:str,var={}):
        """
        按照Friend_ID添加一个好友
        """
        S = self.get_zhuye().goto_zhucaidan().goto_haoyou().goto_haoyouguanli()
        S.search_friend(friend_id)
        self.lock_home()

    def tongguoshenqing(self,
                        name_prefix_valid="",
                        gonghui_prefix_valid="",
                        all_reject=False,
                        var={}
                        ):
        S = self.get_zhuye().goto_zhucaidan().goto_haoyou().goto_haoyouguanli()
        name_prefix_valid = name_prefix_valid.strip()
        gonghui_prefix_valid = gonghui_prefix_valid.strip()
        if name_prefix_valid == "":
            name_prefix_valid = None
        if gonghui_prefix_valid == "":
            gonghui_prefix_valid = None
        S.accept_friend(name_prefix_valid,gonghui_prefix_valid,all_reject)
        self.lock_home()
