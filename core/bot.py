import base64
import time

import urllib.request
import json
import os
from PIL import Image
from io import BytesIO
import cv2
import psutil
import requests
from requests.adapters import HTTPAdapter

from core.pcr_config import s_sckey, log_lev, log_cache, qqbot_key, qqbot_select, qq, qqbot_private_send_switch, \
    qqbot_group_send_switch, tg_token, tg_mute, debug, proxy_http, proxy_https, wework_corpid, wework_corpsecret, \
    wework_agid

BOT_PROXY = {
    "http": proxy_http if len(proxy_http) > 0 else None,
    "https": proxy_https if len(proxy_https) > 0 else None
}


class SendFailed(Exception):
    pass


class Bot:
    """
    公有推送机器人的简单封装
    消息缓存不在区分账号，而是以类型分类（info/warning等）
    By:CyiceK 2021/2/1
    """

    def __init__(self):
        self.qq = qq
        self.cpu_info = None
        self.memory_info = None
        self.img_url = None
        self.wework_url = "https://qyapi.weixin.qq.com"
        self.corpid = wework_corpid
        self.corpsecret = wework_corpsecret
        self.coragid = wework_agid
        self.qqbot_select = qqbot_select
        self.req_post = requests.Session()
        self.req_post.mount('http://', HTTPAdapter(max_retries=5))
        self.req_post.mount('https://', HTTPAdapter(max_retries=5))
        # https://sctapi.ftqq.com/ server酱Turbo版本
        self.server_nike_url = f"https://sctapi.ftqq.com/{s_sckey}.send"
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

    def server_bot(self, s_level, message='', acc_state='', img=None, img_title=''):
        """
        消息推送
        :param s_level:
        :param message:
        :param acc_state:
        :param img: 必须为cv2格式，然后转为base64或者二进制流再post出去
        :param img_title:
        :return:
        """
        if len(s_sckey) != 0 or len(qqbot_key) != 0 or len(tg_token) != 0:
            message = ''.join(message).replace('\n', '')
            if s_level in self.lev_dic[log_lev]:
                # self.acc_message.setdefault(s_level, [])
                self.acc_message[s_level].append(message)
                self.acc_message[s_level].append('\n')
                # print(self.acc_message[s_level])
                # print(len(self.acc_message[self.acc_name]))
                # print(len(self.acc_message[s_level])//2, self.acc_message[s_level])
            if s_level in self.lev_3 or (
                    s_level in self.lev_dic[log_lev] and len(self.acc_message[s_level]) // 2 >= log_cache):
                message = ''.join(self.acc_message[s_level]).replace(',', '\n').replace("'", '')
                # print(message)
                cpu_percent = psutil.cpu_percent(interval=1)
                self.cpu_info = "CPU使用率：%i%%" % cpu_percent
                # print(cpu_info)
                virtual_memory = psutil.virtual_memory()
                used_memory = virtual_memory.used / 1024 / 1024 / 1024
                free_memory = virtual_memory.free / 1024 / 1024 / 1024
                memory_percent = virtual_memory.percent
                self.memory_info = "内存使用：%0.2fG||使用率%0.1f%%||剩余内存：%0.2fG" % (used_memory, memory_percent, free_memory)
                # print(memory_info)
                # 兼容老接口
                if len(s_sckey) != 0 and img == '':
                    self.wechat_bot(s_level, message=message, acc_state=acc_state)
                if len(qqbot_key) != 0 and img == '':
                    self.qq_bot(s_level, message=message, acc_state=acc_state)
                if len(tg_token) != 0:
                    self.tg_bot(s_level, message=message, acc_state=acc_state, img=img, img_title=img_title)
                if len(wework_corpid) != 0 and len(wework_corpsecret) != 0 and len(wework_agid) != 0:
                    qywx = Qywx(s_level, acc_state)
                    if not message == '':
                        qywx.send_msg_message(message)
                    if img is not None:
                        upload_file = Image.open(BytesIO(img.read()))
                        upload_file = upload_file.convert("RGB")
                        # print(tr.run(img.copy().convert("L"), flag=tr.FLAG_ROTATED_RECT))
                        result_img = upload_file.copy().convert("L")
                        qywx.send_image_message(result_img)
                if s_level not in self.lev_dic['3']:
                    # 发送完后清空消息队列
                    self.acc_message[s_level] = []

    def wechat_bot(self, s_level, message='', acc_state=''):
        """
        server酱连接 2020/7/21 by:CyiceK
        更新于2021/1/31
        s_level 为日志级别
        """
        # 日志级别所区分的头
        # STATE头为任务状态头，发送及包含STATE
        # 先不填acc_state
        info = {
            'title': f'公主连结农场脚本【{s_level}】',
            'desp': '#### 系统运行信息：\n- %s\n- %s\n\n------\n\n农场信息：\n\n```\n\n%s\n\n%s\n\n```\n\n'
                    '来自GITHUB一款开源脚本: https://github.com/SimonShi1994/Princess-connection-farm\n\n ' % (
                        self.cpu_info, self.memory_info, message, acc_state)

        }
        try:
            self.req_post.post(self.server_nike_url, proxies=BOT_PROXY, params=info)
        except Exception as e:
            raise SendFailed('wechat推送服务器错误', e)
            # self.wechat_bot(s_level, message=message, acc_state=acc_state)
            # pcr_log("__SERVER_BOT__").write_log("error", f"ServerBot发送失败：{e}")

    def info_cutting(self, msg, _max=1500):
        """
        信息切割
        :param msg: 信息题字符串
        :param _max: 大于等于后切割
        :return: 切割的字符串 切割后的字符串
        """
        if len(msg) > _max:
            return msg[:_max], msg[_max:]
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
        # 下面两个字典只是给开发者看得，一目了然格式
        CoolPush_info = {
            'c': f'>>>公主连结农场脚本【{s_level}】<<<\n'
                 f'@face=63@@face=63@@face=63@@at={self.qq}@欢迎您使用~@face=63@@face=63@@face=63@\n'
                 f'#### 当前系统运行信息 ####\n- {self.cpu_info}\n- {self.memory_info}\n——————————————————\n'
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
                   f'#### 当前系统运行信息 ####\n- {self.cpu_info}\n- {self.memory_info}\n——————————————————\n'
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
                        self.req_post.post(self.qqbot_url1, proxies=BOT_PROXY, params=tmp_dict)
                        send, sent = self.info_cutting(sent)
                        time.sleep(0.3)
                    tmp_dict = {'c': sent}
                    self.req_post.post(self.qqbot_url1, proxies=BOT_PROXY, params=tmp_dict)

                if qqbot_group_send_switch == 1:
                    send, sent = self.info_cutting(CoolPush_info['c'])
                    while send is not None:
                        tmp_dict = {'c': send}
                        self.req_post.post(self.qqbot_url2, proxies=BOT_PROXY, params=tmp_dict)
                        send, sent = self.info_cutting(sent)
                        time.sleep(0.3)
                    tmp_dict = {'c': sent}
                    self.req_post.post(self.qqbot_url2, proxies=BOT_PROXY, params=tmp_dict)

            elif self.qqbot_select == 'Qmsgnike':
                if qqbot_private_send_switch == 1:
                    send, sent = self.info_cutting(Qmsgnike_info['msg'])
                    while send is None:
                        tmp_dict = {'msg': send, qq: self.qq}
                        self.req_post.post(self.qqbot_url1, proxies=BOT_PROXY, params=tmp_dict)
                        send, sent = self.info_cutting(sent)
                        time.sleep(0.3)
                    tmp_dict = {'msg': sent, qq: self.qq}
                    self.req_post.post(self.qqbot_url1, proxies=BOT_PROXY, params=tmp_dict)
                if qqbot_group_send_switch == 1:
                    send, sent = self.info_cutting(Qmsgnike_info['msg'])
                    while send is None:
                        tmp_dict = {'msg': send, qq: self.qq}
                        self.req_post.post(self.qqbot_url2, proxies=BOT_PROXY, params=tmp_dict)
                        send, sent = self.info_cutting(sent)
                        time.sleep(0.3)
                    tmp_dict = {'msg': sent, qq: self.qq}
                    self.req_post.post(self.qqbot_url2, proxies=BOT_PROXY, params=tmp_dict)
        except Exception as e:
            raise SendFailed('QQBot推送服务器错误', e)
            # self.qq_bot(s_level, message=message, acc_state=acc_state)

    def tg_bot(self, s_level, message='', acc_state='', img=None, img_title=''):
        # TG推送机器人 By:CyiceK
        # img传进来的是cv2格式
        try:
            # Markdown
            # To escape characters '_', '*', '`', '[' outside of an entity, prepend the characters '\' before them.
            message = message.replace('_', '\_').replace('*', '\*').replace('`', '\`').replace('[', '\[')
            acc_state = acc_state.replace('_', '\_').replace('*', '\*').replace('`', '\`').replace('[', '\[')
            img_title = img_title.replace('_', '\_').replace('*', '\*').replace('`', '\`').replace('[', '\[')

            if img is not None:

                img_delete = ''
                up_img = cv2.imencode('.jpg', img)[1].tobytes()

                # 方案一：imgbb
                img_h = {
                    "Connection": "keep-alive",
                    "Content-Type": "application/x-www-form-urlencoded",
                }
                base64_str = base64.b64encode(up_img)
                data = {
                    "key": '91ae4105b8d04d8ecf82238c234dbc2a',
                    "expiration": '60',
                    "image": base64_str,
                }
                r = self.req_post.post('https://api.imgbb.com/1/upload', data=data, headers=img_h).json()
                if r['status'] == 200:
                    data = r.get("data")
                    self.img_url = data["url"]
                    # img_delete = data["delete_url"]
                else:
                    # 方案二：sm.ms
                    f = {"smfile": up_img}
                    h = {
                        "Authorization": "cPNUy9taJaKvLFJwC4hwirT2c5XOxp9Q"
                    }
                    r = self.req_post.post('https://sm.ms/api/v2/upload', headers=h, files=f).json()
                    if r["code"] == "success":
                        data = r.get("data")
                        self.img_url = data["url"]
                        img_delete = data["delete"]
                    else:
                        pass
                img_h = {
                    "Connection": "keep-alive",
                    "Content-Type": "application/x-www-form-urlencoded",
                }
                tg_imginfo = {
                    'fun': 'sendPhoto',
                    'token': tg_token,
                    'caption': img_title,
                    'photo': self.img_url,
                    'disable_notification': tg_mute,
                }

                self.req_post.post('https://tgmessage-cyicek.vercel.app/api', headers=img_h, data=tg_imginfo)

                if img_delete != '':
                    time.sleep(0.8)
                    self.req_post.get(url=img_delete, proxies=BOT_PROXY, headers=h)
            else:
                tg_textinfo = {
                    'token': tg_token,
                    'message': f'*>>>公主连结农场脚本【{s_level}】<<<*\n'
                               f'欢迎您使用~\n'
                               f'*#### 当前系统运行信息 ####*\n- {self.cpu_info}\n- {self.memory_info}\n——————————————————\n'
                               f'目前农场信息：\n'
                               f'\n{message}\n'
                               f'目前状态信息：\n'
                               f'\n{acc_state}\n'
                               f'[来自GITHUB一款开源脚本 (// . //)](https://github.com/SimonShi1994/Princess-connection-farm)\n ',
                    'parse_mode': 'Markdown',
                    'disable_notification': tg_mute,
                }
                r = self.req_post.post('https://tgmessage-cyicek.vercel.app/api', proxies=BOT_PROXY, data=tg_textinfo)

        except Exception as e:
            pass
            # raise SendFailed('TG推送服务器错误', e)
            # time.sleep(600)
            # self.tg_bot(s_level, message=message, acc_state=acc_state, img=img, img_title=img_title)


class Qywx(Bot):
    """
        # Copy from:https://github.com/huangantai/QywxPython/blob/master/qywx.py
        # Author: huangantai
        # modify by CyiceK
        #-----------发送企业微信的消息格式------------
        #图片（image）:1MB，支持JPG,PNG格式
        #语音（voice）：2MB，播放长度不超过60s，支持AMR格式
        #视频（video）：10MB，支持MP4格式
        #普通文件（file）：20MB
        #--------------------------------
    """

    def __init__(self, s_level, acc_state):
        super().__init__()
        self.message = ''
        self.info_format = f"""*>>>公主连结农场脚本【{s_level}】<<<*\n
        欢迎您使用~\n
        *#### 当前系统运行信息 ####*\n
        - {self.cpu_info}\n- {self.memory_info}\n
        ——————————————————\n
        目前农场信息：\n\n{self.message}\n
        目前状态信息：\n\n{acc_state}\n
        [来自GITHUB一款开源脚本 (// . //)](https://github.com/SimonShi1994/Princess-connection-farm)\n"""

    def send_message(self, msg, msgtype):
        upload_token = self.get_upload_token(self.corpid, self.corpsecret)
        agid = self.coragid
        if msgtype == "text":
            self.message = msg
            data = self.msg_messages(self.info_format, agid, msgtype='text', msgid="content")
        elif msgtype == "image":
            media_id = self.net_get_media_ID(msg, upload_token, msgtype="image")
            data = self.msg_messages(media_id, agid, msgtype='image', msgid="media_id")
        elif msgtype == "voice":
            media_id = self.get_media_ID(msg, upload_token, msgtype="voice")
            data = self.msg_messages(media_id, agid, msgtype='voice', msgid="media_id")
        elif msgtype == "video":
            media_id = self.get_media_ID(msg, upload_token, msgtype="video")
            data = self.msg_messages(media_id, agid, msgtype='video', msgid="media_id")
        elif msgtype == "file":
            media_id = self.get_media_ID(msg, upload_token, msgtype="file")
            data = self.msg_messages(media_id, agid, msgtype='file', msgid="media_id")
        else:
            raise Exception("msgtype参数错误，参数只能是image或text或voice或video或file")
        url = "https://qyapi.weixin.qq.com"
        token = self.get_token(url, self.corpid, self.corpsecret)
        send_url = '%s/cgi-bin/message/send?access_token=%s' % (url, token)
        respone = urllib.request.urlopen(urllib.request.Request(url=send_url, data=data)).read()
        x = json.loads(respone.decode())['errcode']
        if x == 0:
            # TODO: Bot作为一个log的扩展插件，暂时无法接入log
            print("{} 发送成功".format(msg))
        else:
            raise SendFailed("{} 发送失败".format(msg))

    def send_msg_message(self, msg):
        try:
            self.send_message(msg, 'text')
        except Exception as e:
            pass

    def send_image_message(self, path):
        if path.endswith("jpg") == False and path.endswith("png") == False:
            raise Exception("图片只能为jpg或png格式")
        if os.path.getsize(path) > 1048576:
            raise Exception("图片大小不能超过1MB")
        try:
            self.send_message(path, 'image')
        except Exception as e:
            pass

    def send_voice_message(self, path):
        if path.endswith("amr") == False:
            raise Exception("语音文件只能为amr格式，并且不能大于2MB，不能超过60s")
        if os.path.getsize(path) > 2097152:
            raise Exception("语音文件大小不能超过2MB，并且不能超过60s，只能为amr格式")
        try:
            self.send_message(path, 'voice')
        except Exception as e:
            pass

    def send_video_message(self, path):
        if path.endswith("mp4") == False:
            raise Exception("视频文件只能为mp4格式，并且不能大于10MB")
        if os.path.getsize(path) > 10485760:
            raise Exception("视频文件大小不能超过10MB,只能为mp4格式")
        try:
            self.send_message(path, 'video')
        except Exception as e:
            pass

    def send_file_message(self, path):
        if os.path.getsize(path) > 20971520:
            raise Exception("文件大小不能超过20MB")
        try:
            self.send_message(path, 'file')
        except Exception as e:
            pass

    def get_token(self, url, corpid, corpsecret):
        token_url = '%s/cgi-bin/gettoken?corpid=%s&corpsecret=%s' % (url, corpid, corpsecret)
        token = json.loads(urllib.request.urlopen(token_url).read().decode())['access_token']
        return token

    def get_upload_token(self, corid, corsec):
        gurl = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}".format(corid, corsec)
        r = requests.get(gurl)
        dict_result = (r.json())
        return dict_result['access_token']

    def net_get_media_ID(self, media_bit, token, msgtype="image"):
        """上传资源到企业微信的存储上,msgtype有image,voice,video,file"""
        media_url = "https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={}&type={}".format(token,
                                                                                                      msgtype)
        files = {msgtype: media_bit}
        r = requests.post(media_url, files=files)
        re = json.loads(r.text)
        return re['media_id']

    def get_media_ID(self, path, token, msgtype="image"):
        """上传资源到企业微信的存储上,msgtype有image,voice,video,file"""
        media_url = "https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={}&type={}".format(token,
                                                                                                      msgtype)
        with open(path, 'rb') as f:
            files = {msgtype: f}
            r = requests.post(media_url, files=files)
            re = json.loads(r.text)
            return re['media_id']

    def msg_messages(self, msg, agid, msgtype='text', msgid="content"):
        """
            msgtype有text,image,voice,video,file；如果msgytpe为text,msgid为content，如果是其他，msgid为media_id。
            msg为消息的实际内容，如果是文本消息，则为字符串，如果是其他类型，则传递media_id的值。

            """
        values = {
            "touser": '@all',
            "msgtype": msgtype,
            "agentid": agid,
            msgtype: {msgid: msg},
            "safe": 0
        }
        msges = (bytes(json.dumps(values), 'utf-8'))
        return msges
