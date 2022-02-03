# import matplotlib.pylab as plt
import os
import pathlib

import cv2
import numpy as np

from core import log_handler
from core.pcr_config import debug, use_template_cache


def cv_imread(file_path):  # 用于中文目录的imread函数
    """
    项目地址:https://github.com/bbpp222006/Princess-connection
    作者：bbpp222006
    协议：MIT License
    """
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return cv_img


class UIMatcher:
    # log
    _log = log_handler.pcr_log("cv")

    # template 缓存
    template_cache = dict()

    @staticmethod
    def RotateClockWise90(img):
        """
        项目地址:https://github.com/bbpp222006/Princess-connection
        作者：bbpp222006
        协议：MIT License
        """
        trans_img = cv2.transpose(img)
        new_img = cv2.flip(trans_img, 0)
        return new_img

    @staticmethod
    def AutoRotateClockWise90(img):
        if img.shape[0] > img.shape[1]:
            return UIMatcher.RotateClockWise90(img)
        else:
            return img

    @staticmethod
    def findpic(screen, template_paths=None):
        """
        项目地址:https://github.com/bbpp222006/Princess-connection
        作者：bbpp222006
        协议：MIT License

        # 返回相对坐标
        # 已使用img_where代替
        检测各种按钮(头像?)
        @return: 中心坐标lists, 对应的可信度list
        """
        if template_paths is None:
            template_paths = ['img/juqing/tiaoguo_2.bmp']
        zhongxings = []
        max_vals = []
        # 增加判断screen方向
        if screen.shape[0] > screen.shape[1]:
            screen = UIMatcher.RotateClockWise90(screen)
        screen_show = screen.copy()
        # screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        # plt.imshow(screen)
        # plt.show()
        for template_path in template_paths:
            # template = cv_imread(template_path)#用于中文目录
            template = cv2.imread(template_path)
            # template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)cv_imread
            h, w = template.shape[:2]  # rows->h, cols->w
            res = UIMatcher.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            x = (max_loc[0] + w // 2) / screen.shape[1]
            y = (max_loc[1] + h // 2) / screen.shape[0]
            zhongxings.append([x, y])
            max_vals.append(max_val)
            if max_val > 0.8:
                cv2.rectangle(screen_show, (int(max_loc[0]), int(max_loc[1])),
                              (int(max_loc[0] + w), int(max_loc[1] + h)), (0, 0, 255), 2)
                cv2.putText(screen_show, str(round(max_val, 3)) + os.path.basename(template_path),
                            (int(max_loc[0]), int(max_loc[1]) - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
        # cv2.rectangle(screen, (0, 0), (10, 10), (0, 0, 255), 2)
        # plt.cla()
        # img4 = cv2.cvtColor(screen_show, cv2.COLOR_BGR2RGB)
        # plt.imshow(img4)
        # plt.pause(0.01)
        # if max_val>yuzhi:
        #     match_flag = 1
        # else:
        #     match_flag = 0
        # ax.hist(res.reshape(-1,1), 100, facecolor='b', alpha=0.5, label="rand_mat")
        # plt.show()
        return zhongxings, max_vals

    @staticmethod
    def matchTemplate(screen, template, method):
        """
        为了使用sq这个1-SQDIRR_NORMED，没办法再封装一层吧。
        之后可以开发更多match映射方法。
        """
        if method == "sq":
            ans = cv2.matchTemplate(screen, template, cv2.TM_SQDIFF_NORMED)
            ans = 1 - ans
            return ans
        else:
            ans = cv2.matchTemplate(screen, template, method)
            return ans

    @classmethod
    def img_prob(cls, screen, template_path, at=None, method=cv2.TM_CCOEFF_NORMED) -> float:
        """
        在screen里寻找template，若找到多个，则返回第一个的匹配度。
        :param screen:  截图图片
        :param template_path: 文件路径
        :param at:  缩小查找范围
        :return: 匹配度
        """
        if screen.shape[0] > screen.shape[1]:
            screen = UIMatcher.RotateClockWise90(screen)
        if at is not None:
            try:
                x1, y1, x2, y2 = at
                screen = screen[y1:y2 + 1, x1:x2 + 1]
            except:
                cls._log.write_log(level='debug', message="检测区域填写错误")
                exit(-1)
        if screen.mean() < 1:  # 纯黑色与任何图相关度为1
            return 0
        template = cls._get_template(template_path)
        prob = UIMatcher.matchTemplate(screen, template, method).max()
        return prob

    @classmethod
    def _get_template(cls, template_path):
        if isinstance(template_path, np.ndarray):
            return template_path
        if not use_template_cache or template_path not in cls.template_cache:
            template = cv2.imread(template_path)
            cls.template_cache[template_path] = template
        else:
            template = cls.template_cache[template_path]
        return template

    @staticmethod
    def img_cut(screen, at):
        try:
            x1, y1, x2, y2 = at
            screen = screen[y1:y2 + 1, x1:x2 + 1]
        except:
            UIMatcher._log.write_log(level='error', message="检测区域填写错误")
            exit(-1)
        return screen

    @classmethod
    def img_all_where(cls, screen, template_path, threshold=0.84, at=None, method=cv2.TM_CCOEFF_NORMED):
        """
        找全部匹配图
        """
        if isinstance(screen, str):
            screen = cv2.imread(screen)
        screen = cls.AutoRotateClockWise90(screen)
        template = cls._get_template(template_path)
        th, tw = template.shape[:2]  # rows->h, cols->w
        if at is not None:
            x1, y1, x2, y2 = at
        else:
            x1, y1, x2, y2 = 0, 0, 959, 539
        screen = cls.img_cut(screen, (x1, y1, x2, y2))
        res = UIMatcher.matchTemplate(screen, template, method)
        l = []
        for i in range(res.shape[0]):
            for j in range(res.shape[1]):
                if res[i, j] >= threshold:
                    _x = x1 + j + tw // 2
                    _y = y1 + i + th // 2
                    _at = (x1 + j, y1 + i, x1 + j + tw - 1, y1 + i + th - 1)
                    l += [_x, _y, _at]
                    if debug:
                        cls._log.write_log('debug',
                                           f"p({_x},{_y},img={template_path},at={_at}), \nCCOEFF={res[i, j]}")
        return l

    @classmethod
    def img_all_prob(cls, screen, template_path, threshold=0.84, at=None, method=cv2.TM_CCOEFF_NORMED):
        """
        找全部匹配和概率，返回一个列表[(prob,x,y,(at))]
        """
        if isinstance(screen, str):
            screen = cv2.imread(screen)
        screen = cls.AutoRotateClockWise90(screen)
        template = cls._get_template(template_path)
        th, tw = template.shape[:2]  # rows->h, cols->w
        if at is not None:
            x1, y1, x2, y2 = at
        else:
            x1, y1, x2, y2 = 0, 0, 959, 539
        screen = cls.img_cut(screen, (x1, y1, x2, y2))
        res = UIMatcher.matchTemplate(screen, template, method)
        l = []
        for i in range(res.shape[0]):
            for j in range(res.shape[1]):
                if res[i, j] >= threshold:
                    _x = x1 + j + tw // 2
                    _y = y1 + i + th // 2
                    _at = (x1 + j, y1 + i, x1 + j + tw - 1, y1 + i + th - 1)
                    l += [(res[i, j], _x, _y, _at)]
                    if debug:
                        cls._log.write_log('debug',
                                           f"p({_x},{_y},img={template_path if type(template_path) is str else '...'},at={_at}), \nCCOEFF={res[i, j]}")
        return sorted(l, reverse=True)

    @staticmethod
    def filter_edge(img, output3D=True, **cannykwargs):
        """
        边缘检测
        :param img:  输入图片
        :param output3D: 设置为True，则对RGB分别边缘检测，输出RGB图；否则输出灰度图
        :param cannykwargs: cv2.Canny的参数
        :return: 边缘图片
        """
        cannykwargs.setdefault("threshold1", 100)
        cannykwargs.setdefault("threshold2", 200)
        if output3D:
            edges = np.stack([cv2.Canny(img[:, :, i], **cannykwargs) for i in range(3)], axis=-1)
        else:
            edges = cv2.Canny(img, **cannykwargs)
        return edges

    @classmethod
    def img_where(cls, screen, template_path, threshold=0.84, at=None, method=cv2.TM_CCOEFF_NORMED,
                  is_black=False, black_threshold=1500):
        """
        在screen里寻找template，若找到则返回坐标，若没找到则返回False
        注：可以使用if img_where():  来判断图片是否存在
        :param black_threshold: 判断暗点的阈值
        :param is_black: 是否判断为暗色图片（多用于检测点击按钮后颜色变暗）
        :param method:
        :param threshold:
        :param screen:
        :param template_path:
        :param at: 缩小查找范围
        :return:
        """
        if isinstance(screen, str):
            screen = cv2.imread(screen)
        if screen.shape[0] > screen.shape[1]:
            screen = UIMatcher.RotateClockWise90(screen)
        if at is not None:
            try:
                x1, y1, x2, y2 = at
                screen = screen[y1:y2 + 1, x1:x2 + 1]
            except:
                cls._log.write_log(level='error', message="检测区域填写错误")
                exit(-1)
        else:
            x1, y1 = 0, 0

        # 缓存未命中时从源文件读取
        template = cls._get_template(template_path)

        # 全黑直接返回False
        _, black_num, _, _ = cls.find_gaoliang(screen)
        if black_num >= 518400:
            return False

        th, tw = template.shape[:2]  # rows->h, cols->w
        res = UIMatcher.matchTemplate(screen, template, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val >= threshold:

            # 暗点判断
            if is_black:
                _, black_num, _, _ = cls.find_gaoliang(screen)
                # print("暗点:", black_num, "-img:", template_path)
                if debug:
                    cls._log.write_log('debug', f"暗点:{black_num} -img:{template_path}")
                if black_num > black_threshold:
                    return True
                else:
                    return False

            x = x1 + max_loc[0] + tw // 2
            y = y1 + max_loc[1] + th // 2
            if debug:
                cls._log.write_log('debug', "{}--{}--({},{})".format(template_path, round(max_val, 3), x, y))
                # cls._log.write_log(level='debug',
                #                    message="{}--{}--({},{})".format(template_path, round(max_val, 3)
                #                                                     , x, y))
                pass
                if at is None:
                    cls._log.write_log('debug', "{}  at=({}, {}, {}, {})".format(template_path, x1 + max_loc[0],
                                                                                 y1 + max_loc[1],
                                                                                 x1 + max_loc[0] + tw,
                                                                                 y1 + max_loc[1] + th))
                    # cls._log.write_log(level='debug',
                    #                    message="{}  at=({}, {}, {}, {})".format(template_path, x1 + max_loc[0],
                    #                                                             y1 + max_loc[1],
                    #                                                             x1 + max_loc[0] + tw,
                    #                                                             y1 + max_loc[1] + th))
            return x, y
        else:
            if debug:
                cls._log.write_log('debug', "{}--{}".format(template_path, round(max_val, 3)))
                # cls._log.write_log(level='debug',
                #                            message="{}--{}".format(template_path, round(max_val, 3)))
            return False

    @staticmethod
    def imgs_where(screen, template_paths, threshold=0.84, at=None, method=cv2.TM_CCOEFF_NORMED):
        """
        依次检测template_paths中模板是否存在，返回存在图片字典
        :param screen:
        :param template_paths:
        :param threshold:
        :return:
        """
        return_dic = {}
        for template_path in template_paths:
            pos = UIMatcher.img_where(screen, template_path, threshold, at, method)
            if pos:
                return_dic[template_path] = pos
        return return_dic

    @staticmethod
    def find_gaoliang(screen):
        """
        项目地址:https://github.com/bbpp222006/Princess-connection
        作者：bbpp222006
        协议：MIT License

        检测高亮位置(忽略了上板边,防止成就栏弹出遮挡)
        @return: 高亮中心相对坐标[x,y]
        """
        if screen.shape[0] > screen.shape[1]:
            screen = UIMatcher.RotateClockWise90(screen)
        gray = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
        ret, binary = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)
        num_of_white = len(np.argwhere(binary == 255))
        # GPL 3.0
        num_of_black = len(np.argwhere(binary == 0))
        #
        index_1 = np.mean(np.argwhere(binary[63:, :] == 255), axis=0).astype(int)

        screen = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)
        cv2.circle(screen, (index_1[1], index_1[0] + 63), 10, (255, 0, 0), -1)

        # plt.cla()
        # plt.imshow(screen)
        # plt.pause(0.01)
        # print('亮点个数:', len(np.argwhere(binary == 255)), '暗点个数:', len(np.argwhere(binary == 0)))
        return num_of_white, num_of_black, index_1[1] / screen.shape[1], (index_1[0] + 63) / screen.shape[0]

    @classmethod
    def img_similar(cls, screen_short, threshold=0.84, at=None, method=cv2.TM_CCOEFF_NORMED):
        """
        和上次截图匹配相似度
        :param threshold:
        :param screen_short:
        :param at: 缩小查找范围
        :return:
        """
        if screen_short.shape[0] > screen_short.shape[1]:
            screen_short = UIMatcher.RotateClockWise90(screen_short)
        if at is not None:
            try:
                x1, y1, x2, y2 = at
                screen_short = screen_short[y1:y2, x1:x2]
            except:
                cls._log.write_log(level='debug', message="检测区域填写错误")
                exit(-1)
        else:
            x1, y1 = 0, 0
        if cls.screen_short_befor is None:
            cls.screen_short_befor = screen_short
            # print('填空')
        th, tw = screen_short.shape[:2]  # rows->h, cols->w
        res = UIMatcher.matchTemplate(cls.screen_short_befor, screen_short, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # print(max_val)
        if max_val >= threshold:
            x = x1 + max_loc[0] + tw // 2
            y = y1 + max_loc[1] + th // 2
        cls.screen_short_befor = screen_short
        # print(round(max_val, 3))
        return round(max_val, 3)

    @classmethod
    def pic_compare_with_filename(cls, pic, dir):
        """
        text为OCR后的某个值，但是它可能不对。
        则比对dir路径下所有.bmp的图片文件
        如果出现与pic相同的
        那么就返回它的文件名。
        :param dir:
        :return:
        """
        if not os.path.isdir(dir):
            os.makedirs(dir)
        cur = pathlib.Path(dir)
        for item in cur.iterdir():
            if item.suffix == ".bmp":
                prob = cls.img_prob(pic, item)
                if prob > 0.98:
                    return item.stem
        return None


class PreProcesses:
    def __init__(self):
        self.pp = []

    def edge(self, **kwargs):
        self.pp.append(lambda img: UIMatcher.filter_edge(img, **kwargs))
        return self

    def sharpening(self, img):
        # 锐化处理，对文字可能伤害较大
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32)  # 锐化
        part = cv2.filter2D(img, -1, kernel=kernel)
        # part = cv2.GaussianBlur(part, (3, 3), 1)  # 高斯滤波
        return part

    def gussian_blur(self, img):
        # 高斯滤波，处理噪点
        part = cv2.GaussianBlur(img, (3, 3), 1)  # 高斯滤波
        return part

    def __call__(self, img):
        if len(self.pp) > 0:
            img = UIMatcher._get_template(img)
        for p in self.pp:
            img = p(img)
        return img

#
# d = u2.connect()
# screen = d.screenshot(format="opencv")
# # screen = cv_imread('test.jpg')
# UIMatcher.find_gaoliang(screen)
# plt.show()
