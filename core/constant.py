from typing import Tuple, Optional


class PCRelement:
    """
    漂亮地显示一个PCR的元素
    除了正常的位置坐标，还携带图片和裁剪参数
    """

    def __init__(self, x=None, y=None, name: Optional[str] = None, img: Optional[str] = None,
                 at: Optional[Tuple[float, float, float, float]] = None, **kwargs):
        self.x = x
        self.y = y
        self.name = name
        self.img = img
        self.at = at
        self.fc = None  # 进度条：前景色(R,G,B)
        self.bc = None  # 进度条：背景色(R,G,B)
        for keys in kwargs:
            self.__setattr__(keys, kwargs[keys])

    def __iter__(self):
        return (self.x, self.y).__iter__()

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y

    def __repr__(self):
        s1 = f"({self.x},{self.y})"
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


def p(x=None, y=None, name=None, img=None, at=None, **kwargs):
    """
    快速创建一个PCRelement
    """
    return PCRelement(x=x, y=y, name=name, img=img, at=at, **kwargs)


# 主页面的按钮对象
MAIN_BTN = {
    # 主页
    "zhuye": p(131, 533, name="我的主页"),
    # 行会按钮 
    "hanghui": p(693, 430, img="img/home/hanghui_btn.bmp", at=(677, 419, 702, 441), name="行会"),
    # 角色
    "juese": p(213, 507),
    # 剧情
    "juqing": p(342, 510),
    # 冒险按钮
    "maoxian": p(480, 515, img="img/home/maoxian.bmp", at=(421, 447, 535, 535)),
    # 地下城
    "dxc": p(874, 122, img="img/home/dxc.bmp", at=(848, 101, 898, 145)),
    # 主线关卡
    "zhuxian": p(500, 90, img="img/home/zhuxian.bmp", at=(526, 117, 587, 186)),
    # 公会之家
    "gonghuizhijia": p(617, 512),
    # 扭蛋
    "niudan": p(753, 514),
    # 主菜单
    "zhucaidan": p(877, 515),

    # 礼物
    "liwu": p(908, 432, img="img/home/liwu.bmp", at=(891, 417, 927, 448)),
    # 任务
    "renwu": p(837, 432),
    # 体力购买
    "tili_plus": p(320, 31),
    # 体力购买ok
    "tili_ok": p(590, 370, img="img/ui/ok_btn_1.bmp", at=(488, 346, 692, 394)),
    # 体力购买完成ok
    "tili_ok2": p(480, 371, img="img/ui/ok_btn_2.bmp", at=(382, 351, 578, 390)),

    # mana购买
    "mana_plus": p(189, 62),
    # mana购买界面标题
    "mana_title": p(img="img/home/mana_title.bmp", at=(86, 55, 307, 107)),
    # mana购买界面的空白（用于判断是否进行了1次购买，能否进行十连）
    "mana_blank": p(img="img/home/mana_blank.bmp", at=(740, 460, 895, 497)),
    # mana购买确认
    "mana_ok": p(590, 370, img="img/ui/ok_btn_1.bmp", at=(488, 346, 692, 394)),
    # mana购买1次
    "mana_one": p(582, 471),
    # mana购买10次
    "mana_ten": p(802, 475),

    # 赛马时跳过
    "tiaoguo": p(893, 40, img='img/ui/jiasu.jpg', at=(700, 0, 960, 100)),
    # 竞赛开始按钮
    "jingsaikaishi": p(img='img/home/jingsaikaishi.bmp', at=(755, 471, 922, 512)),

    # 用于判断是否处于加载状态（此处只保留at）
    "loading_left": p(at=(36, 87, 224, 386)),

    "exp_bar": p(at=(78, 23, 178, 31), fc=(106, 205, 176), bc=(94, 125, 146)),
    "speaker_box": p(img="img/ui/speaker_box.bmp", at=(182, 395, 209, 409)),  # 有人说话时名字左上角的红色
    "setting_pic": p(74, 268, img="img/home/setting.bmp", at=(59, 253, 91, 281)),
}
LIWU_BTN = {
    "shouqulvli": p(img="img/home/shouqulvli.bmp", at=(98, 461, 202, 489)),
    "quanbushouqu": p(812, 470, img="img/home/quanbushouqu_on.bmp", at=(715, 458, 900, 494)),
    "quxiao": p(597, 478),
    "ok": p(589, 478, img="img/ui/ok_btn_1.bmp", at=(487, 454, 691, 502)),
    "ok2": p(480, 479, img="img/ui/ok_btn_2.bmp", at=(382, 459, 578, 498)),
    "chiyoushangxian": p(img="img/home/chiyoushangxian.bmp", at=(433, 134, 529, 159)),
    "chiyoushangxian_ok": p(481, 371),
    "meiyouliwu": p(img="img/home/meiyouliwu.bmp", at=(381, 239, 571, 274)),

}
RENWU_BTN = {
    "quanbushouqu_off": p(844, 439, img="img/home/quanbushouqu_off.bmp", at=(747, 421, 939, 455)),
    "quanbushouqu": p(844, 439, img="img/home/quanbushouqu_on.bmp", at=(751, 421, 936, 457)),
    "renwutip": p(img="img/home/renwutip.bmp", at=(466, 363, 803, 389)),
    "guanbi": p(img="img/ui/close_btn_1.bmp", at=(374, 455, 580, 503)),
}
JIAYUAN_BTN = {
    "quanbushouqu": p(900, 424, img="img/jiayuan/quanbushouqu.bmp", at=(872, 395, 926, 454)),
    "guanbi": p(477, 479, img="img/ui/close_btn_1.bmp", at=(374, 455, 580, 503)),
}

NIUDAN_BTN = {
    "PT_reset_ok": p(479, 365),
    "putong": p(862, 71),
    "putong_mianfei": p(717, 354, img="img/niudan/putong_mianfei.bmp", at=(680, 358, 754, 383)),
    "putong_quxiao": p(367, 370, img="img/ui/quxiao.bmp", at=(274, 352, 468, 388)),
    "putong_ok": p(591, 360, img="img/ui/ok_btn_1.bmp", at=(493, 347, 688, 387)),
    "niudanjieguo_ok": p(481, 443, img="img/ui/ok_btn_2.bmp", at=(383, 423, 597, 462)),
    "putong_wancheng": p(img="img/niudan/putong_wancheng.bmp", at=(647, 329, 784, 378)),

}
HANGHUI_BTN = {
    "juanzengqingqiu": p(367, 39),
    "juanzeng": p(644, 385),
    # 组建行会（未加入公会）
    "zujianhanghui": p(851,442,img="img/zujianhanghui.bmp",at=(746, 426, 931, 464)),
    # 设定（加入行会）
    "sheding_join": p(860,79,img="img/hanghui/sheding_join.bmp",at=(840,68,879,89)),
    # 加入行会设定输入框
    "input_join": p(370,180,img="img/hanghui/input_join.bmp",at=(320,165,424,191)),
    # 搜索（加入行会，亮）注意，暗的时候为0.97，亮为0.99
    "sousuo_join": p(589,431,img="img/hanghui/sousuo_join.bmp",at=(506,417,663,448)),
    # 进入行会（从搜索界面）
    "in_join": p(890,155,img="img/hanghui/in_join.bmp",at=(878,126,902,185)),
    # 加入行会
    "join_btn": p(854,444,img='img/jiaru.bmp',at=(749, 427, 933, 460)),
    # 支援设定
    "zhiyuansheding": p(83,348,img="img/hanghui/zhiyuansheding.bmp",at=(48,336,120,361)),
    # 地下城支援1
    "zhiyuan_dxc1": p(105,232,img="img/hanghui/zhiyuanjuese1.bmp",at=(65,194,142,272)),
    # 地下城支援2
    "zhiyuan_dxc2": p(102,355,img="img/hanghui/zhiyuanjuese2.bmp",at=(64,315,140,393)),
    # 支援取消
    "zhiyuanquxiao": p(img="img/hanghui/zhiyuanquxiao.bmp",at=(645,438,694,466)),
    # 战力排序（支援界面）用于判断是否处在战力排序状态
    "zhanlipaixu": p(img="img/hanghui/zhanlipaixu.bmp",at=(684,78,722,100)),
    # 降序（支援界面）
    "jiangxu_juese": p(863,90,img="img/hanghui/jiangxu_juese.bmp",at=(828,78,903,99)),
    # 筛选条件（支援界面）
    "shaixuantiaojian_juese": p(788,88,img="img/hanghui/shaixuantiaojian_juese.bmp",at=(777,78,800,99)),
    # 角色战力”确认“蓝点
    "zhanli_juese": p(289, 141,img="img/hanghui/landian_true.bmp",at=(266, 118, 311, 164)),
    # 角色筛选条件界面确认
    "hanghui_ok_juese": p(591, 476,img="img/hanghui/hanghui_ok.bmp",at= (553, 461, 629, 490)),
    # 角色选择1
    "juese1": p(102,162),
    # 角色选择2
    "juese2": p(210,164),
    # 角色选择3
    "juese3": p(318,166),
    # 角色选择4
    "juese4": p(431,166),
    # 角色选择确认
    "juesesheding": p(838,454,img="img/hanghui/juesesheding.bmp",at=(791,440,885,466)),
    # 角色选择二次确认
    "hanghui_ok_double": p(591,431,img="img/hanghui/hanghui_ok.bmp",at=(553, 416, 630, 446)),


    # 返回键隔壁的“行会”字样
    "hanghui_title": p(img="img/hanghui.bmp", at=(63, 12, 123, 45)),
    # 成员信息
    "chengyuanxinxi": p(237,353,img="img/hanghui/chengyuanxinxi.bmp", at=(203, 339, 272, 359)),
    # 成员信息界面的“成员列表”按钮
    "chengyuanliebiao": p(img='img/chengyuanliebiao.bmp',at=(329, 15, 450, 42)),
    # 筛选条件（成员界面）
    "shaixuantiaojian_chengyuan": p(793,84,img="img/hanghui/shaixuantiaojian_chengyuan.bmp",at=(782,80,810,103)),
    # 筛选条件里的分类
    "fenlei": p(img="img/hanghui/fenlei.bmp",at=(454,132,501,158)),
    # 成员全角色战力"确认"蓝点
    "zhanli_chengyuan": p(285,299,img="img/hanghui/landian_true.bmp",at=(265,280,310,326)),
    # 降序按钮（筛选成员界面）
    "jiangxu_chengyuan": p(868,92,img="img/hanghui/jiangxu_chengyuan.bmp",at=(843,82,876,102)),
    # 成员管理(第一个)
    "chengyuanguanli_first": p(727,191,img="img/hanghui/chengyuanguanli.bmp",at=(701,185,768,211)),
    # 开除
    "kaichu": p(647,170,img="img/hanghui/kaichu.bmp",at=(627,161,668,181)),
    # 行会确认
    "hanghui_ok": p(605,365,img="img/hanghui/hanghui_ok.bmp",at=(554,353,630,382)),
}
FIGHT_BTN = {
    "auto_on": p(914, 420, img="img/fight/auto_on.bmp", at=(895, 404, 925, 441)),
    "auto_off": p(914, 421, img="img/fight/auto_off.bmp", at=(895, 407, 929, 441)),
    "speed_1": p(910, 490, img="img/fight/speed_1.bmp", at=(894, 476, 932, 511)),
    "speed_0": p(910, 490, img="img/fight/speed_0.bmp", at=(895, 478, 928, 510)),
    "speed_2": p(911, 495, img="img/fight/speed_2.bmp", at=(893, 477, 931, 511)),
    "empty": {
        # 并不是包住整个格子的，只取了其中的一部分
        # 地下城中，各自下面有进度条，因此格子会上移。
        # 为了能适用于地下城与主线，所以只取交集。计算方式使用方差进行
        5: p(92, 434, at=(48, 409, 48 + 95, 409 + 45)),
        4: p(92 + 110, 434, at=(48 + 110, 409, 48 + 95 + 110, 409 + 45)),
        3: p(92 + 110 * 2, 434, at=(48 + 110 * 2, 409, 48 + 95 + 110 * 2, 409 + 45)),
        2: p(92 + 110 * 3, 434, at=(48 + 110 * 3, 409, 48 + 95 + 110 * 3, 409 + 45)),
        1: p(92 + 110 * 4, 434, at=(48 + 110 * 4, 409, 48 + 95 + 110 * 4, 409 + 45)),
    },
    "sort_down": p(742, 89, img="img/fight/sort_down.bmp", at=(720, 79, 765, 99)),
    "sort_level": p(596, 88, img="img/fight/sort_level.bmp", at=(576, 78, 617, 99)),
    "sort_star": p(596, 90, img="img/fight/sort_star.bmp", at=(577, 78, 616, 99)),
    "sort_up": p(741, 88, img="img/fight/sort_up.bmp", at=(722, 77, 760, 99)),
    "sort_power": p(597, 89, img="img/fight/sort_power.bmp", at=(575, 79, 618, 99)),
    "cat_dengji": p(69, 142, name="等级"),  # cat：分类界面
    "cat_zhanli": p(290, 141, name="战力"),
    "cat_rank": p(511, 142, name="RANK"),
    "cat_star": p(731, 139, name="星数"),
    "cat_ok": p(587, 478, img="img/ui/ok_btn_1.bmp", at=(487, 454, 691, 502)),  # 分类界面：OK
    "my_team": p(867, 88),  # 我的队伍
    "team_h": {
        # 编组1，编组2，。。。，编组5
        1: p(123, 87),
        2: p(268, 90),
        3: p(401, 87),
        4: p(550, 87),
        5: p(695, 87),
    },
    "team_v": {
        # 队伍1，队伍2，队伍3
        1: p(797, 173),
        2: p(788, 291),
        3: p(788, 412),
    },
    "first_five": {
        # 前五个角色
        1: p(111, 166),
        2: p(210, 166),
        3: p(319, 165),
        4: p(425, 167),
        5: p(531, 170),
    },
    "team_close": p(476, 477, img="img/ui/btn_close_1.bmp", at=(374, 455, 580, 503)),  # 选队界面的关闭按钮
    "shbg": p(img="img/fight/shbg.bmp", at=(709, 23, 898, 52)),  # 伤害报告
    "menu": p(img="img/fight/menu.bmp", at=(871, 18, 928, 32)),
    "qwjsyl": p(576, 495, img="img/fight/qwjsyl.bmp", at=(392, 457, 948, 528)),  # 前往角色一览
    "win": p(img="img/fight/win.bmp", at=(400, 6, 551, 127)),  # 过关的帽子
    "zhandoukaishi": p(834, 453, img="img/fight/zhandoukaishi.bmp", at=(761, 431, 911, 472)),
    "xuanguan_quxiao": p(665, 455, img="img/ui/quxiao2.bmp", at=(597, 440, 736, 470)),  # 选关界面（选择使用扫荡券）右下角的取消
    "upperright_stars":  # “挑战”页面右上角的星星位置
        {
            1: p(762, 35),
            2: p(825, 35),
            3: p(889, 35),
        },
    "tiaozhan": p(839, 456, img="img/ui/tiaozhan.bmp", at=(788, 444, 889, 467)),
    "tiaozhan2": p(839, 453, img="img/ui/tiaozhan2.bmp", at=(814, 440, 865, 466)),
    "xiayibu2": p(829, 490, img="img/ui/xiayibu2.bmp", at=(785, 477, 870, 505)),  # 短的下一步，用于“战利品”界面
    "xiayibu": p(832, 504, img="img/ui/xiayibu.bmp", at=(731, 480, 932, 527)),  # 长的下一步，用于经验值、好感度页面
    "qwzxgq": p(808, 493, img="img/fight/qwzxgq.bmp", at=(745, 481, 869, 504)),  # 前往主线关卡：输的时候会显示
    "baochou": p(img="img/fight/baochou.bmp", at=(61, 414, 114, 481)),
    "dengjitisheng": p(img="img/fight/dengjitisheng.bmp", at=(431, 132, 525, 158)),
}

JUESE_BTN = {
    "duiwu": p(img="img/juese/duiwu.bmp", at=(855, 15, 929, 35)),
    "mana_ball": p(img="img/juese/mana_ball.bmp", at=(609, 21, 620, 34)),
    "first_juese": p(175, 140),
    "rank_tisheng": p(246, 333, img="img/juese/rank_tisheng.bmp", at=(204, 323, 289, 335)),
    "rank_tisheng_ok": p(589, 478, img="img/ui/ok_btn_1.bmp", at=(487, 454, 691, 502)),
    "rank_tisheng_ok_noequ": p(588, 369, img="img/juese/ok_btn.bmp", at=(567, 358, 611, 380)),  # 不需要消耗时，强化的OK在上头
    "rank_tisheng_ok2": p(480, 371, img="img/ui/ok_btn_2.bmp", at=(382, 351, 578, 390)),
    "yjzb": p(241, 330, img="img/juese/yjzb.bmp", at=(197, 323, 294, 345)),
    "yjzb_off": p(img="img/juese/yjzb_off.bmp", at=(198, 323, 292, 346)),
    "zdqh": p(368, 436, img="img/juese/zdqh.bmp", at=(313, 418, 418, 450)),
    "tjqhcd": p(img="img/juese/tjqhcd.bmp", at=(414, 31, 541, 49)),
    "sort_down": p(744, 28, img="img/juese/sort_down.bmp", at=(753, 18, 798, 38)),
    "sort_up": p(755, 28, img="img/juese/sort_up.bmp", at=(756, 17, 798, 36)),
    "sort_level": p(629, 27, img="img/juese/sort_level.bmp", at=(611, 16, 647, 36)),
    "tuijianguanqia": p(img="img/juese/tuijianguanqia.bmp", at=(280, 90, 327, 102)),
    "firstqianghua_stars": {
        1: p(587, 257),
        2: p(612, 256),
        3: p(637, 257),
    }
}
MAX_DXC = 3  # 一共出了多少个地下城关

DXC_ELEMENT = {
    "chetui": p(806, 431, img="img/dxc/chetui.bmp", at=(779, 421, 833, 440)),
    "chetui_ok": p(591, 365, img="img/ui/ok_btn_1.bmp", at=(488, 346, 692, 394)),
    "sytzcs": p(723, 438, img="img/dxc/sytzcs.bmp", at=(667, 428, 784, 447)),
    "1/1": p(img="img/dxc/dxc_1_1.bmp", at=(887, 429, 913, 446)),
    "0/1": p(img="img/dxc/dxc_0_1.bmp", at=(883, 429, 910, 445)),
    "qwdxc": p(810, 489),  # 失败：前往地下城
    "shop": p(at=(889, 9, 938, 66)),
    "map": p(at=(7, 66, 954, 391)),
    "xiayibu": p(836, 503, img="img/ui/xiayibu.bmp", at=(731, 480, 932, 527)),
    "shouqubaochou_ok": p(480, 479, img="img/ui/ok_btn_2.bmp", at=(382, 459, 578, 498)),
    "qianwangdixiacheng": p(805, 495),
    "quyuxuanzequeren_ok": p(585, 371, img="img/ui/ok_btn_1.bmp", at=(488, 346, 692, 394)),
    "dxc_kkr": p(img="img/dxc/dxc_kkr.bmp", at=(442, 175, 527, 271)),
    # 判断是否在地下城商店内（用于新手教程）
    "dxc_in_shop": p(873, 437, img="img/dxc/dxc_in_shop.bmp", at=(810, 427, 933, 446)),
    # 商店按钮，此商店按钮与jjc的不同，要大一点
    "dxc_shop_btn": p(918, 30, img="img/dxc/shop.bmp", at=(905, 21, 924, 41)),
    # 地下城选关界面商店
    "dxc_choose_shop": p(917, 28, img="img/dxc/dxc_choose_shop.bmp", at=(906, 19, 928, 36)),
}
DXC_NUM = {
    # 没有OCR用此来检测层数
    3: {
        1: p(img="img/dxc/dxc3/1.bmp", at=(201, 422, 220, 440)),
        2: p(img="img/dxc/dxc3/2.bmp", at=(190, 424, 219, 439)),
        3: p(img="img/dxc/dxc3/3.bmp", at=(196, 425, 220, 439)),
        4: p(img="img/dxc/dxc3/4.bmp", at=(195, 426, 220, 439)),
        5: p(img="img/dxc/dxc3/5.bmp", at=(189, 425, 218, 441)),
        6: p(img="img/dxc/dxc3/6.bmp", at=(189, 423, 220, 441)),
        7: p(img="img/dxc/dxc3/7.bmp", at=(190, 426, 220, 439)),
        8: p(img="img/dxc/dxc3/8.bmp", at=(193, 423, 218, 441)),
        9: p(img="img/dxc/dxc3/9.bmp", at=(193, 424, 220, 440)),
        10: p(img="img/dxc/dxc3/10.bmp", at=(189, 424, 218, 441)),
    }
}
DXC_ENTRANCE = {
    # 大按钮：云海、密林、断崖的坐标
    1: p(252, 255, name="云海的山脉"),
    2: p(485, 250, name="密林的大树"),
    3: p(711, 247, name="断崖的遗迹"),
}
DXC_COORD = {
    # 每个地下城里面每一个关卡的位置
    3: {
        1: p(645, 310),
        2: p(373, 208),
        3: p(623, 206),
        4: p(415, 206),
        5: p(184, 218),
        6: p(483, 216),
        7: p(731, 229),
        8: p(456, 214),
        9: p(234, 230),
        10: p(629, 195),
    }
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

SHOP_BTN = {
    "xianding_ok": p(589, 478, img="img/ui/ok_btn_1.bmp", at=(487, 454, 691, 502)),
    "lijiguanbi": p(527, 438),
    "querenchongzhi": p(590, 370, img="img/ui/ok_btn_1.bmp", at=(488, 346, 692, 394)),
    "fanhui": p(30, 29, img="img/ui/fanhui.bmp", at=(16, 16, 45, 43)),
}
MAOXIAN_BTN = {
    "normal_on": p(699, 82, img="img/maoxian/normal_on.bmp", at=(656, 72, 748, 91)),
    "normal_off": p(701, 82, img="img/maoxian/normal_off.bmp", at=(656, 72, 749, 92)),
    "hard_on": p(825, 83, img="img/maoxian/hard_on.bmp", at=(780, 70, 871, 92)),
    "hard_off": p(824, 83, img="img/maoxian/hard_off.bmp", at=(781, 70, 867, 92)),
    "hard_0_3": p(img="img/maoxian/hard_0_3.bmp", at=(887, 402, 919, 422)),  # 剩余挑战次数0/3
    "ditu": p(img="img/maoxian/ditu.bmp", at=(906, 64, 930, 106)),
    "tili_bar": p(at=(529, 32, 637, 38), fc=(255, 215, 99), bc=(90, 101, 115)),
    "saodang_on": p(753, 334, img="img/maoxian/saodang_on.bmp", at=(679, 314, 826, 349)),  # 使用1张 蓝色
    "saodang_plus": p(878, 328),
    "saodang_ok": p(590, 370, img="img/ui/ok_btn_1.bmp", at=(488, 346, 692, 394)),
    "saodang_tiaoguo": p(475, 477, img="img/maoxian/saodang_tiaoguo.bmp", at=(380, 460, 574, 496)),
    "saodang_ok2": p(480, 479, img="img/ui/ok_btn_2.bmp", at=(382, 459, 578, 498)),
    "saodang_off": p(753, 334, img="img/maoxian/saodang_off.bmp", at=(680, 315, 824, 350)),  # 使用1张 灰色
    "quxiao": p(667, 455, img="img/ui/quxiao2.bmp", at=(597, 440, 736, 470)),
    "xianding": p(586, 368, img="img/maoxian/xianding.bmp", at=(520, 354, 657, 380)),
    "xianding_quxiao": p(371, 370, img="img/ui/quxiao.bmp", at=(274, 352, 468, 388)),
    "zaicitiaozhan": p(658, 489, img="img/maoxian/zaicitiaozhan.bmp", at=(592, 475, 723, 505)),
    "chongshi_ok": p(590, 370, img="img/ui/ok_btn_1.bmp", at=(488, 346, 692, 394)),
    "no_tili": p(img="img/maoxian/no_tili.bmp", at=(429, 242, 518, 287)),
    "buytili_ok": p(590, 370, img="img/ui/ok_btn_1.bmp", at=(488, 346, 692, 394)),
    "buytili_quxiao": p(371, 370, img="img/ui/quxiao.bmp", at=(274, 352, 468, 388)),
    "buytili_ok2": p(480, 371, img="img/ui/ok_btn_2.bmp", at=(382, 351, 578, 390)),
    "tlhf": p(img="img/maoxian/tlhf.bmp", at=(434, 137, 524, 157)),
    "no_cishu": p(img="img/maoxian/no_cishu.bmp", at=(400, 229, 541, 289)),
    "tiaozhan_off": p(img="img/maoxian/tiaozhan_off.bmp", at=(771, 435, 907, 473)),
    "chaochushangxian": p(img="img/maoxian/chaochushangxian.bmp", at=(343, 207, 602, 232)),
}
ZHUXIAN_ID = {
    1: p(img="img/zhuxian/1.bmp", at=(453, 74, 516, 88)),
    2: p(img="img/zhuxian/2.bmp", at=(447, 74, 530, 88)),
    3: p(img="img/zhuxian/3.bmp", at=(456, 77, 520, 88)),
    4: p(img="img/zhuxian/4.bmp", at=(447, 74, 527, 86)),
    5: p(img="img/zhuxian/5.bmp", at=(446, 74, 530, 86)),
    6: p(img="img/zhuxian/6.bmp", at=(447, 75, 527, 86)),
    7: p(img="img/zhuxian/7.bmp", at=(437, 74, 488, 88)),
    8: p(img="img/zhuxian/8.bmp", at=(449, 75, 528, 87)),
    9: p(img="img/zhuxian/9.bmp", at=(447, 75, 527, 87)),
    10: p(img="img/zhuxian/10.bmp", at=(450, 74, 531, 86)),
    11: p(img="img/zhuxian/11.bmp", at=(449, 73, 523, 88)),
    12: p(img="img/zhuxian/12.bmp", at=(442, 74, 507, 88)),
}

NORMAL_COORD = {
    1: {
        "right": {
            -1: None
        },
        "left": {
            10: p(830, 350, name="1-10"),
            9: p(750, 250, name="1-9"),
            8: p(612, 200, name="1-8"),
            7: p(612, 310, name="1-7"),
            6: p(546, 372, name="1-6"),
            5: p(482, 287, name="1-5"),
            4: p(378, 244, name="1-4"),
            3: p(320, 340, name="1-3"),
            2: p(230, 250, name="1-2"),
            1: p(100, 300, name="1-1"),
        },
    },
    2: {
        "right": {
            -1: None
        },
        "left": {
            12: p(809, 226, name="2-12"),
            11: p(830, 333, name="2-11"),
            10: p(725, 383, name="2-10"),
            9: p(596, 379, name="2-9"),
            8: p(480, 309, name="2-8"),
            7: p(454, 222, name="2-7"),
            6: p(338, 158, name="2-6"),
            5: p(235, 217, name="2-5"),
            4: p(327, 267, name="2-4"),
            3: p(373, 393, name="2-3"),
            2: p(250, 410, name="2-2"),
            1: p(127, 410, name="2-1"),
        },
    },
    3: {
        "right": {
            -1: None
        },
        "left": {
            12: p(847, 214, name="3-12"),
            11: p(813, 328, name="3-11"),
            10: p(679, 388, name="3-10"),
            9: p(684, 277, name="3-9"),
            8: p(610, 189, name="3-8"),
            7: p(539, 293, name="3-7"),
            6: p(486, 402, name="3-6"),
            5: p(378, 338, name="3-5"),
            4: p(418, 225, name="3-4"),
            3: p(281, 242, name="3-3"),
            2: p(187, 331, name="3-2"),
            1: p(142, 184, name="3-1"),
        },
    },
    4: {
        "right": {
            13: p(667, 429, name="4-13"),
            12: p(783, 334, name="4-12"),
            11: p(734, 224, name="4-11"),
            10: p(614, 249, name="4-10"),
            9: p(475, 228, name="4-9"),
        },
        "left": {
            8: p(775, 282, name="4-8"),
            7: p(661, 214, name="4-7"),
            6: p(634, 359, name="4-6"),
            5: p(494, 375, name="4-5"),
            4: p(508, 228, name="4-4"),
            3: p(386, 274, name="4-3"),
            2: p(278, 320, name="4-2"),
            1: p(187, 237, name="4-1"),
        },
    },
    5: {
        "right": {
            13: p(737, 247, name="5-13"),
            12: p(598, 247, name="5-12"),
            11: p(473, 267, name="5-11"),
            10: p(415, 374, name="5-10"),
        },
        "left": {
            9: p(778, 307, name="5-9"),
            8: p(679, 401, name="5-8"),
            7: p(526, 430, name="5-7"),
            6: p(355, 407, name="5-6"),
            5: p(442, 343, name="5-5"),
            4: p(502, 228, name="5-4"),
            3: p(356, 232, name="5-3"),
            2: p(257, 183, name="5-2"),
            1: p(139, 197, name="5-1"),
        },
    },
    6: {
        "right": {
            14: p(674, 392, name="6-14"),
            13: p(541, 373, name="6-13"),
            12: p(616, 241, name="6-12"),
            11: p(477, 224, name="6-11"),
            10: p(376, 313, name="6-10"),
        },
        "left": {
            9: p(812, 357, name="6-9"),
            8: p(777, 257, name="6-8"),
            7: p(649, 262, name="6-7"),
            6: p(638, 396, name="6-6"),
            5: p(522, 334, name="6-5"),
            4: p(384, 402, name="6-4"),
            3: p(405, 255, name="6-3"),
            2: p(297, 299, name="6-2"),
            1: p(191, 377, name="6-1"),
        },
    },
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
    9: {
        "right": {
            15: p(736, 278, name="9-15"),
            14: p(611, 346, name="9-14"),
            13: p(543, 222, name="9-13"),
            12: p(425, 288, name="9-12"),
            11: p(467, 421, name="9-11"),
            10: p(318, 398, name="9-10"),
            9: p(208, 357, name="9-9"),
            8: p(287, 249, name="9-8"),
        },
        "left": {
            7: p(724, 236, name="9-7"),
            6: p(616, 294, name="9-6"),
            5: p(602, 420, name="9-5"),
            4: p(501, 355, name="9-4"),
            3: p(445, 235, name="9-3"),
            2: p(321, 178, name="9-2"),
            1: p(199, 196, name="9-1"),
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
    },
    "tuitu_status": {
        # 推图状态
        "last": None,
        "max": None,
        "Hlast": None,
        "Hmax": None,
    }

}
# 显然后面还没写
# 等有空补全
# 准备写个GUI来快速标坐标
