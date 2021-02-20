from typing import Type

from core.pcr_checker import Checker

"""

4. 场景类
场景类PCRScene是一个集合了该场景全部可交互信息的手段，把相关参数和场景交互方法封装在一个类中，
使得程序可读性更高。
PCRScene的每一个交互的返回值均为一个PCRScene类，表示经过该交互后场景的变化。
PCRSceneBase类是全部场景的基类，由于需要对Automator进行操控，PCRSceneBase含有参数_a，表示对应Automator。
    生成场景时，必须要提供_a参数。
PCRSceneBase类也会提供Automator中的常用方法，如click, lock_img等等，只是相当于简化了self._a.click -> self.click。
一个成功的场景切换一般包括两个步骤：
（在特殊ES不触发时）
    当前场景的特征消失
    下一场景的特征出现
因此，为了保证切换的顺利，每个PCRSceneBase类都含有特殊的特征函数：
    PCRSceneBase.feature
    返回值为True时，说明检测到了该场景的特征。
在场景切换中，首先锁定直到该场景特征消失，再锁定直到后一场景特征出现。当然
同时考虑到每个场景刚进入后都可能需要ES，所以每个PCRSceneBase类还提供了一个initFC：
    PCRSceneBase.initFC
    在场景刚进入时会挂载init_FC到特定Group中，直到一次有效的场景交互被成功执行，或手动调用
        PCRSceneBase.clear_initFC()

"""

class PCRSceneBase:

    def __init__(self,a):
        from automator_mixins._base import BaseMixin
        self._a:BaseMixin=a
        self.scene_name = "BaseScene"
        self.initFC = None
        self.feature = None  # screen -> True/False
        self._raise=self._a._raise
        self.check_ocr_running = self._a.check_ocr_running
        self.click=self._a.click
        self.click_img=self._a.click_img
        self.lock_img=self._a.lock_img
        self.lock_no_img=self._a.lock_no_img
        self.click_btn=self._a.click_btn
        self.getFC=self._a.getFC
        self.is_exists=self._a.is_exists
        self.img_prob=self._a.img_prob
        self.img_where_all=self._a.img_where_all
        self.img_equal=self._a.img_equal
        self.wait_for_stable=self._a.wait_for_stable
        self.wait_for_change=self._a.wait_for_change
        self.wait_for_loading=self._a.wait_for_loading
        self.getscreen=self._a.getscreen
        self.lock_fun=self._a.lock_fun
        self.chulijiaocheng=self._a.chulijiaocheng
        self.check_dict_id=self._a.check_dict_id
        self.ocr_center = self._a.ocr_center
        self.ocr_int=self._a.ocr_int
        self.ocr_A_B=self._a.ocr_A_B

    @property
    def last_screen(self):
        return self._a.last_screen

    def goto(self, scene: Type["PCRSceneBase"], gotofun, before_clear=True, timeout=None, interval=8, retry=None):
        def featureout(screen):
            return True if not self.feature(screen) else False

        if before_clear:
            self.clear_initFC()
        if self.feature is not None:
            self._a.getFC().getscreen(). \
                add(Checker(featureout, name=f"{self.scene_name} - Feature Out"), rv=True). \
                add_intervalprocess(gotofun, retry=retry, interval=interval, name="gotofun").lock(timeout=timeout)
        if not before_clear:
            self.clear_initFC()
        return scene(self._a).enter()

    def enter(self,timeout=None):
        def featurein(screen):
            return True if self.feature(screen) else False
        if self.initFC is not None:
            self._a.ES.register(self.initFC,group=self.scene_name)
        if self.feature is not None:
            self._a.getFC().getscreen(). \
                add(Checker(featurein, name=f"{self.scene_name} - Feature In"), rv=True).lock(timeout=timeout)
        return self

    def clear_initFC(self):
        self._a.ES.clear(self.scene_name)
        return self

    def set_initFC(self):
        self._a.ES.register(self.initFC)
        return self

    def no_initFC(self):
        """
        with self.no_initFC():
            XXX

        该部分的内容不会受到InitFC的影响
        """
        obj=self
        class _no_initFC:
            def __init__(self):
                self._flag=True

            def __enter__(self):
                if obj.scene_name not in obj._a.ES.FCs:
                    self._flag = False
                else:
                    obj.clear_initFC()

            def __exit__(self, *args, **kwargs):
                if self._flag:
                    obj.set_initFC()

        return _no_initFC()


class PCRMsgBoxBase(PCRSceneBase):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "PCRMsgBox"
