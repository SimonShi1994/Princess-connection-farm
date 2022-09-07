import time
import os
import cv2
from core.constant import MAOXIAN_BTN, FIGHT_BTN, DXC_ELEMENT, HAOYOU_BTN, JUESE_BTN
from scenes.scene_base import PCRMsgBoxBase
import random
from DataCenter import LoadPCRData
from core.cv import UIMatcher


class FightBianZuBase(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "FightBianZu"
        self.feature = self.fun_feature_exist(FIGHT_BTN["duiwubianzu"])
        self.initFC = self.getFC(False).exist(MAOXIAN_BTN["bianzusheding"],
                                              self.fun_click(476, 437))

    def select_by_sort(self, order="zhanli", change=2):
        """
        按order进行选择
        :param order:
            order in ["zhanli","dengji","xingshu","shoucang","none"]
        :param change:
            0-不换人 1-人全部换下不上 2-默认：全部换人 3 - 不下人直接上
        """
        return self._a.set_fight_team_order(order, change)

    def select_by_duiwu(self, bianzu, duiwu):
        """
        :param bianzu: 编组编号1~5
        :param duiwu: 队伍编号1~3
        :return: False - 选取编组失败
        """
        return self._a.set_fight_team(bianzu, duiwu)

    def click_unit_by_cid(self, cid, screen=None, replace=False):
        # 根据角色cid寻找角色，确认碎片图片中心点并点击。正常点过返回0，没找到返回1。
        if screen is None:
            screen = self.getscreen()
        cid = str(cid)
        b = str(cid[0:4] + "11")
        c = str(cid[0:4] + "31")
        d = str(cid[0:4] + "61")
        imgpath_1 = "img/juese/unit/" + b + ".bmp"
        imgpath_2 = "img/juese/unit/" + c + ".bmp"
        imgpath_3 = "img/juese/unit/" + d + ".bmp"
        imgpath = [imgpath_1, imgpath_2]
        if os.path.exists(imgpath_3):
            imgpath.append(imgpath_3)
        clicked = False
        for i in imgpath:
            at = (47, 116, 908, 363)
            r_list = UIMatcher.img_where(screen, i, threshold=0.8, at=at,
                                         method=cv2.TM_CCOEFF_NORMED, is_black=False, black_threshold=1500)
            if r_list is not False:
                if len(r_list) == 2:
                    x_arg = int(r_list[0])
                    y_arg = int(r_list[1])
                    self.click(x_arg, y_arg)
                    clicked = True
                    break
        if clicked:
            return 0
        else:
            return 1

    def replace(self, position="front", amt: int = 1, prefer_cid=None):
        '''
        队伍补全函数,
        ；amt表示需要补全的个数, >0
        ；position表示角色的位置，前/中/后，可用值："front", "middle", "back"
        ；优先寻找prefer_cid列表中的角色（编号)，如果都没有或者缺数量，自动选择当前编组画面内的可用角色（按最前）补缺
        '''
        assert position in ["front", "middle", "back"]
        if prefer_cid is None:
            prefer_cid = []
        img_path = "img/juese/" + position + ".bmp"
        aa = 0
        if len(prefer_cid) > 0:
            for i in prefer_cid:
                if aa >= amt:
                    break
                c = self.click_unit_by_cid(i)
                if c == 0:
                    amt -= 1
        while True:
            if aa >= amt:
                self.log.write_log("debug", "已从备选中选到")
                break
            self.log.write_log("debug", "无备选，自动选一个同位置的")
            sc1 = self.getscreen()
            time.sleep(1.8)
            sc2 = self.getscreen()
            lst1 = self.img_where_all_prob(img=img_path, at=(58, 114, 906, 341), screen=sc1)
            lst2 = self.img_where_all_prob(img=img_path, at=(58, 114, 906, 341), screen=sc2)
            lst = lst1 + lst2
            lst.sort(key=lambda elem: elem[1])
            lst.sort(key=lambda elem: elem[2])
            t = 0
            while True:
                if self.is_exists(img=img_path, at=lst[t][3], is_black=True, black_threshold=100):
                    t += 1
                else:
                    x = lst[t][1]
                    y = lst[t][2]
                    aa += 1
                    self.click(x, y)
                    if aa < amt:
                        continue
                    else:
                        self.log.write_log("debug", "同位置选到了")
                        break
            break

    def select_by_namelst(self, cname_lst, replace=False, prefer=None):
        # 将角色拆分三种位置，方便选择。注意：此函数选择角色只选第一屏，不翻页
        if prefer is None:
            prefer = []
        data = LoadPCRData()
        if cname_lst is []:
            return
        cidlst = []
        preferlst = []
        for i in cname_lst:
            cidlst.append(data.get_id(name=i))
        for i in prefer:
            preferlst.append(data.get_id(name=i))
        front_lst = []
        middle_lst = []
        back_lst = []
        front_prefer = []
        middle_prefer = []
        back_prefer = []
        a = 0
        b = 0
        c = 0
        for i in cidlst:
            if data.get_position(i) == "front":
                front_lst.append(i)
            if data.get_position(i) == "middle":
                middle_lst.append(i)
            if data.get_position(i) == "back":
                back_lst.append(i)
        for i in preferlst:
            if data.get_position(i) == "front":
                front_prefer.append(i)
            if data.get_position(i) == "middle":
                middle_prefer.append(i)
            if data.get_position(i) == "back":
                back_prefer.append(i)
        # 根据不同位置，加入角色
        fc = [66, 125, 214]
        bc = [231, 235, 239]
        # 前卫
        while True:
            self.click(149, 87)
            if self.check_color(fc, bc, 227, 87, color_type="rgb"):
                break
        time.sleep(2)
        for i in front_lst:
            a += self.click_unit_by_cid(i)
            # 没找的个数
        time.sleep(2)
        if a > 0:
            if replace:
                # 如果需要替代
                self.replace(position="front", amt=a, prefer_cid=front_prefer)

        # 中卫
        while True:
            self.click(244, 87)
            if self.check_color(fc, bc, 326, 87, color_type="rgb"):
                break
        time.sleep(2)
        for i in middle_lst:
            b += self.click_unit_by_cid(i)
        time.sleep(2)
        if b > 0:
            if replace:
                # 如果需要替代
                self.replace(position="middle", amt=b, prefer_cid=middle_prefer)

        # 后卫
        while True:
            self.click(341, 87)
            if self.check_color(fc, bc, 423, 87, color_type="rgb"):
                break
        time.sleep(2)
        for i in back_lst:
            c += self.click_unit_by_cid(i)
        time.sleep(2)
        if c > 0:
            if replace:
                # 如果需要替代
                self.replace(position="back", amt=c, prefer_cid=back_prefer)

    def click_juese_by_rc(self, r, c):
        # 通过行列来选中角色，没什么用。而且仅限前两排
        r1 = [
            (107, 170),
            (214, 168),
            (318, 170),
            (423, 173),
            (531, 175),
            (636, 171),
            (742, 171),
            (849, 170),
        ]
        r2 = [
            (102, 305),
            (214, 303),
            (320, 301),
            (421, 299),
            (529, 299),
            (640, 295),
            (746, 297),
            (851, 291),
        ]
        if 1 <= c <= 8:
            if r == 1:
                self.click(*r1[c - 1])
                return
            elif r == 2:
                self.click(*r2[c - 1])
                return
        raise ValueError("只能1~2行，1~8列！而不是", r, '-', c)

    @staticmethod
    def check_team_AB(team_order):
        return '-' in team_order

    def clear_team(self):
        self.select_by_sort("zhanli", change=1)

    def select_team(self, team_order="zhanli", change=2):
        """
        使用队伍 "A-B" 形式，表示编组A选择B。
        若为 order指令：则按以下order排序后取前5.
            - "none" 不变化
            - "nobody" 不上人（只上支援）
            - "zhanli" 按战力排序
            - "dengji" 按等级排序
            - "xingshu" 按星数排序
            - "shoucang" 按收藏排序
        若为"none"或者""：不换人
        """
        if team_order in ["zhanli", "dengji", "xingshu", "shoucang"]:
            return self.select_by_sort(team_order, change)
        elif team_order in ["none", ""]:
            return None
        elif isinstance(team_order, list):
            return self.select_by_namelst(cname_lst=team_order)
        elif team_order == "nobody":
            self.select_by_sort("none", 1)
        else:
            A, B = team_order.split("-")
            A = int(A)
            B = int(B)
            return self.select_by_duiwu(A, B)

    def get_fight_current_member_count(self):
        return self._a.get_fight_current_member_count()

    def sort_down(self):
        if self.is_exists(FIGHT_BTN["sort_down"]):
            return
        else:
            self.click_btn(FIGHT_BTN["sort_up"], until_appear=FIGHT_BTN["sort_down"])
        time.sleep(1)

    def sort_by(self, cat=None):
        cor_dict = {
            'level': (69, 137),
            'zhanli': (287, 137),
            'rank': (508, 137),
            'star': (727, 137),
            'atk': (69, 193),
            'mat': (287, 193),
            'def': (508, 193),
            'mdf': (727, 193),
            'hp': (69, 251),
            'zhuanwu': (287, 251),
            'six': (510, 252)
        }
        # 兼容
        name_dict = {
            "dengji": "level",
            "xingshu": "star",
            "shoucang": "fav",
        }
        if cat in name_dict:
            cat = name_dict[cat]
        if cat is None:
            return
        else:
            self.click_btn(FIGHT_BTN["sort_by"], until_appear=JUESE_BTN["fenlei"])
            time.sleep(1)
            self.click(cor_dict.get(cat)[0], cor_dict.get(cat)[1])
            # 点击分类类型
            time.sleep(1)
            self.click(597, 477)
            # 点击确认
            time.sleep(1)

    def get_zhiyuan(self, assist_num=1, force_haoyou=False, if_full=0, zhiyuan_sort="zhanli"):
        # 从左到右获取一个可能的支援
        # out: 0- Success 1- 人满 2- 等级不够 3- 无支援人物 4- 无好友
        # force_haoyou: 只借好友，不然不借
        # if full: 人满时？ -1： 返回人满；  0： 随机下一个人  1~5： 下第n个人
        # zhiyuan_sort: 排序方式，方便确认想借的角色
        out = 0
        if self.click_btn(DXC_ELEMENT["zhiyuan_white"], until_appear=DXC_ELEMENT["zhiyuan_blue"],
                          retry=3, wait_self_before=True):
            if zhiyuan_sort is not None:
                self.sort_down()
                self.sort_by(cat=zhiyuan_sort)
                self.log.write_log("info", f"已经按{zhiyuan_sort}排序！")

            if force_haoyou and not self.is_exists(HAOYOU_BTN["haoyou_sup"]):
                out = 4
                self.log.write_log("info", "没有好友了，不借了！")
            else:
                now_count = self.get_fight_current_member_count()
                if now_count == 5:
                    if if_full == -1:
                        self.log.write_log("warning", "已经人满，无法借人！")
                        out = 1
                    else:
                        if if_full == 0:
                            choose = random.choice([1, 2, 3, 4, 5])
                        else:
                            choose = if_full
                        self.click(FIGHT_BTN["empty"][choose], pre_delay=1, post_delay=0.5)
                        if if_full == 0:
                            self.log.write_log("info", f"已经人满，随机换下第{choose}人！")
                        else:
                            self.log.write_log("info", f"已经人满，换下第{choose}人！")
                        now_count -= 1
                for c in range(assist_num, assist_num + 2):
                    if c <= 8:
                        self.click_juese_by_rc(1, c)
                    else:
                        self.click_juese_by_rc(2, c - 8)
                time.sleep(0.5)
                new_count = self._a.get_fight_current_member_count()
                if new_count == now_count + 1:
                    self.log.write_log(level='info', message="借人成功！")
                else:
                    self.log.write_log(level='warning', message="借人失败，可能因为等级不够！")
                    out = 2
            # if self.lock_no_img(DXC_ELEMENT["zhiyuan_blue"], retry=1):
        else:
            self.log.write_log(level='info', message="无支援人物!")
            out = 3
        self.click_btn(DXC_ELEMENT["quanbu_white"], until_appear=DXC_ELEMENT["quanbu_blue"], elsedelay=0.1)
        return out
