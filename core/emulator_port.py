#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

import copy
import gettext
import json
import os
# import platform
import queue
import re
import subprocess
import threading

import psutil

from core.log_handler import pcr_log
from core.pcr_config import adb_dir, emulators_port_interval, emulators_port_list, one_way_search_auto_find_emulator
from core.safe_u2 import run_adb

emulator_ip = "127.0.0.1"
emulator_ip2 = "0.0.0.0"

domains = ['emulator_port']
languageDir = os.path.abspath('src/locale')
for domain in domains:
    gettext.bindtextdomain(domain, languageDir)
    gettext.textdomain(domain)
_ = gettext.gettext

_CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.abspath(__file__), os.path.pardir, 'emulator_config.json'))

_EMULATORS = {}

_log = pcr_log('emulator_port')


class Emulator(object):
    def __init__(self, d):
        self.type = d['type']
        self.name = d['name']
        # handle with different emulators with same process name
        self.unique_id = d.get('unique_id')
        self.process_name = d['process_name']
        self.default_ports = d['default_ports']
        self.re_port = d.get('re_port')
        self.desc = d.get('desc')
        # 2: never tips
        # 1: tip when unknown emulator found
        # 0: tip when known emulator port change and unknown emulator found
        self.upload_tip_level = \
            d.get('upload_tip_level') if d.get('upload_tip_level') else 0


def get_processes(emulator):
    return [x for x in psutil.process_iter()
            if emulator.unique_id == get_process_unique_id(x)]


def check_adb_connectable_by_port(port, auto_disconnect=True):
    result = check_adb_connectable_by_ports(
        [port], auto_disconnect=auto_disconnect)
    return len(result) > 0 and result[0] == port


def check_adb_connectable_by_ports(ports, auto_disconnect=True):
    lock = threading.Lock()
    ports_len = len(ports)
    devices_queue = queue.Queue(ports_len)
    ports_queue = queue.Queue(ports_len)
    for port in ports:
        ports_queue.put(port)

    class connectPort(threading.Thread):
        def __init__(self, ports_queue, devices_queue):
            threading.Thread.__init__(self)
            self.ports_queue = ports_queue
            self.devices_queue = devices_queue

        def run(self) -> None:
            port_now = self.ports_queue.get()
            device_now = "%s:%s" % (emulator_ip, port_now)
            run_adb(f"connect {device_now}", timeout=1)
            self.devices_queue.put(device_now)

    connet_thread_list = []
    for i in range(ports_len):
        t = connectPort(ports_queue=ports_queue, devices_queue=devices_queue)
        t.start()
        connet_thread_list.append(t)

    for i in connet_thread_list:
        i.join()

    result = check_adb_connected(devices_queue)
    if auto_disconnect:
        for i in range(devices_queue.qsize()):
            device = devices_queue.get()
            run_adb(f"disconnect {device}")
    ports = [int(x.split(':')[1]) for x in result]
    return ports


def sh(command, print_msg=True, timeout=0):
    # print("命令为：" + command)
    p = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True, start_new_session=True)

    format = 'utf-8'
    if sys.platform == "win32":
        format = 'gbk'

    try:
        if timeout != 0:
            (result, errs) = p.communicate(timeout=timeout)
        else:
            (result, errs) = p.communicate()
        ret_code = p.poll()
        if ret_code:
            code = 1
            result = "[Error]Called Error ： " + str(result.decode(format))
        else:
            code = 0
            result = str(result.decode(format))
            # print(result)
    except subprocess.TimeoutExpired:
        # 注意：不能只使用p.kill和p.terminate，无法杀干净所有的子进程，需要使用os.killpg
        p.kill()
        p.terminate()
        # os.killpg(p.pid, signal.SIGTERM)
        # os.kill(p.pid, signal.CTRL_C_EVENT)

        # 注意：如果开启下面这两行的话，会等到执行完成才报超时错误，但是可以输出执行结果
        # (outs, errs) = p.communicate()
        # print(outs.decode('utf-8'))

        code = 1
        result = "[ERROR]Timeout Error : Command '" + command + "' timed out after " + str(timeout) + " seconds"
    except Exception as e:
        code = 1
        result = "[ERROR]Unknown Error : " + str(e)

    return result


def check_adb_connected(devices_queue):
    # check if device is active
    active_result = run_adb("devices")
    connected_devices = []
    for i in range(devices_queue.qsize()):
        device = devices_queue.get()
        devices_queue.put(device)
        if re.search(r"%s\s+device" % (device), active_result):
            connected_devices.append(device)
    return connected_devices


def get_ports(emulator):
    ps = get_processes(emulator)
    _log.write_log(level='debug',
                   message=_("{name}({type}) processes:").format(
                       name=emulator.name, type=emulator.type))
    _log.write_log(level='debug', message=ps)
    # print(
    #     _("{name}({type}) processes:").format(
    #         name=emulator.name, type=emulator.type))
    # print(ps)
    ports = []
    if 1 <= len(ps) <= len(emulator.default_ports):
        for default_port in emulator.default_ports:
            result = check_adb_connectable_by_port(
                default_port, auto_disconnect=False)
            if result:
                ports.append(default_port)
    if ports:
        return ports

    for p in ps:
        connections = [
            x.laddr for x in p.connections() if x.status == psutil.CONN_LISTEN
        ]
        # print(connections)
        if emulator.re_port:
            ports += [
                int(x.port) for x in connections
                if re.match(emulator.re_port, str(x.port)) and x.port > 2000
            ]
        else:
            ports += [int(x.port) for x in connections if x.port > 2000]
    ports = check_adb_connectable_by_ports(ports)
    return ports


def read_config(src=_CONFIG_PATH):
    with open(src, 'r', encoding='utf-8') as f:
        config = json.load(f)
    for e in config['emulators']:
        _EMULATORS[e['re_port']] = Emulator(e)
        _EMULATORS[e['unique_id']] = Emulator(e)
        _EMULATORS[e['name']] = Emulator(e)


def is_known_port_changed(emulator, new_ports):
    if not emulator or emulator.upload_tip_level >= 1:
        return False
    old_ports = emulator.default_ports
    if not old_ports:
        old_ports = []
    if not new_ports:
        new_ports = []
    if len(new_ports) > len(old_ports):
        for port in old_ports:
            if port not in new_ports:
                return True
    else:
        for port in new_ports:
            if port not in old_ports:
                return True
    return False


def get_process_unique_id(p):
    relative_path = None
    try:
        # read system process propertity may throw an exception.
        path = os.path.dirname(p.exe())
        path = os.path.basename(os.path.dirname(path)) + \
               '/' + os.path.basename(path)
        relative_path = path
    except (PermissionError, psutil.AccessDenied):
        pass
    return "%s/%s" % (relative_path, p.name())


def get_port(PID, re_rules=None):
    """通过pid获取端口号"""
    # print("get_port run now!")
    i = 0
    flag = 0
    por = 65599
    cmd = 'netstat -ano | findstr' + ' ' + str(PID)
    # print(cmd)
    a = os.popen(cmd)
    # 此时打开的a是一个对象，如果直接打印的话是对象内存地址
    text = a.read()
    # 要用read（）方法读取后才是文本对象
    first_line = text.split(':')
    # print(first_line)
    if not first_line:
        _log.write_log('info', "模拟器程序获取列表为空")
        return por
    while True:
        # print(len(first_line))
        # print(i)
        flag = 0
        ab = first_line[i].replace('\r\n', '')
        cd = ab.split(' ')
        # print(cd[-1])
        # print(cd[0])
        # print(ab)

        if (i < len(first_line) - 1) and (cd[-1] == "0.0.0.0" or cd[-1] == "127.0.0.1"):
            # print(cd[0])
            try:
                if not emulators_port_interval[0] >= int(cd[0]) >= emulators_port_interval[1]:
                    # print("失效", int(cd[0]))
                    i += 1
                    continue
            except ValueError as e:
                i += 1
                continue

            if re_rules:
                if not re.match(re_rules, cd[0], flags=0):
                    i += 1
                    continue

            if sys.platform == "win32":
                adb_connect_info = subprocess.Popen(
                    f' cd {adb_dir} & adb connect ' + emulator_ip + ':' + str(cd[0]),
                    shell=True, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    encoding='utf-8').communicate()[0].split(' ')
            else:
                adb_connect_info = subprocess.Popen(
                    f' adb connect ' + emulator_ip + ':' + str(cd[0]),
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    encoding='utf-8').communicate()[0].split(' ')
            error_str = ["failed", "10068", "cannot", "already"]
            for check_str in error_str:
                if check_str in adb_connect_info:
                    _log.write_log(level='info', message=f"连接模拟器[{emulator_ip2 + ':' + str(cd[0])}]失败，"
                                                         f"不是这个模拟器,继续查找中...")
                    i += 1
                    continue
                elif "connected" in adb_connect_info:
                    if sys.platform == "win32":
                        adb_connect_info = subprocess.Popen(
                            f' cd {adb_dir} & adb devices',
                            shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            encoding='utf-8').communicate()[0].split(' ')
                    else:
                        adb_connect_info = subprocess.Popen(
                            f' adb devices',
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            encoding='utf-8').communicate()[0].split(' ')

                    # print(adb_connect_info)
                    if adb_connect_info:
                        _log.write_log(level='info', message=f"连接模拟器[{emulator_ip2 + ':' + str(cd[0])}]成功，"
                                                             f"是这个模拟器,查找完毕")
                        flag = 1
                    else:
                        _log.write_log(level='info', message=f"连接模拟器[{emulator_ip2 + ':' + str(cd[0])}]失败，"
                                                             f"不是这个模拟器,继续查找中...")
                        i += 1
                        continue

            if emulators_port_interval[0] >= int(cd[0]) >= emulators_port_interval[1] and flag == 1:
                # print(cd)
                if emulators_port_list:
                    if int(cd[0]) in emulators_port_list:
                        por = cd[0]
                        # print("1-",por)
                        break
                    else:
                        break
                else:
                    por = cd[0]
                    # print(por)
                    break
        elif i < len(first_line) - 1:
            i += 1
        else:
            # print("模拟器adb端口获取列表为空")
            break
    # print(por)
    return por


def check_known_emulators():
    _log.write_log('info', "混搭请注意下端口是否相互冲突！")
    read_config()
    emulators = {}
    filtered_emulator = []
    result = []
    ischanged = False
    for p in psutil.process_iter():
        unique_id = get_process_unique_id(p)
        if unique_id in filtered_emulator:
            continue
        filtered_emulator.append(unique_id)
        # print(unique_id)
        # for t, e in _EMULATORS.items():
        for t, e in _EMULATORS.items():
            if e.unique_id == unique_id:
                # print(e)
                # result = get_ports(e)
                ps = get_processes(e)
                # print(ps)
                if one_way_search_auto_find_emulator:
                    if not result:
                        for i in range(0, len(ps)):
                            if ps[i].status() == "stopped":
                                # print("进程不存活")
                                continue
                            if str(get_port(ps[i].pid, e.re_port)) not in result:
                                _log.write_log('info', "检测到【" + e.name + "】模拟器")
                                result.append(get_port(ps[i].pid, e.re_port))
                else:
                    for i in range(0, len(ps)):
                        if ps[i].status() == "stopped":
                            # print("进程不存活")
                            continue
                        if str(get_port(ps[i].pid, e.re_port)) not in result:
                            _log.write_log('info', "检测到【" + e.name + "】模拟器")
                            result.append(get_port(ps[i].pid, e.re_port))
                            # print(result)
                        # result = [5565]
                        # a = get_processes(e)
                        # print(port(24664))
                        # print(a)
                        # print(result)
                if result:
                    if not emulators.get(e.unique_id):
                        emulators[e.unique_id] = copy.deepcopy(e)
                    emulators[e.unique_id].default_ports = result
                if not ischanged:
                    ischanged = is_known_port_changed(
                        e, emulators[e.unique_id].default_ports)
    result_ports = []
    for i, j in emulators.items():
        result_ports += j.default_ports
    # return ischanged, emulators.values()
    # return emulators
    return result_ports
