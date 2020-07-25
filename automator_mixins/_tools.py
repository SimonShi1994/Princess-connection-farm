import time

import cv2
from PIL import Image

from core.cv import UIMatcher
from core.log_handler import pcr_log
from ._base import BaseMixin

# 临时，等待config的创建
from pcr_config import baidu_secretKey, baidu_apiKey


class ToolsMixin(BaseMixin):
    """
    工具类插片
    包含一些辅助功能和辅助类脚本
    """

    def setting(self):
        self.d.click(875, 517)
        time.sleep(2)
        self.d.click(149, 269)
        time.sleep(2)
        self.d.click(769, 87)
        time.sleep(1)
        self.d.click(735, 238)
        time.sleep(0.5)
        self.d.click(735, 375)
        time.sleep(0.5)
        self.d.click(479, 479)
        time.sleep(1)
        self.d.click(95, 516)

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
        client = AipOcr(**config)

        screen_shot_ = self.d.screenshot(format="opencv")
        if screen_shot_.shape[0] > screen_shot_.shape[1]:
            screen_shot_ = UIMatcher.RotateClockWise90(screen_shot_)
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

        self.d.click(871, 513)  # 主菜单
        while True:  # 锁定帮助
            screen_shot_ = self.d.screenshot(format="opencv")
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
        self.d.click(871, 513)  # 主菜单
        self.lockimg('img/bangzhu.bmp', ifclick=[(370, 270)])  # 锁定帮助 点击简介
        self.lockimg('img/bianji.bmp', ifclick=[(900, 140)])  # 锁定 点击铅笔修改按钮
        self.lockimg('img/biangeng.bmp', ifclick=[(480, 270)])  # 锁定 玩家名 点击游戏渲染编辑框
        time.sleep(1)
        self.d.click(290, 425)  # 点击编辑框
        self.d.clear_text()
        self.d.send_keys(name)
        self.d.click(880, 425)  # 点击确定
        time.sleep(0.5)
        self.d.click(590, 370)  # 变更按钮
        time.sleep(1)
        self.lockimg('img/bangzhu.bmp', elseclick=[(32, 32)])  # 锁定帮助
        pcr_log(self.account).write_log(level='info', message='账号：%s已修改名字' % name)
