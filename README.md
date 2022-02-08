 <img src="webclient/src/assets/logo.jpg" width = "80" height = "80" alt="LOGO" align=center />

# Princess connection 公主连结农场脚本v2.8.20220208

![](https://img.shields.io/badge/license-GPL--3.0-blue)![](https://img.shields.io/badge/opencv-2.0-blue)![](https://img.shields.io/badge/UIAutomator-2-blue)

## :bookmark_tabs:简介

此项目为国服公主连结脚本，使用opencv图像识别进行按钮分析。本项目基于公主连接opencv高级脚本(https://github.com/bbpp222006/Princess-connection) 开发。

**支持模拟器多开**

**使用多进程优化+异步Python性能**

**支持异常报错卡住自动重启**

**支持自动填写验证码**

**支持24小时挂机**

**支持40to1mana农场**

**支持每日自动三捐**

**支持开关一键修改配置**

**支持自定义任务（如果你会python）**

**支持数据中心（库存、角色、刷图规划）**

## :books:详细功能

1. 行会

- [x] 组建行会
- [x] 支援助战
- [x] 行会捐赠
- [x] 行会点赞
- [x] 公会战自动出甜心刀

2. 地下城

- [x] 地下城借人
- [x] 通关地下城

3. 竞技场

- [x] 战斗竞技场
- [x] 公主竞技场

4. 日常任务

- [x] 家园领取/升级
- [x] 免费扭蛋
- [x] 免费十连
- [x] 收取礼物
- [x] 收取任务
- [x] 购买体力
- [x] 购买mana
- [x] 购买经验
- [x] 探索
- [x] 调查
- [x] 收取女神祭

5. 工具

- [x] 账号重命名
- [x] box截图
- [x] OCR获取账号信息
- [ ] 卖出过量装备
- [x] 暂停手操
- [x] 库存识别 （仅限装备）
- [x] 角色识别

6. 刷图

- [x] 刷经验
- [x] 副本扫荡
- [x] 初始化
- [x] 自动推图
- [x] 自动升级  
- [x] 借人推图

## :globe_with_meridians:环境

- 需要 3.9>Python **64位**版本>3.6（安装时记得把带有**PATH**字母选项的勾上）**不要3.9！！！**

- **Q**我可以不要OCR吗？**A**不行，以后只会对非OCR越来越不友好=。=

- 【不推荐】本地OCR 1/2 需求 [[本地OCR1]VS C++ Build Tool](https://download.microsoft.com/download/5/f/7/5f7acaeb-8363-451f-9425-68a90f98b238/visualcppbuildtools_full.exe) 或 [[本地OCR2]VC_redist.x64.exe](https://download.visualstudio.microsoft.com/download/pr/89a3b9df-4a09-492e-8474-8f92c115c51d/B1A32C71A6B7D5978904FB223763263EA5A7EB23B2C44A0D60E90D234AD99178/VC_redist.x64.exe)

- 自行打开`requirements.txt`确认依赖无误

- 先cd进项目目录下

- 需要执行指令安装依赖（可能需要到`换源/科学上网`）:

  ```
  pip install -r requirements.txt
  ```

- 如果上面的指令执行后感觉比较慢的话，可以试一下:

  ```
  pip install -r requirements.txt -i https://pypi.douban.com/simple
  ```

~~可能需要将模拟器设置为桥接模式，同时需要打开开发者usb调试，也可能用不上。（建议先试一下不设置的情况

建议使用雷电模拟器4但不意味着其他模拟器无法使用，本项目中均以雷电模拟器4为示例。

**重要：模拟器分辨率要求540*960**

**重要**：目前关于API部分已经移入 config.ini 中，如何填入请参考目录下的md文件，config.ini在运行main_new.py后自动生成

## :loudspeaker:推送

|     支持推送的API     | 是否可以交互 | 是否支持图片发送   | 支持‘不受限制’的文字发送 | 使用第三方服务API  | 衍生支持                                              |
| :-------------------: | ------------ | ------------------ | ------------------------ | ------------------ | ----------------------------------------------------- |
| QQpush QQ:cold_sweat: | :x:          | :x:                | :heavy_check_mark:       | :heavy_check_mark: | :x:                                                   |
| Wechat 微信（:hand:） | :x:          | :x:                | :heavy_check_mark:       | :heavy_check_mark: | :x:                                                   |
|    Wework 企业微信    | :x:          | :x:                | :heavy_check_mark:       | :heavy_check_mark: | APP Bark_IOS Wework群机器人 钉钉群机器人 飞书群机器人 |
|      Wework 本地      | :x:          | :x:                | :heavy_check_mark:       | :x:                | :x:                                                   |
|    TG 电报（:+1:）    | :x:          | :heavy_check_mark: | :heavy_check_mark:       | :heavy_check_mark: | :x:                                                   |
|     QQBot[开发中]     |              |                    |                          |                    |                                                       |

Tips:QQPush机器人经常换号 Wechat在4月底将全部弃用，转Wework

## :taxi:使用方式

- 环境配置完成后，再检查模拟器分辨率为540*960。确认无误

- 使用OCR相关的服务，必须启动app。使用2021-01-23后的版本程序默认自动启动app。

- 关于本地OCR1删库问题，可以使用清华源安装

  也可以到docs文件夹下打开cmd

  ```shell
  pip install muggle_ocr-1.0.3-py3-none-any.whl
  ```

- 输入`python main_new.py`，启动脚本。该项目支持控制台，可以输入help查看帮助。

- 出现`“No module named 'XXX'`，请在项目目录执行`pip install -r requirements.txt`重新安装依赖

- 可以参照**run.bat**写一个一键启动脚本，更多参见Schedule使用方法 - 2.5命令运行

- 如果模拟器没有安装 ATX ，请在打开模拟器后，在控控制台里输入init进行初始化模拟器环境

- **第一次使用，完全不懂怎么办，请阅读下列新手方法** 

  [Schedule使用方法](docs/introduce_to_schedule.md)

  [如何接入打码平台](docs/如何接入打码平台.md)

  [如何使用开关模块](docs/switch_guide.md)

- 感觉还是不会使用，怎么办？

更详细的使用方法会陆续更新，我们也会尽快简化使用方式及上线WebGUI控制版本，敬请期待！也欢迎大家入群交流讨论。↓↓


## :warning:额外说明

1. 请不要用于商业用途。代码交流和bug反馈请加群加qq群 1130884619

   ![image](https://s1.ax1x.com/2020/06/26/NsXjh9.png)

2. 感谢[CyiceK](https://github.com/1076472672) 、[Dr-Bluemond](https://github.com/Dr-Bluemond) 、[TheAutumnOfRice](https://github.com/TheAutumnOfRice) 、[UVJkiNTQ](https://github.com/UVJkiNTQ)以及其他众多贡献者对本项目的倾力帮助。

3. **来个 star 吧(*/ω＼*)，有问题请提交issue**

4. 您的一点支持会是我们完善本项目的强大动力！(*/ω＼*)

   **STAR近来统计图**

   [![Stargazers over time](https://starchart.cc/SimonShi1994/Princess-connection-farm.svg)](https://starchart.cc/SimonShi1994/Princess-connection-farm)

## :date:更新计划

- [x] 滑动验证码问题
- [x] 模拟器自启动控制
- [x] 简化Schedule操作模式
- [ ] WebGUI界面
- [x] 提高刷图效率
- [ ] 刷活动本
- [x] 女神祭
- [ ] 跳过18图切图动画

## :mute:免责声明

当你**下载或使用**本项目，将默许

本项目仅供交流和学习使用，请勿用此从事 违法/商业盈利等，开发者团队拥有本项目的最终解释权

## :hammer:更新历史:wrench:

<details>
<summary>更新日志（点击展开）</summary>

2022/02/08 By TheAutumnOfRice

- 新增大号自动刷图规划`s9-auto`功能
- 修复探索中一次不扫荡满的问题
- 修复图号识别中second_id识别出错的BUG

2022/02/07 By CyiceK

- 优化验证码图片截图识别
- easyocr支持allowlist参数
- 依赖安装优化
- 内置最新的完整的谷歌安装开发sdk（adb）
- 本地ocr核心逐步移动到easyocr（本地4）+pcrocr上，比老muggle_ocr（本地1），内存占用比大约为20M/130M

2022/02/07 By TheAutumnOfRice

- 模块追加
  - 新增pcrocr，专门为bcr量身定制，设置中允许Rank和图号使用OCR获得而不是图像匹配。
    ！需要cnocr库！
  
- 功能更新
  - 重写角色识别，修复了六星无法识别的问题。
  - 修复了自动推图所用的自动升级，增加了收藏顺序,允许装备升星。通用刷图允许失败升级功能。
  - 新增通用OCR推图`s9-t`，对s9进行了封装
  - 允许VH刷图/推图；允许设置碎片达到目标数则跳过图
  - 初始化、主线推图等功能因为自动升级的原因现在恢复可用状态
  
- BUG修复
  - 修复了限定商店卡ok_btn的BUG
  - 修复买体力后不更新可刷图flag的BUG
  - 修复刷图规划无图可刷时的BUG
  - 修复基本信息获取，适配pcrocr
  
- 配置更新
  - debuglog增加一些过滤器config
  - 优化screencut调试体验
  
- 框架升级
  - _base新增lock_change，用于检测区域变化。
  - 新增prechecks，可以在getscreen后即时操作。
  - PCRRetry新增BreakNow异常，用于直接跳转到函数尾


2022/02/04 By UVJkiNTQ

- 增加角色头像资源
- 修复加入行会的log错误

2022/02/03 By CyiceK

- 增加自动清理大于6天的过期日志功能
- 增添自动关闭pcr功能，由max_free_time控制
- 日志已经大部分规范化
- 验证码答案获取速度稍微提点速
- 修复百度OCR queue命名错误
- 修复某些bug

2022/02/01 By CyiceK

- ocr_center接入cv预处理，部分函数功能整理合一
- 修改了部分ocr识别范围
- cv预处理增加锐化和高斯滤波
- ocr_int增强，现在对数字识别更加准确（带有数字+符号识别的请调整size为10.0或者5.0，并开启锐化/高斯滤波测试看看？
- 修复百度OCR导入时，queue未能正确添加的bug

2022/01/31 By TheAutumnOfRice

- 新增32图
- 修复Rank16图片显示模糊问题
- 新增img_helper.py，向导式图号坐标编辑，可由img命令进入
- 增加cv预处理接口，但似乎没什么用。

2022/01/30 By CyiceK

- 依赖减肥，muggle_ocr非本地OCR的唯一解决方案，有更加轻便的OCR
- 本地OCR非强制性安装，现在需在requirements.txt里取消#注释后再pip install
- 老ocr_mode配置废弃，采用主次ocr_mode，切换更灵活、容错率更高
- 增添主次OCR双向对比，结果相同才输出，不同用另一个用户指定的OCR
- 增添ocr.space（网络2）、ddddocr（本地3）、easyocr（本地4）三种ocr方法
- 修复openCV部分依赖版本过高问题
- 修复_login.py在处理验证码时，识图失败导致一直卡住的bug
- 修复d1在ocr处理上/识别成1导致无法识别次数的问题
- 修复enter_dxc中wait_for_stable未添加阀值导致进错地下城的bug
- 修复购买体力宝石不足时在宝石购买界面卡住

2022/01/19 By UVJkiNTQ

- 改进了Box识别流程，直接识别Box九宫格

2022/01/15 By UVJkiNTQ

- 31图更新及Rank16
- 新增角色插片部分场景，可以对Box界面识别和操作
- 改进了角色强化流程，现在可以从Box进入

2022/01/10 By TheAutumnOfRice

- initFC相关内核优化，支持给场景加sidecheck了
- 修复JJC/PJJC卡编组设定的BUG
- 修复调查卡剧情问题

2022/01/08 By UVJkiNTQ

- 添加了角色Box界面的图片资源
- 改进加入行会的识别
- 修改部分角色强化的异常处理
- 修复task s8的默认值错误

2022/01/03 By UVJkiNTQ

- 修复加入行会 h8，并对已在行会的情况作出处理（跳过）
- 为任务 t3 增加了角色识别的选项
- 添加一些任务说明

2022/01/01 By CyiceK

- 修复更新程序未结束导致无法覆盖adb.exe问题
- 支持模拟器内装有bilibili客户端，不影响登陆
- 修复免费10连抽取的图片bug

2022/01/01 By UVJkiNTQ

- 加入碎片购买，任务编号 t9
- 修复女神祭领取 r11
- 重写角色自动升级 s8，加入角色界面插片

2021/12/28 By TheAutumnOfRice

- 修复重启造成的全局设定混乱情况
- 试图修复圣迹调查的剧情跳过

2021/12/26 By TheAutumnOfRice

- 试图修复圣迹调查的卡剧情问题

2021/12/21 By UVJkiNTQ

- 更新30图
- 角色碎片图片更新
- 修复免费十连，增加多次抽取
- 角色自动升级小修复
- 部分UI变动

2021/12/2 By TheAutumnOfRice

- 调试工具优化
- 修复角色装备识别阈值错误问题
- 修复领取体力但不开启刷图的BUG

2021/11/27 By UVJkiNTQ

- 增加角色升级插片及场景
- 更新剧情插片
- 新增主线剧情任务t8

2021/11/16 By UVJkiNTQ

- 修复主线难度选择
- 更新29图
- 新增过主线剧情插片

2021/11/9 By CyiceK

- 提高点选坐标验证码上传截图的准度

2021/11/1 By TheAutumnOfRice

- 修复Rank15图片被误识别为Rank13的问题
- 给主界面增加了一点颜色

2021/10/30 By UVJkiNTQ

- 修复刷图跳过扫荡，修复N2图标引起的图号识别错误

2021/10/23 By UVJkiNTQ

- 更新28图，Rank15

2021/10/17 By CyiceK

- 修复d1地下城UI变动bug

2021/10/17 By TheAutumnOfRice

- 修复地下城无法进入的问题

2021/10/17 By UVJkiNTQ

- 修复体力及mana购买，修复普通商店购买

2021/10/16 By TheAutumnOfRice

- 进一步修复UI
- Config相关设置
  - 增加Config人性化提示
  - 增加force_timeout_reboot，默认开启，防止死循环
  - 默认Config参数改动：
    - 快速截图： 开启 —> 关闭
    - 清除缓存： 开启 -> 关闭
  
- 修复调查本`r12`，允许神殿调查`r10`
- ver.4 修复一些图片问题，增加图片at检查


2021/10/14 By UVJkiNTQ

- 修复UI改动导致的部分失效

2021/10/7 By CyiceK

- 自动搜寻模拟器支持re匹配，修复找不到Nox（夜神）模拟器的问题
- 修复验证码无法刷新

2021/10/2 By UVJkiNTQ

- 新增26、27图

2021/9/30 By CyiceK

- 修复登陆u2控件验证码-662的红字retry，更新刷新验证码的位置

2021/9/26 By UVJkiNTQ

- 尝试修复行会捐赠、支援移位

2021/9/25 By CyiceK

- 增添重试后的验证码时延设置

2021/9/21 By UVJkiNTQ
- 修复行会点赞

2021/9/14 By UVJkiNTQ

- 修复战斗失败后未正常退出问题
- 修复设置选项失效问题

2021/9/11 By TheAutumnOfRice

- 修复推图中点二倍速突然报错问题

2021/9/10 By TheAutumnOfRice

- 新增主线借人。
  - 新增快速借人(s10)，借人推图(s11-n,s11-h)，
  - OCR推图支持借人参数 (s9,s7-a-ocr,s7-ocr)
- 新增好友模块 (HaoYouMixin)
  - 新增好友申请(f1)，好友通过(f2)
  
- 修复六星开花下无法角色识别(t7)的问题
- 修复OCR通关地下城(d5)满人编组后无法借人的问题
  

2021/9/7 By TheAutumnOfRice

- 修复登录和登出问题
- 尝试新增蓝叠的自启动
- 修复OCR刷图的问题
- 密码错误和账号异常现在不会多次重启
- Ver. 0907.2 修复主线一直点Normal

2021/8/26 By CyiceK

- 修复bugs:1.免费十连位置偏移 2.刷图函数报错 3.更新系统判断问题
- 修复登陆密码错误toast判断
- 修复免费扭蛋、加入行会h8

2021/8/22 By TheAutumnOfRice

- OCR探索： 修复探索记录不更新的BUG
- OCR刷图：修复无法重试多次刷图的BUG
- 修复踢出行会BUG
- 修复ocrfix对角色识别无效的BUG

2021/8/12 By TheAutumnOfRice

- OCR刷图：
  - 试图修复因为不显示图号导致的“进入失败”问题
- OCR探索
  - 修复可可萝出场被误识别为教程的问题
  - 试图修复最后一次手动探索后右下角“进入探索首页”无法识别的问题
- 控制台新增adb命令
- config支持utf-8-bom解码

2021/8/2 By TheAutumnOfRice

- 修复d1无限卡主页
- “无法进入N3-1”增加相关debug
- 新增Rank14，2425图
- PCRInitializer中增加get_all_commands

2021/7/28 By CyiceK

- 临时修复OCR地下城1卡塔币教程，修复剧情/设置/协议在特定情况下一直初始化的问题
- PCR清理缓存函数，使用时请打开模拟器ROOT权限

2021/7/27 By CyiceK

- 适配新版登陆UI
- 升级PCR清理缓存函数，输出干净无扰

2021/7/19 By CyiceK

- 修复行会点赞点不到第二个人的问题

2021/6/14 By TheAutumnOfRice

- 修复参数map不正确问题

2021/6/11 By TheAutumnOfRice

- BUG修复
  - 通关地下城OCR：
    - 修复跳过KKR卡在主界面
    - 修复打Boss死亡后重开卡住
    - 修复打Boss死亡后直接结束
  - JJC,PJJC：修复胜利卡住
  - 升级/角色识别：卡在九宫格界面
- 坐标：增加主线22，主线23坐标
- 优化：
  - 主线关卡识别
  - 战斗设置auto/速率
- 其它
  - 移除install_requirements.py
  - 删除部分冗余任务

2021/5/30 By CyiceK

- 修复失效的实名验证
- 本地OCR依赖修复

2021/5/23 By thsheep

- 修复了战斗结束点击下一步错位的问题
- 修复了战斗失败卡死在Failed的界面上

2021/5/21 By UVJkiNTQ

- 修复自动重命名

2021/5/9 By CyiceK

- 修复自动搜寻模拟器-蓝叠的问题
- 修复无法关闭活动剧情提示

2021/4/22 By TheAutumnOfRice

- 修复一些BUG
- 修复JJC，PJJC

2021/4/21 By TheAutumnOfRice

- 修复图号识别，Normal Hard图特征
- 修复跳过按钮图片
- 新增通关地下城OCR，增加攒TP模式(mode 4)，借人参数(assist)

2021/4/16 By TheAutumnOfRice

- 试图提高选图稳定性
- 进一步解决无限右上角问题

2021/4/5 By CyiceK

- 上线另一个本地OCR（Tr）`本地2`，需要安装新的依赖

2021/4/5 By TheAutumnOfRice

- 进一步增加OCR识别扫荡次数稳定性
- 增加登录稳定性，进一步防止无限右上角
- 给行会捐赠增加300s TimeOut，防止无限卡战斗

2021/3/31 By TheAutumnOfRice

- 更新到Ver2.6版本
- 新增21图

2021/3/25 By TheAutumnOfRice

- 自动更新程序和Requirements的微调

2021/3/24 By UVJkiNTQ

- 添加了xlsx导出支持，可兼容pandas>=1.2.0
- 移除了xls导出

2021/3/16 By TheAutumnOfRice

- 试图修复地下城5图问题
- 增加地下城5图

2021/3/9 By:TheAutumnOfRice

- 新增`force_as_ocr_as_possible`一键修改所有任务为OCR任务
- 新增OCR探索`r9-ocr`
- 修复诸多BUG

2021/3/8 By:TheAutumnOfRice

- 使用Scenes框架解构方法
- 内核使用FunctionChecker框架改写，增加稳定性
- 增加了OCR刷图推图 `s9`
- OCR增加效率 `s7-ocr` `s7-a-ocr`

2021/3/5 By:Klarkxy

- "r8购买经验" 新增参数"qianghuashi"，用来进行额外购买强化石。

2021/3/4 By:TheAutumnOfRice

- 修复升级/角色识别中的切换错误

2021/3/3 By:TheAutumnOfRice

- 增加更多调试句柄
- 修复进入Hard图的问题

2021/3/2 By:Klarkxy

- 编辑界面增加友好提示，方便编辑时使用。

2021/3/2 By:CyiceK

- 新增TGbot推送，去本地化设计，本地无需科学上网即可食用（因此也失去了脚本交互功能）

2021/3/2 By:TheAutumnOfRice

- 新增舒爽的流程控制
  - 新增暂停继续指令 `pause`/`resume`
  - 新增任务查看与跳转 `task`/`skip`
  - 
- 新增强大的调试工具
  - 单独开关指定debug `debug`
  - 记录Automator和u2的操作信息 `rec`/`u2rec`
  - 支持命令调试 `exec`
- 增加Bot的代理设置 （proxy_http,proxy_https)

2021/3/1 By:TheAutumnOfRice

- 新增20图
- 修复data > js trackinfo中部分角色不显示的BUG

2021/2/24 By:TheAutumnOfRice

- 新增女神祭`r11`

2021/2/10 By:TheAutumnOfRice

- 修复自定义任务无法导入的BUG

2021/2/9 By:TheAutumnOfRice

- 修复19图图号错乱

2021/2/5 By:CyiceK

- 上线公会战自动摸`h10`

2021/2/5 By:TheAutumnOfRice

- 数据中心新增角色养成状态总览 `js trackinfo`
- 修复一个计算Rank所需装备的BUG

2021/2/4 By:CyiceK

- 修复QQBot推送的些许bug，彻底解决了因推送内容字数过多导致发不出去的问题

2021/2/3 By:TheAutumnOfRice

- 修复角色识别覆盖追踪信息的BUG
- 修复角色识别中OCR爆炸的BUG
- 增加刷图规划的体验
- 优化requirements文件
- 修复19图刷图识别问题

2021/2/2 By:TheAutumnOfRice

- 上线数据中心（DataCenter)，可于主界面data启动
  - 增加干炸里脊数据库支持
  - 增加刷图规划
  - 支持兰德索尔图书馆数据交互
- 增加角色识别，修复一些识别BUG
- 修复QQBot不启用时报错的BUG
- 增加19图

2021/1/31 By:CyiceK

- 优化推送机器人的代码结构
- 上线QQbot，已知问题是QQbot推送有字数限制，有几率触发无法推送
- 快速截图默认关闭，若有脚本问题 卡住等，需要速率的再自行开启

2021/1/27 By:TheAutumnOfRice

- 修复一些BUG
- OCR信息获取体验更佳
- 增加库存识别 `t6`

2021/1/26 By:TheAutumnOfRice

- 修复了list_all_groups的一些BUG
- 增加了便捷的组管理命令
- 给ocr信息获取增加了“所在组”
- 增加了开关的使用说明
- 增加自定义模块 `customtask`

2021/1/24 By:TheAutumnOfRice

- 修复inline_app, pcr_config.py的一些BUG
- 将config.ini加入.gitignore

2021/1/23 By:TheAutumnOfRice

- pcr_config结构变动：现在允许动态增删改查以及自动补全缺失了
- 增加app的内部模式`inline_app`，优化app启动体验，防止app过量启动
- batch支持随机优先级了（见edit-batch-random）
- 修复了开关相关的BUG

2021/1/20 By:TheAutumnOfRice

- 开关（Switch)模块上线！
- 为task和schedule增加了enable/disable/flag命令
- task现在支持编辑、移动、显示详细信息了。

2021/1/19 By:CyiceK

- 注意，使用自动填写验证码的请务必在2.1前更新到此版本！！！
- 将后缀txt转为json，为前端铺路（直接在控制台init就可以一键懒人转化啦0.0）
- 修复无法跳过抽签的问题

2021/1/4 By:TheAutumnOfRice

- 修复rename的BUG （修完发现已经被CyiceK修复了）
- 新增18图（但尚不能跳过切图动画）
- 修复不能购买超级经验药水的BUG
- 增加app.py启动和自启动（默认不开启`auto_start_app`）

2020/12/29 By:CyiceK

- 支持单账号自定义捐赠次数
- 支持自动清空PCR产生的缓存垃圾，尝试用雷电的downcpu降低模拟器本身cpu占用

2020/12/26 By:CyiceK

- 修复自启动模拟器，因掉队产生的“自杀”行为，修复一些bug

2020/12/21 By:CyiceK

- 对验证码进行了处理（

2020/12/21 By:TheAutumnOfRice

- 出现未知类型验证码时转手动

2020/12/17 By:CyiceK

- 尝试修复模拟器自启动bug

2020/12/4 By:CyiceK

- 重命名支持批量随机指定字符集+随机数字的组合改名了，方便快速定位账号

2020/12/2 By:TheAutumnOfRice

- 增加17图
- 增加自动点击“下载”（更新数据）的功能
- 如果没有来得及更新图导致检测失败，则向左点三次图
- Config中fastscreen_timeout的默认值从10改为3

2020/11/11 By:TheAutumnOfRice

- 增加16图
- 修复通关地下城中进入地下城容易点进4图的Bug

2020/11/7 By:Monkey

- 新增日常圣迹调查的扫荡
- 新增run.bat，一键启动脚本

2020/11/4 By:CyiceK

- 修复雷电三读取不到控件的bug（感谢群友Stack的发现）
- 修复验证码四坐标的无法识别问题
- 增加验证码速度识别速度模式切换
- 升级自动申诉题目

2020/11/2 By:TheAutumnOfRice

- 修复可推图探索卡在jingyan的BUG
- 打码配置BUG修复
- 增加模拟器过滤 ignore_serials
- 防止“游客登陆”

2020/11/1 By:CyiceK

- 接码功能完善

2020/11/1 By:TheAutumnOfRice

- 在模拟器开着的情况下，仍然支持自动控制了。
- 优化了Login中对于验证码的处理

2020/10/31 By:CyiceK

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

</details>