"""
刷图新思路，在这里把整个刷图的流程理顺。

首先明确刷图/推图的应用场景：
    1. Normal图
    2. Hard图
    3. 地下城图
    4. 探索/调查本
    5. 活动图
    6. 露娜塔
    7. 竞技场/公主竞技场
    ……

我们把上述刷图/推图操作统称为"刷图"
不论对于何种任务，刷图任务都可以主要分为一下流程：
    1. 进图：进入选关/选人界面
    2. 选关/选人
    3. 如果是推图：
        3.1 角色选择
        3.2 战斗进行
        3.3 战斗结束
    4. 如果是刷图：
        进行扫荡
当然，过程总不是一番风顺，可能会出现很多异常情况，我们把异常情况分为以下类型。
    1. 强制引导型
        一些剧情任务等会强制改变当前场景。
    2. 过场动画型
        如kkr跳脸，17图进18图动画剧情等，并不会导致场景的改变。
    3. 弹窗型
        如”体力不足，是否购买“，”礼物存储到达上限“等等。
显然，每一种异常情况的发生时机是确定的，因此对异常的检测只需要在两次操作中添加即可。
    Eg. 推图结束 - 剧情强制引导
    推完3-1之后出了解锁工会之家剧情，则：
    [点击返回]->
        Exception{
            有剧情的kkr跳脸 -> 触发引导，并从进图开始继续
            ……
        }
    此时，raise一个包含引导函数的异常，并回到开头重新进入。
    Eg. 进入18图 - 过场动画型
    进入18图/推完3-1之后出现了过场动画，则：
    [点击进图]->
        Exception{
            奇怪的绿发恶魔跳脸 -> 进入指定的跳过函数
            ……
        }
    跳过函数结束后，考虑到可能还会出现其它的Exception，则此时仍处于该步骤的异常判断中。
    Eg. 扫荡之后 - 弹窗型
    [点击扫荡]->
        Exception{
            等级提升 -> 记录信息
            公会战提示 -> 记录信息/前往公会战
            经验到达上限提示 -> 记录信息/点击以后不再提示
            礼物收满提示 -> 记录信息/前往卖装备/...
            ……
        }
     接收到某个异常后，可能对不同的需求会触发不同的函数，可能涉及到强制场景跳转，或者对之后的逻辑产生影响。
     因此，信息共享和场景跳转必须重视。

根据以上需求，下面从基建开始重新理顺。

1. FunctionChecker

首先对原先的lock_img族进行功能延拓。
新建立一个函数检测类FunctionChecker(FC)，并且提供注册方法插入一系列决策。
FC与Automator绑定，一个FC中必然含有参数_a，表示绑定的Automator
可以通过Automator.getFC()获得一个含有参数_a的FC
    FC.add(Checker,DoFunction=None,rv=None,**kwargs)
        这表示增加一个决策：当Checker满足时，执行DoFunction
    Checker是一个特殊的类，它不仅包含函数本身，还指定了该函数所用到的变量名称。
        Checker(fun:Callable[*->bool])
        FC在执行Checker时会先检测自身环境中有无fun所需变量，
        如果没有，报错；如果有，将该变量传入Checker中。

    DoFunction是一个函数，如果Checker成立，将会执行DoFunction
    如果要执行多个Function，可以传入一个List[Callable]
    如果DoFunction含有参数self，则会传入self=FC._a，以便进行信息交互
    如果需要返回特定值，则在DoFunction中插入一个特殊的异常即可：
        ReturnValue(*args)
    或者可以简写为：
        FC.add(Checker,rv=*) - Checker为真时，返回rv
        FC.add(Checker,DoFunction,rv=*) - Checker为真时，先执行DoFunction，再返回rv
        注意：rv如果设置为None，则不会返回值，除非DoFunction有值。
        DoFunction和rv必须至少有一个不为None

此时，对于“检测到存在图片则返回True”，可写为：
    FC.add(IsExistChecker,rv=True)
        其中，IsExistChecker可定义为Checker(self.is_exist,v=["screen"])
    或者可以用相关api：
        FC.add_exist(PCRElement,rv=True,**kwargs)
        FC.add_not_exist(PCRElement,rv=True,**kwargs)
        ...

当我们已经添加了一系列决策后，我们可以执行这一决策：
    FC.run() - 执行一次决策。
        按照从上到下的顺序依次检测决策， 并且执行相关函数。
        如果遇到返回值，则返回指定值，结束运行。

    FC.lock(delay=1,timeout=None,retry=None,until=None) - 锁定
        按照从上到下的顺序依次检测决策，直到：
            - 若until为None，则直到ReturnValue
            - 若until为非None，则直到ReturnValue=until
            - 若until为Callable，则直到ReturnValue且until(ReturnValue) is True
            - 若until为iterable，则直到ReturnValue in until
        全部进行一遍后，sleep(delay)
        如果时间超过了timeout，则返回超时错误
            LockError - LockTimeoutError
        如果重试次数超过retry，则返回重试过多错误
            LockError - LockMaxRetryError
        如果希望达到SideCheck的效果，则可以在**kwargs中增加一个flag：
            clear=True
            则如果某一条Checker为真，会归零计时器/计数器

此时，如果我们要定义一个“进入升级”任务：
    如果出现玛娜图标 - 返回True
    如果出现kkr头 - 执行跳过剧情
则只需要定义一个FC:
    self.getFC()\
        .add_exist(MANA,rv=True)\
        .add_exist(KKR,SkipFun,clear=True)\
        .lock(timeout=30)

2. Retry处理
在上述“进入升级”任务中的异常属于“过场动画”型。但如进入地下城的kkr跳脸此类则属于“强制引导”型，此时执行完引导过程后
需要重新进入函数，即“retry”
解决方法是给函数加上retry装饰器：
    @PCRRetry(name=None)
强制引导结束后只需要raise一个RetryNow异常，由装饰器捕获后，重新进入函数。


3.异常集
根据第一部分的需求，我们需要在两个动作之间定义可能发生的异常及其处理方案。
我们需要建立一个异常检测集ExceptionSet (ES)，并且提供一个注册方法来向其中插入异常检测切片。
每一个Automator带有唯一的ES实例。
    self.ES.register(FunctionChecker,group=None) 在指定Group中注册FC
    self.ES.clear(group=None) 方法用来清除指定Group的异常检测集。
    此后，每一次调用self.getFC()时，都会自动绑定ES中全部异常。
    可以用一个简单的with语句来实现register和clear：
    with self.ES(FunctionChecker,group=None):
        pass

"""
import collections
import inspect
import random
import time
from math import inf
from typing import Callable, Any, Dict, Optional, Union, List, Type, TYPE_CHECKING

from core.constant import PCRelement
from core.pcr_config import lockimg_timeout

if TYPE_CHECKING:
    from automator_mixins._base import BaseMixin

class Checker:
    """
    一个指令检查类：会执行fun函数的内容，并且返回一个值为真或假。
    Example 1：
        fun：截图->检查图片上有无可可萝  返回值：若有，则返回True；若无，则返回False
        （这个例子被广泛应用在大多数场合）
    当然也可以在fun里面进行一些交互操作，如：
    Example 2：
        fun：循环截图，如果检测到可可萝则点掉他，直到可可萝消失。 如果曾经检查到可可萝，返回True，否则返回False。
        （这个可以制作sidecheck)
    当然也可以制作返回制永远为True的，如：
    Example 3：
        fun：检查app是否启动，若未启动，raise一个错误。 返回：永远为True
        （可以用于触发强制重启）
    """

    def __init__(self, fun: Callable[[Any], bool], vardict: Optional[Dict[str, Any]] = None,
                 funvar: Optional[List[str]] = None, name=None):
        """
        :param fun:  返回bool的检查函数
        :param vardict:   fun参数的default value dict
        :param funvar:   指定fun函数需要额外给出的参数，若None，则用inspect自动检查
        :param name: 调试用，命名这个Checker
        """
        self.name = name
        if vardict is None:
            vardict = {}
        self._fun = getattr(fun, "__call__", fun)
        self._v = vardict
        if funvar is not None:
            self._funvar = funvar
            self._default = [inspect.Parameter.empty] * len(self._funvar)
        else:
            try:
                pars = inspect.signature(fun).parameters
                self._funvar = []
                self._default = []
                for i, j in pars.items():
                    if j.kind in [1, 3]:
                        # 非args kwargs
                        self._funvar += [i]
                        self._default += [j.default]
            except Exception as e:
                assert funvar is not None, f"inspect检查失败，必须指定funvar！{e}"
                self._funvar = funvar
                self._default = [inspect.Parameter.empty] * len(self._funvar)

    def __repr__(self):
        return f"<Checker name={self.name} funvar={self._funvar}>"

    def _check_exist(self, more):
        # 确保环境中存在所需的变量
        v = self._v
        v.update(more)
        p = {}
        for i, j in zip(self._funvar, self._default):
            if i not in v:
                if j is not inspect.Parameter.empty:
                    p[i] = j
                else:
                    raise AttributeError("vardict中不存在Checker所需的变量：", i)
            else:
                p[i] = v[i]
        return p

    def _run(self, vardict: Optional[Dict] = None) -> bool:
        if vardict is None:
            vardict = {}
        p = self._check_exist(vardict)
        return self._fun(**p)

    def __call__(self, vardict: Optional[Dict] = None) -> bool:
        """
        执行这条Checker。
        :param vardict: 环境参数，额外传入fun的参数。
        :return: True或False
        """
        return self._run(vardict)

    @staticmethod
    def true(name=None):
        """
        恒为真的Checker
        """

        def f(*args, **kwargs):
            return True

        return Checker(f, funvar=[], name=name)


class ReturnValue(Exception):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"<Return Value>: {self.value}"


class LockError(Exception):
    def __init__(self, *args):
        self.args = args
        super().__init__(*args)

    def __repr__(self):
        return f"<{type(self)}> {','.join(self.args)}"

class LockTimeoutError(LockError):
    def __init__(self, *args):
        super().__init__(*args)


class LockMaxRetryError(LockError):
    def __init__(self, *args):
        super().__init__(*args)


class FunctionChecker:
    """
    简称FC，一系列Checker按照顺序执行，并且根据Checker的返回制进行多种操作。
    设定好一系列”当……就……“的指令集之后，可以用self.run来执行整个指令，并获得一个返回制。
    或执行self.lock，在目标函数条件不满足时，反复执行self.run


    -- vardict
    FC自带vardict，是每个子Checker公用的存储空间。
    Example:
        截图后放入vardict，此后所有后续的Checker可以公用同一张截图避免重复截图。

    -- checkers
    一个列表：
        List[Tuple[Checker, DoFunction]]
    执行self.run时，按顺序依次执行各个Checker，若Checker为真（或self.target_flag)，则执行对应的DoFunction。
    self.run的返回值见self.add函数中的rv参数。

    -- last_time
    这个FC开始被执行的起始时间戳。可用于计时。
    Example：
        30s内检测是否存在某按钮，若30s后仍然没有检测到按钮，则爆超时错误。
    注：add函数中有特殊的clear参数可以重置时间戳，方便为暂停等功能做铺垫。

    -- target_flag
    在谁做什么的逻辑中，通常默认Checker为真，则做dofunction，所以target_flag默认为True；
    但你也可以手动调整target_flag为False，甚至其它值，如果你一定要写返回制不为布尔类型的Checker的话。

    """

    def __init__(self):
        self.vardict = {}  # 公共存储空间
        self.fcdict = {}  # 私人存储空间，仅供FC的内部函数使用
        self.checkers = []  # Checkers序列
        self.last_time = 0  # 起始时间戳
        self.target_flag = True  # 需要Chechker为真

    def set_target(self, target):
        self.target_flag = target
        return self

    def update_var(self, fun, varname, name="update_var", *args, **kwargs):
        """
        添加一个更新公共存储的命令。
        执行fun(*args,**kwargs)，fun函数会有一个返回制，用该返回值来更新self.vardict[varname]。

        Checker： 恒真
        DoFunction： 用fun的返回制更新self.vardict
        return self
        """

        # 用fun的返回值更新vardict
        def f():
            self.vardict[varname] = fun(*args, **kwargs)

        self.checkers += [(Checker.true(name), f)]
        return self

    def add(self, checker: Union[Checker, bool], dofunction: Optional[Callable] = None, rv=None, raise_=None,
            clear=False):
        """
        添加一个If Checker==self.target_flag Then dofunction的命令
        :param checker: 进行检测的Checker
        :param dofunction: Checker为真（self.target_flag)时，执行的函数（无传入参数）
        :param rv: 非None时，若Checker为真，则终止self.run，并返回rv
        :param raise_: 非None时，raise raise_
        :param clear: 非None时，重置内部时间戳。
        :return: self
        """
        # 增加一个checker-dofunction
        assert rv is None or raise_ is None, "返回值和弹出异常只能存在一个！"

        def f():
            if dofunction is not None:
                dofunction()
            if rv is not None:
                raise ReturnValue(rv)
            if raise_ is not None:
                raise raise_
            if clear:
                self.last_time = time.time()
                self.retry_times = 0

        self.checkers += [(checker, f)]
        return self

    def add_process(self, dofunction: Callable, name="process"):
        """
        添加一个过程，不做检查，直接执行dofunction
        Checker: 恒真
        DoFunction: 指定的dofunction
        :return: self
        """
        self.checkers += [(Checker.true(name), dofunction)]
        return self

    def add_intervalprocess(self, dofunction: Callable, retry=None, interval=1, name="interval_process",
                            raise_retry=False, ):
        """
        每过一段时间，执行一次dofunction。
        Example:
            被广泛应用在lockimg等函数中，由于对模拟器的操作有延迟，通常需要每过一段时间试者点击模拟器。
            但是在这段时间需要持续观测模拟器的变化。若模拟器长时间没有变化，则需要再次尝试点击模拟器。
            此时，检测操作为正常的Checker，但是点击操作需要用add_intervalprocess完成。

        :param dofunction:  执行的函数。
        :param retry: 最多重试几次。设为None时，不进行判断；设为整数时，当dofunction即将执行第retry+1次（但还未执行）时，
                若raise_retry，则报LockMaxRetryError错，否则只是让self.lock返回False
        :param interval: 重试间隔（秒）
        :param name: 随便起名字
        :param raise_retry: 见retry
        :return:
        """
        # 每隔interval执行一次的process，第一次不需等待
        # 重复执行次数（包括第一次）达到retry后，弹出错误
        # retry=0等价于retry=None （历史遗留原因）。
        if "__retry__" not in self.vardict:
            self.vardict["__retry__"] = collections.OrderedDict()
        if "__last_time__" not in self.vardict:
            self.vardict["__last_time__"] = collections.OrderedDict()
        ID_R = len(self.vardict["__retry__"])
        ID_I = len(self.vardict["__last_time__"])
        if retry == 0:
            retry = None
        if retry is not None:
            retry -= 1  # 兼容历史
            self.vardict["__retry__"][ID_R] = 0
        self.vardict["__last_time__"][ID_I] = 0

        def f(__last_time__, __retry__):
            if time.time() - __last_time__[ID_I] > interval:
                __last_time__[ID_I] = time.time()
                if retry is not None:
                    if __retry__[ID_R] > retry:
                        if raise_retry:
                            raise LockMaxRetryError("重试次数超过", retry, "次！")
                        # master版本里重试过多是返回的False
                        else:
                            raise ReturnValue(False)
                dofunction()
                if retry is not None:
                    __retry__[ID_R] += 1

        self.add(Checker(f, funvar=["__last_time__", "__retry__"], name=name))
        return self

    def run(self):
        """
        执行Checker-Dofunction指令集。
        :return:
            若使用add设置了rv参数，返回对应的rv。
            若触发ReturnValue(rv)异常，返回rv。
            若interval_process超出重试次数且raise_retry为False，返回False。
            否则，返回None
        """
        # 跑Checker
        try:
            for c, f in self.checkers:
                if c is True:
                    flag = self.target_flag
                else:
                    flag = c(self.vardict)
                if flag == self.target_flag:
                    if f is not None:
                        f()
        except ReturnValue as rv:
            return rv.value
        return None

    def lock(self, delay=0.5, timeout=None, until=None, is_raise=True):
        """
        循环执行全部的Checker-Dofunction指令集，直到对应返回值出现。
        返回值可以由add的rv参数产生，或任何ReturnValue(rv)的异常产生。
        :param delay:  每遍循环之间的间隔。
        :param timeout:
            每一遍指令跑完后，检查当前时间和记录的时间戳之差，若超过timeout，则报错LockTimeoutError。
            若timeout设置为0， 则不进行超时检查。
            若timeout设置为None，则用config中的lockimg_timeout作为值。
        :param until:
            若until未设置，只要某次run产生了返回值（见self.run)，则终止lock，并返回该返回制。
            若until设置非None，则必须要某次run产生的返回制和until相同，才终止。
        :param is_raise: timeout超时时是否报错，若设置为False，则不报错，只返回None。
        :return: 返回值或None
        """
        # 锁Checker
        # 直到检测到ReturnValue，或者当until设置时，ReturnValue满足until条件
        self.last_time = time.time()
        self.retry_times = 0
        if timeout is None:
            timeout = lockimg_timeout
        if timeout == 0:
            timeout = None
        if isinstance(until, str):
            until = [until]
        while True:
            try:
                rv = self.run()
            except LockMaxRetryError as e:
                if is_raise:
                    raise e
                else:
                    return None
            if until is None and rv is not None:
                return rv
            elif isinstance(until, collections.Iterable) and rv in until:
                return rv
            elif isinstance(until, collections.Callable) and until(rv):
                return rv
            elif until is not None and rv == until:
                return rv
            self.retry_times += 1
            if timeout is not None and time.time() - self.last_time > timeout:
                if is_raise:
                    raise LockTimeoutError("锁定时间超过", timeout, "秒！")
                else:
                    return None
            time.sleep(delay)


class ExceptionSet:
    """
    异常集由很多FC组成。
    每次异常集运行，都依次把各个FC运行一遍，仅此而已。
    通过register函数可以在异常集中注册新的FC。
    支持with，使得可以在一段中应用异常集。
    """

    def __init__(self, a: "BaseMixin"):
        self._a = a
        self.FCs = collections.OrderedDict()

    def register(self, fc: FunctionChecker, group="_default"):
        self.FCs[group] = fc

    def clear(self, group="_default"):
        if group in self.FCs:
            del self.FCs[group]

    def clear_all(self):
        self.FCs.clear()

    def run(self):
        for FC in self.FCs.values():
            FC.run()

    def __call__(self, fc: FunctionChecker, group=None):
        if group is None:
            group = str(random.random())
        ES = self

        class es_with:
            def __enter__(self):
                ES.register(fc, group)

            def __exit__(self, *args, **kwargs):
                ES.clear(group)

        return es_with()


class ElementChecker(FunctionChecker):
    """
    基于FC定制的，专为PCR打造的ElementChecker。
    已经制作好了一大堆现成的指令集可以方便调用。

    -- header：“头”
        正常来说，你的每一条指令都会被嵌入“头”：
        Example：
            你以为的click_btn： 截图->检测按钮存在->点击按钮
            实际上的click_btn：
                头[截图->点掉可可萝Checker->等待Loading结束Checker] -> click_btn
        所以插入“头”可以很方便地进行全局的检测操作。
        这种含有头的FC，会被标记为header=True
        而不含有头的FC，header=False
        为了防止头套头的循环爆栈事件发生，加了这个header方便区分。
        更多详见Automator.getFC(header)函数。

    """

    def __init__(self, a: "BaseMixin"):
        super().__init__()
        self._a = a
        self._have_getscreen = False
        self.header = False

    def getscreen(self, force=False):
        # 使用add_exist族函数前必须使用
        # 否则将每次拍摄新的截图，浪费时间
        # 向公共空间中增加一个截图参数screen
        # force=False时，只有第一个getscreen起作用
        if force or self._have_getscreen is False:
            self.update_var(self._a.getscreen, "screen", "getscreen")
            self._have_getscreen = True
        return self

    def wait_for_loading(self, force_getscreen=False):
        # force_getscreen：第一次使用新截图。不开：使用老截图。
        def waiting_force():
            screen = self._a.getscreen()
            if self._a.not_loading(screen):
                pass
            else:
                self._a.wait_for_loading(delay=0.5)

        def waiting():
            if self._a.last_screen is not None:
                if self._a.not_loading(self._a.last_screen):
                    pass
                else:
                    self._a.wait_for_loading(delay=0.5)

        if force_getscreen:
            self.add_process(waiting_force, "force_loading")
        else:
            self.add_process(waiting, "loading")
        return self

    def exist(self, img: Union[PCRelement, str], dofunction: Optional[Callable] = None, rv=True, raise_=None,
              clear=False,
              **kwargs):
        def f(screen=None) -> bool:
            return self._a.is_exists(img, screen=screen, **kwargs)

        self.add(Checker(f, self.vardict, name=f"Exist[{img}] -> {rv}", ), dofunction=dofunction, rv=rv, raise_=raise_,
                 clear=clear)
        return self

    def not_exist(self, img: Union[PCRelement, str], dofunction: Optional[Callable] = None, rv=True, raise_=None,
                  clear=False,
                  **kwargs):
        def f(screen=None) -> bool:
            return not self._a.is_exists(img, screen=screen, **kwargs)

        self.add(Checker(f, self.vardict, name=f"NotExist[{img}] -> {rv}"), dofunction=dofunction, rv=rv, raise_=raise_,
                 clear=clear)
        return self

    def add_sidecheck(self, sidecheck, dofunction=None, rv=None, raise_=None, clear=True, name="SideCheck"):
        my_id = random.random()
        self.fcdict[my_id] = False

        def named_sidecheck(screen):
            # 防止重复执行该sidecheck
            if not self.fcdict[my_id]:
                self.fcdict[my_id] = True
                out = sidecheck(screen)
                self.fcdict[my_id] = False
                return out
            else:
                # 占用中，就当没看见
                return False

        return self.add(Checker(named_sidecheck, funvar=["screen"], name=name), dofunction, rv, raise_, clear)

    def click(self, *args, pre_delay=0., post_delay=0., interval=0, retry=None, **kwargs):
        def f():
            self._a.click(*args, pre_delay=pre_delay, post_delay=post_delay, **kwargs)

        if interval == 0:
            self.add_process(f, f"click {args}")
        else:
            self.add_intervalprocess(f, retry, interval, f"click {args} interval={interval} maxretry={retry}")
        return self

    def sleep(self, sec):
        def f():
            time.sleep(sec)

        self.add_process(f, name=f"sleep {sec} s")
        return self

    def bind_ES(self, es: ExceptionSet, name="ExceptionSet"):
        for i in es.FCs.values():
            if isinstance(i, ElementChecker):
                assert i.header is False, "绑定的异常集中不能含有header,请设置getFC(false)！"
        self.add_process(es.run, name=name)
        return self

    def lock(self, delay=0.5, timeout=None, until=None, is_raise=True):
        def ClearTimeout():
            if self._a._paused:
                self._a._paused = False
                return True
            else:
                return False

        self.add(Checker(ClearTimeout, name="Reset Timer If Pause"), clear=True)
        self._a._last_lock_FC = self
        return super().lock(delay, timeout, until, is_raise)


class GotoException(Exception):
    def __init__(self, ident):
        super().__init__()
        self.ident = ident

class RetryNow(Exception):
    def __init__(self, name=None):
        super().__init__()
        self.name = name

class ContinueNow(Exception):
    # 立即重试，不过不会retry++
    def __init__(self, name=None):
        super().__init__()
        self.name = name

class BreakNow(Exception):
    # 立即跳出，不过不会触发任何异常
    # value：返回值
    def __init__(self, name=None, value=None):
        super().__init__()
        self.name = name
        self.value = value


class TooMuchRetry(Exception):
    pass


class PCRRetry:
    """
    很方便的重试工具，和自带的retry很像，但是更加方便PCR。可以直接使用，也可以作为装饰器使用。(见retry_now）

    Example 1:
        @PCRRetry()
        def DoRetry():
            raise RetryNow()

    如上例子所示，每当raise RetryNow被执行，都会跳转到最近的一个名称相同的PCRRetry装饰器处，可以重新执行该函数。

    Example 2:
        @PCRRetry(name="A")
        def DoRetry():
            raise RetryNow(name="A")

    指定name后，RetryNow只会返回到最近的相同name的PCRRetry处。默认的name为None，不过这并不代表不进行name匹配检测，只不过匹配的name为None。

    Example 3：
        @PCRRetry(max_retry=3)
        def DoRetry():
            raise RetryNow()

    指定max_retry后，最多重试这么多次，然后就会报一个TooMuchRetry的错误。

    Example 4：
        @PCRRetry(max_retry=3)
        def DoRetry():
            raise ContinueNow()

    使用ContinueNow就和for循环中的continue类似，会回到对应PCRRetry处，但不会增加重试次数计数器。

    没有出现在例子里的其他参数似乎都没啥用。

    """

    def __init__(self,
                 name=None,
                 max_retry=inf,
                 delay=0,
                 include_errors: Optional[Union[List, bool]] = None,
                 record_list=False,
                 raise_return=None,
                 ):
        self.name = name
        self.max_retry = max_retry
        self.delay=delay  # 失败延迟
        self.include_errors = include_errors  # None或False时，只检测RetryNow，其它不拦截；List时，还包括List中指定的错误, True全包括
        self.record_list = record_list  # 是否记录全部产生得错误
        self.raise_return = raise_return  # 非None时，产生错误时，不raise，return这个值

    def __call__(self, fun):
        def f(*args, **kwargs):
            count = 0
            output_error = None
            output_errors = []
            while True:
                try:
                    out = fun(*args, **kwargs)
                    return out
                except RetryNow as r:
                    if r.name == self.name:
                        count += 1
                        if count > self.max_retry:
                            output_error = TooMuchRetry(f"尝试次数过多{'' if self.name is None else f'Name {self.name}'}")
                            break
                        time.sleep(self.delay)
                        continue
                except ContinueNow as r:
                    if r.name == self.name:
                        time.sleep(self.delay)
                        continue
                except BreakNow as r:
                    if r.name == self.name:
                        return r.value
                except Exception as e:
                    if self.include_errors in [None, False]:
                        raise e
                    if self.include_errors is True or type(e) in self.include_errors:
                        count += 1
                        if self.record_list:
                            output_errors += [e]
                        if count > self.max_retry:
                            if self.record_list:
                                output_error = TooMuchRetry(
                                    f"尝试次数过多{'' if self.name is None else f'Name {self.name}'}\n" +
                                    " 异常列表：\n" + '\n'.join([str(o) for o in output_errors]))
                            else:
                                output_error = TooMuchRetry(
                                    f"尝试次数过多{'' if self.name is None else f'Name {self.name}'}\n" +
                                    " 最后一次异常：" + str(e))
                            break
                        time.sleep(self.delay)
                        continue
                    raise e
                break
            if output_error is not None:
                if self.raise_return is not None:
                    return self.raise_return
                else:
                    raise output_error

        return f

    def run(self, fun):
        return self.__call__(fun)()


def retry_run(fun, max_retry=inf, raise_error: Optional[Type[Exception]] = None, delay=0, **kwargs):
    kwargs.setdefault("max_retry", max_retry)
    kwargs.setdefault("include_errors", True)
    kwargs.setdefault("record_list", False)
    kwargs.setdefault("delay",delay)
    try:
        out = PCRRetry(**kwargs).run(fun)
        return out
    except TooMuchRetry as e:
        if raise_error is None:
            raise e
        else:
            raise raise_error()
