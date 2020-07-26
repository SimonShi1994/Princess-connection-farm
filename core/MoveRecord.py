import json
import os
import pickle
from copy import deepcopy
from typing import Callable, Any, Optional, Dict, Union, Tuple, List

MoveFun = Callable[[Dict], Any]
AnyFun = Union[Callable[..., Any], str, None]
ConFun = Union[Callable[[Dict], bool], str]
IDType = Union[int, str]
IDFun = Union[Callable[..., IDType], IDType]
FunTuple = Tuple[AnyFun, IDType, Tuple, Dict, Dict, bool, bool, Any]
ErrTuple = Tuple[Any, bool]


class moveerr(Exception):
    """
    行动错误类
    捕获含有特定code的错误，在run外层进行捕获
    根据moveset.catch映射转到对应解决方案分支
    """

    def __init__(self, code, desc=""):
        """
        :param code: 错误代码
        :param desc: （可选）错误描述
        """
        self.code = code
        self.desc = desc


class movevar:
    """
    变量区操作类，可以通过moveset.wvar(var)获得。
    对var对象，尤其__self__进行操作，从而在函数中轻松操作变量区域
    :param autosave: 是否开启自动保存。
    :param var: 所操作的var对象。
    """

    def __init__(self, var: Dict, autosave=True):

        self.var = var
        self.autosave = autosave

    def save(self):
        """
        保存当前变量区域
        方式：通过__self__，调用moveset.savestate
        :return:
        """
        s = self.var["__self__"]
        s.savestate()

    def setflag(self, flagkey, flagvalue=1, save=None):
        """
        立flag
        类似T_nextflag，立即生效。
        将flagkey的值赋值为flagvalue
        立为flag的变量可以通过cflag一键删除
        :param flagkey: flag名称
        :param flagvalue: flag值
        :param save: 是否对该操作进行save。默认None，则根据movevar的autosave设置决定。
        """
        if save is None:
            save = self.autosave
        self.var.setdefault("__flag__", {})
        self.var["__flag__"][flagkey] = flagvalue
        if save:
            self.save()

    def clearflags(self, save=None):
        """
        清除flag
        类似T_clearflags，立即生效
        将所有通过flag或者T_nextflag立下的flag全部删除。
        :param save: 是否对该操作进行save。默认None，则根据movevar的autosave设置决定。
        """
        if save is None:
            save = self.autosave
        if "__flag__" in self.var:
            del self.var["__flag__"]
        if save:
            self.save()

    def flag(self, flagkey, flagvalue=1, mode="==") -> bool:
        """
        类似T_ifflag，对flag进行判断。如果flagkey不存在，一定输出false，否则按照mode与flagvalue比较。
       :param flagkey: flag名称
       :param flagvalue: flag比较值
       :param mode: 比较模式(==,<=,>=,!=,<,>...)
       :return: 判断的值
        """
        cmd = "'__flag__' in self.var and '%s' in self.var['__flag__'] and self.var['__flag__']['%s']%s%s" % (
            str(flagkey), str(flagkey), mode, str(flagvalue))
        return eval(cmd)

    def notflag(self, flagkey, flagvalue=1, mode="==") -> bool:
        cmd = "'__flag__' not in self.var or '%s' not in self.var['__flag__'] or not self.var['__flag__']['%s']%s%s" % (
            str(flagkey), str(flagkey), mode, str(flagvalue))
        return eval(cmd)


class moveset:
    """
    行动列表类，存放一系列行动列表
    行动函数要求返回值为下一次行动的ID，并且没有输入
    可以用start,next,end,exit函数族自动创建moveset序列
    也可以使用w,wv,wif对函数进行wrap后调用addmove手动创建
    变量区 self.var中的常驻变量：
        __return__ moveset执行完毕后的返回值
        __current__ 当前执行（还没有执行完）的步骤
        __start__ moveset的入口ID
        __flag__ 存放flag（临时变量）的Dict
        __onstart__ 可选参数，moveset执行时不管current首先跳转的ID
        __parent__ 上层moveset，该变量建议不修改，且会在save和load时主动跳过
        __self__ 自己moveset实例，请勿使用
        __stack__ 用于捕获异常后，记录上一次current。该变量建议不修改。
    可以使用addvar添加一个变量（或者在运行中使用带有v后缀的wrap函数动态创建）
    """

    def __init__(self, name, addr=None, use_json=True):
        """
        :param name: REC的名称
        :param addr: REC的存放路径（可以不写，在run函数中实现）
        :param use_json: 是否使用json格式存放REC，否则采用pickle格式存放
        """
        self.moves = {}  # 存放一系列MoveFun函数，{IDType:MoveFun->IDType}
        self.var = {}  # 变量区
        self.varinit = {}  # 存放初始化var的信息
        self.catch = {}  # 异常情况处理跳转
        self.errcode = None  # 自身异常代码
        self.parent = None  # 是否有父moveset（被其它moveset调用）
        self.addr = addr
        self.name = name
        self.use_json = use_json  # 警告：json类型只能支持数字和字符串变量！
        self.last_move = None  # 自动创建序列时记录上一次的创建参数
        self.tmp = {}  # 临时存放空间

    @staticmethod
    def str2fun(fun):
        """
        把一个str类型的fun用eval或exec函数执行，返回wrap后的函数
        :param fun: 字符串，如果不是字符串则直接返回。
        :return:
        """
        if type(fun) is str:
            funstr = fun

            def f(var: Dict = None):
                try:
                    return eval(funstr)
                except:
                    exec(funstr)

            fun = f
        elif fun is None:
            def f(var: Dict = None):
                pass

            fun = f
        return fun

    def copy(self):
        """
        复制自身，对变量区深拷贝，moves浅拷贝
        如果var中含有__parent__，则跳过
        跳过__self__
        """
        t = moveset(self.name, self.addr)
        t.moves = self.moves.copy()
        p = None
        if "__parent__" in self.var:
            p = self.var["__parent__"]
            del self.var["__parent__"]
        s = None
        if "__self__" in self.var:
            s = self.var["__self__"]
            del self.var["__self__"]
        t.var = deepcopy(self.var)
        if p is not None:
            self.var["__parent__"] = p
        if s is not None:
            self.var["__self__"] = s
        t.varinit = deepcopy(self.varinit)
        t.parent = self.parent
        t.use_json = self.use_json
        return t

    def setstart(self, id: IDType):
        self.varinit["__start__"] = id

    def setstatic(self, id: IDType):
        self.varinit["__start__"] = id

    def seterr(self, code) -> None:
        """
        如果该moveset运行时报错，且错误类型不为moveerr
        则该moveset向上报moveerr(code)错误
        设置为None时，向上传递原始错误
        :param code: 错误代码
        """
        self.errcode = code

    def addcatch(self, code, nextid: IDType, savecur=True) -> None:
        """
        新增一个错误解决方案
        :param code: 捕获的moveerr的code
        :param nextid: 捕获到code后跳转的ID
        :param savecur: 是否存储当前位置（存储后，可以使用__last__跳转）
        """
        self.catch[code] = (nextid, savecur)

    def addmove(self, id: IDType, fun: MoveFun, start=False) -> None:
        """
        新增一个行动
        :param id: 行动的ID
        :param fun: 行动函数，传入dict类型的变量var，返回值为下一次行动的ID
        :param start: 是否为第一个执行的行动
        """
        self.moves[id] = fun
        if start:
            self.setstart(id)

    def onstart(self, id: IDType):
        """
        设置当发生start事件（脚本运行）时，跳转的代码
        """
        self.varinit["__onstart__"] = id

    def _autoadd(self, fun: AnyFun, mode, *args, use_var=False, varmap=None, kwargs=None,
                 start_id=None, next_id=None, wrap=True, ret=None) -> int:
        """
        自动增加一个move，ID递增，后一个连接前一个
        该函数是总处理函数，具体调用可以看更详细的start,next,end,exith函数
        :param fun: 一个待wrap的函数
        :param mode: 增加模式
            0：用于start，开始一系列新的自动递增IDd的move
            1：用于next，第2个至倒数第二个move
            2：用于end和exit，最后一个move，此后连接到其它指定move（或__exit__)
            3：用于exit，指定返回值时。此时传来的fun应该是MoveFun类型，则最后一步不进行wrap。
        :param args: fun函数的参数
        :param use_var: fun函数是否包含var参数以接受变量区self.var
        :param varmap: var中变量到fun参数的映射
        :param kwargs: fun函数的参数，字典类型
        :param start_id: 用于mode 0：初始的ID，必须是一个整数
        :param next_id: 用于mode 2：结束时连接到的ID
        :param wrap: 设置为False则需要进一步wrap，设置为True则自动wrap
        :param ret: 将var中的ret变量设置为该函数返回值
        :return: int类型,该步骤的ID
        """
        if kwargs is None:
            kwargs = {}
        last = self.last_move
        fun = self.str2fun(fun)
        assert mode == 0 or last is not None, "必须先start！"
        if mode == 0:
            assert type(start_id) is int, "自动组建move，必须以int类型的id开始"
            self.last_move = (fun, start_id, args, varmap, kwargs, use_var, wrap, ret)
        if mode >= 1:
            last_fun, last_id, last_args, last_varmap, last_kwargs, last_use_var, last_wrap, last_ret = last
            assert type(last_id) is int, "自动组建move，上一个id必须是int类型！"
            if last_use_var:
                wpfun = self.wv(last_fun, last_id + 1, *last_args, ret=last_ret,
                                **last_kwargs) if last_wrap else last_fun
                self.addmove(last_id, wpfun)
            else:
                wpfun = self.w(last_fun, last_id + 1, *last_args, ret=last_ret, varmap=last_varmap,
                               **last_kwargs) if last_wrap else last_fun
                self.addmove(last_id, wpfun)
            self.last_move = (fun, last_id + 1, args, varmap, kwargs, use_var, wrap, ret)
        if mode == 2:
            last_id = self.last_move[1]
            if use_var:
                wpfun = self.wv(fun, next_id, *args, ret=ret, **kwargs) if wrap else fun
                self.addmove(last_id, wpfun)
            else:
                wpfun = self.w(fun, next_id, *args, ret=ret, varmap=varmap,
                               **kwargs) if wrap else fun
                self.addmove(last_id, wpfun)
            self.last_move = None
        elif mode == 3:
            last_id = self.last_move[1]
            self.addmove(last_id, fun)
            self.last_move = None
        if self.last_move is None:
            self.tmp["autoid"] = last_id
            return last_id
        else:
            self.tmp["autoid"] = self.last_move[1]
            return self.last_move[1]

    def startw(self, fun: AnyFun, *args, start_id: int = 0, ret=None, varmap=None, kwargs=None, start=False) -> int:
        """
           指定一个编号为start_id的move，此后可以利用next依次连接id递增的move
           不会将变量self.var传入fun中。
           要求start_id必须为整数
           :param fun: 一个待wrap的函数
           :param args: fun函数的参数
           :param ret: 将var中的ret变量设置为该函数返回值
           :param varmap: var中变量到fun参数的映射
           :param kwargs: fun函数的参数，字典类型
           :param start_id: 初始的ID，必须是一个整数
           :param start: 是否作为moveset的入口
           :return: int类型,该步骤的ID
           """
        if start:
            self.setstart(start_id)
        return self._autoadd(fun, 0, *args, use_var=False, ret=ret, varmap=varmap, kwargs=kwargs, start_id=start_id)

    def startwv(self, fun: AnyFun, *args, start_id: int = 0, ret=None, kwargs=None, start=False) -> int:
        """
           指定一个编号为start_id的move，此后可以利用next依次连接id递增的move
           要求fun含有参数var以接受变量区self.var
           要求start_id必须为整数
           :param fun: 一个待wrap的函数
           :param args: fun函数的参数
           :param ret: 将var中的ret变量设置为该函数返回值
           :param kwargs: fun函数的参数，字典类型
           :param start_id: 初始的ID，必须是一个整数
            :param start: 是否作为moveset的入口
           :return: int类型,该步骤的ID
           """
        if start:
            self.setstart(start_id)
        return self._autoadd(fun, 0, *args, use_var=True, ret=ret, kwargs=kwargs, start_id=start_id)

    def startset(self, ms, start_id: int = 0, start=False, ret=None, static=False,
                 initvar: Optional[Dict] = None) -> int:
        """
        wrap个moveset，并作为start。
        :param ms: moveset类
        :param ret: 将var中的ret变量设置为该函数返回值
        :param static: 如果设置为True，在子moveset结束后，其变量区不删除
        :param initvar: 补充修改原movesetd的初值
        :param start_id: 初始的ID，必须是一个整数
        :param start: 是否作为moveset的入口
        :return: int类型,该步骤的ID
        """
        fset = self.wset(ms, 0, ret, static, initvar)
        return self.startwv(fset, ret=None, start_id=start_id, start=start)

    def nextw(self, fun: AnyFun, *args, ret=None, varmap=None, kwargs=None) -> int:
        """
            wrap一个fun，并将它与上一次start或next的fun连接。
            不会将变量self.var传入fun中。
         :param fun: 一个待wrap的函数
         :param args: fun函数的参数
         :param ret: 将var中的ret变量设置为该函数返回值
         :param varmap: var中变量到fun参数的映射
         :param kwargs: fun函数的参数，字典类型
         :return: int类型,该步骤的ID
         """
        return self._autoadd(fun, 1, *args, use_var=False, ret=ret, varmap=varmap, kwargs=kwargs)

    def nextwv(self, fun: AnyFun, *args, ret=None, kwargs=None) -> int:
        """
            wrap一个fun，并将它与上一次start或next的fun连接。
            要求fun含有参数var以接受变量区self.var
         :param fun: 一个待wrap的函数
         :param args: fun函数的参数
         :param ret: 将var中的ret变量设置为该函数返回值
         :param kwargs: fun函数的参数，字典类型
         :return: int类型,该步骤的ID
         """
        return self._autoadd(fun, 1, *args, use_var=True, ret=ret, kwargs=kwargs)

    def nextset(self, ms, ret=None, static=False, initvar: Optional[Dict] = None) -> int:
        """
        wrap个moveset，并连接到next。
        :param ms: moveset类
        :param ret: 将var中的ret变量设置为该函数返回值
        :param static: 如果设置为True，在子moveset结束后，其变量区不删除
        :param initvar: 补充修改原movesetd的初值
        :return: int类型,该步骤的ID
        """
        fset = self.wset(ms, 0, ret, static, initvar)
        return self.nextwv(fset, ret=None)

    def endw(self, fun: AnyFun, *args, next_id: Optional[IDFun] = None, ret=None, varmap=None, kwargs=None) -> int:
        """
         wrap一个fun，并将它与上一次start或next的fun连接。
         结束整个自动创建流程，新fun将指向next_id处
         不会将变量self.var传入fun中。
        :param fun: 一个待wrap的函数
        :param args: fun函数的参数
        :param ret: 将var中的ret变量设置为该函数返回值
        :param varmap: var中变量到fun参数的映射
        :param kwargs: fun函数的参数，字典类型
        :param next_id: 结束时连接到的ID
        :return: int类型,该步骤的ID
        """
        return self._autoadd(fun, 2, *args, next_id=next_id, kwargs=kwargs, ret=ret, varmap=varmap, use_var=False)

    def endwv(self, fun: AnyFun, *args, next_id: Optional[IDFun] = None, ret=None, kwargs=None) -> int:
        """
          wrap一个fun，并将它与上一次start或next的fun连接。
          结束整个自动创建流程，新fun将指向next_id处
          要求fun含有参数var以接受变量区self.var
         :param fun: 一个待wrap的函数
         :param args: fun函数的参数
         :param ret: 将var中的ret变量设置为该函数返回值
         :param kwargs: fun函数的参数，字典类型
         :param next_id: 结束时连接到的ID
         :return: int类型,该步骤的ID
         """
        return self._autoadd(fun, 2, *args, next_id=next_id, ret=ret, kwargs=kwargs, use_var=True)

    def endset(self, ms, next_id: Optional[IDFun] = None, ret=None, static=False, initvar: Optional[Dict] = None):
        """
          wrap个moveset，并连接到end。
          :param ms: moveset类
          :param ret: 将var中的ret变量设置为该函数返回值
          :param static: 如果设置为True，在子moveset结束后，其变量区不删除
          :param initvar: 补充修改原movesetd的初值
          :param next_id: 结束时连接到的ID
          :return: int类型,该步骤的ID
          """
        fset = self.wset(ms, next_id, ret, static, initvar)
        return self.endwv(fset, ret=None, next_id=None)

    def endif(self, con: ConFun, trueid: IDType, falseid: IDType) -> int:
        """
        结束一个自动添加系列，按照con条件转到其它分支
        :param con: 条件函数，参数为var字典，返回true或false
        :param trueid: 返回为true时进行的分支
        :param falseid: 返回为false时进行的分支:
        :return: int类型,该步骤的ID
        """
        iffun = self.wif(con, trueid, falseid)
        return self._autoadd(iffun, mode=2, use_var=True, wrap=False)

    def exitw(self, fun: AnyFun, *args, ret=None, return_=None, varmap=None, kwargs=None) -> int:
        """
         wrap一个fun，并将它与上一次start或next的fun连接。
         结束整个moveset，并且返回return_（如果设置为None，则不会特别设置返回值）
         不会将变量self.var传入fun中。
        :param fun: 一个待wrap的函数
        :param args: fun函数的参数
        :param varmap: var中变量到fun参数的映射
        :param kwargs: fun函数的参数，字典类型
        :param ret: 将var中的ret变量设置为该函数返回值，设置为__return__时，若存在return_参数，则__return__看return_
        :param return_: 返回值，设置为None时，不会特别设置返回值
        :return:int类型,该步骤的ID
        """
        if return_ is None:
            return self._autoadd(fun, 2, *args, next_id="__exit__", varmap=varmap, ret=ret, kwargs=kwargs,
                                 use_var=False)
        else:
            def f(var: Dict) -> IDType:
                a = fun(*args, **kwargs)
                if ret is not None:
                    var[ret] = a
                var["__return__"] = return_
                return "__exit__"

            return self._autoadd(f, 3)

    def exitwv(self, fun: AnyFun, *args, ret=None, return_=None, kwargs=None) -> int:
        """
         wrap一个fun，并将它与上一次start或next的fun连接。
         结束整个moveset，并且返回return_（如果设置为None，则不会特别设置返回值）
        要求fun含有参数var以接受变量区self.var
        :param fun: 一个待wrap的函数
        :param args: fun函数的参数
        :param kwargs: fun函数的参数，字典类型
        :param ret: 将var中的ret变量设置为该函数返回值，设置为__return__时，若存在return_参数，则__return__看return_
        :param return_: 返回值，设置为None时，不会特别设置返回值
        :return: int类型,该步骤的ID
        """
        if return_ is None or ret:
            return self._autoadd(fun, 2, *args, next_id="__exit__", ret=ret, kwargs=kwargs, use_var=True)
        else:
            def f(var: Dict) -> IDType:
                a = fun(var, *args, **kwargs)
                if ret is not None:
                    var[ret] = a
                var["__return__"] = return_
                return "__exit__"

            return self._autoadd(f, 3)

    def exitset(self, ms, ret=None, return_=None, static=False, initvar: Optional[Dict] = None) -> int:
        """
          wrap个moveset，并连接到end。
          :param ms: moveset类
          :param static: 如果设置为True，在子moveset结束后，其变量区不删除
          :param initvar: 补充修改原movesetd的初值
          :param ret: 将var中的ret变量设置为该函数返回值，设置为__return__时，若存在return_参数，则__return__看return_
          :param return_: 返回值，设置为None时，不会特别设置返回值
          :return: int类型,该步骤的ID
          """
        fset = self.wset(ms, 0, None, static, initvar)
        return self.exitwv(fset, ret=ret, return_=return_)

    def addvar(self, varname, init=None) -> None:
        """
        新增一个变量
        :param varname: 变量的名称
        :param init: 变量的初值
        """
        self.varinit[varname] = init

    def setdefault(self):
        """
        初始化变量区
        """
        for i, j in self.varinit.items():
            self.var.setdefault(i, j)
        self.var.setdefault("__current__", None)
        self.var.setdefault("__return__", None)
        self.var.setdefault("__start__", None)

    @staticmethod
    def w(fun: AnyFun, nextid: Optional[IDFun] = None, *args, ret=None, varmap: Optional[Dict] = None,
          **kwargs) -> MoveFun:
        """
        wrap一个普通函数为行动函数，并且该函数不会使用到变量var
        :param fun: 需要wrap的函数
        :param ret: 将var中的ret变量设置为该函数返回值
        :param varmap: 指定某些var中变量到fun参数的映射
        :param nextid: 下一个行动的ID，若设置为None，则以fun的返回值为准；也可以为映射函数
        :param args: fun函数的参数
        :param kwargs: fun函数的参数
        :return: wrap后的函数
        """
        fun = moveset.str2fun(fun)
        if varmap is None:
            varmap = {}

        def f(var: Dict):
            for i, j in varmap.items():
                kwargs[j] = var[i]
            a = fun(*args, **kwargs)
            if ret is not None:
                var[ret] = a
            if callable(nextid):
                nid = nextid(a)
            else:
                nid = nextid
            return a if nid is None else nid

        return f

    @staticmethod
    def wv(fun: AnyFun, nextid: Optional[IDFun] = None, *args, ret=None, **kwargs) -> MoveFun:
        """
        wrap一个普通函数为行动函数，该函数必须携带var参数来接受变量区
        :param fun: 需要wrap的函数
        :param ret: 将var中的ret变量设置为该函数返回值
        :param nextid: 下一个行动的ID，若设置为None，则以fun的返回值为准
        :param args: fun函数的参数
        :param kwargs: fun函数的参数
        :return: wrap后的函数
        """
        fun = moveset.str2fun(fun)

        def f(var: Dict):
            a = fun(*args, **kwargs, var=var)
            if ret is not None:
                var[ret] = a
            if callable(nextid):
                nid = nextid(a)
            else:
                nid = nextid
            return a if nid is None else nid

        return f

    @staticmethod
    def wif(con: ConFun, trueid: IDType, falseid: IDType) -> MoveFun:
        """
        wrap一个分支跳转函数
        :param con: 条件函数，参数为var字典，返回true或false
        :param trueid: 返回为true时进行的分支
        :param falseid: 返回为false时进行的分支
        :return: wrap后的函数
        """
        con = moveset.str2fun(con)

        def f(var: Dict):
            if con(var):
                return trueid
            else:
                return falseid

        return f

    @staticmethod
    def wset(ms, nextid: Optional[IDFun] = None, ret=None, static=False,
             initvar: Optional[Dict] = None) -> MoveFun:
        """
        wrap个moveset
        :param ms: moveset类
        :param nextid: 下一个行动的ID，若设置为None，则以ms的的返回值为准
        :param ret: 将var中的ret变量设置为该函数返回值
        :param static: 如果设置为True，在子moveset结束后，其变量区不删除
        :param initvar: 补充修改原movesetd的初值
        """
        sub_name = "__moveset__%s" % ms.name
        ms = ms.copy()
        if initvar is None:
            initvar = {}

        def f(var: Dict):
            var.setdefault(sub_name, {})
            var[sub_name].update(initvar)
            try:
                a = ms.run(var=var[sub_name], continue_=True, parent=var["__self__"])
                if ret is not None:
                    var[ret] = a
            finally:
                if not static:
                    del var[sub_name]
            if callable(nextid):
                nid = nextid(a)
            else:
                nid = nextid
            return a if nid is None else nid

        return f

    @staticmethod
    def wvar(var: Dict):
        return movevar(var)

    @staticmethod
    def addstack(var: Dict, stack_id: IDType):
        var.setdefault("__stack__", [])
        var["__stack__"] += [stack_id]

    @staticmethod
    def popstack(var: Dict):
        if "__stack__" in var:
            s = var["__stack__"]
            p = s[-1]
            del s[-1]
            if len(s) == 0:
                del var["__stack__"]
            return p
        else:
            raise Exception("Stack Empty!")

    def T_mapstart(self,
                   id_map: Union[Dict[Union[IDType, List[IDType]], IDType], Callable[[IDType], Union[IDType, None]]],
                   self_id=999999, popstack=True):
        """
        模板：进入moveset时，如果上一步current在某些特殊位置时，跳转到特定ID。
        要求：该模板会重写onstart！
        :param id_map:
            若id_map为一个IDType->IDType的函数，则直接执行current->id_map(current)的映射
                若映射结果为None，则执行__last__。请不要自己跳转__last__。
            若id_map为一个IDType:IDType的字典，则检测到指定左值，跳转到对应右值，其余__last__。
                该字典的左值也可以为列表[]，表示多点映射
                或者一个返回布尔类型的函数，则该函数返回值为True时跳转到右值
                或者一个二元Tuple[a,b],则a<=current<=b的全部ID跳转到右值。
        :param self_id:
            mapstart跳转逻辑存放的ID
        :param popstack:
            是否自动删除多余的cur
            若选择手动删除，则需要在程序中自行跳转__last__或者用moveset.popstack(var)手动删除
            若选择自动删除，请不要将id映射到__last__上，而应该为None。
        """
        self.onstart(self_id)

        def f(var):
            def do(next_cur):
                if next_cur is None:
                    return "__last__"
                else:
                    if popstack:
                        moveset.popstack(var)
                    return next_cur

            last_cur = var["__stack__"][-1]
            if callable(id_map):
                next_cur = id_map(last_cur)
                return do(next_cur)
            else:
                for con, next_cur in id_map.items():
                    if callable(con):
                        if con(last_cur):
                            return do(next_cur)
                    elif type(con) is list:
                        if last_cur in con:
                            return do(next_cur)
                    elif type(con) is tuple:
                        if con[0] <= last_cur <= con[1]:
                            return do(next_cur)
                    else:
                        if last_cur == con:
                            return do(next_cur)
            return "__last__"

        self.addmove(self_id, self.wv(f))

    def T_forcestart(self, start_id: IDType, self_id: IDType = 999999):
        """
        模板：强制从某ID开始
        不沦上次运行到哪里，重新进入moveset后强制跳转到start_id
        与onstart，start冲突。
        :param start_id: 强制跳转位置
        :param self_id: 自身逻辑位置
        """
        self.T_mapstart(lambda x: start_id, self_id)

    def T_nextflag(self, flagkey, flagvalue=1):
        """
        模板：基于nextwv，设置某flag的值为某数
        :param flagkey: flag名称
        :param flagvalue: flag新值
        :return: 该步骤的ID
        """

        def f(var):
            var.setdefault("__flag__", {})
            var["__flag__"][flagkey] = flagvalue

        return self.nextwv(f)

    def T_clearflags(self):
        """
        模板：清除所有flag
        :return: 该步骤的ID
        """

        def f(var):
            if "__flag__" in var:
                del var["__flag__"]

        return self.nextwv(f)

    def _T_if(self, cmd) -> IDType:
        self_id = self.tmp["autoid"] + 1
        self.endw(None, next_id=self_id)
        self.tmp.setdefault("ifflag", [])  # if栈
        ifpack = {"self": self_id, "true": self_id + 1, "cmd": cmd}
        self.tmp["ifflag"] += [ifpack]
        return self.startw(None, start_id=self_id + 1)

    def T_ifflag(self, flagkey, flagvalue=1, mode="==") -> IDType:
        """
        模板：只有当flag满足条件时才执行后续语句块内容
        注：flag为临时变量，存储在__flag__中，对一般变量，见T_if
        last->IFFLAG{
            END-><IF>
                True-> ** start **
                False-> ...
            -> ...
        }
        其中** start ** 为该模板最后一步，所以使用T_ifflag后，需要使用next,end或exit继续。
        :param flagkey: flag名称
        :param flagvalue: flag比较值
        :param mode: 比较模式(==,<=,>=,!=,<,>...)
        :return: start的ID
        """
        cmd = "'__flag__' in var and '%s' in var['__flag__'] and var['__flag__']['%s']%s%s" % (
            str(flagkey), str(flagkey), mode, str(flagvalue))
        return self._T_if(cmd)

    def T_if(self, key, value=1, mode="=="):
        """
        模板：只有当key满足条件时才执行后续语句块内容
        :param key: key名称
        :param value: key比较值
        :param mode: 比较模式(==,<=,>=,!=,<,>...)
        :return: start的ID
        """
        cmd = "'%s' in var and var['%s']%s%s" % (str(key), str(key), mode, str(value))
        return self._T_if(cmd)

    def T_ifnotflag(self, flagkey, flagvalue=1, mode="=="):
        cmd = "'__flag__' not in var or '%s' not in var['__flag__'] or not var['__flag__']['%s']%s%s" % (
            str(flagkey), str(flagkey), mode, str(flagvalue))
        return self._T_if(cmd)

    def T_ifnot(self, key, value=1, mode="=="):
        cmd = "'%s' not in var or not var['%s']%s%s" % (str(key), str(key), mode, str(value))
        return self._T_if(cmd)

    def T_else(self) -> IDType:
        """
        模板：与T_if或T_ifflag成对使用
        last->IFFLAG{
            END-><IF>
                True-> ...
                False-> ** start **
            -> ...
        }

        其中** start ** 为该模板最后一步，所以使用T_if或T_ifflag后，需要使用next,end或exit继续。
        :return: ；start的ID
        """
        # 取出之前的IF包
        lastpack = self.tmp["ifflag"][-1]
        # 检查配对性
        assert "self" in lastpack and "true" in lastpack and "cmd" in lastpack, "else需要和if配对"
        # 结束前面的IF，准备跳转
        endif_id = self.tmp["autoid"] + 1
        self.endw(None, next_id=endif_id + 1)
        else_id = endif_id + 1
        # 构造新的IF包
        self.tmp["ifflag"][-1] = {"endif_id": endif_id}
        # 补全之前的IF
        self_id = lastpack["self"]
        true_id = lastpack["true"]
        cmd = lastpack["cmd"]
        self.addmove(self_id, self.wif(cmd, true_id, else_id))
        # start
        return self.startw(None, start_id=else_id)

    def T_end(self):
        """
        模板：与T_if或T_ifflag成对使用
        last->IFFLAG{
            END-><IF>
                True-> ...
                False-> ...
            -> ** start **
        }
        其中** start ** 为该模板最后一步，所以使用T_if或T_ifflag后，需要使用next,end或exit继续。
        :return: start的ID
        """
        # 取出之前的IF包
        lastpack = self.tmp["ifflag"][-1]
        del self.tmp["ifflag"][-1]
        # 结束之前的部分
        if self.last_move is not None:
            end_id = self.nextw(None)
        else:
            end_id = self.tmp["autoid"] + 1
            self.startw(None, start_id=end_id)
        # 如果是IF包：
        if "self" in lastpack and "true" in lastpack and "cmd" in lastpack:
            # 补全IF
            self_id = lastpack["self"]
            true_id = lastpack["true"]
            cmd = lastpack["cmd"]
            self.addmove(self_id, self.wif(cmd, true_id, end_id))
        # 如果是else包：
        elif "endif_id" in lastpack:
            # 补全Else
            endif_id = lastpack["endif_id"]
            self.addmove(endif_id, self.w(None, nextid=end_id))
        else:
            raise Exception("Cannot find IF flag or ELSE flag!")
        return end_id

    def _savestate(self):
        if not os.path.isdir(self.addr):
            os.makedirs(self.addr)
        path = "%s\\%s.rec" % (self.addr, self.name)
        if not self.use_json:
            mode = "wb"
        else:
            mode = "w"
        file = open(path, mode)
        if self.use_json:
            json.dump(self.var, file, indent=1)
        else:
            pickle.dump(self.var, file)
        file.close()

    def _loadstate(self):
        path = "%s\\%s.rec" % (self.addr, self.name)
        if not os.path.exists(path):
            return
        if not self.use_json:
            mode = "rb"
        else:
            mode = "r"
        file = open(path, mode)
        self.var.clear()
        if self.use_json:
            self.var.update(json.load(file))
        else:
            self.var.update(pickle.load(file))
        file.close()

    def savestate(self):
        """
        保存变量区的内容
        跳过全部的__parent__
        """
        p = self
        if p.parent is not None:
            del p.var["__parent__"]
            del p.var["__self__"]
            p.parent.savestate()
            p.var["__parent__"] = p.parent.var
            p.var["__self__"] = p
        else:
            del p.var["__self__"]
            p._savestate()
            p.var["__self__"] = p

    def loadstate(self):
        """
        从文件加载变量区的内容
        """
        p = self
        while p.parent is not None:
            p = p.parent
        p._loadstate()

    def run(self, addr=None, continue_=True, var=None, start: Optional[IDType] = None, parent=None):
        """
        启动moveset
        :param var: 指定变量区域的（某些）值，其余使用初值
        :param continue_: 是否从上一次中断处继续
        :param start: 指定开始ID
        :param parent: moveset类型，指定父亲
        :param addr: 设置存储路径位置
        :return: moveset的返回值（self.var["__return__"]）
        """
        if var is not None:
            self.var = var
        self.setdefault()
        self.parent = parent
        if addr is not None:
            self.addr = addr
        cur = None
        if continue_:
            if self.parent is None:
                self.loadstate()
            cur = self.var["__current__"]

        if cur is None:
            cur = start if start is not None else self.var["__start__"]
        if self.parent is not None:
            self.var["__parent__"] = self.parent.var
        self.var["__self__"] = self

        # OnStart 检测
        if "__onstart__" in self.var and self.var["__onstart__"] is not None:
            self.addstack(self.var, cur)
            cur = self.var["__onstart__"]
        while cur in self.moves or cur == "__last__":
            if cur == "__last__":
                # 跳转到上一次保存的位置
                if "__stack__" in self.var:
                    cur = self.var["__stack__"][-1]
                    del self.var["__stack__"][-1]
                    if len(self.var["__stack__"]) == 0:
                        del self.var["__stack__"]
                else:
                    cur = "__exit__"
                    raise Exception("Current Stack Empty!")
            self.var["__current__"] = cur
            self.savestate()
            try:
                cur = self.moves[cur](self.var)
            except moveerr as me:
                if me.code in self.catch:
                    # 暂存当前cur并跳转
                    nextid, savecur = self.catch[me.code]
                    if savecur:
                        self.var.setdefault("__stack__", [])
                        self.var["__stack__"] += [cur]
                    cur = nextid
                else:
                    raise me
            except Exception as e:
                if "__parent__" in self.var:
                    del self.var["__parent__"]
                del self.var["__self__"]
                if type(e) is not moveerr and self.errcode is not None:
                    raise moveerr(self.errcode, desc=self.name)
                else:
                    raise e

        self.var["__current__"] = None
        self.savestate()
        if cur != "__exit__":
            raise Exception("Unknown Moveset:", cur)
        if "__parent__" in self.var:
            del self.var["__parent__"]
        del self.var["__self__"]
        return self.var["__return__"]
