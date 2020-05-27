# Princess connection 公主连结农场脚本v0.2

[TOC]

## 简介

此项目为国服公主连结脚本，使用opencv图像识别进行按钮分析。本项目基于公主连接opencv高级脚本(https://github.com/bbpp222006/Princess-connection)开发。

目前实现的功能有

1. 账号批量登录/退出；
2. 收取所有礼物；
3. 检测行会捐赠请求并捐赠；
4. 地下城自动刷支援，默认第一个人，请确保支援角色不大于农场号等级+30；
5. 购买3次体力；
6. 收取所有任务报酬；
7. 刷全部10图3次（请确保你的农场号已经全部3星通关）；
8. 购买70次mana（主程序中没有包含，为额外脚本）。


## 环境

需要安装下列python包:

```
pip install opencv-python==3.* -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install uiautomator2 -i https://mirrors.aliyun.com/pypi/simple/
```

windows端需要adb工具，在adb文件夹，请自行手动添加到path中

若使用模拟器,则需要将模拟器设置为桥接模式.  具体参考这个项目(https://github.com/Jiahonzheng/JGM-Automator)
mumu模拟器无需设置，建议使用mumu模拟器

**重要：模拟器分辨率要求540*960**


## 使用方式

1. 启动mumu模拟器，设置分辨率为540*960

2. 在任意终端（如cmd）中输入

```
adb connect 127.0.0.1:7555
python -m uiautomator2 init
```

会自动在模拟器上安装一个图标为小黄车的app（ATX）

3. 在模拟器上打开 ATX(小黄车) ，点击 ***启动 UIAutomator*** 选项，确保 UIAutomator 是运行的。

4. 在模拟器中启动公主连结，请确保安装的是b服版本；

5. 然后在终端中输入

```
cd main.py文件所在的目录（自己复制）
例如：cd C:\Users\Administrator\Documents\Princess-connection-farm
```

6. 再输入

```
python main.py
```

程序将按顺序自动完成简介中功能1-7。



## 额外说明

1. **本项目下zhanghao.txt为待刷账号与密码**;
   账号与密码之间用tab键作为分割，不要用空格；

   不同账号之间按行分割；

   第一行的zhanghao mima请也改成自己的账号密码。

2. **本项目下goumaimana.py为购买70次mana**，执行方法参照main.py

3. **本项目下juanzeng.py为行会捐赠装备**；

   建议每天上午跑一次main.py，8小时后请求新的装备后再跑juanzeng.py

4. 请不要用于商业用途。代码交流和bug反馈请联系qq 2785242720

