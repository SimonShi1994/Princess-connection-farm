# 公会40to1脚本使用说明

请务必看完，readme中有的，开发者不予解答

开发者：Moment，邮箱：momincong@foxmail.com

## 用前提醒：

1. 本脚本依赖于主程序，config.ini中的设置对本脚本一样有效（bug也是）
2. 使用40to1前请务必学会使用主程序
3. 下面的介绍中，会将guild_40to1_resource目录称为资源目录

## 脚本思路：

本脚本使用主程序中提供的接口，将两个公会的账号前后分别导入，分别运行，期间增加会长，大号之间的任务，执行顺序：

先引用设置中的task_name_refer，作为小号们的日常任务，以task_name_daily中的值保存为新任务

然后将资源目录下的remove_guild_task.txt（踢出公会任务）复制到tasks文件夹中，

将资源目录下的goto_guild1_task.txt，goto_guild2_task.txt中的公会名替换成设置中的公会名，然后将其复制到tasks文件夹中，

备份users目录为user_baks，然后清空users，再将资源目录下的account_guild1.txt（公会1信息）导入到users中，

然后开始跑公会1

公会1跑完后将清空users目录，导入会长1的账号，将大号踢出（remove_guild_task任务）

然后清空users目录，登录大号，加入公会2，设置支援（goto_guild2_task任务）

然后清空users目录，再将资源目录下的account_guild2.txt（公会2信息）导入到users中，

然后开始跑公会1

公会1跑完后将清空users目录，导入会长2的账号，将大号踢出

然后清空users目录，登录大号，加入公会1，设置支援（goto_guild1_task任务）

将备份的user信息还原

## 脚本使用步骤（推荐）

1. 40to1的设置在资源目录下的guild_setting.py中，其中大部分默认值即可

2. 现在主程序中创建好小号的日常任务，实验好能跑，没问题后，将任务名填入设置文件的task_name_refer中
3. 填入公会1，公会2的会长账号密码，公会名称（公会名称必须是唯一的，搜索的时候只有一个）
4. 然后在account_guild1.txt和account_guild2.txt中准备好公会1、2的账号密码，task为默认的40to1_daily_task就行（这里可以填写别的任务名，到时候以这两个文件中的任务名为准）
5. 然后就可以开始跑了
6. 由于主程序自带中断重启的功能，所以在这里继承了一小部分特性，在大步骤中是可以手动中断重启的，步骤如下：
   1. 先判断好当前属于什么状态，参照上面的脚本思路
   2. 来到脚本的main部分，将执行完的步骤注释
   3. 重新运行脚本
   4. 结束后记得把注释修改回来