import datetime
import os
import random
import time

import cv2
import numpy as np
import pandas as pd
import requests
import xlrd
from xlutils.copy import copy

from core.constant import MAIN_BTN, PCRelement, ZHUCAIDAN_BTN
from core.constant import USER_DEFAULT_DICT as UDD
from core.cv import UIMatcher
from core.log_handler import pcr_log
from core.pcr_config import baidu_secretKey, baidu_apiKey, baidu_ocr_img, anticlockwise_rotation_times, lockimg_timeout, \
    ocr_mode, debug
from core.safe_u2 import timeout
from ._base import BaseMixin


class ToolsMixin(BaseMixin):
    """
    工具类插片
    包含一些辅助功能和辅助类脚本
    还有很多常用函数，比如回首页
    """

    @timeout(300, "lock_home执行超时：超过5分钟")
    def lock_home(self):
        """
        锁定首页
        要求场景：存在“我的主页”按钮
        逻辑：不断点击我的主页，直到右下角出现“礼物”
        """
        last = time.time()
        while True:
            sc = self.getscreen()
            num_of_white, _, x, y = UIMatcher.find_gaoliang(sc)
            if num_of_white < 77000:
                self.chulijiaocheng(None)  # 增加对教程的处理功能
                last = time.time()
            if self.is_exists(MAIN_BTN["liwu"], screen=sc):
                return
            self.click(MAIN_BTN["zhuye"])
            # 防卡公告
            self.click(1, 1)
            time.sleep(1.5)
            if time.time() - last > lockimg_timeout:
                raise Exception("lock_home时出错：超时！")

    @timeout(300, "init_home执行超时：超过5分钟")
    def init_home(self):
        # 2020-07-31 TheAutumnOfRice: 检查完毕
        while True:
            screen_shot_ = self.getscreen()
            if self.is_exists(MAIN_BTN["liwu"], screen=screen_shot_):
                break
            if self.is_exists(MAIN_BTN["tiaoguo"], screen=screen_shot_):
                self.click(893, 39, post_delay=0.5)  # 跳过
                continue
            if self.is_exists(MAIN_BTN["xzcw"], screen=screen_shot_):
                raise Exception("下载错误")
            if self.is_exists(MAIN_BTN["jingsaikaishi"], screen=screen_shot_):
                self.click(786, 308, post_delay=0.2)  # 选角色
                self.click(842, 491)  # 开始
                continue
            num_of_white, _, x, y = UIMatcher.find_gaoliang(screen_shot_)
            if num_of_white < 77000:
                break

            self.click(1, 1, post_delay=0.5)
            self.click(330, 270, post_delay=1)
            # 跳过特别庆典

        self.lock_home()
        time.sleep(0.5)
        # 这里防一波第二天可可萝跳脸教程
        screen_shot_ = self.getscreen()
        num_of_white, _, _, _ = UIMatcher.find_gaoliang(screen_shot_)
        if num_of_white < 50000:
            self.lock_img('img/renwu_1.bmp', elseclick=[(837, 433)], elsedelay=1)
            self.lock_home()
            return
        if UIMatcher.img_where(screen_shot_, 'img/kekeluo.bmp'):
            self.lock_img('img/renwu_1.bmp', elseclick=[(837, 433)], elsedelay=1)
            self.lock_home()
        time.sleep(1)
        self.lock_home()  # 追加检测

    def setting(self):
        self.lock_home()
        self.click_btn(MAIN_BTN["zhucaidan"], until_appear=MAIN_BTN["setting_pic"])
        self.click_btn(MAIN_BTN["setting_pic"])
        self.click(769, 87)
        time.sleep(1)
        self.click(735, 238)
        time.sleep(0.5)
        self.click(735, 375)
        time.sleep(0.5)
        self.click(479, 479)
        time.sleep(1)
        self.click(95, 516)
        self.lock_home()

    def maizhuangbei(self, day_interval):
        """
        卖掉数量前三的装备，（如果超过1000）
        适合小号
        :param day_interval: 日期间隔：每过day_interval天进行一次卖出
        """

        def get_last_record():
            ts = self.AR.get("time_status", UDD["time_status"])
            return ts["maizhuangbei"]

        def set_last_record():
            ts = self.AR.get("time_status", UDD["time_status"])
            ts["maizhuangbei"] = time.time()
            self.AR.set("time_status", ts)

        tm = get_last_record()
        diff = time.time() - tm
        if diff < day_interval * 3600 * 24:
            self.log.write_log("info", f"离下次卖装备还有{day_interval - int(diff / 3600 / 24)}天，跳过。")
            return
        self.lock_home()
        self.lock_img(ZHUCAIDAN_BTN["bangzhu"], elseclick=[(871, 513)])  # 锁定帮助
        self.click_btn(ZHUCAIDAN_BTN["daoju"], until_appear=ZHUCAIDAN_BTN["daojuyilan"])
        self.click_btn(ZHUCAIDAN_BTN["zhuangbei"], until_appear=ZHUCAIDAN_BTN["chushou"])
        if not self.is_exists(ZHUCAIDAN_BTN["chiyoushu"]):
            self.click(723, 32, post_delay=3)
            self.click(285, 228, post_delay=1)
            self.click(587, 377, post_delay=3)
        self.click_btn(ZHUCAIDAN_BTN["jiangxu"], until_appear=ZHUCAIDAN_BTN["jiangxu"])
        for _ in range(3):
            self.click_btn(ZHUCAIDAN_BTN["chushou"], until_appear=ZHUCAIDAN_BTN["chushouqueren"])
            self.click(645, 315, post_delay=2)  # max
            th_at = (518, 267, 530, 282)  # 千位
            img = self.getscreen()
            cut_img = UIMatcher.img_cut(img, th_at)
            if debug:
                print("VAR:", cut_img.var())
            if cut_img.var() > 1000:
                # 有千位，卖
                self.click_btn(ZHUCAIDAN_BTN["chushou2"], until_appear=ZHUCAIDAN_BTN["chushouwanbi"])
                for _ in range(5):
                    self.click(1, 1)
            else:
                break
        set_last_record()
        self.lock_home()

    def ocr_center(self, x1, y1, x2, y2, screen_shot=None, size=1.0):
        """
        :param size: 放大的大小
        :param x1: 左上坐标
        :param y1: 左上坐标
        :param x2: 右下坐标
        :param y2: 右下坐标
        :param screen_shot: 截图
        :return:
        """
        global ocr_text

        try:
            requests.get(url="http://127.0.0.1:5000/ocr/")
        except:
            pcr_log(self.account).write_log(level='error', message='无法连接到OCR,请尝试重新开启app.py')
            return -1

        if len(ocr_mode) == 0:
            return -1
        # OCR识别任务分配
        if ocr_mode == "智能":
            baidu_ocr_ping = requests.get(url="https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic")
            code = baidu_ocr_ping.status_code
            if code == 200:
                ocr_text = self.baidu_ocr(x1, y1, x2, y2, screen_shot=screen_shot, size=size)
                if ocr_text == -1:
                    ocr_text = self.ocr_local(x1, y1, x2, y2, screen_shot=screen_shot, size=size)
            else:
                ocr_text = self.ocr_local(x1, y1, x2, y2, screen_shot=screen_shot, size=size)
        elif ocr_mode == "网络":
            ocr_text = self.baidu_ocr(x1, y1, x2, y2, screen_shot=screen_shot, size=size)
        elif ocr_mode == "本地":
            ocr_text = self.ocr_local(x1, y1, x2, y2, screen_shot=screen_shot, size=size)
        elif ocr_mode == "混合":
            # 机器伪随机
            ocr_way = random.randint(1, 2)
            if ocr_way == 1:
                ocr_text = self.baidu_ocr(x1, y1, x2, y2, screen_shot=screen_shot, size=size)
            elif ocr_way == 2:
                ocr_text = self.ocr_local(x1, y1, x2, y2, screen_shot=screen_shot, size=size)

        # OCR返回的数据 纠错
        try:
            if ocr_text:
                return str(ocr_text)
            else:
                return -1
        except:
            raise Exception("ocr-error", "OCR识别错误。")

    def ocr_local(self, x1, y1, x2, y2, screen_shot=None, size=1.0):
        if screen_shot is None:
            screen_shot = self.getscreen()

        try:
            if screen_shot.shape[0] > screen_shot.shape[1]:
                if anticlockwise_rotation_times >= 1:
                    for _ in range(anticlockwise_rotation_times):
                        screen_shot = UIMatcher.AutoRotateClockWise90(screen_shot)
                screen_shot = UIMatcher.AutoRotateClockWise90(screen_shot)
            part = screen_shot[y1:y2, x1:x2]  # 对角线点坐标
            part = cv2.resize(part, None, fx=size, fy=size, interpolation=cv2.INTER_LINEAR)  # 利用resize调整图片大小
            img_binary = cv2.imencode('.png', part)[1].tobytes()
            files = {'file': ('tmp.png', img_binary, 'image/png')}
            local_ocr_text = requests.post(url="http://127.0.0.1:5000/ocr/local_ocr/", files=files)
            pcr_log(self.account).write_log(level='info', message='本地OCR识别结果：%s' % local_ocr_text.text)
            return local_ocr_text.text
        except Exception as ocr_error:
            pcr_log(self.account).write_log(level='error', message='本地OCR识别失败，原因：%s' % ocr_error)
            return -1

    # 对当前界面(x1,y1)->(x2,y2)的矩形内容进行OCR识别
    # 使用Baidu OCR接口
    def baidu_ocr(self, x1, y1, x2, y2, size=1.0, screen_shot=None):
        # size表示相对原图的放大/缩小倍率，1.0为原图大小，2.0表示放大两倍，0.5表示缩小两倍
        # 默认原图大小（1.0）
        if len(baidu_apiKey) == 0 or len(baidu_secretKey) == 0:
            pcr_log(self.account).write_log(level='error', message='读取SecretKey或apiKey失败！')
            return -1

        # 强制size为1.0，避免百度无法识图
        size = 1.0

        if screen_shot is None:
            screen_shot = self.getscreen()
        # from numpy import rot90
        # screen_shot_ = rot90(screen_shot_)  # 旋转90°
        if baidu_ocr_img:
            cv2.imwrite('baidu_ocr.bmp', screen_shot)
        if screen_shot.shape[0] > screen_shot.shape[1]:
            if anticlockwise_rotation_times >= 1:
                for _ in range(anticlockwise_rotation_times):
                    screen_shot = UIMatcher.AutoRotateClockWise90(screen_shot)
            screen_shot = UIMatcher.AutoRotateClockWise90(screen_shot)
            # cv2.imwrite('fuck_rot90_test.bmp', screen_shot_)
            # screen_shot_ = rot90(screen_shot_)  # 旋转90°
            pass
        part = screen_shot[y1:y2, x1:x2]  # 对角线点坐标
        part = cv2.resize(part, None, fx=size, fy=size, interpolation=cv2.INTER_LINEAR)  # 利用resize调整图片大小
        partbin = cv2.imencode('.jpg', part)[1]  # 转成base64编码（误）

        try:
            files = {'file': ('tmp.png', partbin, 'image/png')}
            result = requests.post(url="http://127.0.0.1:5000/ocr/baidu_ocr/", files=files)
            # 原生输出有助于开发者
            result = result.json().get('words_result')[0].get('words')
            return result
        except:
            pcr_log(self.account).write_log(level='error', message='百度云识别失败！请检查apikey和secretkey以及截图范围返回结果'
                                                                   '是否有误！')
            return -1

    def get_base_info(self, base_info=False, introduction_info=False, props_info=False, out_xls=False, s_sent=False,
                      acc_nature=0):
        """
        账号基本信息获取
        By:CyiceK
        有bug请反馈
        :param acc_nature: 小/大号
        :param s_sent: 是否发送到Server酱
        :param out_xls: 是否输出为Excel表格
        :param base_info: 是否读取主页面的基本信息
        :param introduction_info: 是否读取介绍的基本信息
        :param props_info: 是否读取道具的基本信息-扫荡券
        :return: acc_info_dict
        """
        # 笨方法转化时间戳"%Y-%m-%d-%H-%M-%S"
        date_start = datetime.datetime(1899, 12, 30)
        date_now = datetime.datetime.now()
        delta = date_now - date_start
        # 时间戳
        date_1900 = float(delta.days) + (float(delta.seconds) / 86400)
        # 日期
        date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        acc_info_dict = {
            "dengji": 'None',
            "jianjie_name": 'None',
            "tili": 'None',
            "mana": 'None',
            "baoshi": 'None',
            "jianjie_zhanli": 'None',
            "jianjie_hanghui": 'None',
            "jianjie_id": 'None',
            "zhanghao": self.account,
            "saodangquan": 'None',
            "date": date,
        }
        acc_info_list = []
        self.lock_home()
        try:
            if base_info:
                time.sleep(2)
                self.lock_home()
                screen_shot = self.getscreen()
                # 体力 包括/
                acc_info_dict["tili"] = self.ocr_center(243, 6, 305, 22, screen_shot=screen_shot, size=2.0) \
                    .replace('=', '').replace('-', '').replace('一', '').replace('_', '')
                # 等级
                acc_info_dict["dengji"] = self.ocr_center(29, 43, 60, 67, screen_shot=screen_shot, size=2.0)
                # mana
                acc_info_dict["mana"] = self.ocr_center(107, 54, 177, 76, screen_shot=screen_shot, size=2.0) \
                    .replace(',', '').replace('.', '')
                # 宝石
                acc_info_dict["baoshi"] = self.ocr_center(258, 52, 306, 72, screen_shot=screen_shot, size=2.0) \
                    .replace(',', '').replace('.', '')
            if introduction_info:
                self.lock_img(ZHUCAIDAN_BTN["bangzhu"], elseclick=[(871, 513)])  # 锁定帮助
                # 去简介
                self.lock_no_img(ZHUCAIDAN_BTN["jianjie"], elseclick=[(382, 268)])
                self.lock_img(ZHUCAIDAN_BTN["jianjie_L"], elseclick=[(382, 268)])  # 锁定简介
                screen_shot = self.getscreen()
                acc_info_dict["jianjie_name"] = self.ocr_center(607, 126, 880, 152, screen_shot=screen_shot, size=2.0)
                acc_info_dict["dengji"] = self.ocr_center(761, 163, 799, 182, screen_shot=screen_shot, size=2.0)
                acc_info_dict["jianjie_zhanli"] = self.ocr_center(703, 195, 801, 216, screen_shot=screen_shot, size=2.0)
                acc_info_dict["jianjie_hanghui"] = self.ocr_center(703, 230, 917, 248, screen_shot=screen_shot,
                                                                   size=2.0)
                acc_info_dict["jianjie_id"] = self.ocr_center(600, 415, 765, 435, screen_shot=screen_shot, size=1.2)
            if props_info:
                self.lock_img(ZHUCAIDAN_BTN["bangzhu"], elseclick=[(871, 513)])  # 锁定帮助
                # 去道具
                self.lock_no_img(ZHUCAIDAN_BTN["daoju"], elseclick=[(536, 159)])
                self.lock_img(ZHUCAIDAN_BTN["daojuyilan"], elseclick=[(536, 159)])  # 锁定道具一览
                screen_shot = self.getscreen()
                self.click_img(screen=screen_shot, img="img/zhucaidan/saodangquan.bmp")
                time.sleep(2)
                screen_shot = self.getscreen()
                acc_info_dict["saodangquan"] = self.ocr_center(627, 196, 713, 216, size=1.1, screen_shot=screen_shot) \
                    .replace('x', '').replace('.', '').replace('X', '')
            acc_info_list.append(acc_info_dict)
            self.lock_home()
            # 表格数据整理和转换
            if out_xls:
                # 将字典列表转换为DataFrame
                pf = pd.DataFrame(list(acc_info_list))
                # 指定字段顺序
                order = ['dengji', 'jianjie_name', 'tili', 'mana', 'baoshi', 'jianjie_zhanli',
                         'jianjie_hanghui', 'jianjie_id', 'zhanghao', 'saodangquan', 'date']
                pf = pf[order]
                # 将列名替换为中文
                columns_map = {
                    'dengji': '等级',
                    'jianjie_name': '名字',
                    'tili': '体力',
                    'mana': '玛娜数量',
                    'baoshi': '宝石数量',
                    'jianjie_zhanli': '全角色战力',
                    'jianjie_hanghui': '所属行会',
                    'jianjie_id': '玩家ID',
                    'zhanghao': '账号',
                    'saodangquan': '所拥有的扫荡券',
                    'date': '录入日期',
                }
                pf.rename(columns=columns_map, inplace=True)

                if acc_nature == 0:
                    # 小号/农场号输出格式
                    xls_path = 'xls/%s-pcr_farm_info.xls' % self.today_date
                elif acc_nature == 1:
                    # 大号统一文件格式
                    xls_path = 'xls/pcr_farm_info.xls'
                else:
                    # 乱输入就这样的格式
                    xls_path = 'xls/%s-pcr_farm_info.xls' % self.today_date

                # 指定生成的Excel表格名称
                file_path = pd.ExcelWriter(xls_path)
                # 将空的单元格替换为空字符
                pf.fillna('', inplace=True)
                # 判断文件是否存在
                if not os.path.exists(xls_path):
                    # 输出
                    pf.to_excel(file_path, encoding='utf-8', index=False)
                    # 保存表格
                    file_path.save()
                    return acc_info_dict
                # 多进程怎么加锁QAQ

                # 保存表格
                index = len(list(acc_info_list))  # 获取需要写入数据的行数
                workbook = xlrd.open_workbook(file_path)  # 打开表格
                sheets = workbook.sheet_names()  # 获取表格中的所有表格
                worksheet = workbook.sheet_by_name(sheets[0])  # 获取表格中所有表格中的的第一个表格
                rows_old = worksheet.nrows  # 获取表格中已存在的数据的行数
                new_workbook = copy(workbook)  # 将xlrd对象拷贝转化为xlwt对象
                new_worksheet = new_workbook.get_sheet(0)  # 获取转化后工作簿中的第一个表格
                for i in range(0, index):
                    for j in range(0, len(list(acc_info_list)[i])):
                        # 追加写入数据，注意是从i+rows_old行开始写入
                        new_worksheet.write(i + rows_old, j, list(acc_info_dict.values())[j])
                new_workbook.save(file_path)  # 保存表格

            if s_sent:
                pcr_log(self.account).server_bot('info', message='未完成')
        except Exception as e:
            print('get_base_info-出现异常：', e)
        finally:
            return acc_info_dict

    def get_tili(self):
        # 利用baiduOCR获取当前体力值（要保证当前界面有‘主菜单’选项）
        # API key存放在baiduocr.txt中
        # 格式：apiKey secretKey（中间以一个\t作为分隔符）
        # 返回值：一个int类型整数；如果读取失败返回-1

        self.click(871, 513)  # 主菜单
        while True:  # 锁定帮助
            screen_shot_ = self.getscreen()
            if UIMatcher.img_where(screen_shot_, 'img/zhucaidan/bangzhu.bmp'):
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
        self.lock_img('img/zhucaidan/bangzhu.bmp', ifclick=[(370, 270)])  # 锁定帮助 点击简介
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
        self.lock_img('img/zhucaidan/bangzhu.bmp', elseclick=[(32, 32)])  # 锁定帮助
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

