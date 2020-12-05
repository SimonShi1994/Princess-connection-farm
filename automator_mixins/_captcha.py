# coding=utf-8
import base64
import random
import time

import cv2
import requests
from requests.adapters import HTTPAdapter

from core.pcr_config import captcha_userstr, captcha_software_key, captcha_level
from core.log_handler import pcr_log
from core.safe_u2 import timeout


class CaptionSkip:
    """
    2020/11/24
    小型码验证码模块
    by：CyiceK
    """

    def __init__(self):
        self.host_result = ''
        self._count_times = 0
        self.img = None
        self.question_type = 0
        self.conversation = requests.Session()
        self.conversation.keep_alive = False
        self.conversation.mount('http://', HTTPAdapter(max_retries=3))
        self.conversation.mount('https://', HTTPAdapter(max_retries=3))
        self.img_post_url = 'http://' + self.host_result + '/UploadBase64.aspx'
        self.img_answer = 'http://' + self.host_result + '/GetAnswer.aspx'
        self.img_send_error = 'http://' + self.host_result + '/SendError.aspx'
        self.img_getpoint = 'http://' + self.host_result + '/GetPoint.aspx'
        self.error_feature = ['#', '', ' ']
        self.no_result = ["#答案不确定", "超时", "不扣分", "#"]
        self.img_hear_dict = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

    def get_host(self, num=0):
        try:
            while True:
                # 获取host
                time.sleep(random.uniform(0.10, 1.00))
                self.host_result = self.conversation.get(url="http://3.haoi23.net/svlist.html").text
                if self.host_result is not None:
                    self.host_result = str(self.host_result).replace("===", '').replace("+++", '')
                    self.host_result = self.host_result.split("--")

                if num == 1:
                    # 如果num为1，证明出现了Max retries exceeded with url，最大连接数错误，换下备用的
                    if self.conversation.get(('http://' + self.host_result[1])).status_code == 200:
                        self.host_result = self.host_result[1]
                        break
                    else:
                        continue

                # print(host_result)
                if self.conversation.get(('http://' + self.host_result[0]), timeout=(0.8, 0.5)).status_code == 200:
                    # print("host_result[0] 200")
                    self.host_result = self.host_result[0]
                    break
                elif self.conversation.get(('http://' + self.host_result[1]), timeout=(0.8, 0.5)).status_code == 200:
                    self.host_result = self.host_result[1]
                    # print("host_result[1] 200")
                    break
                else:
                    # print("无结果", host_result)
                    time.sleep(2)
                    continue
            self.img_post_url = 'http://' + self.host_result + '/UploadBase64.aspx'
            self.img_answer = 'http://' + self.host_result + '/GetAnswer.aspx'
            self.img_send_error = 'http://' + self.host_result + '/SendError.aspx'
            self.img_getpoint = 'http://' + self.host_result + '/GetPoint.aspx'
        except:
            time.sleep(2)
            return self.get_host(num=1)

    @timeout(60, "验证码验证超时：超过60秒")
    def skip_caption(self, captcha_img, question_type):

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

        print("!验证码识别模块开始运行!")
        self.get_host()

        # 发送图片
        # img = cv2.imread('yanzhengma.png')
        img = captcha_img
        b64_img = cv2.imencode('.png', img)[1].tobytes()  # 把ndarray转换成字符串
        b64_img = base64.b64encode(b64_img)

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
        caption_id = self.conversation.post(url=self.img_post_url, data=img_post, headers=self.img_hear_dict)
        print(">图片发送了……")
        if caption_id.text in self.error_feature:
            pcr_log('admin').write_log(level='error', message=caption_id.text)
        # print(caption_id.text)
        img_answer_get = {
            'id': caption_id,
            'r': random.randint(1000000000, 9999999999),
        }

        print(">>等待验证码识别返回值")
        while True:
            # 获取答案
            answer_result = self.conversation.get(url=self.img_answer, data=img_answer_get, headers=self.img_hear_dict)
            time.sleep(random.uniform(0.5, 2.88))
            self._count_times += 1
            count_len = len(answer_result.text)
            if answer_result.text not in self.error_feature:
                # print("开始处理")
                if count_len > 6:
                    # 466,365
                    answer_result = answer_result.text.split(',')
                    return answer_result, count_len, caption_id.text
                else:
                    # 废弃，无实际作用！

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

            elif answer_result.text in self.no_result or self._count_times >= 7:
                # 答案不确定(不扣分)
                print(">刷新验证码")
                # 刷新验证码
                answer_result = [162, 420]
                # answer_result = tmp_list.split(',')
                return answer_result, count_len, 0
            # print(answer_result, '', answer_result.text, '', _count_times)
            # 565,296
            # print("跳出")

    def getpoint(self):

        print("3s后发起查询题分！")
        time.sleep(3)

        self.get_host()

        if len(captcha_userstr) == 0 or len(captcha_software_key) == 0:
            return 0

        img_post = {
            'user': captcha_userstr,
            'r': random.randint(1000000000, 9999999999),
        }
        c = self.conversation.get(url=self.img_getpoint, data=img_post, headers=self.img_hear_dict)
        if int(c.text) > 0 and c.text not in self.error_feature:
            return int(c.text)
            # print("剩余题分：", int(c.text))

    def send_error(self, _id):

        self.get_host()

        if len(captcha_userstr) == 0 or len(captcha_software_key) == 0:
            return 0
        _send_error = {
            'id': _id,
            'r': random.randint(1000000000, 9999999999),
        }
        requests.get(url=self.img_send_error, data=_send_error, headers=self.img_hear_dict)
