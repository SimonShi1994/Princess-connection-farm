# coding=utf-8
import base64
import random
import time

import cv2
import requests

from core.pcr_config import captcha_userstr, captcha_software_key, captcha_level
from core.log_handler import pcr_log


def skip_caption(captcha_img, question_type):
    """
    2020/10/31
    关于验证码自动填写的独立出来一个py
    by:CyiceK
    :param question_type: 题型
    :param captcha_img:
    :return: answer_result[0], answer_result[1] = x,y
    """
    if len(captcha_userstr) == 0 or len(captcha_software_key) == 0:
        pcr_log('admin').write_log(level='error', message='接码-密码串为空！')
        return False

    if captcha_level == "小速":
        question_type = question_type.replace('T', 'X')
    elif captcha_level == "特速":
        question_type = question_type.replace('X', 'T')

    while True:
        # 获取host
        host_result = requests.get(url="http://3.haoi23.net/svlist.html").text
        if host_result is not None:
            host_result = str(host_result).replace("===", '').replace("+++", '')
            host_result = host_result.split("--")
            # print(host_result)
            break

    img_post_url = 'http://' + host_result[0] + '/UploadBase64.aspx'
    img_answer = 'http://' + host_result[0] + '/GetAnswer.aspx'
    # 发送图片
    # img = cv2.imread('yanzhengma.png')
    img = captcha_img
    b64_img = cv2.imencode('.png', img)[1].tobytes()  # 把ndarray转换成字符串
    b64_img = base64.b64encode(b64_img)
    img_hear_dict = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    img_post = {
        'userstr': captcha_userstr,
        'gameid': question_type,
        'timeout': 10,
        'rebate': captcha_software_key,
        'daiLi': 'haoi',
        'kou': 0,
        'ver': 'web2',
        'key': random.randint(1000000000, 9999999999),
        'Img': b64_img,
    }

    # print(img_post_url)
    # 题号
    caption_id = requests.post(url=img_post_url, data=img_post, headers=img_hear_dict)
    error_feature = ['#']
    if caption_id.text in error_feature:
        pcr_log('admin').write_log(level='error', message=caption_id.text)
    # print(caption_id.text)
    img_answer_get = {
        'id': caption_id,
        'r': random.randint(1000000000, 9999999999),
    }
    while True:
        # 获取答案
        error_feature = ['#', '']
        answer_result = requests.get(url=img_answer, data=img_answer_get, headers=img_hear_dict)
        time.sleep(2)
        count_len = len(answer_result.text)
        if answer_result.text not in error_feature:
            if count_len > 6:
                # 466,365
                answer_result = answer_result.text.split(',')
                return answer_result, count_len, caption_id.text
            else:
                # 多坐标处理
                answer_result = answer_result.text.split('|')
                if len(answer_result) >= 4:
                    tmp_list = []
                    # 多坐标处理
                    # 466,365|549,374|494,252|387,243
                    # 转元组
                    for i in range(0, count_len):
                        tmp = answer_result[i]
                        # print(tmp)
                        tmp_list.append(tuple(map(int, tmp.split(','))))
                        # [(466, 365), (549, 374), (494, 252), (387, 243)]
                        return tmp_list, count_len, caption_id.text
            # print(answer_result.text)565,296
            # print("跳出")


def getpoint():
    if len(captcha_userstr) == 0 or len(captcha_software_key) == 0:
        return 0
    while True:
        # 获取host
        host_result = requests.get(url="http://3.haoi23.net/svlist.html").text
        if host_result is not None:
            host_result = str(host_result).replace("===", '').replace("+++", '')
            host_result = host_result.split("--")
            # print(host_result)
            break
    img_getpoint = 'http://' + host_result[0] + '/GetPoint.aspx'
    img_post = {
        'user': captcha_userstr,
        'r': random.randint(1000000000, 9999999999),
    }
    img_hear_dict = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    c = requests.get(url=img_getpoint, data=img_post, headers=img_hear_dict)
    error_feature = ['#', '']
    if int(c.text) > 0 and c.text not in error_feature:
        return int(c.text)
        # print("剩余题分：", int(c.text))


def send_error(_id):
    if len(captcha_userstr) == 0 or len(captcha_software_key) == 0:
        return 0
    while True:
        # 获取host
        host_result = requests.get(url="http://3.haoi23.net/svlist.html").text
        if host_result is not None:
            host_result = str(host_result).replace("===", '').replace("+++", '')
            host_result = host_result.split("--")
            # print(host_result)
            break
    img_send_error = 'http://' + host_result[0] + '/SendError.aspx'
    _send_error = {
        'id': _id,
        'r': random.randint(1000000000, 9999999999),
    }
    img_hear_dict = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    requests.get(url=img_send_error, data=_send_error, headers=img_hear_dict)
