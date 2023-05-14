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
    WZ_CODE = {
        "01": Map01,
        "02": Map02,
        "03": Map03,
        "04": Map04,
        "05": Map05,
        "06": Map06,
        "07": Map07,
        "09": Map09,
        "10": Map10,
        "11": Map11,
        "13": Map13,
        "14": Map14
    }

    return WZ_CODE[code]


class Map01(WZ_Menu):
    NAME = "初音礼物大作战"
    NXY1 = (171, 297)
    HXY1 = (47, 266)


class Map02(WZ_Menu):
    NAME = "小小甜心冒险家"
    NXY1 = (171, 348)
    HXY1 = (144, 255)


class Map03(WZ_Menu):
    NAME = "吸血鬼猎人伊利亚"
    NXY1 = (171, 297)
    HXY1 = (122, 266)


class Map04(WZ_Menu):
    NAME = "危险假日 海边的美食家公主"
    NXY1 = (171, 319)
    HXY1 = (80, 276)


class Map05(WZ_Menu):
    NAME = "珠希和美冬的无人岛0金币生活"
    NXY1 = (171, 288)
    HXY1 = (103, 196)


class Map06(WZ_Menu):
    NAME = "黑铁的亡灵"
    NXY1 = (142, 371)
    HXY1 = (105, 187)


class Map07(WZ_Menu):
    NAME = "不给布丁就捣蛋 约定的万圣节派对"
    NXY1 = (84, 325)
    HXY1 = (105, 187)
    N_slice = 3
    N1 = 6
    N2 = 12
    NXY2 = (659, 285)
    NXY3 = (227, 246)


# 有个抽象的过场剧情，暂时不好写
# class Map08(WZ_Menu):
#     NAME = "暮光破坏者"
#     NXY1 = (136, 235)
#     HXY1 = (138, 319)
#     N_slice = 1


class Map09(WZ_Menu):
    NAME = "忘却的圣歌"
    NXY1 = (281, 223)
    HXY1 = (102, 402)
    N_slice = 1


class Map10(WZ_Menu):
    NAME = "破晓之星大危机"
    NXY1 = (136, 235)
    HXY1 = (138, 319)
    N_slice = 1


class Map11(WZ_Menu):
    NAME = "情人节之战！ 正中红心的甜蜜战斗"
    NXY1 = (63, 208)
    NXY2 = (196, 377)
    HXY1 = (90, 356)
    N_slice = 2
    N1 = 6


# 有个抽象的解谜任务，暂时不好写
# class Map12(WZ_Menu):
#     NAME = "王都的名侦探 叹息的追缉者"
#     NXY1 = (169, 386)
#     HXY1 = (138, 319)
#     MT1 = (394, 191)
#     ans1 = (522, 280)
#     N_slice = 1


class Map13(WZ_Menu):
    NAME = "盛开在阿斯特莱亚的双轮之花"
    NXY1 = (113, 393)
    NXY2 = (104, 387)
    HXY1 = (73, 405)
    N_slice = 1
    N1 = 12


class Map14(WZ_Menu):
    NAME = "将军道中记 白翼的武士"
    # 坐标有问题先别用
    NXY1 = (177, 287)
    HXY1 = (138, 319)
    N_slice = 1