import datetime
from scenes.waizhuan.wz_base import WZ_Menu, WZ_MapBase

'''
NMAP： Normal在图1的最后关卡
XY11： 第一图的第一个坐标
XY21： 第二图的第一个坐标
N_slice： Normal图切了几段
N1： Normal图如果分段，第1段最后一图的图号
    ...
'''


def get_wz_by_code(code: str):
    return "Map" + str(code)


class Map01(WZ_MapBase):
    NAME = "初音礼物大作战"
    NXY1 = (171, 297)
    HXY1 = (47, 266)


class Map02(WZ_MapBase):
    NAME = "小小甜心冒险家"
    NXY1 = (171, 348)
    HXY1 = (144, 255)


class Map03(WZ_MapBase):
    NAME = "吸血鬼猎人伊利亚"
    NXY1 = (171, 297)
    HXY1 = (47, 266)


class Map04(WZ_MapBase):
    NAME = "危险假日 海边的美食家公主"
    NXY1 = (171, 319)
    HXY1 = (80, 276)


class Map05(WZ_MapBase):
    NAME = "珠希和美冬的无人岛0金币生活"
    NXY1 = (171, 288)
    HXY1 = (103, 196)


class Map06(WZ_MapBase):
    NAME = "黑铁的亡灵"
    NXY1 = (142, 371)
    HXY1 = (105, 187)


class Map07(WZ_MapBase):
    NAME = "不给布丁就捣蛋 约定的万圣节派对"
    NXY1 = (142, 371)
    HXY1 = (105, 187)
    N_slice = 3
    NXY2 = (659, 285)
    NXY3 = (227, 246)

