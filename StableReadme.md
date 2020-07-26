# PCR中断运行框架
-- 警告：该框架目前还在测试阶段，暂不能投入使用 --

基于MoveRecord：https://github.com/TheAutumnOfRice/MoveRecord

对原Automator的成员函数进行简单封装为一个“行动`move`”。

多个`move`串成一个行动集合`moveset`。例如，一个可能的行动集合为：购买玛娜->购买体力->刷经验->一键领取。PCR中断运行框架所做的事情是在执行每一个`move`前，向记录文件`.rec`中记录执行步骤。如果在某一个`move`中断了，再次运行`moveset`时会读取上一次执行的步骤，然后跳过已经完成的部分，直接执行后续部分。

例如，在执行购买体力的过程中程序中断或重启，则下一次脚本运行时将跳过购买玛娜部分直接从购买体力开始执行。

此外，还可以在每一个`move`中增加回复逻辑。如购买5次玛娜，但是在购买第3次时程序崩溃，再次进入时，只会购买剩下的3次玛娜；或在刷图逻辑中，如果执行刷11图脚本，但是在刷到11-8时崩溃，下一次进入脚本将从11-8开始继续刷。

但是，详细回复逻辑需要手动构建，当前暂时没有完成全部的恢复逻辑。

## 包含文件
- [x] Moverecord.py --- 中断恢复框架
- [x] PCRMoves.py --- 依赖Automator.py，将其中的成员函数封装为`move`以支持中断回复，可以增加回调逻辑。
- [x] AutomatorS.py --- 依赖Automator.py，保持了原API不变，但其中所有脚本支持中断回复。

## 目前实现的回复逻辑
- [x] Automator.tichuhanghui
- [x] Automator.yaoqinghanghui
- [x] Automator.jieshouhanghui
- [x] Automator.joinhanghui
- [x] Automator.goumaitili
- [x] Automator.goumaimana
- [x] Automator.shuatu8
- [x] Automator.shautu10
- [x] Automator.shuatu11

其余的`move`目前暂不支持回复逻辑。

## 样例脚本
[mainS.py]
main.py的稳定版本（支持中断回复）

在稳定脚本中加载AutomatorS库：
```python
from core.AutomatorS import AutomatorS
```
在Automator类构造后，以此为参数传入AutomatorS类
```python
sa=AutomatorS(a)
```
定义行动内容，其API与Automator一致：
```python
sa.gonghuizhijia()  # 家园一键领取
sa.goumaimana(3,0)  # 购买mana 10次
sa.mianfeiniudan()  # 免费扭蛋
sa.shouqu()  # 收取所有礼物
sa.goumaitili(3)  # 购买3次体力
sa.shouqurenwu()  # 收取任务
sa.shuajingyan(map=3)
sa.shouqurenwu()  # 二次收取任务
```
执行行动内容使用`sa.run`方法。在确保进入主界面后，调用该方法即可。

## 框架使用例

### 一般方法（无回复逻辑）
参考`PCRMoves.py`中对gonghuizhijia函数的封装：
```python
def ms_gonghuizhijia(self):
    ms=moveset("gonghuizhijia")
    OneFun(ms,self.a.gonghuizhijia)
    return ms
```
首先，建立一个名称为`gonghuizhijia`的脚本集合`moveset`

接着使用OneFun方法给该`moveset`定义行动。该`moveset`仅包含一条行动`self.a.gonghuizhijia`。

注：`self.a`为原Automator。

最后，将定义好的`moveset`返回即可。

此后，在`AutomatorS.py`中增加这一条API

AutomatorS类具有如下成员：
1. self.a --- 原来的Automator
2. self.ms --- 整体moveset，在里面增加由PCRMoves定义的各种行动组成某一次脚本逻辑
3. self.p --- 对应的PCRMoves类

封装gonghuizhijia函数如下：
```python
def gonghuizhijia(self):
    return self.ms.nextset(self.p.ms_gonghuizhijia())
```

self.ms.nextset函数在整题行动集合ms中增加了一个新的行动集合self.p.ms_gonghuizhijia()，这就是之前在PCRMoves.py定义的行动集合。

该函数的返回值为该步骤的行动ID，仅作开发调试使用。一般而言，使用nextset创建的函数，其行动ID递增。（1,2,3,...)

定义完成后，使用AutomatorS.run方法执行脚本即可。

###　高级方法（有回复逻辑） 【新版】
`适合必须从头开始执行的脚本`

2020-7-16更新了MoveRecord框架，现在可以使用movevar直接对工作区进行保存操作，具体见Example13.

之前使用了T_forcestart模板的恢复逻辑都太过繁琐，之后会慢慢修改。

暂时没有在PCR中使用该方法，之后的更新中增加例子后继续更新readme。

### 高级方法（有回复逻辑）【旧版】
`适合不要求从头开始执行的脚本`

参考`PCRMoves.py`中对`goumaimana`函数的封装

该方法实现了对原goumainana的重构，将原先的整个函数拆分为四个部分：

1. self.ms_menu_home() --- 已经封装过的锁定主页的脚本
2. Part1 --- 点击加号，进入购买页面
3. Part2A --- 购买一次一连
4. Part2B --- 购买一次十连
5. PartOK --- 购买完成后，点击OK

该脚本传入的参数有times和mode，若mode==1（默认），则购买times次10连；若mode==0，则购买times次一连。

由于需要记录已经买了记词mana，所以要引入一个计数变量：

```python
ms.addvar("now",0)
```
该命令初始化了一个now变量，初值设置为0

此后，在脚本中可以使用T_ifflag和T_end命令来增加一段条件逻辑，然后利用ms.nextwv函数对变量区`var`中的计数器`now`自加。如：

```python
ms.T_ifflag("now",0)
ms.nextw(Part2A,self.a)  # 购买一次一连
ms.nextwv("var['now']+=1")
ms.nextw(PartOK,self.a)
A=ms.T_end()
```

该段的逻辑为：如果now计数器为0（暂未买过体力），则执行购买一连，此后计数器now自增，再点击OK按钮。

注意到点击OK按钮被包含在了ifflag和endflag之间。这意味着如果在点击OK之前，买体力之后崩溃，下一次重新进入脚本，则无需再从点击OK继续，可以直接跳过这一段脚本。

整体的回复逻辑为：
```
锁定主页->
    若没有购买第一次一连：
        购买一连； ->
    若购买一连或十连次数没有到达times次：
        购买一连或购买十连 ->
->锁定主页
```

注意到，该脚本实现的前提是初始情况在主页上，因此，即使之前脚本运行到中间某一步时崩溃了，也需要在下次脚本执行之前强制回到第一步“锁定主页”。

使用T_forcestart方法强制回到主页：

```python
ENT=ms.startset(self.ms_menu_home())
ms.T_forcestart(ENT)  # 强制回到主页
```
第一句ms.startset增加了一步回到主页的操作，返回值为该步骤的ID，传给ENT
接下来，使用ms.T_forcestart(ENT)，表示执行moveset时，强制从ENT步骤开始执行。

更多关于MoveRecord的内容可以见https://github.com/TheAutumnOfRice/MoveRecord,内涵12个example，介绍了更多关于MoveRecord的用法，包括：

1. 使用addmove方法手动创建moveset
2. 使用wrap函数对普通函数进行快速封装
3. 利用字符串快速创建函数
4. moveset的嵌套
5. 上下级moveset之间的通讯
6. moveset的链式构造
7. 异常处理
8. 自定义返回值和跳转映射
9. __onstart__跳转方法
10. 复杂断点恢复例
11. ifflag,elseflag,endflag逻辑段使用
12. 强制重新运行与子moveset的关系
13. movevar对于工作区的简单操作

其中，与高级逻辑关系比较紧密的例子为Example6 Example10 Example11，Example 13，可供参考。