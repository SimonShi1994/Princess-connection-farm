 <img src="webclient/src/assets/logo.jpg" width = "80" height = "80" alt="LOGO" align=center />

 # Princess connection 公主连结农场脚本v2.1.20201031

![](https://img.shields.io/badge/license-GPL--3.0-blue)![](https://img.shields.io/badge/opencv-2.0-blue)![](https://img.shields.io/badge/UIAutomator-2-blue)

## 简介

此项目为国服公主连结脚本，使用opencv图像识别进行按钮分析。本项目基于公主连接opencv高级脚本(https://github.com/bbpp222006/Princess-connection) 开发。

**支持模拟器多开**

**支持自动填写验证码**

**支持24小时挂机**

**支持40to1mana农场**

**支持每日自动三捐**

## 详细功能

1. 行会

- [x] 组建行会
- [x] 支援助战
- [x] 行会捐赠
- [x] 行会点赞

2. 地下城

- [x] 地下城借人
- [x] 通关地下城

3. 竞技场

- [x] 战斗竞技场
- [x] 公主竞技场

4. 日常任务

- [x] 家园领取
- [x] 免费扭蛋
- [x] 免费十连
- [x] 收取礼物
- [x] 收取任务
- [x] 购买体力
- [x] 购买mana
- [x] 购买经验
- [x] 探索

5. 工具

- [x] 账号重命名
- [x] box截图
- [x] OCR获取账号信息
- [x] 卖出过量装备
- [x] 暂停手操

6. 刷图

- [x] 刷经验
- [x] 副本扫荡
- [x] 初始化
- [x] 自动推图

## 环境

需要 Python **64位**版本>=3.6（安装时记得把带有**PATH**字母选项的勾上）**不要3.9！！！**

需要执行指令安装依赖:

```
pip install -r requirements.txt
```

若使用模拟器，则可能需要将模拟器设置为桥接模式，同时需要打开开发者usb调试。

建议使用雷电模拟器4，本项目中均以雷电模拟器4为示例。

**重要：模拟器分辨率要求540*960**

**重要**：目前关于API部分已经移入 config.ini 中，如何填入请参考目录下的md文件

如何申请百度文字识别apikey和Secret Key:(https://blog.csdn.net/biao197/article/details/102907492 )

Server酱食用方法：(http://sc.ftqq.com/3.version)

## 使用方式

- 环境配置完成后，再检查模拟器分辨率为540*960。确认无误
- 使用OCR相关的服务，请先启动**app.py**(双击/`python app.py`)
- 输入`python main_new.py`，启动脚本。该项目支持控制台，可以输入help查看帮助。
- 出现“No module named 'XXX'，请在项目目录执行`pip install -r requirements.txt`重新安装依赖
- **第一次使用，完全不懂怎么办？** 
[Schedule使用方法](docs/introduce_to_schedule.md)
- 感觉还是不会使用，怎么办？

更详细的使用方法会陆续更新，我们也会尽快简化使用方式及上线WebGUI控制版本，敬请期待！也欢迎大家入群交流讨论。↓↓


## 额外说明

1. 请不要用于商业用途。代码交流和bug反馈请加群加qq群 1130884619

   ![image](https://s1.ax1x.com/2020/06/26/NsXjh9.png)

2. 感谢CyiceK(https://github.com/1076472672) 、Dr-Bluemond(https://github.com/Dr-Bluemond) 、TheAutumnOfRice(https://github.com/TheAutumnOfRice) 对本项目的倾力帮助。

3. **来个 star 吧(*/ω＼*)，有问题请提交issue**

4. 您的一点支持会是我们完善本项目的强大动力！(*/ω＼*)

## 更新计划

- [x] 模拟器自启动控制
- [x] 简化Schedule操作模式
- [ ] WebGUI界面
- [ ] 提高刷图效率
- [ ] 刷活动本

## 免责声明

当你**下载或使用**本项目，将默许

本项目仅供交流和学习使用，请勿用此从事 违法/商业盈利等，开发者团队拥有本项目的最终解释权

## 更新历史

2020/10/31By:CyiceK

- 接入打码平台实现验证码自动填写，教程在docs-如何接入打码平台.md

2020/10/28 By:TheAutumnOfRice

- 出现验证码时弹窗提醒（config - captcha_popup）
- 增加“暂停”任务，便于手动操作账号
- 修复通关地下城一系列误入/卡住的BUG

2020/10/24 By:CyiceK

- 修复异步暂停线程溢出
- 修复timeout与暂停冲突问题
- OCR地下城在无支援任务时，会自动退出不撤退

2020/10/21 By:TheAutumnOfRice

- 增加地下城1图
- 通关地下城增加模式3：只打第一关

2020/10/20 By:TheAutumnOfRice

- 增加卖出装备

2020/10/18 By:TheAutumnOfRice

- 通关地下城提示信息修复
- 8-15参数缺失，进行了补充
- 部分体力相关BUG导致无法刷图的修复

2020/10/10 By:TheAutumnOfRice

- 紧急修复v2.0.20201009验证码配置混乱的Bug
- 增加了等待验证码输入的时间，可以通过`captcha_wait_time`配置控制

2020/10/9 By:TheAutumnOfRice

- 更新15图
- 登录强退时长增加180s->300s
- 修复文件损坏读取Nonetype时的报错
- 修复登陆时快速截图异常导致狂点右上角的报错
- 快速截图连接失败时，如果配置了force_fastscreen_cut以及模拟器自动控制，将自动重启模拟器
- 修复验证码无法跳过的Bug

2020/10/1 By:CyiceK

- 对验证码的问题进行处理，通过Sever酱进行通知并且跳过该账号，写入异常记录

2020/9/29 By:TheAutumnOfRice

- 用户协议检测时间增加 10s -> 20s
- 修复推图大概率卡限定商店的BUG

2020/9/28 By:TheAutumnOfRice

- 新增跳过用户协议

2020/9/24 By:TheAutumnOfRice

- 通过将自带adb添加到环境变量，也许修复了自启动的BUG
- 增加timeout，全面防止彻底卡死
- 进一步提升u2调用稳定性

2020/9/15 By:TheAutumnOfRice

- 更新14图
- 修复部分BUG，解决推图遇到限定商店的问题（大概

2020/9/7By:CyiceK

- 本地OCR与百度OCR并入app.py中
- 对于百度OCR的QPS并发限制已做处理，基本成功率为100%

2020/9/3 By:TheAutumnOfRice

- 控制台使用更新，更加丝滑，扩展实时控制功能
- 上线模拟器控制

2020/9/2 By:TheAutumnOfRice

- Schedule控制模式上线

2020/8/24 By:CyiceK

- 本地OCR上线，注意需要重新pip。会有大约500M的下载量!

2020/8/22 By:CyiceK

- 增加XLS表格支持（`add t3`)，修复部分bug

2020/8/19 By:TheAutumnOfRice

- 推图细节优化，自动推NORMAL图功能上线（`add s6`）
- 自动发起装备捐赠上线（`add h9`）

2020/8/19 By:CyiceK

- 随心所欲的暂停 shift+p
- 改动了 lock方法然后异步剧情跳过弃用

2020/8/18 By:TheAutumnOfRice

- 增加box截图功能

2020/8/17 By:TheAutumnOfRice

- 增加超级刷图功能：刷1-1最快速榨干体力
- 通用刷图/手刷函数，用于主线NORMAL,HARD
- 基于通用刷图/手刷函数的自动推图功能
- 基于通用刷图/手刷函数的自动强化功能
- 新增初始化和快速初始化功能

2020/8/17 By:zsdostar

- 前端编辑子任务的基本交互
- 后端提供 VALID_TASK 的转义成子任务 schema 的接口, 部分接口返回值微调

2020/8/15 By:CyiceK

- OCR版地下城部分代码使用异步自动时间堵塞（根据CPU的负载判断
- 修复异步+扭蛋的一些bug
- 使用异步自动时间堵塞增加了运行效率（应该吧

2020/8/12 By:zsdostar

- 任务前端页面除对任务详情的编辑查看外, 大部分完成
- 账号列表增加编辑和查看任务的功能

2020/8/10 By:Moment

- guild_40to1.py修复并测试完毕，写了readme

2020/8/6 By:CyiceK

- 修复异步线程泄漏和一些bug

2020/8/6 By:zsdostar

- 账号前端页面完成, 前后端联调完毕
- 优化页面样式, 增加阴影等, 提高立体感
- 把 Moment 手绘的 logo 换上去了

2020/8/4 By:CyiceK

- 修改部分地下城OCR逻辑，使得ocr稳定了些
- 脚本增加暂停函数（shift+p）暂停/恢复，后面追加自定义

2020/8/3 By:Moment

- 快速截图函数换成长连接（一堆bug，在之后的几天中群里的大佬们慢慢修复了，至8/9修复完毕，爽到飞起）

2020/8/2 By:CyiceK

- 上线config，添加截图手动纠错方向（百度OCR的

2020/8/1 By:Moment

- 增加适用于新版的40to1（guild_40to1.py)，使用方法见上方readme

2020/7/30 By:CyiceK

- 修改了Server酱的格式和修复了日志多输出 (应该
- cv.py 增加界面相似度的判断，异步添加卡死界面判断（测试

2020/7/30 By:Moment

- 增加N3-1的刷经验函数
- 将N图坐标完全补全
- 完善进入地图的函数（应该不会卡在冒险界面了）

2020/7/28 By:TheAutumnOfRice

- 修复了异步不自启动的Bug
- 添加截图小工具

2020/7/26 By:TheAutumnOfRice

- 脚本任务统一由用户json控制
- 合并了刷图函数，弃用了shuatuXX和DoXXtoXX函数，改用shuatuNN和shuatuHH函数
- 支持简单的断点恢复。当程序运行崩溃，再次打开脚本，会重新开启上一次没有完成的脚本。
- 修改了异步逻辑：如果异步线程Bad_connecting发现错误，则直接重启重进。
- 新增了`非常简陋`的脚本控制器、用户信息编辑器和任务编辑器
- 大改了Automator的逻辑，现在Automator只需要读入address参数，通过init_account在内部读取用户配置文件，从而一气喝成完成所有任务。
  因为改动了Automator的使用方式，目前goumaimana,juanzeng等等脚本都无法使用，需要尽快写成配置文件从而使用。

2020/7/22 By:CyiceK

- 改善异步的占用，应该吧（
- 修改日志功能，增添Server酱（微信推送）
- 删除baidu_ocr.txt，临时组建pcr_config.py
- 修复传入百度OCR的截图玄学问题
- 其他小方面调整，逃）

2020/7/20 By:Ailumar

- 再扩充了main.py中<刷图控制中心>处理范围,可支持hard本刷角色碎片和主线刷装备和探索一起处理,探索新加的,可能不太完善先用用看.
- 新增主线12村的装备扫荡.
- 新增主线困本12村扫荡.

2020/7/19 By:Ailumar

- hard图和主线图要求皆为3星通关或者被注释掉不刷
- 扩充了main.py中<刷图控制中心>处理范围,可支持hard本刷角色碎片和主线刷装备一起处理,注意体力,注意账号填写方式!!
- 新增主线困难1-11村角色碎片扫荡.
- 新增主线7村的装备扫荡.
- 修改了8,10,11的装备扫荡逻辑.
- 优化了主线刷装备容易刷错图的问题并进行了简单的防卡死,防模拟器卡顿处理.

2020/7/19 By:Yuki_Asuuna

- 用logging库重写了日志类（log_handler.py），所有日志重定向到标准输出和文件（日志文件位于log文件夹下），每个账号都对应一个日志文件a.log，调用方法为a.log.write_log(level,message)，两个参数都为str类型，其中level表示该条日志信息的类型（['debug','info','warning','error','critical']之一），message表示内容。

2020/7/17 By:CyiceK

- 优化OCR地下城的判断
- 异步 多进程协调降低性能占用
- OCR地下城与非OCR的自动切换
- 新增 家园新家具提示关闭的判断，全局异步跳过可可萝剧情的异步(包括地下城吃塔币后出发的但未测试)
- 其他方面小调整

2020/7/14 By:Dr_Bluemond

- 另写一版地下城函数，可选择更换为dixiacheng_dev，不使用ocr，不处理获得塔币的可可萝教程
- 优化赛马
- lockimg增加retry参数，elseclick超过retry次则返回False
- 增加lock_no_img函数，在有图片时一直点击elseclick，图片消失时点击ifclick
- 增加区域定位辅助，现在如果搜图没有加上at则会在运行发现时提供at的坐标，直接复制即可使用
- 优化初始化程序，大幅增加其效率

2020/7/12 By:CyiceK

- 封装异步类，启动异步跳过剧情 异步判断处理 connect/nowloading/返回标题 三种异常情况
- 尝试性使用协程来初始化
- 优化 改动ocr函数，log_handler.py ，cv.py，lock函数
- 完全重写地下城，去除冗余代码**需要百度OCR文字识别的API**
- 只要在界面上出现剧情都会进行跳过，出现异常即重启app

2020/7/11 By:Yuki_Asuuna

- 区域OCR函数(x1,y1,x2,y2,size)增加参数size（默认size=1.0，参数可省略）。

  表示先对选定区域(x1,y1)->(x2,y2)进行放大/缩小，再进行识别。

  避免因图片过大or过小而导致识别错误。

  若size=2.0表示将截取区域放大2倍，size=0.5则表示将截取区域缩小一半。

- 增加项目更新的脚本（updater.py），自动下载最新版本的项目代码到本地文件夹，满足快速更新的需求（详情请参考AboutUpdater.md），仅供小白使用，开发组的大佬们请无视。

2020/7/10

* 修复行会多次捐赠bug，增加跳过地下城战斗（参数skip=True）

2020/7/8 By:Dr_Bluemond

- 优化刷图控制

2020/7/7 By:Yuki_Asuuna

- 增加日志功能：帐号的登陆登出信息将会被记录在AccountRecord.txt，方便大家定位哪个号卡了

2020/7/6

* 更新农场号自动加入指定行会功能（zujianhanghui.py）

2020/7/6 By:Dr_Bluemond

- 优化识图代码
- 修复公会之家跳过剧情
- 使用正则表达式读取账号

2020/7/2 By:Yuki_Asuuna

- 增加获取当前体力值的函数
- 矩形区域OCR函数已完成（ocr_baidu）

2020/6/30 By:Dr_Bluemond

* 更新角色强化代码
* 将mana农场号建立脚本完善为从全新B站账号刷到3-1。

2020/6/29 By:CyiceK

- 行会多捐赠
- 截图小更新

2020/6/29

* 更新40对1行会功能
* 修改adb连接函数，现在会自动忽略处于offline的设备

2020/6/28  By:Dr_Bluemond

- 增加免费十连功能，需手动开启
- 增加初始化mana号功能，从已完成新手任务的账号（已打过1-2）变成刷完3-1的账号（多线程未调试）

2020/6/26  By:CyiceK

- 重写刷图逻辑，现在可以自定义刷图了（适合进度不同的农场号）

2020/6/23  By:CyiceK

- 优化代码，去除需要手动配置adb环境的步骤
- 改进地下城和刷图逻辑，效率提升
- 改进行会捐赠，现在绝大部分不会失败了
- 刷图无体力无次数会结束剩下的刷图任务
- 跟进官方更新，添加 跳过扫荡过程
- 地下城逻辑重写，无次数 卡住会跳出，不会死循环了
- 识别卡死会自动跳转
- 大部分次数 可以自定义了
- 整合了购买mana

2020/6/22

* 增加了对雷电模拟器多开的支持
* 免除了在终端中手动输入命令的步骤
* 脚本函数均移到了Automator.py
* 修改协议为GPL 3.0

2020/6/21  By:CyiceK

- 添加自动免费扭蛋功能
- 添加刷经验关(1-1)功能

2020/6/20

* 增加了供大号使用的自动刷完第三个地下城及探索的功能

2020/6/20  By:CyiceK

- 添加家园收取和公会点赞功能
- 更替maoxian文件名为dixiacheng
- 优化一小点代码 XD

2020/6/18

- 修复了issue中地下城撤退时可能截图到撤退按钮的问题
- 修复了地下城双倍期间无法识别地下城图标问题
- 修复了登录时可能因控件未能及时弹出而失败的问题
- 收取礼物函数优化了逻辑，去掉了全部收取按钮的锁定
- 行会捐赠函数优化了逻辑，现在大概不会捐赠失败了
- 地下城函数优化了逻辑增加了鲁棒性，加入跳过剧情/首次进入时已经进了地下城 两种情况的初始号的处理法
