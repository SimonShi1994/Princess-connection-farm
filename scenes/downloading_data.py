from core.constant import START_UI

from scenes.scene_base import PCRSceneBase


class DownloadingDataScene(PCRSceneBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "ShopBase"
        self.feature = self.fun_feature_exist(START_UI["downloading_logo"])
