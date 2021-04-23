# [For Developer] Scene框架的使用

> 从v2.6dev之后，引入了FunctionChecker框架和Scene框架，这使得程序的可读性大大提高，并且增加了程序运行的稳定性。
> 该文档仅为一个引入，具体使用还是看代码吧。

## 名词解释和使用方式

- Checker

  Checker是种特殊的函数的封装，它的输入参数不作限制，但是输出为bool类型。
  ```
  Checker(fun: Callable[[Any], bool], vardict: Optional[Dict[str, Any]] = None, funvar=None, name=None)
  ```
  其中，vardict可以给该函数传递默认参数，funvar则是该函数需求参数的列表（如果不指定，则会通过inspect自动分配），
  name则是用于__repr__的一个Checker名字。
  
  Checker是FunctionChecker的重要组成部分，在众多“发生了什么 - 就做什么”之中， Checker扮演了那个判断“发生了什么”的函数。
  
- FunctionChecker
  
  一套“发生了什么 - 就做什么”的规则，通常简写为FC。通过`add`函数添加一条“发生了什么 - 就做什么” 的规则，通过`run`来执行检查流程。
  
  ```
  FunctionChecker().add(checker: Union[Checker, bool], dofunction: Optional[Callable] = None, rv=None, raise_=None,
            clear=False)
  ```
  其中最重要的元素为Checker和dofunction，分别代表了“发生了什么 - 就做什么”。
  
  注意：dofunction是一个没有输入参数也与FunctionChecker内部作用域无关的函数，并不能共享变量，使用起来可能不太方便。
  一个替代方法是直接在checker里写执行逻辑，这也是一种比较推荐的写法。
  实际应用中，大部分常用Checker都已经被封装好，因此`add`函数使用频次并不多。
  
  一条“发生了什么 - 就做什么”的触发逻辑为：
  ```
  Checker 为真 {
    执行dofunction
    如果clear为True，则清除FunctionChecker的内部计时器（基本用不到这个，仅当暂停恢复后重置lock的timeout时使用）
    如果raise不为None，则整个FunctionChecker().run()停止运行并触发指定异常。
    如果rv不为None，则整个FunctionChecker().run()停止并返回rv。
  }
  ```  
  
  当用一系列`.add`编辑好FunctionChecker之后，就可以使用`.run()`运行了，如果内部产生了返回值，则run()函数将产生相应的返回值。

- ReturnValue

  ReturnValue是一种特殊的异常。在FunctionChecker.run()函数执行中，如果需要终止整个run的执行并让run返回指定的值，
  则在任何Checker或者dofunction中触发ReturnValue异常，并注明相应的返回值即可。
  
  ```
  raise ReturnValue(value=...)
  ```

- lock
  
  锁定是FunctionChecker的另一个常用函数。和run不同的是，run只会检查一次该FC所含有的全部”发生了什么 - 就做什么“规则，
  而lock会持续检查该规则，直到产生了返回值为止。
  
  ```
  FC.lock(delay=0.5, timeout=None, until=None, is_raise=True)
  ```
  
  其中delay为每次检查之间的间隔，timeout为lock运行时间上限，如果超时且is_raise设置为True，则会返回LockTimeoutError。
  如果设置了until，则跳出lock的条件必须返回值满足until所代表的条件。until可为一个值、一个容器或一个函数。

- LockError

  LockError是lock所对应的错误，包含两个子错误：LockTimeoutError和LockMaxRetryError。其中常用的是LockTimeoutError。
  它不仅在lock中被使用，也应该在其它任何想使用超时错误的地方使用。
  
- FunctionChecker的其它成员

  - set_target(target)
  
    设置Checker的目标返回值，默认为True，表示Checker返回True则执行dofunction。
    
  - update_var(fun, varname, name="update_var", *args, **kwargs)
  
    使用fun(*args,**kwargs)的返回值更新内部作用域中varname的值。
    
    回忆Checker含有funname参数（指定或自动生成），如果内部作用域中含有**同名**的参数，该参数将被传入Checker中。
    后文介绍的ElementFunction.getscreen就是一个最常用、最经典的update_var函数，它截图后将图片传入
    内部的screen参数中，则如果Checker含有screen变量，就会自动使用该screen作为判断的标准，如`exist`函数等。
    
  - add_process(dofunction: Callable, name="process")
  
    添加一个过程（也就是Checker恒真的规则）。
    
  - add_intervalprocess(dofunction: Callable, retry=None, interval=1, name="interval_process",
                            raise_retry=False)
    
    添加一个定时触发的过程。与add_process不同的是，dofunction触发一次后，再过`interval`秒才会触发下一次。
    可以增加retry参数指定最多【再次】触发的次数（第一次不算）。如果触发满retry次，则会终止run并返回False。
    但如果设置了raise_retry，则会触发`LockMaxRetryError`。
    
    该方法用来模拟lockimg中的elseclick和elsedelay参数时非常管用。
  
- ElementChecker

  ElementChecker是FunctionChecker的派生类，初始化一个ElementChecker需要包含参数a，表示一个Automator类。
  
  基于Automator，ElementChecker提供了很多常用的规则。
  
  - getscreen(force=False)
    
    截屏，并且记录屏幕信息到内部存储空间**screen**中。如果设置了force=True，则每次运行到该规则都会重新截屏。
    
    默认设置为force=False，这意味着在一次规则运行过程中，只有第一个getscreen会截屏，后面的getscreen都将跳过。
    
  - wait_for_loading(force_getscreen=False)
  
    等待，直至loading画面结束。如果设置了force_getscreen，则检查的画面将被强制更新，否则第一次检查的画面为Automator.last_screen。
    
  - exist(img: Union[PCRelement, str], dofunction: Optional[Callable] = None, rv=True, raise_=None,
              clear=False,
              **kwargs):
    
    判断是否有img存在。使用exist前，必须保证至少含有一个getscreen函数。
    
  - not_exist(img: Union[PCRelement, str], dofunction: Optional[Callable] = None, rv=True, raise_=None,
                  clear=False,
                  **kwargs)
  
    判断是否img不存在。需要前置getscreen函数
    
  - click(*args, pre_delay=0., post_delay=0., interval=0, retry=None, **kwargs)
  
    点击屏幕的操作。
    
  - sleep(sec)
  
    其实就是time.sleep
    
  - bind_ES(es: ExceptionSet, name="ExceptionSet")
  
    运行一个异常集ExceptionSet，ExceptionSet将在下文介绍。

- ExceptionSet

  异常集，通常简写为ES，是多个FunctionChecker的集合。之所以叫异常集，是因为ExceptionSet.run是没有返回值的，只能通过
  异常来与外界交互（其实一般也不交互）。ExceptionSet中的每个FC通常对应了一组异常处理的方法。
  
  每一个Automator都自带一个初始的异常集`Automator.ES`，并且提供了一个`Automator.getFC`的操作来获得一个绑定了
  该Automator的ElementChecker。回忆ElementChecker，它的初始化必须要有Automator实例来进行相关操作的绑定。
  
  ```
  getFC(self,header=True)
  ```
  其中header=True时，会默认在生成的ElementChecker中，事先增加一条`bind_ES`与自身的ExceptionSet绑定。也就是说，
  如果在ExceptionSet中增加一些预先的异常判断，这些异常判断将会贯穿在每一个基本操作之中（所有基础操作都已经用getFC改写）！
  这对于保证稳定性是非常有利的。
  
  Automator在进入时会默认启动`register_base_ES`，增加一条wait_for_loading(force=False)的判断。也就是说，此后
  任何操作的执行（包括click，lockimg，……）都会预先判断last_screen是否为loading，否则就等待。
  
  此外，我们也可以自行向ExceptionSet中注册一条FunctionChecker，可以参考其register和clear成员函数，通过指定不同的group
  我们可以同时在一个ExceptionSet上挂载多个自定义异常规则。
  
  一个典型的应用场景是延迟弹出的提示框。如果有一个提示框延迟弹出，那么前一个lockimg可能误以为并没有该提示框从而
  执行后一个lockimg了，那么当该提示框阻挡界面，将没有任何方法可以跳过该提示框。此时，通过挂在一个“出现提示框就点击确认”的
  FunctionChecker到默认异常集上，就能完美解决该问题，只需要定期清除即可。
  
  使用with命令可以暂时性挂载FC。
  
  ```
  with self.ES(myFunctionChecker):
      # Do Something
  ```
  
  ！注意： 需要挂载到ES上的FC，不能含有相同的bind_ES，否则会循环调用导致错误。使用Automator.getFC(header=False)，可以避免
  挂载自身ES。
  
- Scene

  最后就是场景的概念。使用场景之前，大量函数全部积压在Automator类中，导致调用困难，修改困难。例如战斗函数，不同的场景战斗函数其实
  有细微的区别，但如果在Automator中写zhuxian_zhandou, tansuo_zhandou, dxc_zhandou ... ，就完全不能做到代码重用，并且命名也
  非常反人类。
  
  使用场景的好处是，通过判断脚本运行到的当前的场景，绑定只会在该场景出现的各种方法。这样就可以在同一个场景中随意添加子函数而不用
  担心命名问题，且调用时一目了然。如果多个场景共享大部分的操作，可以写一个场景基类，如FightingBase为战斗场景的基类，如果竞技场
  的战斗需要微调其中的某些函数，则只需写FightingJJC来继承该基类，重写部分函数即可。
  
  关于场景的更多细节见下文。
  
## 场景使用简介

- PCRSceneBase

  PCRSceneBase类是所有场景类的基类，可以在scenes/scene_base.py中找到相关的实现。所有场景类必须在初始化时传入参数a，为Automator，
  以便提供场景的控制方法。在init函数中，可以看到场景类中复制了Automator中的很多基础函数，因此在Automator中的代码可以直接
  复制到scene中，如click, lockimg等等。如果需要调用其它的方法或属性，可以直接访问self._a即可。
  
  构造一个场景的起手式如下：
```python
from scenes.scene_base import PCRSceneBase
class MyScene(PCRSceneBase):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.scene_name="MyScene"
        self.initFC = ...
        self.feature = ...
```
  在初始化函数中，最重要的三个属性就是scene_name，initFC，feature。
  
  scene_name用于指定该场景的名字，通常就是类名即可，用于__repr__。
  
  initFC参数为进入该场景时自动挂载（到self.ES）的FunctionChecker，通常无需特殊设置（默认值None）。
  如果设置了initFC，可以应对某些场景进入时的特殊判断（如可可萝跳过等）。
  注意该FC会一直伴随直到场景切换，所以对于加载了initFC的场景，通常需要手动使用self.clear_initFC来手动清除它。
  此外也可以通过set_initFC方法手动再次加载。
  
  feature为最最最重要的scene参数，它是一个特征函数，其参数有且只有一个**screen** （不能换成其它名称）且返回值为True或False，
  表示该场景的特征是否出现。一个场景可能有一个特征，也可能有多个特征。特征是判断场景出现和消失的最重要的属性，所以尽量选择
  与相邻场景不一致的、与点击位置不同（点击的地方会有涟漪特效）的地方作为特征。feature函数里不应该出现任何u2操作（点击、拖动等），
  而只应含有对screen的相关图像操作(exist等)。
  
  对于常用的feature，PCRSceneBase提供了fun_feature_exist函数用来快速创建一个“存在某一元素”的feature，详见代码。
  
- 场景的分类

  我们把PCR中的场景分为两类，一种是整体场景（PCRSceneBase），一种是消息框场景(PCRMsgBoxBase)，其中PCRMsgBoxBase是PCRSceneBase的
  子类。它们的跳转逻辑有稍许不同，因此在构建场景时，选择继承正确的场景很重要。
  
  区别消息框场景的最大特点就是：消息框是可以通过狂点外部区域（如(1,1)）使其消失的，不过部分消息框可能不具备这一属性，但
  因为其表现为大场景上的某一个含有功能性按钮的小部分（如网路错误提示）也应该算作PCRMsgBoxBase。
  
- 场景的基本方法

  - enter方法
  ```
  enter(self,timeout=None)
  ```
  该函数将首先清除其它场景的initFC，并挂载自身场景的initFC，随后等待自身feature的出现。如果超出了timeout，则产生LockTimeoutError。
  
  通常不会主动使用这一函数。该函数返回值为场景本身。
  
  - goto方法
  
  ```
  goto(self, scene: Union[Type["PCRSceneBase"], Type["PCRMsgBoxBase"]], gotofun, use_in_feature_only=None,
             before_clear=True, timeout=None, interval=8, retry=None)
  ```
  最重要最基础的场景跳转函数。
  
  scene为一个场景类的**TYPE**，不是实例！表示跳转的目标场景。
  
  gotofun为为了达到该场景所不断执行的函数，该函数通常仅仅是一个普通的click而不需要lockimg等，因为goto本身就lock了场景的触发了。
  
  PCRSceneBase提供了fun_click函数可以简单地封装click操作，详见程序。
  
  use_in_feature_only针对跳转的对象是PCRSceneBase或者PCRMsgBoxBase提供了不同的默认属性，但还是建议手动设置。
  设置为False时，判断跳转成功的方法是原场景特征消失，新场景特征出现；而设置为True时，判断的标准仅为新场景特征出现。
  （在弹出MsgBox时，原场景的特征不一定消失。）
  
  before_clear参数决定了是否在goto执行之前就清除自身的initFC。
  
  timeout，interval，retry见FC的lock与add_intervalprocess。
  
  goto函数将返回对应场景类的实例，因此可以使用连用goto。如：
  
  ```
  M = self.get_zhuye().goto_maoxian().goto_normal()
  ```
  其中get_zhuye为起手式，内含lock_home逻辑，返回的是WoDeZhuYe场景类。
  
  注意：为了保证自动补全的舒适，建议每一个自建场景类的goto都加上返回值的类型标识。
  
  - exit方法
  
  ```
  exit(self, exitfun, before_clear=True, timeout=None, interval=8, retry=None)
  ```
  不断执行exitfun直到自身feature消失，类似goto，不过通常用于MsgBox中，因为像“关闭”操作并不会进入一个新的场景。
  
- 多场景判断

  有时，某一个操作之后可能会出现多个不同的场景，我们并不知道它会进入哪一个场景，或者弹出哪一个MsgBox。使用PossibleSceneList类
  可以完美解决这一问题。
  
  PossibleSceneList类是一个特殊的PCRSceneBase子类，它主要用于场景的中转。关于它的使用例可以见scenes/zhuxian/zhuxian_msg.py中的AfterSaoDangScene。
```python
class AfterSaoDangScene(PossibleSceneList):
    def __init__(self, a, *args, **kwargs):
        msgbox_list = [
            ChaoChuShangXianBox(a),
            LevelUpBox(a),
            TuanDuiZhanBox(a),
            XianDingShangDianBox(a),
        ]
        self.ChaoChuShangXianBox = ChaoChuShangXianBox
        self.LevelUpBox = LevelUpBox
        self.TuanDuiZhanBox = TuanDuiZhanBox
        self.XianDingShangDianBox = XianDingShangDianBox
        super().__init__(a,msgbox_list)

```
  PossibleSceneList的初始化除了需要Automator（a）之外，还需要一个List，里面为各种场景的**实例**。并且为了使用方便，建议像上例
  一样把用到的可能场景类全部存入自身（只是为了自动补全而已）。
  
  此处定义了一个扫荡之后可能出现的各种提示框的集合，包括超出上限提示、升级提示、团队战提示和限定商店提示。
  
  关于它的调用例子可以见shuatu_daily_ocr函数。
  
```python
MsgList = SD.OK()  # 扫荡后的一系列MsgBox
while True:
    out = MsgList.check()
    if out is None:  # 无msgbox
        break
    if isinstance(out, MsgList.XianDingShangDianBox):
        # 限定商店
        if xianding:
            shop = out.Go()
            shop.buy_all()
            shop.back()
            break
        else:
            out.Cancel()
    if isinstance(out,MsgList.TuanDuiZhanBox):
        out.OK()
    if isinstance(out,MsgList.LevelUpBox):
        out.OK()
        self.start_shuatu()  # 体力又有了！
    if isinstance(out,MsgList.ChaoChuShangXianBox):
        out.OK()
# 扫荡结束
```
  其中SD.OK()所返回的对象就是AfterSaoDangScene的实例。
  
  起手一个while True，紧接一个check函数，返回None则找不到场景，最后用多个不同的isinstance来判定场景类型并执行不同操作。
  
  check函数是PossibleSceneList的核心函数，其参数与PossibleSceneList的初始化函数有关。初始化函数定义如下：
  
  ```
  def __init__(self, a, scene_list: List[PCRSceneBase], no_scene_feature=None, double_check=2., timeout=10.,
                 max_retry=3)
  ```
  其中a为绑定的Automator，scene_list为需要判断的场景的实例列表。
  
  no_scene_feature为一个特殊的特征，用来判断是否上述场景均未出现，如果不加特别设置，则当列表中所有Scene的feature均不满足时就
  判定为“场景均未出现”，否则则靠no_scene_feature定义的feature函数进行判断。timeout和max_retry也是为此设置的，
  也就是说通常情况下不用设置no_scene_feature, timeout和max_retry三个参数。
  
  double_check是一个二重确认，如果不使用可以设置为0即可。它的意思是：如果没有找到符合scene_list中各场景的feature,先不退出，等待double_check秒
  后，再次进行判断，如果还找不到各feature，则退出。有时两个MsgBox跳出时间间存在延迟，用二重确认可以避免漏掉重要的提示框。
  但是由于这是一个基于sleep的防暴毙方法，只要电脑足够卡都能卡掉double_check，此时只能使用ExceptionSet的方法来解决问题了，会比较繁琐。
  
## 场景使用规范

  1. 场景的目录存放在scenes/中
  2. 尽量考虑多场景的方法重用：多写一个Base类是目光长远的表现。
  3. 不强求纯坐标填写于constant.py中，但是对出现的图片，至少需要在constant.py中出现一次，以便进行资源检查。
  4. goto的返回值需要加上类型标识以便于自动补全。 

