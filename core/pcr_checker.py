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
from typing import Callable, Any, Dict, Optional, Union, List, Type

from core.constant import PCRelement
from core.pcr_config import disable_timeout_raise, lockimg_timeout


class Checker:
    def __init__(self, fun: Callable[[Any], bool], vardict: Optional[Dict[str, Any]] = None, funvar=None, name=None):
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
        return self._run(vardict)

    @staticmethod
    def true(name=None):
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
        super().__init__(*args)


class LockTimeoutError(LockError):
    def __init__(self, *args):
        super().__init__(*args)


class LockMaxRetryError(LockError):
    def __init__(self, *args):
        super().__init__(*args)


class FunctionChecker:
    def __init__(self):
        self.vardict = {}  # 公共存储空间
        self.checkers = []  # Checkers序列
        self.last_time = 0  # 起始时间戳
        self.target_flag = True  # 需要Chechker为真

    def set_target(self, target):
        self.target_flag = target
        return self

    def update_var(self, fun, varname, name="update_var", *args, **kwargs):
        # 用fun的返回值更新vardict
        def f():
            self.vardict[varname] = fun(*args, **kwargs)

        self.checkers += [(Checker.true(name), f)]
        return self

    def add(self, checker: Union[Checker, bool], dofunction: Optional[Callable] = None, rv=None, raise_=None,
            clear=False):
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
        self.checkers += [(Checker.true(name), dofunction)]
        return self

    def add_intervalprocess(self, dofunction: Callable, retry=None, interval=1, name="interval_process"):
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
                        raise LockMaxRetryError("重试次数超过", retry, "次！")
                dofunction()
                if retry is not None:
                    __retry__[ID_R] += 1

        self.add(Checker(f, funvar=["__last_time__", "__retry__"], name=name))
        return self

    def run(self):
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

    def lock(self, delay=0, timeout=None, until=None, is_raise=True):
        # 锁Checker
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
    def __init__(self, a: "BaseMixin"):
        self._a = a
        self.FCs = collections.OrderedDict()

    def register(self, fc: FunctionChecker, group="_default"):
        self.FCs[group] = fc

    def clear(self, group="_default"):
        if group in self.FCs:
            del self.FCs[group]

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
            assert i.header is False, "绑定的异常集中不能含有header,请设置getFC(false)！"
        self.add_process(es.run, name=name)
        return self


class RetryNow(Exception):
    def __init__(self, name=None):
        super().__init__()
        self.name = name


class TooMuchRetry(Exception):
    pass


class PCRRetry:
    def __init__(self,
                 name=None,
                 max_retry=inf,
                 delay=0,
                 include_errors: Optional[Union[List, bool]] = None,
                 record_list=False,
                 ):
        self.name = name
        self.max_retry = max_retry
        self.delay=delay  # 失败延迟
        self.include_errors = include_errors  # None或False时，只检测RetryNow，其它不拦截；List时，还包括List中指定的错误, True全包括
        self.record_list = record_list  # 是否记录全部产生得错误

    def __call__(self, fun):
        def f():
            count = 0
            output_error = None
            output_errors = []
            while True:
                try:
                    out = fun()
                    return out
                except RetryNow as r:
                    if r.name == self.name:
                        count += 1
                        if count > self.max_retry:
                            output_error = TooMuchRetry(f"尝试次数过多{'' if self.name is None else f'Name {self.name}'}")
                            break
                        time.sleep(self.delay)
                        continue
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
