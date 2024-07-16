import datetime
import time

from core.constant import HUODONG_BTN
from scenes.huodong.huodong_base import HuodongMapBase


def get_huodong_by_code(code: str):
    HUODONG_CODE = {
        "20240628": Map20240628,
        "20240618": Map20230531,
        "20240531": Map20240531,
        "20240430": Map20240430,
        "20240418": Map20230331,
        "20240329": Map20240329,
        "20240311": Map20230228,
        "20240229": Map20240229,
        "20240216": Map20240216,
        "20240210": Map20240210,
        "20240207": Map20240207,
        "20240131": Map20240131,
        "20240118": Map20221231,
        "20231229": Map20231229,
        "20231217": Map20221130,
        "20231130": Map20231130,
        "20231118": Map20221031,
        "20231031": Map20231031,
        "20231018": Map20220930,
        "20230930": Map20230930,
        "20230917": Map20220831,
        "20230831": Map20230831,
        "20230818": Map20220731,
        "20230731": Map20230731,
        "20230718": Map20220630,
        "20230630": Map20230630,
        "20230618": Map20220531,
        "20230531": Map20230531,
        "20230516": Map20220430,
        "20230428": Map20230428,
        "20230416": Map20230416,
        "20230331": Map20230331,
        "20230316": Map20230316,
        "20230308": Map20230308,
        "20230228": Map20230228,
        "20230216": Map20230216,
        "20230210": Map20230210,
        "20230131": Map20230131,
        "20230115": Map20230115,
        "20221231": Map20221231,
        "20221216": Map20221216,
        "20221130": Map20221130,
        "20221110": Map20221110,
        "20221031": Map20221031,
        "20221016": Map20221016,
        "20220930": Map20220930,
        "20220917": Map20220917,
        "20220831": Map20220831,
        "20220816": Map20220816,
        "20220731": Map20220731,
        "20220716": Map20220716,
        "20220629": Map20220630,
        "20220616": Map20220616,
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
        if code == "current":
            today = str(datetime.datetime.now().strftime("%Y%m%d"))
            series = list(HUODONG_CODE.keys())
            series.sort(reverse=True)
            for i in series:
                if today >= i:
                    return HUODONG_CODE[i]
        else:
            raise ValueError(f"没有编号为{code}的活动，请检查scenes/huodng/huodong_manager.py！")


'''
NMAP： Normal在图1的最后关卡
XY11： 第一图的第一个坐标
XY21： 第二图的第一个坐标
N_slice： Normal图切了几段
N1： Normal图如果分段，第1段最后一图的图号
    ...
'''


class Map20240628(HuodongMapBase):
    N_slice = 2
    N1 = 5
    NAME = "破晓之星夏日游戏 闪耀于夏天海边的三份思念"
    XY11 = (147, 229)
    XY21 = (154, 183)
    XY_VH_BOSS = (864, 290)
    HARD_COORD = {
        1: (90, 230),
        2: (237, 319),
        3: (374, 237),
        4: (462, 363),
        5: (688, 330),
    }


class Map20240531(HuodongMapBase):
    N_slice = 1
    NAME = "Enjoy&Refresh 性格迥异的女子露营"
    XY11 = (162, 394)
    XY_VH_BOSS = (833, 315)
    HARD_COORD = {
        1: (113, 295),
        2: (258, 377),
        3: (475, 233),
        4: (580, 340),
        5: (713, 228),
    }


class Map20240430(HuodongMapBase):
    N_slice = 1
    NAME = "海盗逸话 海盗岛被诅咒的遗宝"
    XY11 = (137, 257)
    XY_VH_BOSS = (870, 284)
    HARD_COORD = {
        1: (88, 316),
        2: (245, 214),
        3: (315, 407),
        4: (533, 401),
        5: (645, 212),
    }


class Map20240329(HuodongMapBase):
    N_slice = 2
    N1 = 4
    NAME = "交出宝物!神出鬼没的怪盗"
    XY11 = (243, 251)
    XY21 = (107, 373)
    XY_VH_BOSS = (868, 270)
    HARD_COORD = {
        1: (90, 309),
        2: (247, 204),
        3: (338, 396),
        4: (564, 319),
        5: (698, 214),
    }

class Map20240229(HuodongMapBase):
    N_slice = 2
    N1 = 10
    NAME = "Sweet tiny stage!新人女演员与小小淑女"
    XY11 = (279, 195)
    XY21 = (152, 390)
    XY_VH_BOSS = (812, 282)
    HARD_COORD = {
        1: (115, 226),
        2: (258, 413),
        3: (423, 408),
        4: (504, 224),
        5: (632, 320),
    }

class Map20240210(HuodongMapBase):
    N_slice = 1
    NAME = "情相连 心相系前篇"
    XY11 = (158, 193)
    XY_VH_BOSS = (837, 304)
    HARD_COORD = {
        1: (112, 323),
        2: (271, 205),
        3: (360, 389),
        4: (535, 395),
        5: (647, 235),
    }

    def enter_huodong(self, xx, yy):
        super().enter_huodong(xx, yy)
        time.sleep(2)
        # 检测到“去前篇”：点它
        if self.is_exists(HUODONG_BTN["qian"]):
            self.click_btn(HUODONG_BTN["qian"], until_appear=HUODONG_BTN["hou"])


class Map20240216(HuodongMapBase):
    N_slice = 1
    NAME = "情相连 心相系后篇"
    XY11 = (96, 208)
    XY_VH_BOSS = (876, 309)
    HARD_COORD = {
        1: (71, 263),
        2: (221, 361),
        3: (348, 214),
        4: (486, 396),
        5: (679, 308),
    }

    def enter_huodong(self, xx, yy):
        super().enter_huodong(xx, yy)
        time.sleep(2)
        # 检测到“去后篇”：点它
        if self.is_exists(HUODONG_BTN["hou"]):
            self.click_btn(HUODONG_BTN["hou"], until_appear=HUODONG_BTN["qian"])


class Map20240207(HuodongMapBase):
    N_slice = 2
    N1 = 10
    NAME = "Re:member 吾愿所织的未来后篇"
    XY11 = (119, 185)
    XY21 = (165, 291)
    XY_VH_BOSS = (839, 299)
    HARD_COORD = {
        1: (104, 274),
        2: (268, 396),
        3: (417, 237),
        4: (506, 369),
        5: (674, 262),
    }

    def enter_huodong(self, xx, yy):
        super().enter_huodong(xx, yy)
        time.sleep(2)
        # 检测到“去后篇”：点它
        if self.is_exists(HUODONG_BTN["hou"]):
            self.click_btn(HUODONG_BTN["hou"], until_appear=HUODONG_BTN["qian"])    

class Map20240131(HuodongMapBase):
    N_slice = 4
    N1 = 6
    N2 = 9
    N3 = 12
    NAME = "Re:member 吾愿所织的未来前篇"
    XY11 = (142, 367)
    XY21 = (212, 301)
    XY31 = (228, 292)
    XY41 = (187, 334)
    XY_VH_BOSS = (835, 270)
    HARD_COORD = {
        1: (121, 276),
        2: (280, 208),
        3: (429, 245),
        4: (522, 373),
        5: (651, 251),
    }
    
    def enter_huodong(self, xx, yy):
        super().enter_huodong(xx, yy)
        time.sleep(2)
        # 检测到“去前篇”：点它
        if self.is_exists(HUODONG_BTN["qian"]):
            self.click_btn(HUODONG_BTN["qian"], until_appear=HUODONG_BTN["hou"])

class Map20231229(HuodongMapBase):
    N_slice = 4
    N1 = 5
    N2 = 8
    N3 = 11
    NAME = "新年美食记忆·雪菲的大作战"
    XY11 = (160, 299)
    XY21 = (212, 301)
    XY31 = (198, 297)
    XY41 = (158, 270)
    XY_VH_BOSS = (837, 262)
    HARD_COORD = {
        1: (121, 282),
        2: (284, 214),
        3: (431, 235),
        4: (527, 348),
        5: (653, 214),
    }

class Map20231130(HuodongMapBase):
    NAME = "公主圣诞节快乐！舞动的少女与真情点心"
    XY11 = (158, 243)
    XY_VH_BOSS = (789, 280)
    HARD_COORD = {
        1: (91, 386),
        2: (187, 209),
        3: (271, 357),
        4: (411, 429),
        5: (596, 346),
    }

class Map20231031(HuodongMapBase):
    N_slice = 2
    N1 = 9
    NAME = "魔法少女外传 黑暗世界"
    XY11 = (157, 360)
    XY21 = (116, 312)
    XY_VH_BOSS = (835, 295)
    HARD_COORD = {
        1: (89, 388),
        2: (375, 404),
        3: (429, 245),
        4: (540, 329),
        5: (682, 227),
    }

class Map20230930(HuodongMapBase):
    N_slice = 2
    N1 = 12
    NAME = "万圣节救援队·紧急出动！捕获毛茸茸大作战"
    XY11 = (189, 293)
    XY21 = (218, 268)
    XY_VH_BOSS = (838, 291)
    HARD_COORD = {
        1: (111, 287),
        2: (259, 367),
        3: (374, 224),
        4: (575, 306),
        5: (714, 223),
    }

class Map20230831(HuodongMapBase):
    N_slice = 2
    N1 = 5
    NAME = "大江户的非法病历 Dr.深月的诊疗室"
    XY11 = (174, 264)
    XY21 = (218, 189)
    XY_VH_BOSS = (857, 301)
    HARD_COORD = {
        1: (85, 359),
        2: (217, 203),
        3: (406, 234),
        4: (560, 341),
        5: (674, 229),
    }


class Map20230731(HuodongMapBase):
    N_slice = 1
    NAME = "慈乐之音的夏日演唱会 转瞬即逝的时光"
    XY11 = (157, 203)
    XY_VH_BOSS = (867, 288)
    HARD_COORD = {
        1: (88, 218),
        2: (234, 315),
        3: (381, 227),
        4: (465, 359),
        5: (697, 328),
    }


class Map20230630(HuodongMapBase):
    N_slice = 3
    N1 = 5
    N2 = 13
    NAME = "无限夏日计划 两人独占的盛夏乐园"
    XY11 = (133, 321)
    XY21 = (254, 272)
    XY31 = (208, 262)
    XY_VH_BOSS = (860, 285)
    HARD_COORD = {
        1: (119, 336),
        2: (274, 193),
        3: (413, 264),
        4: (535, 353),
        5: (674, 243),
    }


class Map20230531(HuodongMapBase):
    N_slice = 2
    N1 = 11
    NAME = "碧与她的玩具朋友"
    XY11 = (133, 321)
    XY21 = (164, 267)
    XY_VH_BOSS = (860, 285)
    HARD_COORD = {
        1: (115, 285),
        2: (280, 252),
        3: (365, 407),
        4: (564, 325),
        5: (705, 227),
    }


class Map20230428(HuodongMapBase):
    N_slice = 2
    N1 = 10
    NAME = "时间旅行的龙族们"
    XY11 = (196, 354)
    XY21 = (129, 358)
    XY_VH_BOSS = (853, 302)
    HARD_COORD = {
        1: (102, 351),
        2: (206, 192),
        3: (398, 223),
        4: (562, 329),
        5: (700, 227),
    }


class Map20230416(HuodongMapBase):
    NAME = "恩赐的财团与神圣学院的问题儿童复刻"
    XY11 = (123, 230)
    XY_VH_BOSS = (864, 288)
    HARD_COORD = {
        1: (115, 346),
        2: (258, 233),
        3: (351, 379),
        4: (547, 324),
        5: (684, 230),
    }


class Map20230331(HuodongMapBase):
    NAME = "钢铁圣女与神圣学院的问题儿童"
    XY11 = (159, 318)
    XY_VH_BOSS = (864, 291)
    HARD_COORD = {
        1: (86, 310),
        2: (235, 188),
        3: (427, 232),
        4: (539, 337),
        5: (682, 246),
    }

class Map20230316(HuodongMapBase):
    NAME = "星光公主 Re:M@ster 复刻后篇"
    XY11 = (150, 306)
    XY_VH_BOSS = (860, 238)
    HARD_COORD = {
        1: (72, 217),
        2: (175, 378),
        3: (393, 372),
        4: (537, 250),
        5: (664, 328),
    }
    N_slice = 1

    def enter_huodong(self, xx, yy):
        super().enter_huodong(xx, yy)
        time.sleep(2)
        # 检测到“去后篇”：点它
        if self.is_exists(HUODONG_BTN["hou"]):
            self.click_btn(HUODONG_BTN["hou"], until_appear=HUODONG_BTN["qian"])


class Map20230308(HuodongMapBase):
    NAME = "星光公主 Re:M@ster 复刻前篇"
    XY11 = (142, 340)
    XY_VH_BOSS = (854, 258)
    HARD_COORD = {
        1: (109, 242),
        2: (214, 395),
        3: (409, 358),
        4: (548, 253),
        5: (673, 313),
    }
    N_slice = 1

    def enter_huodong(self, xx, yy):
        super().enter_huodong(xx, yy)
        time.sleep(2)
        # 检测到“去前篇”：点它
        if self.is_exists(HUODONG_BTN["qian"]):
            self.click_btn(HUODONG_BTN["qian"], until_appear=HUODONG_BTN["hou"])


class Map20230228(HuodongMapBase):
    NAME = "灰姑娘课程 璀璨的日子 有着苹果的滋味"
    XY11 = (95, 211)
    XY21 = (166, 276)
    XY_VH_BOSS = (868, 256)
    HARD_COORD = {
        1: (110, 300),
        2: (280, 251),
        3: (365, 410),
        4: (570, 331),
        5: (704, 232),
    }
    N_slice = 2
    N1 = 11


class Map20230216(HuodongMapBase):
    NAME = "魔法少女 二人是Misty&Purely复刻"
    XY11 = (151, 375)
    XY_VH_BOSS = (844, 289)
    HARD_COORD = {
        1: (106, 222),
        2: (251, 351),
        3: (372, 223),
        4: (552, 226),
        5: (640, 377),
    }


class Map20230210(HuodongMapBase):
    NAME = "羁绊相连心相惜后篇"
    XY11 = (96, 208)
    XY_VH_BOSS = (875, 296)
    HARD_COORD = {
        1: (72, 272),
        2: (208, 382),
        3: (330, 243),
        4: (430, 400),
        5: (687, 341),
    }

    def enter_huodong(self, xx, yy):
        super().enter_huodong(xx, yy)
        time.sleep(2)
        # 检测到“去后篇”：点它
        if self.is_exists(HUODONG_BTN["hou"]):
            self.click_btn(HUODONG_BTN["hou"], until_appear=HUODONG_BTN["qian"])


class Map20230131(HuodongMapBase):
    NAME = "羁绊相连心相惜前篇"
    XY11 = (160, 204)
    XY_VH_BOSS = (837, 303)
    HARD_COORD = {
        1: (111, 328),
        2: (268, 214),
        3: (357, 390),
        4: (535, 375),
        5: (644, 210),
    }

    def enter_huodong(self, xx, yy):
        super().enter_huodong(xx, yy)
        time.sleep(2)
        # 检测到“去前篇”：点它
        if self.is_exists(HUODONG_BTN["qian"]):
            self.click_btn(HUODONG_BTN["qian"], until_appear=HUODONG_BTN["hou"])


class Map20230115(HuodongMapBase):
    NAME = "狂奔!兰德索尔公会竞速赛复刻"
    XY11 = (200, 369)
    XY21 = (241, 341)
    XY_VH_BOSS = (869, 284)
    HARD_COORD = {
        1: (54, 313),
        2: (203, 247),
        3: (314, 360),
        4: (561, 347),
        5: (697, 223),
    }
    N_slice = 2
    N1 = 9


class Map20221231(HuodongMapBase):
    NAME = "新年美食公主，孤注一掷的少女们!"
    XY11 = (184, 342)
    XY_VH_BOSS = (869, 242)
    HARD_COORD = {
        1: (51, 229),
        2: (240, 213),
        3: (314, 391),
        4: (551, 350),
        5: (661, 223),
    }


class Map20221216(HuodongMapBase):
    NAME = "礼物大恐慌！兰德索尔的圣诞老人们复刻"
    XY11 = (88, 353)
    XY21 = (130,351)
    XY_VH_BOSS = (837, 259)
    HARD_COORD = {
        1: (78, 317),
        2: (221, 216),
        3: (321, 361),
        4: (544, 345),
        5: (673, 225),
    }
    N_slice = 2
    N1 = 9


class Map20221130(HuodongMapBase):
    NAME = "名媛初登梦想秘境 圣诞夜的恋爱游戏"
    XY11 = (153, 393)
    XY_VH_BOSS = (0, 0)
    HARD_COORD = {
        1: (108, 192),
        2: (260, 225),
        3: (298, 359),
        4: (437, 410),
        5: (616, 336),
    }


class Map20221110(HuodongMapBase):
    NAME = "Re:从零开始收集的异世界餐桌"
    XY11 = (152, 195)
    XY21 = (139, 221)
    XY_VH_BOSS = (825, 216)
    HARD_COORD = {
        1: (113, 253),
        2: (216, 400),
        3: (382, 348),
        4: (518, 251),
        5: (640, 313),
    }
    N_slice = 2
    N1 = 10


class Map20221031(HuodongMapBase):
    NAME = "魔法提督可爱莫妮卡！"
    XY11 = (166, 367)
    XY_VH_BOSS = (869, 252)
    HARD_COORD = {
        1: (92, 313),
        2: (250, 212),
        3: (385, 398),
        4: (555, 351),
        5: (687, 214),
    }


class Map20221016(HuodongMapBase):
    NAME = "龙之探索者复刻"
    XY11 = (143, 350)
    XY_VH_BOSS = (817, 234)
    HARD_COORD = {
        1: (73, 356),
        2: (228, 246),
        3: (314, 345),
        4: (512, 342),
        5: (668, 321),
    }


class Map20220930(HuodongMapBase):
    NAME = "回响!尖叫!万圣鬼怪狂欢节"
    XY11 = (159, 306)
    XY_VH_BOSS = (830, 274)
    HARD_COORD = {
        1: (94, 211),
        2: (201, 344),
        3: (326, 216),
        4: (524, 233),
        5: (628, 328),
    }


class Map20220917(HuodongMapBase):
    NAME = "小小的勇气·万圣节之夜复刻"
    XY11 = (88, 380)
    XY21 = (131,355)
    XY_VH_BOSS = (845, 286)
    HARD_COORD = {
        1: (54, 314),
        2: (203, 220),
        3: (338, 348),
        4: (572, 328),
        5: (696, 221),
    }
    N_slice = 2
    N1 = 9


class Map20220831(HuodongMapBase):
    NAME = "快乐变身 双生天使"
    XY11 = (167, 363)
    XY_VH_BOSS = (841, 278)
    HARD_COORD = {
        1: (105, 224),
        2: (251, 354),
        3: (378, 235),
        4: (572, 226),
        5: (660, 354),
    }
    N_slice = 1
    XINLAI = True


class Map20220816(HuodongMapBase):
    NAME = "森林里的胆小鬼与神圣学院的问题儿童复刻"
    XY11 = (140, 371)
    XY_VH_BOSS = (863, 265)
    HARD_COORD = {
        1: (89, 211),
        2: (215, 294),
        3: (379, 226),
        4: (499, 335),
        5: (684, 325),
    }
    XINLAI = False


class Map20220731(HuodongMapBase):
    NAME = "美里的夏日声援 追梦的盛夏棒球队"
    XY11 = (130, 268)
    XY_VH_BOSS = (845, 238)
    HARD_COORD = {
        1: (106, 257),
        2: (397, 230),
        3: (258, 370),
        4: (471, 395),
        5: (673, 357),
    }
    XINLAI = False


class Map20220716(HuodongMapBase):
    NAME = "盛夏的真步真步王国复刻"
    XY11 = (219, 252)
    XY_VH_BOSS = (867, 296)
    HARD_COORD = {
        1: (106, 225),
        2: (280, 308),
        3: (424, 226),
        4: (515, 340),
        5: (691, 330),
    }
    XINLAI = False


class Map20220630(HuodongMapBase):
    NAME = "七夕剑客旅情谭 天际川流夏之恋"
    XY11 = (197, 270)
    XY21 = (168, 360)
    XY_VH_BOSS = (868, 282)
    HARD_COORD = {
        1: (76, 321),
        2: (234, 221),
        3: (289, 396),
        4: (579, 329),
        5: (718, 227),
    }
    N_slice = 2
    N1 = 10


class Map20220616(HuodongMapBase):
    NAME = "玲奈的彩虹舞台复刻"
    XY11 = (131, 417)
    XY_VH_BOSS = (868, 296)
    HARD_COORD = {
        1: (91, 231),
        2: (236, 310),
        3: (416, 231),
        4: (503, 340),
        5: (706, 331),
    }
    N_slice = 1
    N1 = 15


class Map20220531(HuodongMapBase):
    NAME = "不可思议之国的璃乃 小小爱丽丝与希望的绘本"
    XY11 = (165, 277)
    # XY_VH_BOSS = (543, 206)
    HARD_Legacy = False
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
