from scenes.huodong.huodong_base import HuodongMapBase


def get_huodong_by_code(code: str):
    HUODONG_CODE = {
        "current": Map20220331,
        "20220331": Map20220331,
        "20220208": Map20220208,
    }
    if code in HUODONG_CODE:
        return HUODONG_CODE[code]
    else:
        raise ValueError(f"没有编号为{code}的活动，请检查scenes/huodng/huodong_manager.py！")


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


