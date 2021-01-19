# encoding=utf-8
import configparser
import json
import os
from typing import Optional

cfg = configparser.ConfigParser()
cfg.read('config.ini', encoding="utf-8")

# cfg.sections() 全部头
# cfg.get('debug', 'trace_exception_for_debug')
# cfg.getint('log', 'log_cache')
# cfg.getboolean('debug', 'debug')
# 上面为读取的三种方法（str/int/bool)

debug = cfg.getboolean('debug', 'debug')
ignore_warning = cfg.getboolean('debug', 'ignore_warning')
trace_exception_for_debug = cfg.getboolean('debug', 'trace_exception_for_debug')
use_template_cache = cfg.get('debug', 'use_template_cache')
baidu_ocr_img = cfg.getboolean('debug', 'baidu_ocr_img')
disable_timeout_raise = cfg.getboolean('debug', 'disable_timeout_raise')

s_sckey = cfg.get('log', 's_sckey')
log_lev = cfg.get('log', 'log_lev')
log_cache = cfg.getint('log', 'log_cache')
s_sentstate = cfg.getint('log', 's_sentstate')

baidu_apiKey = cfg.get('pcrfarm_setting', 'baidu_apiKey')
baidu_secretKey = cfg.get('pcrfarm_setting', 'baidu_secretKey')
baidu_QPS = cfg.getint('pcrfarm_setting', 'baidu_QPS')
ocr_mode = cfg.get('pcrfarm_setting', 'ocr_mode')
anticlockwise_rotation_times = cfg.getint('pcrfarm_setting', 'anticlockwise_rotation_times')
async_screenshot_freq = cfg.getint('pcrfarm_setting', 'async_screenshot_freq')
bad_connecting_time = cfg.getint('pcrfarm_setting', 'bad_connecting_time')
fast_screencut = cfg.getboolean('pcrfarm_setting', 'fast_screencut')
force_fast_screencut = cfg.getboolean('pcrfarm_setting', 'force_fast_screencut')
fast_screencut_delay = cfg.getfloat('pcrfarm_setting', 'fast_screencut_delay')
fast_screencut_timeout = cfg.getint('pcrfarm_setting', 'fast_screencut_timeout')
end_shutdown = cfg.getboolean('pcrfarm_setting', 'end_shutdown')
lockimg_timeout = cfg.getint('pcrfarm_setting', 'lockimg_timeout')
enable_pause = cfg.getboolean('pcrfarm_setting', 'enable_pause')
max_reboot = cfg.getint('pcrfarm_setting', 'max_reboot')
running_input = cfg.getboolean('pcrfarm_setting', 'running_input')
captcha_skip = cfg.getboolean('pcrfarm_setting', 'captcha_skip')
captcha_userstr = cfg.get('pcrfarm_setting', 'captcha_userstr')
captcha_software_key = "5259|4A96796C70C8F0EA"
captcha_senderror = cfg.getboolean('pcrfarm_setting', 'captcha_senderror')
captcha_senderror_times = cfg.getint('pcrfarm_setting', 'captcha_senderror_times')
captcha_level = cfg.get('pcrfarm_setting', 'captcha_level')
captcha_wait_time = cfg.getint('pcrfarm_setting', 'captcha_wait_time')
captcha_popup = cfg.getboolean("pcrfarm_setting", "captcha_popup")
clear_traces_and_cache = cfg.getboolean("pcrfarm_setting", "clear_traces_and_cache")
auto_start_app = cfg.getboolean("pcrfarm_setting", "auto_start_app")

enable_auto_find_emulator = cfg.getboolean('emulator_setting', 'enable_auto_find_emulator')
emulator_ports: Optional[list] = json.loads(cfg.get('emulator_setting', 'emulator_ports'))
adb_dir = os.path.abspath(cfg.get('emulator_setting', 'adb_dir'))
add_adb_to_path = cfg.getboolean('emulator_setting', 'add_adb_to_path')
selected_emulator = cfg.get('emulator_setting', 'selected_emulator')
emulator_console = cfg.get('emulator_setting', 'emulator_console')
emulator_id = json.loads(cfg.get('emulator_setting', 'emulator_id'))
auto_emulator_address = cfg.getboolean("emulator_setting", "auto_emulator_address")
emulator_address = json.loads(cfg.get('emulator_setting', 'emulator_address'))
quit_emulator_when_free = cfg.getboolean('emulator_setting', 'quit_emulator_when_free')
max_free_time = cfg.getint('emulator_setting', 'max_free_time')
wait_for_launch_time = cfg.getint('emulator_setting', 'wait_for_launch_time')
ignore_serials: Optional[list] = json.loads(cfg.get('emulator_setting', 'ignore_serials'))
