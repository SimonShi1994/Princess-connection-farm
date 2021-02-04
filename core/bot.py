import time

import psutil
import requests

from core.pcr_config import s_sckey, log_lev, log_cache, qqbot_key, qqbot_select, qq, qqbot_private_send_switch, \
    qqbot_group_send_switch


class Bot:
    """
    公有推送机器人的简单封装
    消息缓存不在区分账号，而是以类型分类（info/warning等）
    By:CyiceK 2021/2/1
    """

    def __init__(self):
        self.qq = qq
        self.qqbot_select = qqbot_select
        self.server_nike_url = f"https://sc.ftqq.com/{s_sckey}.send"
        self.lev_0 = ['info', 'warning', 'error', 'STATE', '']
        self.lev_1 = ['warning', 'error', 'STATE', '']
        self.lev_2 = ['error', 'STATE', '']
        # 3为0级消息，是消息队列的最高级别,无视log_cache堵塞
        self.lev_3 = ['STATE', '']
        # 日志级别
        self.lev_dic = {
            '0': self.lev_0,
            '1': self.lev_1,
            '2': self.lev_2,
            '3': self.lev_3
        }
        # 日志缓存
        self.acc_message = {
            'info': [],
            'warning': [],
            'error': [],
            'STATE': [],
            '': []
        }

        # 私人消息
        self.private_url = {
            'CoolPush_private_url': f"https://push.xuthus.cc/send/{qqbot_key}",
            'Qmsgnike_private_url': f"https://qmsg.zendee.cn/send/{qqbot_key}"
        }
        # 群组消息
        self.group_url = {
            'CoolPush_group_url': f"https://push.xuthus.cc/group/{qqbot_key}",
            'Qmsgnike_group_url': f"https://qmsg.zendee.cn/group/{qqbot_key}"
        }

        self.qqbot_url1 = self.private_url.get(f"{self.qqbot_select}_private_url", "")
        self.qqbot_url2 = self.group_url.get(f"{self.qqbot_select}_group_url", "")

    def server_bot(self, s_level, message='', acc_state=''):
        # 兼容老接口
        if len(s_sckey) != 0:
            self.wechat_bot(s_level, message=message, acc_state=acc_state)
        if len(qqbot_key) != 0:
            self.qq_bot(s_level, message=message, acc_state=acc_state)

    def wechat_bot(self, s_level, message='', acc_state=''):
        """
        server酱连接 2020/7/21 by:CyiceK
        更新于2021/1/31
        s_level 为日志级别
        """
        # 日志级别所区分的头
        # STATE头为任务状态头，发送及包含STATE
        # 先不填acc_state
        if len(s_sckey) != 0:
            message = ''.join(message).replace('\n', '')
            if s_level in self.lev_dic[log_lev]:
                # self.acc_message.setdefault(s_level, [])
                self.acc_message[s_level].append(message)
                self.acc_message[s_level].append('\n')
                # print(self.acc_message[s_level])
                # print(len(self.acc_message[self.acc_name]))
                # print(len(self.acc_message[s_level])//2, self.acc_message[s_level])
            if s_level in self.lev_dic['3'] or (
                    s_level in self.lev_dic[log_lev] and len(self.acc_message[s_level]) // 2 >= log_cache):
                message = ''.join(self.acc_message[s_level]).replace(',', '\n').replace("'", '')
                # print(message)
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_info = "CPU使用率：%i%%" % cpu_percent
                # print(cpu_info)
                virtual_memory = psutil.virtual_memory()
                used_memory = virtual_memory.used / 1024 / 1024 / 1024
                free_memory = virtual_memory.free / 1024 / 1024 / 1024
                memory_percent = virtual_memory.percent
                memory_info = "内存使用：%0.2fG||使用率%0.1f%%||剩余内存：%0.2fG" % (used_memory, memory_percent, free_memory)
                # print(memory_info)
                info = {
                    'text': f'公主连结农场脚本【{s_level}】',
                    'desp': '#### 系统运行信息：\n- %s\n- %s\n\n------\n\n农场信息：\n\n```\n\n%s\n\n%s\n\n```\n\n'
                            '来自GITHUB一款开源脚本: https://github.com/SimonShi1994/Princess-connection-farm\n\n ' % (
                                cpu_info, memory_info, message, acc_state)

                }
                try:
                    requests.get(self.server_nike_url, params=info)
                except Exception as e:
                    pass
                    # pcr_log("__SERVER_BOT__").write_log("error", f"ServerBot发送失败：{e}")
                # 不因为0级消息而清空消息队列
                if s_level not in self.lev_dic['3']:
                    # 发送完后清空消息队列
                    self.acc_message = {}

    def info_cutting(self, msg, _max=1500):
        """
        信息切割
        :param msg: 信息题字符串
        :param _max: 大于等于后切割
        :return: 切割的字符串 切割后的字符串
        """
        if len(msg) > _max:
            return msg[:1500], msg[1500:]
        else:
            return None, msg

    def qq_bot(self, s_level, message='', acc_state=''):
        """
        CoolPush与Qmsg酱 2021/1/31 by:CyiceK
        s_level 为日志级别
        """
        # 日志级别所区分的头
        # STATE头为任务状态头，发送及包含STATE
        # 先不填acc_state
        if len(s_sckey) != 0:
            message = ''.join(message).replace('\n', '')
            if s_level in self.lev_dic[log_lev]:
                # self.acc_message.setdefault(s_level, [])
                self.acc_message[s_level].append(message)
                self.acc_message[s_level].append('\n')
                # print(self.acc_message[s_level])
                # print(len(self.acc_message[self.acc_name]))
                # print(len(self.acc_message[s_level])//2, self.acc_message[s_level])
            if s_level in self.lev_dic['3'] or (
                    s_level in self.lev_dic[log_lev] and len(self.acc_message[s_level]) // 2 >= log_cache):
                message = ''.join(self.acc_message[s_level]).replace(',', '\n').replace("'", '')
                # print(message)
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_info = "CPU使用率：%i%%" % cpu_percent
                # print(cpu_info)
                virtual_memory = psutil.virtual_memory()
                used_memory = virtual_memory.used / 1024 / 1024 / 1024
                free_memory = virtual_memory.free / 1024 / 1024 / 1024
                memory_percent = virtual_memory.percent
                memory_info = "内存使用：%0.2fG||使用率%0.1f%%||剩余内存：%0.2fG" % (used_memory, memory_percent, free_memory)
                # print(memory_info)

                # 下面两个字典只是给开发者看得，一目了然格式
                CoolPush_info = {
                    'c': f'>>>公主连结农场脚本【{s_level}】<<<\n'
                         f'@face=63@@face=63@@face=63@@at={self.qq}@欢迎您使用~@face=63@@face=63@@face=63@\n'
                         f'#### 当前系统运行信息 ####\n- {cpu_info}\n- {memory_info}\n——————————————————\n'
                         f'目前农场信息：\n@face=72@@face=72@@face=72@'
                         f'\n{message}\n'
                         f'目前状态信息：\n@face=72@@face=72@@face=72@'
                         f'\n{acc_state}\n'
                         f'@face=72@@face=72@@face=72@\n '
                         f'@face=185@来自GITHUB一款开源脚本 (// . //): '
                         'ht【删】tps://gith【删】ub.【删】com/SimonShi1994/【删】Princess-connection-farm\n '
                }

                Qmsgnike_info = {
                    'msg': f'>>>公主连结农场脚本【{s_level}】<<<\n'
                           f'@face=63@@face=63@@face=63@@at={self.qq}@欢迎您使用~@face=63@@face=63@@face=63@\n'
                           f'#### 当前系统运行信息 ####\n- {cpu_info}\n- {memory_info}\n——————————————————\n'
                           f'目前农场信息：\n@face=72@@face=72@@face=72@'
                           f'\n{message}\n'
                           f'目前状态信息：\n@face=72@@face=72@@face=72@'
                           f'\n{acc_state}\n'
                           f'@face=72@@face=72@@face=72@\n '
                           f'@face=185@来自GITHUB一款开源脚本 (// . //): '
                           'ht【删】tps://gith【删】ub.【删】com/SimonShi1994/【删】Princess-connection-farm\n ',
                    'qq': self.qq
                }

                try:
                    send = None
                    tmp_dict = {'c': ''}
                    if self.qqbot_select == 'CoolPush':
                        if qqbot_private_send_switch == 1:
                            send, sent = self.info_cutting(CoolPush_info['c'])
                            while send is None:
                                tmp_dict = {'c': send}
                                requests.post(self.qqbot_url1, params=tmp_dict)
                                send, sent = self.info_cutting(sent)
                                time.sleep(0.3)
                            tmp_dict = {'c': sent}
                            requests.post(self.qqbot_url1, params=tmp_dict)

                        if qqbot_group_send_switch == 1:
                            send, sent = self.info_cutting(CoolPush_info['c'])
                            while send is not None:
                                tmp_dict = {'c': send}
                                requests.post(self.qqbot_url2, params=tmp_dict)
                                send, sent = self.info_cutting(sent)
                                time.sleep(0.3)
                            tmp_dict = {'c': sent}
                            requests.post(self.qqbot_url2, params=tmp_dict)

                    elif self.qqbot_select == 'Qmsgnike':
                        if qqbot_private_send_switch == 1:
                            send, sent = self.info_cutting(Qmsgnike_info['msg'])
                            while send is None:
                                tmp_dict = {'msg': send, qq: self.qq}
                                requests.post(self.qqbot_url1, params=tmp_dict)
                                send, sent = self.info_cutting(sent)
                                time.sleep(0.3)
                            tmp_dict = {'msg': sent, qq: self.qq}
                            requests.post(self.qqbot_url1, params=tmp_dict)
                        if qqbot_group_send_switch == 1:
                            send, sent = self.info_cutting(Qmsgnike_info['msg'])
                            while send is None:
                                tmp_dict = {'msg': send, qq: self.qq}
                                requests.post(self.qqbot_url2, params=tmp_dict)
                                send, sent = self.info_cutting(sent)
                                time.sleep(0.3)
                            tmp_dict = {'msg': sent, qq: self.qq}
                            requests.post(self.qqbot_url2, params=tmp_dict)
                except Exception as e:
                    pass
                    # pcr_log("__SERVER_BOT__").write_log("error", f"ServerBot发送失败：{e}")
                # 不因为0级消息而清空消息队列
                if s_level not in self.lev_dic['3']:
                    # 发送完后清空消息队列
                    self.acc_message = {}
