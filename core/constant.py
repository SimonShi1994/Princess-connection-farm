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


# 游戏登陆界面的UI
START_UI = {
    "queren": p(572, 464, img="img/ui/caption_queding.bmp", at=(514, 440, 634, 487)),
    "imgbox": p(at=(354, 152, 613, 366)),
    "anying": p(img="img/ui/anying.bmp"),
    "xuanzedian": p(img="img/ui/xuanzedian.bmp"),
    "wenzidianji": p(img="img/ui/wenzidianji.bmp"),
    "yanzhengshibai": p(img="img/ui/yanzhengshibai.bmp"),
}

HAOYOU_BTN = {
    "hysqqr": p(img="img/haoyou/hysqqr.bmp", at=(414, 28, 542, 56)),  # 战斗中的
    "hysqqr_gl": p(img="img/haoyou/hysqqr.bmp", at=(414, 132, 542, 160)),  # 好友管理中的
    "lvmaoicon": p(img="img/haoyou/lvmaoicon.bmp", at=(696, 197, 730, 234)),
    "haoyouguanli_icon": p(img="img/haoyou/haoyouguanli_icon.bmp", at=(66, 17, 155, 44)),
    "xunzhaohaoyou": p(722, 29),
    "sousuosheding": p(839, 90, img="img/haoyou/sousuosheding.bmp", at=(807, 79, 869, 97)),
    "wanjiaidsousuo": p(img="img/haoyou/wanjiaidsousuo.bmp", at=(422, 132, 533, 157)),
    "jianjie": p(img="img/haoyou/jianjie.bmp", at=(454, 28, 499, 55)),
    "info_btn": p(454, 176),
    "name_box": p(at=(385, 149, 595, 172)),
    "hanghui_box": p(at=(531, 237, 695, 255)),
    "accept_btn": p(843, 198),  # 同意
    "reject_btn": p(733, 198),  # 拒
    "hysqtgqr": p(img="img/haoyou/hysqtgqr.bmp", at=(393, 135, 558, 153)),  # 好友申请通过确认
    "hysqjjqr": p(img="img/haoyou/hysqjjqr.bmp", at=(394, 133, 559, 158)),
    "haoyou_sup": p(img="img/haoyou/haoyou_sup.bmp", at=(69, 123, 146, 138)),
    "sqhy": p(img="img/haoyou/sqhy.bmp", at=(434, 133, 524, 160)),
}

# 主页面的按钮对象
MAIN_BTN = {
    # 下载
    "xiazai": p(584, 369, img="img/home/xiazai.bmp", at=(564, 356, 615, 382)),
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
    "dxc": p(935, 77, img="img/home/dxc.bmp", at=(841, 94, 903, 126)),
    # 主线关卡
    "zhuxian": p(500, 90, img="img/home/zhuxian.bmp", at=(526, 117, 587, 186)),
    # 公会之家
    "gonghuizhijia": p(617, 530),
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
    "tili_ok": p(587, 370, img="img/ui/queren_blue.bmp", at=(560, 355, 614, 384)),
    # 体力购买完成ok
    "tili_ok2": p(480, 369, img="img/ui/queren.bmp", at=(382, 351, 578, 390)),

    # mana购买
    "mana_plus": p(189, 62),
    # mana购买界面标题
    "mana_title": p(img="img/home/mana_title.bmp", at=(86, 55, 307, 107)),
    # mana购买界面的空白（用于判断是否进行了1次购买，能否进行十连）
    "mana_blank": p(img="img/home/mana_blank.bmp", at=(740, 460, 895, 497)),
    # mana购买确认
    "mana_ok": p(587, 370, img="img/ui/queren_blue.bmp", at=(560, 355, 614, 384)),
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
    "setting_pic": p(158, 225, img="img/home/setting.bmp", at=(44, 198, 254, 257)),
    "tansuo": p(738, 137),

    # 换号确认
    "huidaobiaotihuamian": p(165, 409),
    "changeacc_queren": p(587, 369, img="img/ui/queren_blue.bmp", at=(560, 355, 614, 384)),
    "querenhuamian_title": p(img="img/home/querenhuamian_title.bmp", at=(437, 131, 522, 159)),
    # 探索
    "jingyanzhiguanqia": p(591, 237, img="img/tansuo/jingyan.bmp", at=(529, 160, 605, 236)),  # 经验值关卡
    "managuanqia": p(801, 221),  # 玛娜关卡
    "tansuo_zero": p(img="img/tansuo/zero.bmp", at=(654, 433, 678, 448)),
    "tansuo_sytzcs": p(img="img/tansuo/sytzcs.bmp", at=(485, 432, 575, 452)),
    "tansuo_back": p(30, 32),
    "tansuo_saodangok2": p(472, 478, img="img/tansuo/jrtssy.bmp", at=(412, 462, 539, 487)),
    "jrtssy2": p(829, 491, img="img/tansuo/jrtssy2.bmp", at=(756, 472, 900, 506)),
    "zdjjc": p(578, 402),
    "gzjjc": p(820, 395),

    # 圣迹调查 （可能不用了）
    # "shengjiguanqia": p(570, 261, img="img/shengji/shengji.bmp", at=(520, 220, 597, 297)),  # 圣迹调查
    # "shengji": p(736, 267, img="img/shengji/shengjidiaocha.bmp", at=(700, 225, 777, 302)),
    "karin_middle": p(img="img/girl/karin_middle.bmp", at=(410, 309, 572, 390)),
    "kailu_middle": p(img="img/girl/kailu_middle.bmp", at=(616, 303, 685, 336)),

    # 调查本
    "diaocha": p(740, 275),
    "shengjidiaocha": p(572, 202, img="img/diaocha/shengjidiaocha.bmp", at=(528, 133, 628, 260)),
    "shendiandiaocha": p(814, 213),
    "shengji_title": p(img="img/diaocha/shengji_title.bmp", at=(61, 11, 163, 47)),
    "shendian_title": p(img="img/diaocha/shendian_title.bmp", at=(62, 12, 161, 44)),

    # 右侧的kkr
    "right_kkr": p(img="img/home/right_kkr.bmp", at=(266, 74, 933, 463)),

    "xzcw": p(img="img/home/xzcw.bmp", at=(438, 135, 520, 157)),  # 下载错误
    # 女神祭
    "nsj": p(541, 430),
    "wanfa": p(img="img/home/wanfa.bmp", at=(234, 6, 275, 64)),  # 玩法

    # 动画设定
    "dhsd": p(img="img/home/donghuasheding.bmp", at=(435, 29, 527, 55)),

    # 活动提示关闭（大范围检测
    "guanbi": p(430, 487, img="img/hanghui/close_btn_1.bmp", at=(199, 393, 742, 526)),
}
JJC_BTN = {
    "list": p(img="img/jjc/list.bmp", at=(821, 77, 888, 103)),  # 列表更新
    "plist": p(img="img/jjc/plist.bmp", at=(826, 79, 886, 102)),
    "shouqu": p(289, 334),
    "shouqu_ok": p(480, 371, img="img/ui/ok_btn_2.bmp", at=(382, 351, 578, 390)),
    "player": p(866, 168),
    "tzcs": p(img="img/jjc/tzcs.bmp", at=(433, 134, 520, 158)),  # 挑战次数
    "zdks": p(834, 454, img="img/jjc/zdks.bmp", at=(760, 429, 911, 473)),  # 战斗开始
    "xyb": p(img="img/jjc/xyb.bmp", at=(794, 474, 857, 503)),
    "pxyb": p(img="img/jjc/pxyb.bmp", at=(774, 476, 844, 505)),
    "dwbz": p(img="img/jjc/dwbz.bmp", at=(431, 24, 524, 51)),  # 队伍编组

}
JUQING_BTN = {
    "caidanyuan": p(920, 36, img="img/juqing/caidanyuan.bmp", at=(903, 26, 931, 55)),
    "xinneirong": p(img="img/ui/xinneirong.bmp", at=(462, 70, 495, 87)),
    "zhuxianjuqing": p(836, 111, img="img/juqing/zhuxianjuqing.bmp", at=(812, 97, 858, 125)),
    "tiaoguo_1": p(804, 38, img="img/juqing/tiaoguo_1.bmp", at=(765, 24, 849, 65)),
    "tiaoguo_2": p(589, 367, img="img/juqing/tiaoguo_2.bmp", at=(567, 356, 611, 379)),
    "new_content": p(img="img/juqing/new_content.bmp", at=(479, 71, 527, 82)),
    "wanfa": p(img="img/juqing/wanfa.bmp", at=(906, 17, 918, 42)),
    "quxiao": p(334, 372, img="img/hanghui/quxiao.bmp", at=(313, 361, 355, 382)),
    "wuyuyin": p(481, 362, img="img/juqing/wuyuyin.bmp", at=(453, 353, 508, 371)),
    "guanbi": p(476, 432, img="img/juqing/guanbi.bmp", at=(454, 418, 498, 445)),
}

LIWU_BTN = {
    "shouqulvli": p(img="img/home/shouqulvli.bmp", at=(98, 461, 202, 489)),
    "quanbushouqu": p(812, 470, img="img/home/quanbushouqu_on.bmp", at=(715, 458, 900, 494)),
    "quxiao": p(597, 478),
    "ok": p(589, 478, img="img/ui/ok_btn_1.bmp", at=(487, 454, 691, 502)),
    "ok2": p(480, 479, img="img/ui/ok_btn_2.bmp", at=(382, 459, 578, 498)),
    "chiyoushangxian": p(img="img/home/chiyoushangxian.bmp", at=(433, 134, 529, 159)),
    "chiyoushangxian_ok": p(481, 371),
    "meiyouliwu": p(img="img/home/meiyouliwu.bmp", at=(342, 243, 512, 272)),
    "yijianshouqu": p(img="img/home/yiijianshouqu_text.bmp", at=(382, 65, 572, 89)),
    "shouqule": p(img="img/home/text_shouqule.bmp", at=(412, 66, 542, 87)),
}
RENWU_BTN = {
    "quanbushouqu_off": p(844, 439, img="img/home/quanbushouqu_off.bmp", at=(747, 421, 939, 455)),
    "quanbushouqu": p(844, 439, img="img/home/quanbushouqu_on.bmp", at=(751, 421, 936, 457)),
    "renwutip": p(img="img/home/renwutip.bmp", at=(456, 364, 794, 393)),
    "guanbi": p(img="img/ui/close_btn_1.bmp", at=(374, 455, 580, 503)),
}
JIAYUAN_BTN = {
    "jiaju": {
        "saodangquan": p(213, 243),
        "jingyan": p(311, 272),
        "mana": p(265, 219),
        "tili": p(264, 294),
    },
    "quxiao": p(img="img/jiayuan/quxiao.bmp"),
    "quanbushouqu": p(900, 424, img="img/jiayuan/quanbushouqu.bmp", at=(872, 395, 926, 454)),
    "guanbi": p(477, 479, img="img/ui/close_btn_1.bmp", at=(374, 455, 580, 503)),
    "jiayuan_shengjiok": p(img="img/jiayuan/jiayuan_shengji.bmp"),
    "jy_dengjitisheng": p(520, 473, img="img/jiayuan/jy_dengjitisheng.bmp", at=(493, 450, 547, 504)),
    "jy_dengjitisheng2": p(img="img/jiayuan/jy_dengjitisheng2.bmp", at=(488, 445, 552, 506)),
    "dengjitisheng": p(589, 431, img="img/jiayuan/dengjitisheng.bmp", at=(491, 410, 682, 452)),
    "xinxi": p(img="img/jiayuan/xinxi.bmp"),
    "zhuye": p(img="img/jiayuan/wodezhuye.bmp", at=(47, 488, 130, 537)),
}

NIUDAN_BTN = {
    # 扭蛋的坐标会偏移！
    "PT_reset_ok": p(479, 365),
    "putong": p(862, 71),
    "putong_mianfei": p(717, 364, img="img/niudan/putong_mianfei.bmp", at=(650, 340, 750, 400)),
    "putong_quxiao": p(367, 370, img="img/ui/quxiao.bmp", at=(274, 352, 468, 388)),
    "putong_ok": p(591, 360, img="img/ui/ok_btn_1.bmp", at=(493, 347, 688, 387)),
    "putong_quxiao_new": p(370, 433, img="img/ui/quxiao2.bmp", at=(300, 418, 439, 449)),
    "putong_ok_new": p(588, 436, img="img/ui/queren_blue.bmp", at=(559, 418, 613, 447)),
    "niudanjieguo_ok": p(481, 443, img="img/ui/ok_btn_2.bmp", at=(383, 423, 597, 462)),
    "putong_wancheng": p(img="img/niudan/putong_wancheng.bmp", at=(610, 320, 750, 450)),
    "niudan_shilian": p(872, 355),
    "juesexiangqing": p(70, 445, img="img/niudan/juesexiangqing.bmp", at=(35, 433, 106, 458)),
    "mianfeishilian": p(img="img/niudan/mianfeishilian.bmp", at=(829, 322, 909, 384)),
    "xiangqing": p(883, 279, img="img/niudan/xiangqing.bmp", at=(865, 268, 906, 286)),
    "again": p(588, 441, img="img/niudan/again.bmp", at=(538, 424, 638, 458)),
    "jiaohuanliebiao": p(852, 442, img="img/niudan/jiaohuanliebiao.bmp", at=(817, 431, 887, 453)),
    "juesejiaohuan": p(477, 42, img="img/niudan/juesejiaohuan.bmp", at=(435, 28, 520, 56)),
    "weijiefang": p(454, 253, img="img/niudan/weijiefang.bmp", at=(420, 242, 488, 265)),
    "new_char": p(454, 253, img="img/niudan/new_char.bmp"),  # 占位，位置不确定，一般直接引用

}

HANGHUI_BTN = {
    "juanzengqingqiu": p(367, 39),
    "juanzeng": p(644, 385),
    # 组建行会（未加入公会）
    "zujianhanghui": p(842, 446, img="img/zujianhanghui.bmp", at=(722, 418, 949, 475)),
    # 设定（加入行会）
    "sheding_join": p(860, 79, img="img/hanghui/sheding_join.bmp", at=(840, 68, 879, 89)),
    # 加入行会设定输入框
    "input_join": p(370, 145, img="img/hanghui/input_join.bmp", at=(303, 86, 458, 124)),
    # 搜索（加入行会蓝条）
    "sousuo_join": p(589, 478, img="img/hanghui/sousuo_join.bmp", at=(480, 447, 702, 507)),
    # 进入行会（从搜索界面）
    "in_join": p(890, 155, img="img/hanghui/in_join.bmp", at=(878, 126, 902, 185)),
    # 加入行会
    "join_btn": p(854, 444, img='img/jiaru.bmp', at=(749, 427, 933, 460)),
    # 支援设定
    "zhiyuansheding": p(84, 357, img="img/hanghui/zhiyuansheding.bmp", at=(52, 346, 119, 369)),
    # 地下城支援1
    "zhiyuan_dxc1": p(78, 208, img="img/hanghui/zhiyuanjuese.bmp", at=(52, 182, 103, 233)),
    # 地下城支援2
    "zhiyuan_dxc2": p(78, 353, img="img/hanghui/zhiyuanjuese.bmp", at=(52, 327, 103, 378)),
    # 团队露娜塔支援1
    "zhiyuan_lnt1": p(381, 208, img="img/hanghui/zhiyuanjuese.bmp", at=(355, 182, 406, 233)),
    # 团队露娜塔支援2
    "zhiyuan_lnt2": p(381, 353, img="img/hanghui/zhiyuanjuese.bmp", at=(355, 327, 406, 378)),
    # 主线支援1
    "zhiyuan_zx1": p(684, 208, img="img/hanghui/zhiyuanjuese.bmp", at=(658, 182, 709, 233)),
    # 主线支援2
    "zhiyuan_zx2": p(684, 353, img="img/hanghui/zhiyuanjuese.bmp", at=(658, 327, 709, 378)),
    # 支援取消
    "zhiyuanquxiao": p(img="img/hanghui/zhiyuanquxiao.bmp", at=(645, 438, 694, 466)),
    # 战力排序（支援界面）用于判断是否处在战力排序状态
    "zhanlipaixu": p(img="img/hanghui/zhanlipaixu.bmp", at=(684, 78, 722, 100)),
    # 降序（支援界面）
    "jiangxu_juese": p(863, 90, img="img/hanghui/jiangxu_juese.bmp", at=(828, 78, 903, 99)),
    # 筛选条件（支援界面）
    "shaixuantiaojian_juese": p(788, 88, img="img/hanghui/shaixuantiaojian_juese.bmp", at=(777, 78, 800, 99)),
    # 角色战力”确认“蓝点
    "zhanli_juese": p(289, 141, img="img/hanghui/landian_true.bmp", at=(266, 118, 311, 164)),
    # 角色筛选条件界面确认
    "hanghui_ok_juese": p(591, 476, img="img/hanghui/hanghui_ok.bmp", at=(553, 461, 629, 490)),
    # 角色选择1
    "juese1": p(102, 162),
    # 角色选择2
    "juese2": p(210, 164),
    # 角色选择3
    "juese3": p(318, 166),
    # 角色选择4
    "juese4": p(431, 166),
    # 角色选择确认
    "juesesheding": p(838, 454, img="img/hanghui/juesesheding.bmp", at=(791, 440, 885, 466)),
    # 角色选择二次确认
    "hanghui_ok_double": p(591, 431, img="img/hanghui/hanghui_ok.bmp", at=(553, 416, 630, 446)),

    # 返回键隔壁的“行会”字样
    "hanghui_title": p(img="img/hanghui.bmp", at=(63, 12, 123, 45)),
    # 成员信息
    "chengyuanxinxi": p(239, 356, img="img/hanghui/chengyuanxinxi.bmp", at=(203, 345, 271, 366)),
    # 成员信息界面的“成员列表”按钮
    "chengyuanliebiao": p(img='img/chengyuanliebiao.bmp', at=(329, 15, 450, 42)),
    # 筛选条件（成员界面）
    "shaixuantiaojian_chengyuan": p(793, 84, img="img/hanghui/shaixuantiaojian_chengyuan.bmp", at=(782, 80, 810, 103)),
    # 筛选条件里的分类
    "fenlei": p(img="img/hanghui/fenlei.bmp", at=(454, 132, 501, 158)),
    # 成员全角色战力"确认"蓝点
    "zhanli_chengyuan": p(285, 299, img="img/hanghui/landian_true.bmp", at=(265, 280, 310, 326)),
    # 降序按钮（筛选成员界面）
    "jiangxu_chengyuan": p(868, 92, img="img/hanghui/jiangxu_chengyuan.bmp", at=(843, 82, 876, 102)),
    # 成员管理(第一个)
    "chengyuanguanli_first": p(727, 191, img="img/hanghui/chengyuanguanli.bmp", at=(701, 185, 768, 211)),
    # 开除
    "kaichu": p(647, 170, img="img/hanghui/kaichu.bmp", at=(627, 159, 668, 182)),
    # 行会确认（这里兼顾了两个不同的ok，一个正中，一个偏右）
    "hanghui_ok": p(588, 369, img="img/hanghui/hanghui_ok.bmp", at=(557, 354, 620, 385)),
    # 请求捐赠装备
    "qqjzzb": p(402, 430, img="img/hanghui/qqzjzb.bmp", at=(356, 422, 449, 441)),
    # 发起捐赠请求
    "fqjzqq": p(585, 477, img="img/hanghui/fqjzqq.bmp", at=(521, 460, 651, 495)),
    # 确认发出请求
    "jzqq_ok": p(589, 433, img="img/ui/ok_btn_1.bmp", at=(487, 409, 691, 457)),
    # 稀有度
    "sort_xiyou": p(694, 83, img="img/hanghui/sort_xiyou.bmp", at=(670, 73, 719, 90)),
    # 降序（捐赠装备）
    "sort_down": p(860, 82, img="img/hanghui/sort_down.bmp", at=(841, 73, 877, 91)),
    # 分类（捐赠装备）-ok
    "sort_ok": p(590, 370, img="img/ui/ok_btn_1.bmp", at=(488, 346, 692, 394)),
    # 捐赠请求情况
    "jzqqqk": p(405, 429, img="img/hanghui/jzqqqk.bmp", at=(351, 421, 450, 441)),
    # 捐赠请求结果
    "jzqqjg": p(402, 432, img="img/hanghui/jzqqjg.bmp", at=(357, 422, 447, 436)),
    # 撤下支援 1
    "zyjs_1": p(239, 255),
    # 撤下支援 2
    "zyjs_2": p(239, 404),
    # 支援结束确认
    "zyjsqr": p(img="img/hanghui/zyjsqr.bmp", at=(419, 133, 540, 155)),
    # 支援结束确认_ok
    "zyjsqr_ok": p(590, 370, img="img/ui/ok_btn_1.bmp", at=(533, 348, 649, 390)),
    # 收取报酬
    "sqbc": p(img="img/hanghui/sqbc.bmp", at=(439, 32, 521, 52)),

}
TUANDUIZHAN_BTN = {
    "tuanduizhan": p(img="img/hanghui/tuanduizhan.bmp", at=(805, 204, 950, 346)),
    "shangbiao": p(img="img/hanghui/shangbiao.bmp"),
    "taofaxinxi": p(img="img/hanghui/taofaxinxi.bmp", at=(248, 412, 356, 454)),
    "tiaozhan": p(833, 462, img="img/hanghui/tiaozhan.bmp", at=(738, 422, 924, 497)),
    "zhandou": p(587, 374, img="img/hanghui/zhandou.bmp", at=(473, 334, 696, 400)),
    "qianwangguanqia": p(592, 436, img="img/hanghui/qianwangguanqia.bmp", at=(478, 404, 697, 462)),
    "guanbi": p(430, 487, img="img/hanghui/close_btn_1.bmp", at=(199, 393, 742, 526)),
}
ZHUCAIDAN_BTN = {
    "bangzhu": p(img="img/zhucaidan/bangzhu.bmp", at=(52, 293, 253, 335)),
    "jianjie": p(img="img/zhucaidan/jianjie.bmp", at=(267, 241, 499, 290)),
    "daoju": p(475, 160, img="img/zhucaidan/daoju.bmp", at=(475, 112, 610, 187)),
    "saodangquan": p(img="img/zhucaidan/saodangquan.bmp"),
    "jianjie_L": p(img="img/zhucaidan/jianjie_L.bmp", at=(59, 1, 137, 48)),
    "daojuyilan": p(img="img/zhucaidan/daojuyilan.bmp", at=(57, 3, 172, 51)),
    "chushou": p(843, 428, img="img/zhucaidan/chushou.bmp", at=(786, 410, 901, 441)),
    "chiyoushu": p(705, 31, img="img/zhucaidan/chiyoushu.bmp", at=(680, 20, 730, 40)),
    "zhuangbei": p(460, 33),
    "jiangxu": p(865, 31, img="img/zhucaidan/jiangxu.bmp", at=(849, 22, 881, 41)),
    "chushouqueren": p(img="img/zhucaidan/chushouqueren.bmp", at=(434, 30, 521, 53)),
    "chushouwanbi": p(img="img/zhucaidan/chushouwanbi.bmp", at=(434, 133, 522, 154)),
    "chushou2": p(584, 483),
    "sortico": p(img="img/zhucaidan/sortico.bmp", at=(800, 21, 824, 41)),
    "sale_short": p(846, 428, img="img/zhucaidan/sale_short.bmp", at=(820, 419, 871, 436)),
    "sale_long": p(771, 428, img="img/zhucaidan/sale_short.bmp", at=(745, 419, 796, 436))

}
FIGHT_BTN = {
    "auto_on": p(914, 420, img="img/fight/auto_on.bmp", at=(892, 410, 930, 434)),
    "auto_off": p(914, 421, img="img/fight/auto_off.bmp", at=(894, 411, 931, 433)),
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
    "cat_ok": p(587, 478, img="img/ui/queren_blue.bmp", at=(559, 463, 613, 492)),  # 分类界面：OK
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
    "team_close": p(476, 477, img="img/ui/close_btn_1.bmp", at=(374, 455, 580, 503)),  # 选队界面的关闭按钮
    "shbg": p(img="img/fight/shbg.bmp", at=(804, 24, 902, 54)),  # 伤害报告
    "duiwu_icon": p(img="img/fight/duiwu_icon.bmp", at=(896, 78, 924, 97)),
    "huodedaoju": p(img="img/fight/huodedaoju.bmp", at=(442, 135, 514, 160)),
    "xiayibu_fight": p(img="img/fight/xiayibu.bmp", at=(794, 475, 864, 502)),
    "menu": p(img="img/fight/menu.bmp", at=(871, 18, 928, 32)),
    "qwjsyl": p(576, 495, img="img/fight/qwjsyl.bmp", at=(392, 457, 948, 528)),  # 前往角色一览
    "win": p(img="img/fight/win.bmp", at=(400, 6, 551, 127)),  # 过关的帽子
    "zhandoukaishi": p(834, 453, img="img/fight/zhandoukaishi.bmp", at=(761, 431, 911, 472)),
    "duiwubianzu": p(img="img/fight/duiwubianzu.bmp", at=(433, 31, 520, 53)),
    "xuanguan_quxiao": p(665, 455, img="img/ui/quxiao2.bmp", at=(597, 440, 736, 470)),  # 选关界面（选择使用扫荡券）右下角的取消
    "upperright_stars":  # “挑战”页面右上角的星星位置
        {
            1: p(762, 35),
            2: p(825, 35),
            3: p(889, 35),
        },
    "tiaozhan": p(839, 456, img="img/ui/tiaozhan.bmp", at=(788, 444, 889, 467)),
    "tiaozhan2": p(839, 453, img="img/ui/tiaozhan2.bmp", at=(814, 440, 865, 466)),
    # 应对周年庆UI变动，删除xiayibu2 的 at=(785, 477, 870, 505)
    "xiayibu2": p(829, 490, img="img/ui/xiayibu2.bmp"),  # 短的下一步，用于“战利品”界面
    # 应对周年庆UI变动，删除xiayibu 的 at=(729, 465, 939, 521)
    "xiayibu": p(832, 504, img="img/ui/xiayibu.bmp"),  # 长的下一步，用于经验值、好感度页面
    "qwzxgq": p(808, 493, img="img/fight/qwzxgq.bmp", at=(745, 481, 869, 504)),  # 前往主线关卡：输的时候会显示
    "baochou": p(img="img/fight/baochou.bmp", at=(61, 414, 114, 481)),
    "dengjitisheng": p(img="img/fight/dengjitisheng.bmp", at=(431, 132, 525, 158)),
    "caidan": p(902, 33, img="img/fight/menu.bmp", at=(856, 14, 942, 35)),
    "fangqi_1": p(625, 376, img="img/fight/fangqi_1.bmp", at=(558, 346, 690, 392)),
    "fangqi_2": p(625, 376, img="img/fight/fangqi_2.bmp", at=(491, 346, 686, 392)),
    "tgdw": p(img="img/fight/tgdw.bmp", at=(805, 82, 900, 105)),
    "infinity": p(img="img/fight/infinity.bmp", at=(897, 407, 920, 420)),
    "fighting_caidan": p(img="img/fight/fighting_caidan.bmp", at=(882, 18, 918, 32)),
    "zhandou_failed": p(img="img/fight/zhandou_failed.bmp"),
}

SHOP_BTN = {
    "mana_ball": p(img="img/shop/mana_ball.bmp", at=(744, 13, 762, 34)),
    "dxc_coin": p(img="img/shop/dxc_coin.bmp", at=(744, 14, 762, 33)),
    "jjc_coin": p(img="img/shop/jjc_coin.bmp", at=(744, 14, 763, 32)),
    "pjjc_coin": p(img="img/shop/pjjc_coin.bmp", at=(744, 14, 765, 33)),
    "clan_coin": p(img="img/shop/clan_coin.bmp", at=(744, 14, 763, 33)),
    "nvshenshi": p(img="img/shop/nvshenshi.bmp", at=(527, 13, 544, 33)),
    "xianding_cishu": p(img="img/shop/xianding_cishu.bmp", at=(252, 427, 299, 447)),
    "xianding_close": p(img="img/shop/xianding_close.bmp", at=(516, 213, 666, 244)),
    "dxc_btn": p(363, 68, img="img/shop/dxc_btn.bmp", at=(314, 56, 400, 80)),
    "jjc_btn": p(447, 68, img="img/shop/jjc_btn.bmp", at=(411, 57, 485, 78)),
    "pjjc_btn": p(543, 68, img="img/shop/pjjc_btn.bmp", at=(500, 56, 588, 78)),
    "clan_btn": p(640, 65, img="img/shop/clan_btn.bmp", at=(602, 57, 666, 79)),
    "nvshen_btn": p(829, 65, img="img/shop/nvshen_btn.bmp", at=(776, 57, 864, 77)),
    "xianding_ok": p(589, 478, img="img/ui/ok_btn_1.bmp", at=(487, 454, 691, 502)),
    "shop_left_kkr": p(img="img/girl/kkr_middle.bmp", at=(78, 311, 179, 339)),
    "lijiguanbi": p(527, 438),
    "querenchongzhi": p(590, 370, img="img/ui/ok_btn_1.bmp", at=(488, 346, 692, 394)),
    "fanhui": p(30, 29, img="img/ui/fanhui.bmp", at=(16, 16, 45, 43)),
    "middle_kkr": p(img="img/girl/kkr_middle.bmp", at=(430, 311, 531, 339)),

}

JUESE_BTN = {
    "duiwu": p(img="img/juese/duiwu.bmp", at=(853, 15, 929, 35)),
    "mana_ball": p(img="img/juese/mana_ball.bmp", at=(609, 21, 620, 34)),
    "first_juese": p(175, 140),
    "nine_juese": {
        1: p(173, 147),
        2: p(464, 150),
        3: p(768, 145),
        4: p(174, 290),
        5: p(480, 292),
        6: p(772, 299),
        7: p(163, 438),
        8: p(476, 430),
        9: p(789, 427),
    },
    "zdqh_0": p(368, 436, img="img/juese/zdqh_0.bmp", at=(422, 407, 440, 423)),
    "zdqh_1": p(368, 436, img="img/juese/zdqh_1.bmp", at=(418, 406, 439, 424)),
    "zdqh_2": p(img="img/juese/zdqh_2.bmp", at=(310, 444, 431, 467)),
    "reachable": p(img="img/juese/reachable.bmp", at=(372, 158, 395, 170)),  # 占位，位置不确定，一般直接引用
    "enter_shuatu": p(669, 230, img="img/juese/enter_shuatu.bmp", at=(657, 202, 680, 258)),
    "equip_selected": p(527, 73, img="img/juese/equip_selected.bmp", at=(511, 63, 549, 86)),
    "equip_unselected": p(527, 73, img="img/juese/equip_unselected.bmp", at=(491, 65, 547, 85)),
    "char_lv_selected": p(611, 74, img="img/juese/char_lv_selected.bmp", at=(579, 63, 645, 85)),
    "char_lv_unselected": p(611, 74, img="img/juese/char_lv_unselected.bmp", at=(572, 64, 627, 86)),
    "skill_lv_selected": p(697, 74, img="img/juese/skill_lv_selected.bmp", at=(664, 63, 734, 87)),
    "skill_lv_unselected": p(697, 74, img="img/juese/skill_lv_unselected.bmp", at=(658, 64, 714, 86)),
    "tuijiancaidan": p(479, 42, img="img/juese/tuijiancaidan.bmp", at=(413, 31, 544, 53)),
    "kaihua_unselected": p(782, 75, img="img/juese/kaihua_unselected.bmp", at=(749, 64, 819, 85)),
    "kaihua_selected": p(782, 75, img="img/juese/kaihua_selected.bmp", at=(752, 63, 818, 87)),
    "kaihua_max": p(img="img/juese/kaihua_max.bmp", at=(590, 319, 807, 339)),
    "kaihua_not_enough": p(img="img/juese/kaihua_not_enough.bmp", at=(651, 385, 751, 403)),
    "do_kaihua": p(802, 433, img="img/juese/do_kaihua.bmp", at=(765, 425, 850, 444)),
    "kaihua_confirm": p(587, 473, img="img/juese/kaihua_confirm.bmp", at=(543, 462, 633, 490)),
    "kaihua_complete": p(417, 462, img="img/juese/kaihua_complete.bmp", at=(416, 30, 542, 53)),
    "zhuanwu_selected": p(869, 75, img="img/juese/zhuanwu_selected.bmp", at=(839, 66, 900, 86)),
    "zhuanwu_unselected": p(869, 75, img="img/juese/zhuanwu_unselected.bmp", at=(831, 64, 886, 85)),
    "kaihua_enough": p(img="img/juese/kaihua_enough.bmp", at=(665, 280, 729, 302)),
    "zhuanwu_lock": p(img="img/juese/zhuanwu_lock.bmp", at=(662, 172, 734, 243)),
    "zhuanwu_equipable": p(img="img/juese/zhuanwu_equipable.bmp", at=(261, 126, 266, 130)),
    "wear": p(802, 435, img="img/juese/wear.bmp", at=(777, 421, 836, 449)),
    "wear_confirm": p(587, 476, img="img/juese/wear_confirm.bmp", at=(561, 462, 615, 491)),
    "unlock_ceiling_confirm": p(585, 476, img="img/juese/unlock_ceiling_confirm.bmp", at=(538, 460, 636, 492)),
    "unlock_ceiling": p(585, 435, img="img/juese/unlock_ceiling.bmp", at=(545, 424, 630, 446)),
    "unlock_ceiling_off": p(img="img/juese/unlock_ceiling_off.bmp", at=(532, 419, 646, 453)),
    "unlock_ceiling_need_lv": p(img="img/juese/unlock_ceiling_need_lv.bmp", at=(388, 420, 458, 443)),
    "levelup_zhuanwu": p(805, 435, img="img/juese/levelup_zhuanwu.bmp", at=(779, 422, 833, 448)),
    "qhscxz": p(img="img/juese/qhscxz.bmp", at=(65, 69, 164, 90)),  # 强化素材选择
    "bnjxqh": p(img="img/juese/bnjxqh.bmp", at=(594, 419, 805, 443)),  # 不能继续强化
    "sucaibuzu": p(img="img/juese/sucaibuzu.bmp", at=(447, 420, 514, 441)),
    "zhuanwuqianghua": p(804, 471, img="img/juese/zhuanwuqianghua.bmp", at=(781, 461, 831, 488)),
    "rank_on": p(245, 332, img="img/juese/rank_on.bmp", at=(209, 326, 282, 343)),
    "rank_up_ok": p(587, 478, img="img/juese/rank_up_ok.bmp", at=(566, 467, 608, 488)),
    "rank_up_complete": p(476, 367, img="img/juese/queren_white.bmp", at=(451, 355, 501, 379)),
    "yjzb_off": p(img="img/juese/yjzb_off.bmp", at=(207, 319, 288, 349)),
    "zdqh_ok": p(580, 480, img="img/juese/zdqh_ok.bmp", at=(563, 462, 612, 490)),
    "rank_tisheng": p(246, 333, img="img/juese/rank_tisheng.bmp", at=(214, 327, 283, 340)),
    "rank_tisheng_ok": p(589, 478, img="img/ui/ok_btn_1.bmp", at=(487, 454, 691, 502)),
    "rank_tisheng_ok_noequ": p(588, 369, img="img/juese/ok_btn.bmp", at=(567, 358, 611, 380)),  # 不需要消耗时，强化的OK在上头
    "rank_tisheng_ok2": p(480, 371, img="img/ui/ok_btn_2.bmp", at=(382, 351, 578, 390)),
    "yjzb": p(241, 330, img="img/juese/yjzb.bmp", at=(197, 323, 294, 345)),
    "zdqh": p(368, 436, img="img/juese/zdqh.bmp", at=(313, 418, 418, 450)),
    "tjqhcd": p(img="img/juese/tjqhcd.bmp", at=(414, 31, 541, 49)),
    "sort_down": p(744, 28, img="img/juese/sort_down.bmp", at=(753, 18, 798, 38)),
    "sort_up": p(755, 28, img="img/juese/sort_up.bmp", at=(756, 17, 798, 36)),
    "sort_by": p(715, 26, img="img/juese/sort_by.bmp", at=(703, 15, 726, 36)),
    "fenlei": p(483, 41, img="img/juese/fenlei.bmp", at=(458, 29, 508, 54)),
    "sort_level": p(629, 27, img="img/juese/sort_level.bmp", at=(611, 16, 647, 36)),
    "tuijianguanqia": p(img="img/juese/tuijianguanqia.bmp", at=(280, 90, 327, 102)),
    "firstqianghua_stars": {
        1: p(587, 257),
        2: p(612, 256),
        3: p(637, 257),
    },
    "return_ok": p(476, 475, img="img/juese/queren_white.bmp", at=(451, 463, 501, 487)),  # 返还强化道具

}
MAX_DXC = 5  # 一共出了多少个地下城关

DXC_ELEMENT = {
    # 由于识别率不佳，暂时不用
    # "right": p(14, 242, img="img/dxc/right.bmp", at=(10, 195, 56, 277)),
    # "left": p(945, 242, img="img/dxc/left.bmp", at=(898, 194, 949, 277)),
    "right": p(14, 242),
    "left": p(945, 242),
    "zyjsqr": p(img="img/dxc/zyjsqr.bmp", at=(412, 29, 549, 54)),
    "zyjsqr_ok": p(595, 471),
    "chetui": p(876, 427, img="img/dxc/chetui.bmp", at=(830, 407, 929, 448)),
    "chetui_ok": p(591, 365, img="img/ui/ok_btn_1.bmp", at=(488, 346, 692, 394)),
    "chetuiqueren": p(img="img/dxc/chetuiqueren.bmp", at=(433, 134, 521, 158)),
    "sytzcs": p(723, 438, img="img/dxc/sytzcs.bmp", at=(667, 428, 784, 447)),
    "kyzdjs": p(img="img/dxc/kyzdjs.bmp", at=(591, 377, 687, 396)),
    "ceng": p(img="img/dxc/ceng.bmp"),
    "in_sytzcs": p(img="img/dxc/in_sytzcs.bmp", at=(639, 421, 731, 438)),
    "1/1": p(img="img/dxc/dxc_1_1.bmp", at=(887, 429, 913, 446)),
    "0/1": p(img="img/dxc/dxc_0_1.bmp", at=(883, 429, 910, 445)),
    "qwdxc": p(810, 489),  # 失败：前往地下城
    "shop": p(at=(889, 9, 938, 66)),
    "map": p(at=(7, 66, 954, 391)),
    "xiayibu": p(836, 503, img="img/ui/xiayibu.bmp", at=(731, 480, 932, 527)),
    "shouqubaochou_ok": p(480, 477, img="img/ui/queren.bmp", at=(450, 465, 509, 489)),
    "qianwangdixiacheng": p(805, 495),
    "qyxzqr": p(img="img/dxc/qyxzqr.bmp", at=(415, 135, 540, 157)),
    "quyuxuanzequeren_ok": p(587, 370, img="img/ui/queren_blue.bmp", at=(560, 355, 614, 384)),
    "dxc_kkr": p(img="img/dxc/dxc_kkr.bmp", at=(442, 175, 527, 271)),
    # 判断是否在地下城商店内（用于新手教程）
    "dxc_in_shop": p(873, 437, img="img/dxc/dxc_in_shop.bmp", at=(810, 427, 933, 446)),
    # 商店按钮，此商店按钮与jjc的不同，要大一点
    "dxc_shop_btn": p(918, 30, img="img/dxc/shop.bmp", at=(883, 1, 947, 69)),
    # 地下城选关界面商店
    "dxc_choose_shop": p(917, 28, img="img/dxc/dxc_choose_shop.bmp", at=(883, 1, 947, 69)),
    # 支援
    "zhiyuan_dianren": {
        1: p(100, 173),
        2: p(213, 208),
        3: p(324, 173),
        4: p(427, 173),
        5: p(533, 173),
        6: p(640, 173),
        7: p(746, 173),
        8: p(855, 173),
    },
    # 勾选了支援
    # 1: p(100, 173, img="img/dxc/dxc_gouxuan.bmp", at=(158, 142, 164, 164)),
    # 2: p(213, 208, img="img/dxc/dxc_gouxuan.bmp", at=(260, 131, 295, 185)),
    "zhiyuan_gouxuan": p(img="img/dxc/dxc_gouxuan.bmp"),
    "quanbu_white": p(98, 88, img="img/dxc/quanbu_white.bmp", at=(49, 71, 141, 109)),
    "quanbu_blue": p(98, 88, img="img/dxc/quanbu_blue.bmp", at=(49, 71, 141, 109)),
    "zhandoukaishi": p(833, 470, img="img/dxc/zhandoukaishi.bmp", at=(761, 430, 912, 471)),
    "zhiyuan_white": p(477, 86, img="img/dxc/zhiyuan_white.bmp", at=(433, 75, 524, 99)),
    "zhiyuan_blue": p(477, 86, img="img/dxc/zhiyuan_blue.bmp", at=(430, 73, 521, 104)),
    "ok_btn_1": p(588, 371, img="img/ui/ok_btn_1.bmp"),
    "d1_queren_blue": p(588, 371, img="img/ui/queren_blue.bmp"),
    "sheding": p(478, 443, img="img/dxc/sheding.bmp"),
}
DXC_NUM = {
    # 没有OCR用此来检测层数
    1: {
        1: p(img="img/dxc/dxc1/1.bmp", at=(214, 425, 226, 439)),
        2: p(img="img/dxc/dxc1/2.bmp", at=(207, 423, 224, 438)),
        3: p(img="img/dxc/dxc1/3.bmp", at=(210, 425, 224, 438)),
        4: p(img="img/dxc/dxc1/4.bmp", at=(211, 424, 226, 441)),
        5: p(img="img/dxc/dxc1/5.bmp", at=(212, 424, 223, 440)),
        6: p(img="img/dxc/dxc1/6.bmp", at=(209, 426, 224, 438)),
        7: p(img="img/dxc/dxc1/7.bmp", at=(206, 425, 225, 442)),
    },
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
    },
    4: {
        1: p(img="img/dxc/dxc4/1.bmp", at=(207, 422, 227, 441)),
        2: p(img="img/dxc/dxc4/2.bmp", at=(206, 424, 224, 439)),
        3: p(img="img/dxc/dxc4/3.bmp", at=(206, 424, 225, 439)),
        4: p(img="img/dxc/dxc4/4.bmp", at=(206, 424, 225, 438)),
        5: p(img="img/dxc/dxc4/5.bmp", at=(201, 426, 226, 439)),
    },
    5: {
        1: p(img="img/dxc/dxc5/1.bmp", at=(216, 423, 226, 440)),
        2: p(img="img/dxc/dxc5/2.bmp", at=(214, 425, 225, 438)),
        3: p(img="img/dxc/dxc5/3.bmp", at=(210, 425, 227, 438)),
        4: p(img="img/dxc/dxc5/4.bmp", at=(214, 425, 226, 439)),
        5: p(img="img/dxc/dxc5/5.bmp", at=(215, 425, 225, 439)),
    }
}
DXC_ENTRANCE = {
    # 大按钮：云海、密林、断崖的坐标
    1: p(129, 244, name="云海的山脉"),
    2: p(366, 245, name="密林的大树"),
    3: p(600, 246, name="断崖的遗迹"),
    4: p(831, 246, name="沧海的孤塔"),
    5: p(831, 246, name="EX 2"),
}
DXC_ENTRANCE_DRAG = {
    1: "left",
    2: "left",
    3: "left",
    4: "left",
    5: "right",
}
DXC_COORD = {
    # 每个地下城里面每一个关卡的位置
    1: {
        1: p(664, 297),
        2: p(474, 272),
        3: p(304, 268),
        4: p(545, 273),
        5: p(419, 283),
        6: p(596, 283),
        7: p(460, 235),
    },
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
    },
    4: {
        1: p(694, 295),
        2: p(614, 278),
        3: p(325, 283),
        4: p(681, 285),
        5: p(297, 190)
    },
    5: {
        1: p(455, 245),
        2: p(629, 266),
        3: p(491, 262),
        4: p(425, 250),
        5: p(502, 259),
    }
}
MAX_MAP = 30
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
    13: {
        1: p(222, 245),
        2: p(485, 348),
        3: p(765, 342),
    },
    14: {
        1: p(214, 346),
        2: p(480, 249),
        3: p(767, 333),
    },
    15: {
        1: p(210, 224),
        2: p(477, 365),
        3: p(765, 278),
    },
    16: {
        1: p(212, 361),
        2: p(481, 266),
        3: p(754, 282),
    },
    17: {
        1: p(215, 282),
        2: p(479, 347),
        3: p(762, 273),
    },
    18: {
        1: p(214, 268),
        2: p(481, 361),
        3: p(762, 287),
    },
    19: {
        1: p(224, 324),
        2: p(473, 262),
        3: p(764, 317),
    },
    20: {
        1: p(215, 270),
        2: p(476, 331),
        3: p(766, 269),
    },
    21: {
        1: p(220, 277),
        2: p(487, 330),
        3: p(765, 265),
    },
    22: {
        1: p(210, 340),
        2: p(478, 271),
        3: p(762, 324),
    },
    23: {
        1: p(216, 287),
        2: p(477, 336),
        3: p(765, 251),
    },
    24: {
        1: p(216, 293),
        2: p(476, 361),
        3: p(766, 262),
    },
    25: {
        1: p(218, 297),
        2: p(481, 359),
        3: p(769, 257),
    },
    26: {
        1: p(214, 288),
        2: p(475, 235),
        3: p(762, 334),
    },
    27: {
        1: p(212, 270),
        2: p(475, 350),
        3: p(765, 282),
    },
    28: {
        1: p(243, 226),
        2: p(491, 338),
        3: p(779, 270),
    },
    29: {
        1: p(175, 330),
        2: p(446, 199),
        3: p(779, 324),
    },
    30: {
        1: p(175, 253),
        2: p(479, 228),
        3: p(775, 324),
    },
}

MAOXIAN_BTN = {
    "bianzusheding": p(img="img/maoxian/bianzusheding.bmp", at=(373, 124, 590, 164)),
    "bianzusheding_ok": p(436, 162),
    "normal_on": p(582, 83, img="img/maoxian/normal_on.bmp", at=(558, 74, 607, 95)),
    "normal_off": p(581, 84, img="img/maoxian/normal_off.bmp", at=(555, 74, 609, 95)),
    "hard_on": p(701, 84, img="img/maoxian/hard_on.bmp", at=(671, 72, 731, 95)),
    "hard_off": p(700, 79, img="img/maoxian/hard_off.bmp", at=(676, 74, 726, 94)),
    "vh_off": p(820, 83, img="img/maoxian/vh_off.bmp", at=(798, 74, 844, 93)),
    "vh_on": p(820, 85, img="img/maoxian/vh_on.bmp", at=(793, 74, 848, 96)),
    "hard_0_3": p(img="img/maoxian/hard_0_3.bmp", at=(887, 402, 919, 422)),  # 剩余挑战次数0/3
    "ditu": p(img="img/maoxian/ditu.bmp", at=(906, 64, 930, 106)),
    "tili_bar": p(at=(529, 32, 637, 38), fc=(255, 215, 99), bc=(90, 101, 115)),
    "saodang_on": p(753, 334, img="img/maoxian/saodang_on.bmp", at=(679, 314, 826, 349)),  # 使用1张 蓝色
    "saodang_plus": p(878, 328),
    "saodang_minus": p(626, 330),
    "saodang_ok": p(590, 370, img="img/ui/ok_btn_1.bmp", at=(488, 346, 692, 394)),
    "saodang_tiaoguo": p(476, 476, img="img/maoxian/saodang_tiaoguo.bmp", at=(435, 463, 525, 489)),
    "saodang_ok2": p(480, 479, img="img/ui/ok_btn_2.bmp", at=(454, 463, 499, 491)),
    "saodang_off": p(753, 334, img="img/maoxian/saodang_off.bmp", at=(680, 315, 824, 350)),  # 使用1张 灰色
    "quxiao": p(667, 455, img="img/ui/quxiao2.bmp", at=(597, 440, 736, 470)),
    "xianding": p(586, 368, img="img/maoxian/xianding.bmp", at=(520, 354, 657, 380)),
    "xianding_quxiao": p(371, 370, img="img/ui/quxiao.bmp", at=(274, 352, 468, 388)),
    "zaicitiaozhan": p(658, 489, img="img/maoxian/zaicitiaozhan.bmp", at=(592, 475, 723, 505)),
    "chongshi_ok": p(590, 370, img="img/ui/ok_btn_1.bmp", at=(488, 346, 692, 394)),
    "no_tili": p(img="img/maoxian/no_tili.bmp", at=(429, 242, 518, 287)),
    "buytili_ok": p(587, 370, img="img/ui/queren_blue.bmp", at=(560, 355, 614, 384)),
    "buytili_quxiao": p(371, 370, img="img/ui/quxiao.bmp", at=(274, 352, 468, 388)),
    "buytili_ok2": p(480, 369, img="img/ui/queren.bmp", at=(382, 351, 578, 390)),
    "tlhf": p(img="img/maoxian/tlhf.bmp", at=(434, 137, 524, 157)),
    "tili_success": p(img="img/maoxian/tili_success.bmp", at=(262, 274, 404, 335)),
    "no_cishu": p(img="img/maoxian/no_cishu.bmp", at=(400, 229, 541, 289)),
    "chaochushangxian": p(img="img/maoxian/chaochushangxian.bmp", at=(343, 207, 602, 232)),
    "sytzcshf": p(img="img/maoxian/sytzcshf.bmp", at=(391, 132, 562, 155)),  # 剩余挑战次数恢复
    "lock": p(img="img/maoxian/lock.bmp"),
    "tiaozhan_off": p(img="img/maoxian/tiaozhan_off.bmp", at=(768, 437, 909, 468)),
    "tiaozhan_on": p(img="img/maoxian/tiaozhan_on.bmp", at=(768, 439, 910, 470)),
    "tuanduizhan": p(img="img/maoxian/tztdzb.bmp", at=(415, 77, 540, 97)),
    "tuanduizhan_quxiao": p(371, 433, img="img/ui/quxiao.bmp", at=(274, 415, 468, 451)),
    "sdqqr": p(img="img/maoxian/sdqqr.bmp", at=(429, 129, 527, 154)),  # 扫荡券确认
    "jsjsqr": p(img="img/maoxian/jsqsqr.bmp", at=(415, 31, 550, 52)),  # 角色解锁确认

    "saodang_query": p(img="img/maoxian/saodang_query.bmp", at=(401, 206, 557, 240)),  # 扫荡券确认提示语
    "query_box": p(at=(263, 193, 698, 315)),  # 弹出提示框的位置
    "saodang_jieguo": p(img="img/maoxian/saodang_jieguo.bmp", at=(435, 28, 521, 56)),  # 扫荡结果：扫荡跳过界面上面的标题:
    "duiwu_win": p(img="img/maoxian/duiwu_win.bmp", at=(897, 77, 922, 105)),  # Normal/Hard胜利时，“队伍”图标偏下
    "duiwu_loss": p(img="img/maoxian/duiwu_loss.bmp", at=(832, 17, 869, 53)),  # Normal/Hard失败时，“队伍”图标偏上

    "no_tili_right": p(img="img/maoxian/no_tili_right.bmp", at=(711, 404, 734, 421)),  # 没有体力的红杠杠 --
}
ZHUXIAN_ID = {
    1: p(img="img/zhuxian/1.bmp", at=(77, 61, 141, 72)),
    2: p(img="img/zhuxian/2.bmp", at=(79, 60, 164, 73)),
    3: p(img="img/zhuxian/3.bmp", at=(78, 61, 147, 72)),
    4: p(img="img/zhuxian/4.bmp", at=(79, 60, 164, 73)),
    5: p(img="img/zhuxian/5.bmp", at=(79, 60, 164, 71)),
    6: p(img="img/zhuxian/6.bmp", at=(77, 60, 163, 73)),
    7: p(img="img/zhuxian/7.bmp", at=(79, 59, 182, 73)),
    8: p(img="img/zhuxian/8.bmp", at=(79, 59, 162, 71)),
    9: p(img="img/zhuxian/9.bmp", at=(81, 59, 163, 71)),
    10: p(img="img/zhuxian/10.bmp", at=(84, 60, 172, 74)),
    11: p(img="img/zhuxian/11.bmp", at=(82, 59, 165, 74)),
    12: p(img="img/zhuxian/12.bmp", at=(88, 61, 185, 71)),
    13: p(img="img/zhuxian/13.bmp", at=(88, 59, 189, 74)),
    14: p(img="img/zhuxian/14.bmp", at=(87, 61, 189, 73)),
    15: p(img="img/zhuxian/15.bmp", at=(87, 60, 172, 75)),
    16: p(img="img/zhuxian/16.bmp", at=(85, 60, 170, 71)),
    17: p(img="img/zhuxian/17.bmp", at=(84, 60, 172, 73)),
    18: p(img="img/zhuxian/18L.bmp", at=(104, 58, 169, 72)),
    19: p(img="img/zhuxian/19L.bmp", at=(104, 60, 170, 72)),
    20: p(img="img/zhuxian/20L.bmp", at=(89, 59, 196, 72)),
    21: p(img="img/zhuxian/21L.bmp", at=(87, 61, 196, 72)),
    22: p(img="img/zhuxian/22L.bmp", at=(109, 58, 175, 73)),
    23: p(img="img/zhuxian/23L.bmp", at=(109, 58, 177, 75)),
    24: p(img="img/zhuxian/24L.bmp", at=(91, 59, 193, 73)),
    25: p(img="img/zhuxian/25L.bmp", at=(91, 59, 193, 71)),
    26: p(img="img/zhuxian/26L.bmp", at=(61, 55, 198, 77)),
    27: p(img="img/zhuxian/27L.bmp", at=(60, 56, 199, 76)),
    28: p(img="img/zhuxian/28L.bmp", at=(60, 57, 201, 78)),
    29: p(img="img/zhuxian/29L.bmp", at=(61, 58, 198, 76)),
    30: p(img="img/zhuxian/30L.bmp", at=(60, 55, 178, 77)),
}
ZHUXIAN_XXXYY_ID = {
    # 小行星原野你长得太像了，无奈增加二级分类
    18: p(img="img/zhuxian/18R.bmp", at=(195, 59, 224, 72)),
    19: p(img="img/zhuxian/19R.bmp", at=(194, 59, 223, 71)),
}
ZHUXIAN_KSTLYSL_ID = {
    20: p(img="img/zhuxian/20R.bmp", at=(218, 59, 248, 70)),  # 卡斯塔里森林
    21: p(img="img/zhuxian/21R.bmp", at=(217, 59, 244, 71)),
}
ZHUXIAN_XXXYF_ID = {
    22: p(img="img/zhuxian/22R.bmp", at=(196, 59, 232, 76)),
    23: p(img="img/zhuxian/23R.bmp", at=(195, 59, 233, 78)),
}
ZHUXIAN_LDWSQF_ID = {
    24: p(img="img/zhuxian/24R.bmp", at=(212, 60, 254, 78)),
    25: p(img="img/zhuxian/25R.bmp", at=(216, 59, 250, 73)),
}
ZHUXIAN_SBDDSL_ID = {
    26: p(img="img/zhuxian/26R.bmp", at=(212, 58, 252, 77)),
    27: p(img="img/zhuxian/27R.bmp", at=(214, 58, 251, 77)),
}
ZHUXIAN_DSTEHSA_ID = {
    28: p(img="img/zhuxian/28R.bmp", at=(217, 59, 254, 77)),
    29: p(img="img/zhuxian/29R.bmp", at=(218, 60, 253, 77)),
}
# ZHUXIAN_FTLDY_ID = {
#     30: p(img="img/zhuxian/30R.bmp", at=(196, 60, 230, 76)),
#     31: p(img="img/zhuxian/31R.bmp", at=(218, 60, 253, 77)),
# }

ZHUXIAN_SECOND_ID = {
    (18, 19): ZHUXIAN_XXXYY_ID,
    (20, 21): ZHUXIAN_KSTLYSL_ID,
    (22, 23): ZHUXIAN_XXXYF_ID,
    (24, 25): ZHUXIAN_LDWSQF_ID,
    (26, 27): ZHUXIAN_SBDDSL_ID,
    (28, 29): ZHUXIAN_DSTEHSA_ID,
    # (30, 31): ZHUXIAN_FTLDY_ID,
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
            15: p(442, 222, name="8-15"),
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
    13: {
        "right": {
            17: p(749, 329),
            16: p(585, 314),
            15: p(659, 424),
            14: p(499, 429),
            13: p(443, 307),
            12: p(333, 385),
            11: p(202, 356),
        },
        "left": {
            10: p(817, 279),
            9: p(686, 259),
            8: p(741, 379),
            7: p(595, 391),
            6: p(475, 351),
            5: p(555, 249),
            4: p(428, 240),
            3: p(321, 280),
            2: p(238, 185),
            1: p(109, 206),
        }
    },
    14: {
        "right": {
            14: p(787, 239),
            13: p(679, 300),
            12: p(674, 411),
            11: p(543, 369),
            10: p(404, 388),
            9: p(457, 268),
            8: p(327, 286),
            7: p(213, 317),
        },
        "left": {
            6: p(582, 369),
            5: p(489, 294),
            4: p(397, 390),
            3: p(298, 302),
            2: p(188, 394),
            1: p(128, 267),
        }
    },
    15: {
        "right": {
            14: p(592, 253),
            13: p(745, 311),
            12: p(648, 404),
            11: p(500, 405),
            10: p(348, 370),
            9: p(289, 249),
            8: p(191, 354),
        },
        "left": {
            7: p(553, 407),
            6: p(600, 248),
            5: p(464, 280),
            4: p(376, 404),
            3: p(256, 337),
            2: p(267, 199),
            1: p(124, 229),
        }
    },
    16: {
        "right": {
            14: p(802, 245),
            13: p(644, 237),
            12: p(723, 365),
            11: p(574, 406),
            10: p(475, 282),
            9: p(353, 365),

        },
        "left": {
            8: p(680, 357),
            7: p(741, 244),
            6: p(570, 267),
            5: p(500, 396),
            4: p(411, 293),
            3: p(255, 279),
            2: p(293, 402),
            1: p(124, 394),
        }
    },
    17: {
        "right": {
            14: p(799, 237),
            13: p(649, 247),
            12: p(516, 294),
            11: p(524, 410),
            10: p(396, 429),
            9: p(316, 342),
            8: p(400, 233),
        },
        "left": {
            7: p(741, 239),
            6: p(585, 256),
            5: p(450, 299),
            4: p(566, 381),
            3: p(422, 422),
            2: p(274, 377),
            1: p(123, 349),
        }
    },
    18: {
        "right": {
            14: p(798, 326),
            13: p(662, 381),
            12: p(571, 291),
            11: p(481, 414),
            10: p(393, 320),
            9: p(269, 428),
        },
        "left": {
            8: p(595, 378),
            7: p(688, 241),
            6: p(547, 250),
            5: p(418, 317),
            4: p(348, 442),
            3: p(268, 346),
            2: p(307, 209),
            1: p(160, 224),
        }
    },
    19: {
        "right": {
            14: p(754, 237),
            13: p(607, 252),
            12: p(685, 383),
            11: p(526, 397),
            10: p(460, 282),
            9: p(322, 230),
        },
        "left": {
            8: p(737, 371),
            7: p(580, 394),
            6: p(546, 252),
            5: p(464, 347),
            4: p(347, 432),
            3: p(203, 375),
            2: p(345, 312),
            1: p(245, 248),
        }
    },
    20: {
        "right": {
            14: p(826, 246),
            13: p(747, 336),
            12: p(611, 386),
            11: p(572, 277),
            10: p(445, 319),
        },
        "left": {
            9: p(733, 418),
            8: p(631, 377),
            7: p(642, 243),
            6: p(514, 272),
            5: p(454, 375),
            4: p(368, 305),
            3: p(303, 205),
            2: p(192, 266),
            1: p(243, 379),
        }
    },
    21: {
        "right": {
            14: p(779, 210),
            13: p(716, 340),
            12: p(593, 259),
            11: p(589, 399),
            10: p(433, 397),
            9: p(447, 254),
            8: p(294, 220),
        },
        "left": {
            7: p(577, 268),
            6: p(682, 361),
            5: p(543, 400),
            4: p(414, 351),
            3: p(379, 221),
            2: p(265, 296),
            1: p(174, 395),
        }
    },
    22: {
        "right": {
            14: p(742, 220),
            13: p(607, 266),
            12: p(757, 344),
            11: p(615, 398),
            10: p(467, 357),
            9: p(457, 209),
            8: p(298, 223),
        },
        "left": {
            7: p(578, 273),
            6: p(714, 359),
            5: p(578, 404),
            4: p(403, 409),
            3: p(427, 275),
            2: p(299, 319),
            1: p(175, 399),
        }
    },
    23: {
        "right": {
            14: p(779, 235),
            13: p(637, 273),
            12: p(702, 393),
            11: p(538, 375),
            10: p(470, 245),

        },
        "left": {
            9: p(783, 326),
            8: p(689, 235),
            7: p(559, 254),
            6: p(589, 385),
            5: p(445, 400),
            4: p(328, 353),
            3: p(429, 242),
            2: p(298, 223),
            1: p(180, 259),
        }
    },
    24: {
        "right": {
            14: p(769, 238),
            13: p(710, 352),
            12: p(585, 391),
            11: p(491, 299),
            10: p(426, 401),
            9: p(300, 366),
            8: p(336, 236),
        },
        "left": {
            7: p(645, 244),
            6: p(554, 337),
            5: p(456, 256),
            4: p(324, 309),
            3: p(420, 385),
            2: p(293, 428),
            1: p(171, 394),
        }
    },
    25: {
        "right": {
            14: p(751, 328),
            13: p(629, 263),
            12: p(600, 401),
            11: p(441, 403),
            10: p(494, 274),
            9: p(347, 282),
            8: p(255, 398),
        },
        "left": {
            7: p(666, 252),
            6: p(516, 296),
            5: p(418, 404),
            4: p(253, 350),
            3: p(380, 283),
            2: p(290, 183),
            1: p(162, 225),
        }
    },
    26: {
        "right": {
            14: p(793, 338),
            13: p(723, 253),
            12: p(603, 231),
            11: p(516, 313),
            10: p(423, 390),
            9: p(365, 280),
            8: p(243, 276),
        },
        "left": {
            7: p(669, 385),
            6: p(576, 301),
            5: p(455, 274),
            4: p(411, 390),
            3: p(291, 346),
            2: p(248, 229),
            1: p(124, 270),
        }
    },
    27: {
        "right": {
            14: p(839, 286),
            13: p(738, 342),
            12: p(673, 245),
            11: p(556, 249),
            10: p(539, 350),
            9: p(421, 382),
            8: p(359, 284),
        },
        "left": {
            7: p(742, 264),
            6: p(659, 348),
            5: p(551, 288),
            4: p(444, 361),
            3: p(313, 392),
            2: p(220, 299),
            1: p(119, 373),
        }
    },
    28: {
        "right": {
            14: p(832, 269),
            13: p(729, 350),
            12: p(645, 257),
            11: p(568, 355),
            10: p(493, 241),
            9: p(355, 245),
            8: p(256, 367),
        },
        "left": {
            7: p(667, 260),
            6: p(543, 276),
            5: p(436, 351),
            4: p(415, 226),
            3: p(301, 303),
            2: p(187, 224),
            1: p(125, 319),
        }
    },
    29: {
        "right": {
            14: p(831, 274),
            13: p(715, 305),
            12: p(645, 216),
            11: p(525, 216),
            10: p(452, 313),
            9: p(369, 239),
            8: p(274, 319),
        },
        "left": {
            7: p(674, 235),
            6: p(624, 350),
            5: p(491, 315),
            4: p(388, 239),
            3: p(287, 311),
            2: p(247, 204),
            1: p(123, 231),
        }
    },
    30: {
        "right": {
            14: p(841, 224),
            13: p(775, 348),
            12: p(678, 253),
            11: p(554, 313),
            10: p(423, 350),
            9: p(241, 328),
            8: p(282, 206),
        },
        "left": {
            7: p(642, 257),
            6: p(510, 206),
            5: p(502, 346),
            4: p(338, 344),
            3: p(369, 245),
            2: p(227, 284),
            1: p(125, 359),
        }
    }
}
RANKS_DICT = {
    1: p(img="img/ranks/1.bmp", at=(217, 110, 275, 135)),
    2: p(img="img/ranks/2.bmp", at=(217, 112, 278, 135)),
    3: p(img="img/ranks/3.bmp", at=(213, 110, 279, 137)),
    4: p(img="img/ranks/4.bmp", at=(216, 112, 277, 135)),
    5: p(img="img/ranks/5.bmp", at=(215, 111, 277, 135)),
    6: p(img="img/ranks/6.bmp", at=(219, 111, 279, 138)),
    7: p(img="img/ranks/7.bmp", at=(213, 109, 279, 137)),
    8: p(img="img/ranks/8.bmp", at=(218, 111, 278, 135)),
    9: p(img="img/ranks/9.bmp", at=(216, 110, 277, 137)),
    10: p(img="img/ranks/10.bmp", at=(213, 113, 282, 137)),
    11: p(img="img/ranks/11.bmp", at=(214, 111, 280, 135)),
    12: p(img="img/ranks/12.bmp", at=(210, 110, 281, 134)),
    13: p(img="img/ranks/13.bmp", at=(212, 110, 282, 136)),
    14: p(img="img/ranks/14.bmp", at=(211, 111, 282, 136)),
    15: p(img="img/ranks/15.bmp", at=(216, 111, 281, 135)),
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
    },
    "time_status": {
        # 时间状态
        "juanzeng": 0,  # 上次捐赠时间
        "dianzan": 0,  # 上次点赞时间
        "buyexp": 0,  # 上次购买经验时间
        "niudan": 0,  # 上次免费扭蛋时间
        "tansuo": 0,  # 上次探索时间
        "maizhuangbei": 0,  # 上次卖装备时间
        "shengji": 0,  # 上次圣迹调查时间
    },
    "daily_status": {
        # 每日刷图
        "buy_tili": 0,  # 当日买体力次数
        "normal": {},  # normal图刷图记录
        "hard": {},  # hard图刷图记录
        "last_time": 0,  # 上一次刷图时间
    },
    "zhuangbei_kucun": {
        # 装备库存状态
        # Key: 装备名称
        # Value:(装备数量,更新时间,备注)
    },
    "juese_info": {
        # 角色信息
        # Key：角色名称
        # Value:{
        # haogan
        # dengji
        # rank
        # zb [bool]*6
        # star
        # last_update
        # }
    }

}

'''
!!!!警告!!!!!
!!!!下面这个是活动的坐标，请加入的时候一定要打上活动的备注！！！！！！
'''
ACTIVITY_COORD = {
    # 珠希与美冬的无人岛0金币生活 2020/8/30
    "shuihei_summer_activity": {
        "left": {
            9: p(835, 340),
            8: p(734, 293),
            7: p(653, 208),
            6: p(580, 278),
            5: p(489, 311),
            4: p(405, 398),
            3: p(334, 301),
            2: p(270, 218),
            1: p(165, 290)
        },
        "right": {
            16: p(822, 239),
            15: p(688, 175),
            14: p(624, 249),
            13: p(541, 330),
            12: p(464, 243),
            11: p(363, 351),
            10: p(301, 216)
        }
    }
}

# 显然后面还没写
# 等有空补全
# 准备写个GUI来快速标坐标
