import random
import time

import cv2
import numpy as np

from core.constant import MAIN_BTN, PCRelement
from core.cv import UIMatcher
from core.log_handler import pcr_log
# 临时，等待config的创建
from pcr_config import baidu_secretKey, baidu_apiKey, baidu_ocr_img, anticlockwise_rotation_times
from ._base import BaseMixin


class ToolsMixin(BaseMixin):
    """
    工具类插片
    包含一些辅助功能和辅助类脚本
    还有很多常用函数，比如回首页
    """

    def lock_home(self):
        """
        锁定首页
        要求场景：存在“我的主页”按钮
        逻辑：不断点击我的主页，直到右下角出现“礼物”
        """
        self.lock_img(MAIN_BTN["liwu"], elseclick=MAIN_BTN["zhuye"], elsedelay=2)  # 回首页

    def setting(self):
        self.click(875, 517)
        time.sleep(2)
        self.click(149, 269)
        time.sleep(2)
        self.click(769, 87)
        time.sleep(1)
        self.click(735, 238)
        time.sleep(0.5)
        self.click(735, 375)
        time.sleep(0.5)
        self.click(479, 479)
        time.sleep(1)
        self.click(95, 516)

        # 对当前界面(x1,y1)->(x2,y2)的矩形内容进行OCR识别
        # 使用Baidu OCR接口
        # 离线接口还没写

    def baidu_ocr(self, x1, y1, x2, y2, size=1.0):
        # size表示相对原图的放大/缩小倍率，1.0为原图大小，2.0表示放大两倍，0.5表示缩小两倍
        # 默认原图大小（1.0）
        from aip import AipOcr
        # print('初始化百度OCR识别')
        # with open('baiduocr.txt', 'r') as faip:
        #     fconfig = faip.read()
        # apiKey, secretKey = fconfig.split('\t')
        if len(baidu_apiKey) == 0 or len(baidu_secretKey) == 0:
            pcr_log(self.account).write_log(level='error', message='读取SecretKey或apiKey失败！')
            return -1
        config = {
            'appId': 'PCR',
            'apiKey': baidu_apiKey,
            'secretKey': baidu_secretKey
        }
        # f百度
        time.sleep(random.uniform(0.8, 1.8))
        client = AipOcr(**config)

        screen_shot_ = self.d.screenshot(format='opencv')
        # from numpy import rot90
        # screen_shot_ = rot90(screen_shot_)  # 旋转90°
        if baidu_ocr_img:
            cv2.imwrite('baidu_ocr.bmp', screen_shot_)
        if screen_shot_.shape[0] > screen_shot_.shape[1]:
            if anticlockwise_rotation_times >= 1:
                for _ in range(anticlockwise_rotation_times):
                    screen_shot_ = UIMatcher.AutoRotateClockWise90(screen_shot_)
            screen_shot_ = UIMatcher.AutoRotateClockWise90(screen_shot_)
            # cv2.imwrite('fuck_rot90_test.bmp', screen_shot_)
            # screen_shot_ = rot90(screen_shot_)  # 旋转90°
            pass
        # cv2.imwrite('test.bmp', screen_shot_)
        part = screen_shot_[y1:y2, x1:x2]  # 对角线点坐标
        # cv2.imwrite('test.bmp', part)
        part = cv2.resize(part, None, fx=size, fy=size, interpolation=cv2.INTER_LINEAR)  # 利用resize调整图片大小
        # cv2.imwrite('test2.bmp', part)
        # cv2.imshow('part',part)
        # cv2.waitKey(0)
        partbin = cv2.imencode('.jpg', part)[1]  # 转成base64编码（误）
        try:
            # print('识别成功！')
            # f百度
            time.sleep(random.uniform(0.8, 1.8))
            result = client.basicGeneral(partbin)
            # result = requests.post(request_url, data=params, headers=headers)
            return result
        except:
            pcr_log(self.account).write_log(level='error', message='百度云识别失败！请检查apikey和secretkey是否有误！')
            return -1

    def get_tili(self):
        # 利用baiduOCR获取当前体力值（要保证当前界面有‘主菜单’选项）
        # API key存放在baiduocr.txt中
        # 格式：apiKey secretKey（中间以一个\t作为分隔符）
        # 返回值：一个int类型整数；如果读取失败返回-1

        self.click(871, 513)  # 主菜单
        while True:  # 锁定帮助
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/bangzhu.jpg'):
                break
        # cv2.imwrite('all.png',screen_shot_)
        # part = screen_shot_[526:649, 494:524]
        ret = self.baidu_ocr(494, 526, 524, 649, 1)  # 获取体力区域的ocr结果
        if ret == -1:
            print('体力识别失败！')
            return -1
        else:
            return int(ret['words_result'][1]['words'].split('/')[0])

    def rename(self, name):  # 重命名
        self.click(871, 513)  # 主菜单
        self.lock_img('img/bangzhu.bmp', ifclick=[(370, 270)])  # 锁定帮助 点击简介
        self.lock_img('img/bianji.bmp', ifclick=[(900, 140)])  # 锁定 点击铅笔修改按钮
        self.lock_img('img/biangeng.bmp', ifclick=[(480, 270)])  # 锁定 玩家名 点击游戏渲染编辑框
        time.sleep(1)
        self.click(290, 425)  # 点击编辑框
        self.d.clear_text()
        self.d.send_keys(name)
        self.click(880, 425)  # 点击确定
        time.sleep(0.5)
        self.click(590, 370)  # 变更按钮
        time.sleep(1)
        self.lock_img('img/bangzhu.bmp', elseclick=[(32, 32)])  # 锁定帮助
        pcr_log(self.account).write_log(level='info', message='账号：%s已修改名字' % name)

    def get_bar(self, bar: PCRelement, screen=None):
        """
        进度条类百分比获取
        :param bar: 含有at,fc,bc元素的PCRelement
            其中,at为截取进度条，fc为进度条【横向中线】前景色，bc为进度条【横向中线】背景色
        :param screen: 设置为None，重新截屏
        :return: 百分比0~1
        """
        if screen is None:
            screen = self.getscreen()
        at, fc, bc = bar.at, bar.fc, bar.bc
        x1, y1, x2, y2 = at
        ym = int((y1 + y2) / 2)  # 只取中之条
        mid_line = UIMatcher.img_cut(screen, (x1, ym, x2, ym))
        # R,G,B -> B G R
        fc = np.array([fc[2], fc[1], fc[0]])
        bc = np.array([bc[2], bc[1], bc[0]])
        tf = np.sqrt(((mid_line - fc) ** 2).sum(axis=2)).ravel()
        tb = np.sqrt(((mid_line - bc) ** 2).sum(axis=2)).ravel()
        t = tf < tb
        left = 0
        right = len(t) - 1
        for ind in range(len(t)):
            if t[ind]:
                left = ind
                break
        for ind in range(len(t) - 1, -1, -1):
            if not t[ind]:
                right = ind
                break
        t = t[left:right + 1]
        return t.sum() / len(t)
