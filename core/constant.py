from typing import Tuple, Optional


class PCRelement(tuple):
    """
    漂亮地显示一个PCR的元素
    除了正常的位置坐标，还携带图片和裁剪参数
    """

    def __init__(self, iterable, name: Optional[str] = None, img: Optional[str] = None,
                 at: Optional[Tuple[float, float, float, float]] = None, **kwargs):
        self.name = name
        self.img = img
        self.at = at
        for keys in kwargs:
            self.__setattr__(keys, kwargs[keys])

    def __new__(cls, iterable, *args, **kwargs):
        return super(PCRelement, cls).__new__(cls, iterable)

    def __repr__(self):
        s1 = super().__repr__()
        s2 = ""
        s3 = ""
        s4 = ""
        if self.name is not None:
            s2 = "  name= %s" % self.name
        if self.img is not None:
            s3 = "  img= %s" % self.img
        if self.at is not None:
            s4 = "  at = %s" % self.at.__str__()
        return "%s%s%s%s" % (s1, s2, s3, s4)


def p(*args, name=None, img=None, at=None):
    """
    快速创建一个PCRelement
    """
    return PCRelement(args, name=name, img=img, at=at)


MAIN_BTN = {
    "hanghui": p(693, 430, name="行会"),  # 行会按钮

}
HANGHUI_BTN = {
    "chengyuan": p(241, 350),  # 点击成员

}
MAX_MAP = 12
HARD_COORD = {
    1: {
        1: p(250, 340),
        2: p(465, 270),
        3: p(695, 325),
    },
    2: {
        1: p(286, 270),
        2: p(474, 370),
        3: p(730, 340),
    },
    3: {
        1: p(255, 260),
        2: p(470, 365),
        3: p(715, 280),
    },
    4: {
        1: p(250, 275),
        2: p(485, 240),
        3: p(765, 260),
    },
    5: {
        1: p(245, 325),
        2: p(450, 245),
        3: p(700, 270),
    },
    6: {
        1: p(265, 305),
        2: p(500, 310),
        3: p(715, 260),
    },
    7: {
        1: p(275, 245),
        2: p(475, 345),
        3: p(745, 290),
    },
    8: {
        1: p(215, 390),
        2: p(480, 355),
        3: p(715, 295),
    },
    9: {
        1: p(220, 270),
        2: p(480, 355),
        3: p(765, 295),
    },
    10: {
        1: p(220, 365),
        2: p(480, 250),
        3: p(765, 330),
    },
    11: {
        1: p(215, 360),
        2: p(480, 250),
        3: p(765, 330),
    },
    12: {
        1: p(215, 255),
        2: p(480, 355),
        3: p(765, 240),
    },
}

NORMAL_COORD = {
    7: {
        "right": {
            14: p(760, 240, name="7-14"),
            13: p(630, 257, name="7-13"),
            12: p(755, 350, name="7-12"),
            11: p(664, 410, name="7-11"),
            10: p(544, 400, name="7-10"),
            9: p(505, 300, name="7-9"),
            8: p(410, 240, name="7-8"),
        },
        "left": {
            7: p(625, 230, name="7-7"),
            6: p(680, 365, name="7-6"),
            5: p(585, 425, name="7-5"),
            4: p(500, 330, name="7-4"),
            3: p(450, 240, name="7-3"),
            2: p(353, 285, name="7-2"),
            1: p(275, 200, name="7-1"),
        },
    },
    8: {
        "right": {
            14: p(584, 260, name="8-14"),
            13: p(715, 319, name="8-13"),
            12: p(605, 398, name="8-12"),
            11: p(478, 374, name="8-11"),
            10: p(357, 405, name="8-10"),
            9: p(263, 324, name="8-9"),
            8: p(130, 352, name="8-8"),
        },
        "left": {
            7: p(580, 401, name="8-7"),
            6: p(546, 263, name="8-6"),
            5: p(457, 334, name="8-5"),
            4: p(388, 240, name="8-4"),
            3: p(336, 314, name="8-3"),
            2: p(230, 371, name="8-2"),
            1: p(193, 255, name="8-1"),
        },
    },
    10: {
        "right": {
            17: p(821, 299, name="10-17"),
            16: p(703, 328, name="10-16"),
            15: p(608, 391, name="10-15"),
            14: p(485, 373, name="10-14"),
            13: p(372, 281, name="10-13"),
            12: p(320, 421, name="10-12"),
            11: p(172, 378, name="10-11"),
            10: p(251, 235, name="10-10"),
            9: p(111, 274, name="10-9"),
        },
        "left": {
            8: p(690, 362, name="10-8"),
            7: p(594, 429, name="10-7"),
            6: p(411, 408, name="10-6"),
            5: p(518, 332, name="10-5"),
            4: p(603, 238, name="10-4"),
            3: p(430, 239, name="10-3"),
            2: p(287, 206, name="10-2"),
            1: p(146, 197, name="10-1"),
        },
    },
    11: {
        "right": {
            17: p(663, 408, name="11-17"),
            16: p(542, 338, name="11-16"),
            15: p(468, 429, name="11-15"),
            14: p(398, 312, name="11-14"),
            13: p(302, 428, name="11-13"),
            12: p(182, 362, name="11-12"),
            11: p(253, 237, name="11-11"),
            10: p(107, 247, name="11-10"),
        },
        "left": {
            9: p(648, 316, name="11-9"),
            8: p(594, 420, name="11-8"),
            7: p(400, 432, name="11-7"),
            6: p(497, 337, name="11-6"),
            5: p(558, 240, name="11-5"),
            4: p(424, 242, name="11-4"),
            3: p(290, 285, name="11-3"),
            2: p(244, 412, name="11-2"),
            1: p(161, 325, name="11-1"),
        },
    },
    12: {
        "right": {
            17: p(760, 255, name="12-17"),
            16: p(610, 245, name="12-16"),
            15: p(450, 270, name="12-15"),
            14: p(565, 415, name="12-14"),
            13: p(400, 425, name="12-13"),
            12: p(280, 365, name="12-12"),
            11: p(265, 245, name="12-11"),
            10: p(130, 265, name="12-10"),
        },
        "left": {
            9: p(675, 380, name="12-9"),
            8: p(550, 440, name="12-8"),
            7: p(445, 365, name="12-7"),
            6: p(575, 245, name="12-6"),
            5: p(435, 250, name="12-5"),
            4: p(310, 285, name="12-4"),
            3: p(265, 395, name="12-3"),
            2: p(155, 315, name="12-2"),
            1: p(185, 210, name="12-1"),
        },
    },

}

USER_DEFAULT_DICT = {
    # 给self.AR.get用的初值dict
    "run_status": {
        # 运行状态
        "finished": False,  # 是否运行完毕
        "current": "...",  # 当前执行的任务
        "error": None  # 报错情况
    }

}
# 显然后面还没写
# 等有空补全
# 准备写个GUI来快速标坐标
