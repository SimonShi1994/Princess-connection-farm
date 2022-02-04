# encoding=utf-8
import configparser
import json
import os
import pathlib
import sys
from typing import Optional

cfg = configparser.ConfigParser()
try:
    cfg.read('config.ini', encoding="utf-8")
except configparser.MissingSectionHeaderError as e:
    if "ufeff" in e.message:
        cfg.read("config.ini", encoding="utf_8_sig")
    else:
        raise e

# cfg.sections() 全部头
# cfg.get('debug', 'trace_exception_for_debug')
# cfg.getint('log', 'log_cache')
# cfg.getboolean('debug', 'debug')
# 上面为读取的三种方法（str/int/bool)

CONFIG_UPDATED = True


def _CGet(method, section, option, default=None):
    global CONFIG_UPDATED
    if not cfg.has_section(section):
        print("未发现配置section：", section)
        CONFIG_UPDATED = False
        cfg.add_section(section)
    if cfg.has_option(section, option):
        return getattr(cfg, method)(section=section, option=option)
    else:
        if default is None:
            value = ""
        else:
            value = str(default)
        cfg.set(section=section, option=option, value=value)
        print("未发现配置", section, "-", option, end=" ")
        CONFIG_UPDATED = False
        if default is not None:
            print("设为默认值", value, '!')
        else:
            print()
        return getattr(cfg, method)(section=section, option=option)


def CGetBool(section, option, default=None) -> bool:
    return _CGet("getboolean", section, option, default)


def CGetInt(section, option, default=None) -> int:
    return _CGet("getint", section, option, default)


def CGetFloat(section, option, default=None) -> float:
    return _CGet("getfloat", section, option, default)


def CGet(section, option, default=None) -> str:
    return _CGet("get", section, option, default)


class GlobalConfig:
    """
    全局配置类
    为之后的动态修改、读取配置做准备
    """

    def __init__(self):
        self.config = {}

    def _set(self, option, value):
        """
        Set: For Own Use
        Will only change the value here but not in other files.
        """
        self.config[option] = value

    def set(self, option, value, find_global=True):
        """
        NB Set Here:
        Not only change the value here, but also
        search every PCR modules and change there values
        """
        self._set(option, value)
        globals()[option] = value
        if find_global:
            mypath = str(pathlib.Path().absolute())

            def is_pcr_pack(module, mypath):
                file_name = getattr(module, "__file__", "")
                if not isinstance(file_name, str):
                    return False
                if file_name.startswith(mypath):
                    return True
                return False

            for name, module in sys.modules.items():
                if is_pcr_pack(module, mypath):
                    # Is PCR modules
                    if hasattr(module, option):
                        # If Pre-Loaded, Change it.
                        setattr(module, option, value)

    def get(self, option, default=None):
        return self.config.get(option, default)

    def __getattr__(self, name):
        if name == "__all__":
            return list(self.config.keys())
        elif name in self.config:
            return self.config[name]
        else:
            raise AttributeError("No Config:", name)

    def config_set(self, option, value):
        global CONFIG_UPDATED
        CONFIG_UPDATED = False
        self._set(option, value)

    def add_bool(self, section, option, default: Optional[bool] = None):
        value = CGetBool(section, option, default)
        self._set(option, value)
        return value

    def add_int(self, section, option, default: Optional[int] = None):
        value = CGetInt(section, option, default)
        self._set(option, value)
        return value

    def add_float(self, section, option, default: Optional[float] = None):
        value = CGetFloat(section, option, default)
        self._set(option, value)
        return value

    def add_str(self, section, option, default: Optional[str] = None):
        value = CGet(section, option, default)
        self._set(option, value)
        return value

    def add_abspath(self, section, option, default: Optional[str] = None):
        value = CGet(section, option, default)
        value = os.path.abspath(value)
        self._set(option, value)
        return value

    def add_list(self, section, option, default: Optional[list] = None) -> list:
        default = json.dumps(default)
        value = CGet(section, option, default)
        value = json.loads(value)
        self._set(option, value)
        return value

    @staticmethod
    def config_update():
        if not CONFIG_UPDATED:
            print("config.ini 不是最新，更新中")
            cfg.write(open("config.ini", "w", encoding="utf-8"))
            print("config.ini 更新成功！")


GC = GlobalConfig()

debug = GC.add_bool('debug', 'debug', False)
save_debug_img = GC.add_bool('debug', 'save_debug_img', True)
ignore_warning = GC.add_bool('debug', 'ignore_warning', True)
trace_exception_for_debug = GC.add_bool('debug', 'trace_exception_for_debug', False)
use_template_cache = GC.add_bool('debug', 'use_template_cache', True)
baidu_ocr_img = GC.add_bool('debug', 'baidu_ocr_img', False)
disable_timeout_raise = GC.add_bool('debug', 'disable_timeout_raise', False)
u2_record_size = GC.add_int('debug', 'u2_record_size', 20)
debug_record_size = GC.add_int('debug', 'debug_record_size', 50)
u2_record_filter = GC.add_list('debug', 'u2_record_filter', [])
debug_record_filter = GC.add_list('debug', 'debug_record_filter', ['_lock_img', '_move_check'])
trace_tree = GC.add_str('debug', 'trace_tree', 'master')
colorlogsw = GC.add_bool('debug', 'colorlogsw', True)

force_as_ocr_as_possible = GC.add_bool("task", "force_as_ocr_as_possible", True)
sent_state_img = GC.add_bool('log', 'sent_state_img', False)
qqbot_key = GC.add_str('log', 'qqbot_key')
qqbot_select = GC.add_str('log', 'qqbot_select')
tg_token = GC.add_str('log', 'tg_token')
tg_mute = GC.add_bool('log', 'tg_mute', False)
qqbot_private_send_switch = GC.add_int('log', 'qqbot_private_send_switch', 0)
qqbot_group_send_switch = GC.add_int('log', 'qqbot_group_send_switch', 0)
qq = GC.add_str('log', 'qq', '0')
s_sckey = GC.add_str('log', 's_sckey')
wework_corpid = GC.add_str('log', 'wework_corpid')
wework_corpsecret = GC.add_str('log', 'wework_corpsecret')
log_lev = GC.add_str('log', 'log_lev', "1")
log_cache = GC.add_int('log', 'log_cache', 3)
sentstate = GC.add_int('log', 'sentstate', 30)
proxy_http = GC.add_str('log', 'proxy_http')
proxy_https = GC.add_str('log', 'proxy_https')

force_primary_equals_secondary = GC.add_bool('pcrfarm_setting', 'force_primary_equals_secondary', False)
force_primary_equals_secondary_use = GC.add_str('pcrfarm_setting', 'force_primary_equals_secondary_use', "本地1")
ocr_mode_main = GC.add_str('pcrfarm_setting', 'ocr_mode_main', "本地1")
ocr_mode_secondary = GC.add_str('pcrfarm_setting', 'ocr_mode_secondary', '网络1,网络2')
baidu_apiKey = GC.add_str('pcrfarm_setting', 'baidu_apiKey')
baidu_secretKey = GC.add_str('pcrfarm_setting', 'baidu_secretKey')
baidu_QPS = GC.add_int('pcrfarm_setting', 'baidu_QPS', 2)
ocrspace_ocr_apikey = GC.add_str('pcrfarm_setting', 'ocrspace_ocr_apikey')
anticlockwise_rotation_times = GC.add_int('pcrfarm_setting', 'anticlockwise_rotation_times', 1)
async_screenshot_freq = GC.add_int('pcrfarm_setting', 'async_screenshot_freq', 5)
bad_connecting_time = GC.add_int('pcrfarm_setting', 'bad_connecting_time', 10)
fast_screencut = GC.add_bool('pcrfarm_setting', 'fast_screencut', False)
force_fast_screencut = GC.add_bool('pcrfarm_setting', 'force_fast_screencut', True)
fast_screencut_delay = GC.add_float('pcrfarm_setting', 'fast_screencut_delay', 0)
fast_screencut_timeout = GC.add_int('pcrfarm_setting', 'fast_screencut_timeout', 3)
end_shutdown = GC.add_bool('pcrfarm_setting', 'end_shutdown', False)
lockimg_timeout = GC.add_int('pcrfarm_setting', 'lockimg_timeout', 90)
enable_pause = GC.add_bool('pcrfarm_setting', 'enable_pause', False)
max_reboot = GC.add_int('pcrfarm_setting', 'max_reboot', 3)
force_timeout_reboot = GC.add_bool('pcrfarm_setting', 'force_timeout_reboot', True)
running_input = GC.add_bool('pcrfarm_setting', 'running_input', False)
captcha_skip = GC.add_bool('pcrfarm_setting', 'captcha_skip', False)
captcha_sleep_times = GC.add_float('pcrfarm_setting', 'captcha_sleep_times', 0.2)
captcha_userstr = GC.add_str('pcrfarm_setting', 'captcha_userstr')
captcha_software_key = GC.add_str('pcrfarm_setting', 'captcha_software_key', "5259|4A96796C70C8F0EA")
captcha_senderror = GC.add_bool('pcrfarm_setting', 'captcha_senderror', True)
captcha_senderror_times = GC.add_int('pcrfarm_setting', 'captcha_senderror_times', 2)
captcha_level = GC.add_str('pcrfarm_setting', 'captcha_level', '小速')
captcha_wait_time = GC.add_int('pcrfarm_setting', 'captcha_wait_time', 60)
captcha_popup = GC.add_bool("pcrfarm_setting", "captcha_popup", True)
clear_traces_and_cache = GC.add_bool("pcrfarm_setting", "clear_traces_and_cache", False)
auto_start_app = GC.add_bool("pcrfarm_setting", "auto_start_app", True)
inline_app = GC.add_bool("pcrfarm_setting", "inline_app", True)
use_my_id = GC.add_bool("pcrfarm_setting", "use_my_id", False)

enable_auto_find_emulator = GC.add_bool('emulator_setting', 'enable_auto_find_emulator', False)
one_way_search_auto_find_emulator = GC.add_bool('emulator_setting', 'one_way_search_auto_find_emulator', False)
emulators_port_interval: Optional[list] = (GC.add_list('emulator_setting', 'emulators_port_interval', [30000, 5000]))
emulators_port_list: Optional[list] = (GC.add_list('emulator_setting', 'emulators_port_list', []))
emulator_ports: Optional[list] = (GC.add_list('emulator_setting', 'emulator_ports', []))
adb_dir = GC.add_abspath('emulator_setting', 'adb_dir', "adb")
add_adb_to_path = GC.add_bool('emulator_setting', 'add_adb_to_path', True)
selected_emulator = GC.add_str('emulator_setting', 'selected_emulator', "雷电")
emulator_console = GC.add_str('emulator_setting', 'emulator_console')
emulator_id = (GC.add_list('emulator_setting', 'emulator_id', []))
auto_emulator_address = GC.add_bool("emulator_setting", "auto_emulator_address", True)
emulator_address = (GC.add_list('emulator_setting', 'emulator_address', []))
quit_emulator_when_free = GC.add_bool('emulator_setting', 'quit_emulator_when_free', True)
max_free_time = GC.add_int('emulator_setting', 'max_free_time', 120)
wait_for_launch_time = GC.add_int('emulator_setting', 'wait_for_launch_time', 600)
ignore_serials: Optional[list] = (GC.add_list('emulator_setting', 'ignore_serials', []))

GC.config_update()

""" BackUp
debug = cfg.getboolean('debug', 'debug')
ignore_warning = cfg.getboolean('debug', 'ignore_warning')
trace_exception_for_debug = cfg.getboolean('debug', 'trace_exception_for_debug')
use_template_cache = cfg.get('debug', 'use_template_cache')
baidu_ocr_img = cfg.getboolean('debug', 'baidu_ocr_img')
disable_timeout_raise = cfg.getboolean('debug', 'disable_timeout_raise')

s_sckey = cfg.get('log', 's_sckey')
log_lev = cfg.get('log', 'log_lev')
log_cache = cfg.getint('log', 'log_cache')
sentstate = cfg.getint('log', 'sentstate')

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
inline_app = cfg.getboolean("pcrfarm_setting", "inline_app")

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

"""
