import time
from math import inf
from typing import Type, List, Union, TYPE_CHECKING

from core.constant import PCRelement
from core.pcr_checker import Checker, LockTimeoutError, LockMaxRetryError

if TYPE_CHECKING:
    from core.Automator import Automator

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

    def __init__(self, a, *args, **kwargs):
        self._a: "Automator" = a
        self.scene_name = "BaseScene"
        self._a.scenes += [self]
        self.initFC = None
        self.feature = None  # screen -> True/False
        self._raise = self._a._raise
        self.check_ocr_running = self._a.check_ocr_running
        self.click = self._a.click
        self.fclick = self._a.fclick
        self.click_img = self._a.click_img
        self.lock_img = self._a.lock_img
        self.lock_no_img=self._a.lock_no_img
        self.click_btn=self._a.click_btn
        self.getFC=self._a.getFC
        self.is_exists=self._a.is_exists
        self.img_prob=self._a.img_prob
        self.img_where_all = self._a.img_where_all
        self.img_where_all_prob = self._a.img_where_all_prob
        self.img_equal = self._a.img_equal
        self.wait_for_stable=self._a.wait_for_stable
        self.wait_for_change = self._a.wait_for_change
        self.wait_for_loading = self._a.wait_for_loading
        self.not_loading = self._a.not_loading
        self.getscreen = self._a.getscreen
        self.lock_fun = self._a.lock_fun
        self.chulijiaocheng = self._a.chulijiaocheng
        self.check_dict_id = self._a.check_dict_id
        self.ocr_center = self._a.ocr_center
        self.ocr_int = self._a.ocr_int
        self.ocr_A_B = self._a.ocr_A_B
        self.start_shuatu = self._a.start_shuatu
        self.check_shuatu = self._a.check_shuatu
        self.stop_shuatu = self._a.stop_shuatu

    def fun_feature_exist(self, element: PCRelement):
        def fun(screen):
            return self.is_exists(element, screen=screen)

        return fun

    def fun_click(self, *args, **kwargs):
        def fun():
            self.click(*args, **kwargs)

        return fun

    @property
    def last_s_shuatucreen(self):
        return self._a.last_screen

    @property
    def log(self):
        return self._a.log

    @property
    def last_screen(self):
        return self._a.last_screen

    @property
    def d(self):
        return self._a.d

    @property
    def debug_record(self):
        return self._a.debug_record

    def goto(self, scene: Union[Type["PCRSceneBase"], Type["PCRMsgBoxBase"]], gotofun, use_in_feature_only=None,
             before_clear=True, timeout=None, interval=8, retry=None):
        def nothing():
            pass

        if gotofun is None:
            gotofun = nothing
        next_scene = scene(self._a)
        if use_in_feature_only is None:
            if PCRMsgBoxBase in scene.__mro__:
                use_in_feature_only = True
            else:
                use_in_feature_only = False

        def featureout(screen):
            if use_in_feature_only:
                return True if next_scene.feature(screen) else False
            else:
                return True if not self.feature(screen) else False

        if before_clear:
            self.clear_initFC()
        if self.feature is not None:
            self._a.getFC().getscreen().wait_for_loading(). \
                add(Checker(featureout, name=f"{self.scene_name} - Feature Out"), rv=True). \
                add_intervalprocess(gotofun, retry=retry, interval=interval, name="gotofun", raise_retry=True).lock(
                timeout=timeout)
        return next_scene.enter()

    def enter(self,timeout=None):
        def featurein(screen):
            return True if self.feature(screen) else False

        # Clear Other Scenes InitFC
        self._a.clear_all_initFC(self.scene_name)
        self._a.scenes = [self]
        if self.initFC is not None:
            self._a.ES.register(self.initFC, group=self.scene_name)
        if self.feature is not None:
            self._a.getFC().getscreen().wait_for_loading(). \
                add(Checker(featurein, name=f"{self.scene_name} - Feature In"), rv=True).lock(timeout=timeout)
        return self

    def clear_initFC(self):
        self._a.ES.clear(self.scene_name)
        return self

    def set_initFC(self):
        self._a.ES.register(self.initFC, self.scene_name)
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
    def exit(self, exitfun, before_clear=True, timeout=None, interval=8, retry=None):
        """
        不断执行exitfun直到退出Scene（feature无法识别）
        """

        def featureout(screen):
            return True if not self.feature(screen) else False

        if before_clear:
            self.clear_initFC()
        if self.feature is not None:
            self._a.getFC().getscreen(). \
                add(Checker(featureout, name=f"{self.scene_name} - Feature Out"), rv=True). \
                add_intervalprocess(exitfun, retry=retry, interval=interval, name="gotofun").lock(timeout=timeout)
        if not before_clear:
            self.clear_initFC()
        return None


class PCRMsgBoxBase(PCRSceneBase):
    def __init__(self, a):
        super().__init__(a)
        self.scene_name = "PCRMsgBox"


class PossibleSceneList(PCRSceneBase):
    """
    可能一个操作之后，产生数个msgbox，这些msgbox的内容、顺序不一定一致，而且可能会有多个跳出。
    使用PossibleMsgBoxList来把这些msgbox全部同时考虑住。
    scene_list:包含msgbox的列表，每个msgbox必须有feature参数以确认是否显示。
    若同时满足多个feature，按照顺序选择。
    no_scene_feature：当检测到时，则认定当前没有msgbox弹出；若不指定，则只有当全部msgbox_list均未弹出才判定为无msgbox；
    no_scene_feature设置为False时，一直等待直到出现scene。

    缺陷：如果两个msgbox之间弹出间隔过长，则可能该方法失效。
    解决方法：双重判定。(double_check)：为一个时间， 表示必须满足间隔为double_check的两次判定均生效才认定无msgbox。
        double_check设置为None则不使用双重判定。

    缺陷：如果对于多场景/多msgbox，则可能出现场景feature已经出现，msgbox未出现情形，并导致跳过。
    解决方法：场景双判。(check_double_scene)：默认开启。使用后，对于检查到的PCRSceneBase类，会对其进行double_check，必须两次满足才行。

    TIPS: 使用check命令可以处理“无scene”的情况。
    若使用enter命令(被goto），则必须保证有一个可以成功跳转的scene，否则返回None。

    Example:
        PossibleSceneList([
    """

    def __init__(self, a, scene_list: List[PCRSceneBase], no_scene_feature=None, double_check=2.,
                 check_double_scene=True, timeout=30.,
                 max_retry=None):
        super().__init__(a)
        self.scene_list = scene_list
        self.no_scene_feature = no_scene_feature
        self.double_check = double_check
        self.timeout = timeout if timeout is not None else inf
        self.max_retry = max_retry if max_retry is not None else inf
        self.check_double_scene = check_double_scene
        self.scene_name = "PossibleSceneList"

    def feature(self, screen=None):
        if screen is None:
            screen = self.getscreen()
        for scene in self.scene_list:
            if scene.feature(screen):
                return True
        return False

    def enter(self, timeout=None):
        if self.initFC is not None:
            self._a.ES.register(self.initFC, group=self.scene_name)
        return self.check(timeout=timeout, max_retry=inf, no_scene_feature=False)

    def check(self, double_check=None, check_double_scene=None, timeout=None, max_retry=None, no_scene_feature=None):
        """
        检查场景上是否存在满足要求的scene。
        若存在指定scene，则返回该scene。
        若无scene，则返回None
        """
        if double_check is None:
            double_check = self.double_check
        if check_double_scene is None:
            check_double_scene = self.check_double_scene
        if timeout is None:
            timeout = self.timeout
        if no_scene_feature is None:
            no_scene_feature = self.no_scene_feature
        if max_retry is None:
            max_retry = self.max_retry
        last_check_time = None
        last_scene = type(None)
        no_scene = False
        start_time = time.time()
        retry = 0

        while retry < max_retry:
            if timeout is not None and time.time() - start_time > timeout:
                raise LockTimeoutError("SceneList判断超时！")
            screen = self.getscreen()
            if not self.not_loading(screen):
                start_time = time.time()
            for scene in self.scene_list:
                if scene.feature(screen):
                    if isinstance(scene, PCRMsgBoxBase):
                        return scene
                    else:
                        # 场景双判
                        if check_double_scene:
                            if isinstance(scene, last_scene):
                                return scene
                            else:
                                last_scene = type(scene)
                                time.sleep(double_check)
                                continue
                        else:
                            return scene
                if no_scene_feature is not None:
                    if no_scene_feature is False:
                        no_scene = False
                    else:
                        no_scene = no_scene_feature(screen)
                else:
                    no_scene = True
            if no_scene:
                start_time = time.time()
                if last_check_time is None:
                    last_check_time = time.time()
                else:
                    if time.time() - last_check_time > double_check:
                        return None  # No Msg
                    else:
                        time.sleep(-time.time() + last_check_time + double_check)  # Double Check
            else:
                last_check_time = None
                retry += 1
        raise LockMaxRetryError("SceneList判断超出尝试上限！")
