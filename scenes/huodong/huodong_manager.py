from scenes.huodong.huodong_base import HuodongMapBase


def get_huodong_by_code(code: str):
    HUODONG_CODE = {
        "current": Map20220531,
        "20220531": Map20220531,
        "20220518": Map20220518,
        "20220430": Map20220430,
        "20220415": Map20220415,
        "20220331": Map20220331,
        "20220208": Map20220208,
    }
    if code in HUODONG_CODE:
        return HUODONG_CODE[code]
    else:
        raise ValueError(f"没有编号为{code}的活动，请检查scenes/huodng/huodong_manager.py！")


'''
TYPE: 活动图类型
    0： 普通，最常见，1-15在同一页
    1： 特殊，1-15分两页，横向分布

NMAP： Normal在图1的最后关卡
XY11： 第一图的第一个坐标
XY21： 第二图的第一个坐标
    ...
'''


class Map20220531(HuodongMapBase):
    NAME = "不可思议之国的璃乃 小小爱丽丝与希望的绘本"
    XY11 = (165, 277)
    # XY_VH_BOSS = (543, 206)
    HARD_COORD = {
        1: (264, 220),
        2: (472, 371),
        3: (709, 342),
        4: (946, 183),
        5: (358, 263),
    }
    N_slice = 1
    N1 = 15


class Map20220518(HuodongMapBase):
    NAME = "将军道中记 白翼的武士"
    XY11 = (184, 296)
    XY_VH_BOSS = (861, 216)
    HARD_COORD = {
        1: (88, 371),
        2: (218, 232),
        3: (333, 275),
        4: (439, 392),
        5: (671, 334),
    }
    N_slice = 1
    N1 = 15


class Map20220430(HuodongMapBase):
    NAME = "牧场里的四农士 贫穷农场奋斗记"
    XY11 = (330, 191)
    XY21 = (134, 249)
    XY31 = (247, 284)
    XY_VH_BOSS = (837, 278)
    HARD_COORD = {
        1: (233, 193),
        2: (344, 272),
        3: (191, 363),
        4: (429, 400),
        5: (653, 322),
    }
    N_slice = 3
    N1 = 5
    N2 = 12
    N3 = 15


class Map20220415(HuodongMapBase):
    NAME = "盛开在阿斯特莱亚的双轮之花复刻"
    XY11 = (152, 398)
    XY21 = (104, 382)
    XY_VH_BOSS = (647, 183)
    HARD_COORD = {
        1: (74, 400),
        2: (249, 380),
        3: (409, 313),
        4: (533, 384),
        5: (750, 332),
    }
    N_slice = 2
    N1 = 11


class Map20220331(HuodongMapBase):
    NAME = "恩赐的财团与神圣学院的问题儿童"
    XY11 = (123, 230)
    XY_VH_BOSS = (864, 288)
    HARD_COORD = {
        1: (115, 346),
        2: (258, 233),
        3: (351, 379),
        4: (547, 324),
        5: (684, 230),
    }


class Map20220208(HuodongMapBase):
    NAME = "星光公主Re:M@STER"
    XY11 = (120, 240)
    XY_VH_BOSS = (851, 268)
    HARD_COORD = {
        1: (104, 255),
        2: (216, 398),
        3: (407, 365),
        4: (545, 264),
        5: (673, 319),
    }


