# INI文件配置解读

|              项              |                             说明                             |  属性  |   备注   |       例        |
| :--------------------------: | :----------------------------------------------------------: | :----: | :------: | :-------------: |
|            debug             |                           输出日志                           |  bool  |          |      False      |
|save_debug_img|输出调试文件|bool|给开发者后，可以帮助减少BUG|True|
|  trace_exception_for_debug   | 开启后，所有的try向上传递错误信息，并且只用第一个device跑第一个任务（单进程） |  bool  |          |      False      |
|      use_template_cache      |                 在开发工具使用时可以将其关闭                 |  bool  |          |      True       |
|        baidu_ocr_img         |      是否输出名为 baidu_ocr.bmp的图片，该图片为原生截图      |  bool  |          |      False      |
|        disable_timeout_raise         |      如果lock_img报错，是否禁用错误      |  bool  |          |      False      |
|u2_record_size|U2指令记录列表大小|int|20      ||
|u2_record_filter|U2指令过滤列表|list|列表中的指令不会被记录|[]      |
|debug_record_size|Automator指令记录列表大小|int|50      ||
|debug_record_filter|Automator指令过滤列表|list|列表中的指令不会被记录|['_lock_img','_move_check']      |
|write_debug_to_log|打印debug信息到log|bool|如果你开发的时候不想搞那么多log到盘里，关闭它|True|
|colorlogsw|是否使用colorlog进行日志输出|bool||True|
|do_not_show_debug_if_in_these_files|以下文件的debug不显示|list||["get_screen.py", "pcr_checker.py", "valid_task.py", "bot.py"]|
|skip_codename_output_if_in_these_files|以下文件的函数名、行号不显示|list||['_base.py','cv.py','scene_base.py','pcr_checker.py']|
|show_codename_in_log|在log中输出函数名|bool||True|
|show_filename_in_log|在log中输出文件名|bool||True|
|show_linenumber_in_log|在log中输出行号|bool||True|
|trace_tree|追踪的分支版本|str||master |
|force_as_ocr_as_possible|开启后，如果某个任务有OCR版本，则自动使用之|bool||True|
|use_pcrocr_to_detect_rank|开启后，使用OCR检测角色Rank而不是图像匹配|bool|推荐，准确度很高|True|
|use_pcrocr_to_detect_zhuxian|开启后，使用OCR检测角色Rank而不是图像匹配|bool|准确度不能保证！但如果新图尚未更新，可以用此苟活|False|
| qqbot_select | qqbot的选择api服务商 | str | CoolPush/Qmsgnike | CoolPush |
| qqbot_private_send_switch | qqbot私聊开关 | int | 0关 1开 | 0 |
| qqbot_group_send_switch | qqbot群聊开关 | int | 0关 1开 | 0 |
| qqbot_key | qqbot的apikey | str | | SCU6390~94d830b |
| qq | 指定接收消息的QQ号或者QQ群号，可以添加多个，以英文逗号分割。如：1244453393,2952937634（指定的QQ号或QQ群号必须在您的QQ号列表中） | str | 这个Qmsgnike才会用到 | 1244453393,2952937634 |
| tg_token | 电报的token | str | 具体看说明文件 | SCU6390~94d830b |
| tg_mute | 电报推送是否静音 | bool |  | Flase |
| proxy_http|推送使用的代理|str|||
| proxy_https|推送使用的代理|str|||
|           s_sckey            |                     s_sckey为Server酱API                     | string |          | SCU6390~94d830b |
| wework_corpid | wework的pid | string | |  |
| wework_corpsecret | wework的secret | string | |  |
|         sentstate          |                 全体BOT播定时报脚本任务状态                 |  int   | 单位分钟 |        5        |
| sent_state_img | 播报任务状态时是否推送运行截图 | bool |  | Flase |
|           log_lev            | log_levBOT的日志等级，微信日志等级 仅有0/1/2/3，越小越详细，注意每天接口调用有上限！ |  int   |          |        1        |
|          log_cache           |                       日志缓冲消息条数                       |  int   |          |        3        |
|         baidu_apiKey         |                  baidu_apiKey为百度ocr api                   | string |          | SCU6390~94d830b |
|       baidu_secretKey        |                 baidu_secretKey为百度ocr api                 | string |          | SCU6390~94d830b |
| baidu_QPS | baidu_QPS为百度并发限制连接数 | int | | 2 |
| ocrspace_ocr_apikey | ocr.space的apikey | string | | SCU6390~94d830b |
|use_pcrocr_to_process_basic_text|是否优先使用pcr定制ocr来识别数字和基础符号|bool|识别字符见pcrocr/label_basic.txt|True|
| force_primary_equals_secondary | 是否当主要OCR和次要OCR识别内容一致时才返回值 | bool | | False |
| force_primary_equals_secondary_use | 比较全部值都无主次一致时使用该OCR | string | | 本地1 |
| ocr_mode_main | 主要OCR | string | | 本地1 |
| ocr_mode_secondary | 次要OCR[可选填] | string | 英文半角逗号分割 | 网络1,本地1 |
| 'anticlockwise_rotation_times |      根据baidu_ocr.bmp需要逆时针旋转90°多少次截图才正向      |  int   |          |        1        |
|    async_screenshot_freq     |                     异步截图一次休眠时间                     |  int   |          |        5        |
|     bad_connecting_time      |                      异步判断异常的时间                      |  int   |          |       30        |
|        fast_screencut        |                       mincap 快速截图，但该截图可能不稳定，默认关闭                        |  bool  |          |      True       |
|     fast_screencut_delay     | 由于截图太快造成脚本崩溃，可以使用这个加上全局的截图delay，模拟卡顿。 | float  |          |       0.5       |
|    fast_screencut_timeout    |                      等待服传输数据超时                      | float  |          |       10        |
|         end_shutdown         |                   非常“危险”的Windows功能:自动关机           |  bool  |          |      True       |
|       lockimg_timeout        |               90秒如果还在lockimg，则跳出重启                |  int   |          |       90        |
|         enable_pause         |              开启后，可以按下Shift+P暂停脚本。                |  bool  |          |     True       |
|max_reboot|最大出错重试次数|int||3|
|force_timeout_reboot|强制超时重启|bool|如果出现线程扰乱，可以关闭该项，但可能造成永久性卡死|True|
|       running_input          |           开启后，可以在运行时向控制台输入指令                   |  bool |          |      True  |
|selected_emulator|使用的模拟器的名称|string||雷电|
|enable_auto_find_emulator|启动自动模拟器搜索，理论支持各种模拟器共同使用|bool|建议关闭|False|
|one_way_search_auto_find_emulator|是否用单向的方式搜寻模拟器|bool|单向不能混搭，但是搜寻速度更快|False|
|emulators_port_interval|自动搜索模拟器端口区间|list||[5565,5566]|
|emulators_port_list|自动搜索模拟器连接的端口list|list||[5565,5566]|
|emulator_ports|（除雷电外的的）模拟器端口|list|雷电可以不写|[]|
|adb_dir|adb目录|str|可以使用脚本自带adb|adb|
|global_adb_restart|全局adb自修复|bool|若adb需要重连，该操作由父进程完成|True|
|restart_adb_during_emulator_launch_delay|自启动时不断重启adb|int|若为0，不重启|10|
|emulator_console|模拟器控制台目录|str|目前仅支持雷电|F:\XuanZhi\LDPlayer\ldconsole.exe|
|emulator_id|模拟器设备编号|list|目前只支持雷电|[0,1]|
|quit_emulator_when_free|空闲时退出模拟器|bool||True|
|max_free_tine|空闲多久触发推出模拟器|int|单位：秒|120|
|captcha_level|接码平台的识别等级|str|特速双倍扣分哦|小速/特速|
|captcha_userstr|接码密码串|str||10001\|QASWC~G3A9|
|captcha_software_key|接码的软件KEY|str||1001\|4A96~F0EA|
|captcha_sleep_times|验证码点击“确认”后的延迟|float|单位：秒|1.5|
|captcha_senderror|                         自动申诉题目                         |bool|成功返回分值，失败扣除双倍|True|
|captcha_senderror_times| 验证失败多少次后触发自动申诉题目 |int||2|
|captcha_skip|出现验证码是否直接跳过该账号|bool||True|
|captcha_wait_time|出现验证码后等待用户输入的时间|int||60|
|clear_traces_and_cache|是否启用PCR干净模式|bool||False|
|use_my_id|是否使用自己提供的身份证|bool|                             |True|
|auto_start_app|执行first/continue后是否自动打开app.py|bool||True|
|inline_app|是否采用内部方式打开app（无窗口，无输出）|bool||True|
|captcha_popup|出现验证码后是否弹出置顶提示框|bool||True|
|wait_for_launch_time|自启动模拟器最大忍耐超时时间|int||600|
|ignore_serials|不连接的模拟器|str||["emulator-5554"]|







------

小脚印

- 2020/8/5 By:CyiceK
- 2020/8/30 By:TheAutumnOfRice