import os
import time

import cv2

from DataCenter import LoadPCRData
from core.constant import JUESE_BTN, RANKS_DICT, MAIN_BTN, DXC_ELEMENT, MAOXIAN_BTN, JUQING_BTN, FIGHT_BTN
from core.cv import UIMatcher
from core.pcr_checker import PCRRetry, ContinueNow
from core.pcr_config import debug, use_pcrocr_to_detect_rank
from core.utils import make_it_as_juese_as_possible, make_it_as_number_as_possible
from scenes.fight.fightbianzu_base import FightBianZuBase
from scenes.fight.fightinfo_base import FightInfoBase
from scenes.root.seven_btn import SevenBTNMixin
from scenes.scene_base import PCRMsgBoxBase


def get_name_from_plate_path(img_path):
    data = LoadPCRData()
    id_1 = str(img_path)
    id_2 = id_1[16:20]
    c_id = id_2 + "01"
    c_name = data.get_name(int(c_id))
    return c_name


def get_plate_img_path(charname):
    data = LoadPCRData()
    a = str(data.get_id(name=charname))
    '''
    example: 
    望返回值 102901
    三星前 102911
    三星后 102931
    六星后 102961
    '''
    b = str(a[0:4] + "11")
    c = str(a[0:4] + "31")
    d = str(a[0:4] + "61")
    imgpath_1 = "img/juese/plate/" + b + ".bmp"
    imgpath_2 = "img/juese/plate/" + c + ".bmp"
    imgpath_3 = "img/juese/plate/" + d + ".bmp"
    imgpath = [imgpath_1, imgpath_2]
    if os.path.exists(imgpath_3):
        imgpath.append(imgpath_3)

    return imgpath


class CharMenu(SevenBTNMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "CharMenu"
        self.initPC = self.kkr_precheck
        self.feature = self.fun_feature_exist(JUESE_BTN["duiwu"])
        # 我的队伍

    def kkr_precheck(self, screen):
        if self.is_exists(DXC_ELEMENT["dxc_kkr"], screen=screen):
            self.chulijiaocheng(turnback=None)
            self._a.restart_this_task()
        return screen

    def click_first(self):
        self.fclick(169, 135)
        time.sleep(1)

    def click_second(self):
        self.click(469, 148)
        time.sleep(1)

    def enter_first_juese(self) -> "CharZhuangBei":
        juese = 1
        while juese <= 9:
            mode = self.click_btn(JUESE_BTN["nine_juese"][juese], until_appear={
                JUESE_BTN["mana_ball"]: 1,
                # DXC_ELEMENT["dxc_kkr"]: 2,
                MAOXIAN_BTN["jsjsqr"]: 3,
            })
            if mode == 3:
                self.click(369, 485)
                for _ in range(5):
                    self.click(5, 117)
                juese += 1
            if mode == 1:
                break
        else:
            self.log.write_log("error", "太惊人了，你有九个待养成的角色！你是什么人？！跳过该任务。")
            self.goto_zhucaidan()
            self._a.skip_this_task()
        self.clear_initFC()
        return CharZhuangBei(self._a).enter()

    def sort_down(self):
        if self.is_exists(JUESE_BTN["sort_down"]):
            return
        else:
            self.click_btn(JUESE_BTN["sort_up"], until_appear=JUESE_BTN["sort_down"])
        time.sleep(1)

    def sort_up(self):
        if self.is_exists(JUESE_BTN["sort_up"]):
            return
        else:
            self.click_btn(JUESE_BTN["sort_down"], until_appear=JUESE_BTN["sort_up"])

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
            'love': (287, 251),
            'zhuanwu': (508, 251),
            'fav': (727, 251),
            'six': (69, 309)
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
            self.click_btn(JUESE_BTN["sort_by"], until_appear=JUESE_BTN["fenlei"])
            time.sleep(1)
            self.click(cor_dict.get(cat)[0], cor_dict.get(cat)[1])
            # 点击分类类型
            time.sleep(1)
            self.click(597, 477)
            # 点击确认
            time.sleep(1)

    def click_plate(self, imgpath, screen=None):
        # 寻找角色，确认碎片图片中心点并点击
        if screen is None:
            screen = self.getscreen()
        at = (24, 67, 919, 384)
        r_list = UIMatcher.img_where(screen, imgpath, threshold=0.8, at=at,
                                     method=cv2.TM_CCOEFF_NORMED, is_black=False, black_threshold=1500)
        if r_list is not False:
            if len(r_list) == 2:
                x_arg = int(r_list[0])
                y_arg = int(r_list[1])
                self.goto(CharZhuangBei, self.fun_click(x_arg, y_arg), use_in_feature_only=True)
                return True
            else:
                return False
        else:
            return False

    def dragdown(self):
        obj = self.d.touch.down(621, 364)
        time.sleep(0.1)
        obj.move(620, 70)
        time.sleep(0.8)
        obj.up(620, 70)

    def check_buttom(self):
        fc = [92, 156, 244]
        bc = [158, 164, 176]
        xcor = 922
        ycor = 448
        return self.check_color(fc, bc, xcor, ycor, color_type="rgb")

    def goto_wodeduiwu(self) -> "CharTeam":
        return self.goto(CharTeam, self.fun_click(JUESE_BTN["duiwu"]))


class CharTeam(PCRMsgBoxBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "CharMenu"
        self.feature = self.fun_feature_exist(JUESE_BTN["duiwuyilan"])

    def sort_down(self):
        if self.is_exists(JUESE_BTN["sort_down2"]):
            return
        else:
            self.click_btn(JUESE_BTN["sort_up2"], until_appear=JUESE_BTN["sort_down2"])
        time.sleep(1)

    def sort_up(self):
        if self.is_exists(JUESE_BTN["sort_up2"]):
            return
        else:
            self.click_btn(JUESE_BTN["sort_down2"], until_appear=JUESE_BTN["sort_up2"])

    def select_group(self, gid: int):
        self.click(FIGHT_BTN["team_h"][gid], pre_delay=1, post_delay=1, )

    def edit_subteam(self, tid: int) -> "CharBianZu":
        tid_dict = {
            1: (872, 201),
            2: (868, 322),
            3: (870, 426)
        }
        self.click_btn(tid_dict[tid], until_appear=JUESE_BTN["duiwubianzu"])

    def edit_team(self, team_slot="1-1") -> "CharBianZu":
        gid, tid = team_slot.split("-")
        gid = int(gid)
        tid = int(tid)
        self.select_group(gid)
        if 0 < tid < 4:
            self.sort_up()
        elif 7 < tid < 11:
            self.sort_down()
            tid = 11 - tid
        else:
            raise Exception("只支持1~3和8~10的队伍序号")
        self.edit_subteam(tid)


class CharBianZu(FightBianZuBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "CharMenu"
        self.feature = self.fun_feature_exist(JUESE_BTN["duiwubianzu"])

    def save_team(self) -> "CharTeam":
        self.click_btn(JUESE_BTN["save_team"])


class CharBase(SevenBTNMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "CharFiveBTN"
        self.initPC = self.char_precheck

    def char_precheck(self, screen):
        ALL_FEATURES = [
            MAIN_BTN["right_kkr"],
            DXC_ELEMENT["dxc_kkr"],
        ]
        for f in ALL_FEATURES:
            if self.is_exists(f, screen=screen):
                self.chulijiaocheng(turnback=None)
                self.clear_initFC()
                self._a.restart_this_task()
        return screen

    def loveplus(self, read_story=False):
        if self.is_exists(JUESE_BTN["hgdjq"]):  # 好感度剧情红点
            # if self.is_exists(img="img/juese/red_mid.bmp", method="sq", at=(53, 331, 61, 341)):  # 好感度剧情红点
            self.click_btn(JUESE_BTN["hgdjq"], until_appear=JUESE_BTN["juesejuqing"])
            self.click_btn(JUESE_BTN["hgdts"], until_appear=JUESE_BTN["zengli"])
            if self.is_exists(JUESE_BTN["haoganzuida"]):
                self.click(367, 473)  # 取消
            else:
                self.click(651, 214)  # Max
                self.click_btn(JUESE_BTN["zengsong"])
                time.sleep(1)
                if self.is_exists(JUESE_BTN["donghuaqueren"]):
                    self.click(349, 260)
                    if not self.is_exists(JUESE_BTN["ticked"].img, at=(362, 330, 416, 385)):
                        self.click(386, 353)  # 勾选
                        self.click(589, 425)  # 确认
                self.lock_img(JUESE_BTN["juqingjiesuo"], at=(429, 22, 525, 257))
                self.lock_img(img=JUESE_BTN["guanbi"].img, at=(358, 280, 595, 509))
                sc = self.getscreen()
                self.click_img(img=JUESE_BTN["guanbi"].img, at=(358, 280, 595, 509), screen=sc)  # 关闭
            self.lock_img(JUESE_BTN["juesejuqing"])
            self.log.write_log("info", "无法再提升好感度")

            if read_story:
                while True:
                    time.sleep(1)
                    lst = self.img_where_all(img="img/juqing/new_content.bmp", method="sq", at=(245, 98, 320, 442))
                    if len(lst) > 0:
                        x = lst[0] + 383
                        y = lst[1] + 50
                        '''
                        280, 246
                        663, 297
                        '''
                        self.click(x, y)  # 进入剧情
                        self._a.guojuqing(story_type="haogandu")
                        continue
                    if self.is_exists(JUESE_BTN["lxydjq"]):
                        self._a.guojuqing(story_type="haogandu")
                        continue
                    if self.is_exists(JUESE_BTN["lxydjq"].img, at=(394, 73, 564, 100)):
                        self._a.guojuqing(story_type="haogandu")
                        continue
                    if self.is_exists(JUESE_BTN["wujuqing"]):
                        self.log.write_log("info", "好感剧情已读完")
                        self.fclick(1, 1)
                        break
                    else:
                        self.log.write_log("info", "无可读好感剧情")
                        self.fclick(1, 1)
                        break

    def goto_zhuangbei(self) -> "CharZhuangBei":
        return self.goto(CharZhuangBei, self.fun_click(JUESE_BTN["equip_unselected"]), before_clear=False)

    def goto_kaihua(self) -> "CharKaihua":
        return self.goto(CharKaihua, self.fun_click(JUESE_BTN["kaihua_unselected"]), before_clear=False)

    def goto_zhuanwu(self) -> "CharZhuanwu":
        return self.goto(CharZhuanwu, self.fun_click(JUESE_BTN["zhuanwu_unselected"]), before_clear=False)

    def goto_menu(self) -> "CharMenu":
        return self.goto(CharMenu, self.fun_click(JUESE_BTN["return_menu"]))

    # 新版本收藏的位置改变了
    # def get_shoucang_state(self, screen=None):
    #     # True: 收藏了；  False： 未收藏
    #     if screen is None: screen = self.getscreen()
    #     A = self.img_prob(JUESE_BTN["yishoucang"], screen=screen)
    #     B = self.img_prob(JUESE_BTN["weishoucang"], screen=screen)
    #     return A > B
    #
    # def set_shoucang_state(self, state: bool, screen=None):
    #     # True - 收藏； False - 取消收藏
    #     if self.get_shoucang_state(screen) != state:
    #         self.click(JUESE_BTN["yishoucang"], post_delay=0.5)

    def get_level(self, screen=None):
        if screen is None: screen = self.getscreen()
        at = (259, 416, 291, 433)
        return self.ocr_int(*at, screen)

    def get_haogan(self, screen=None):
        if screen is None: screen = self.getscreen()
        at = (271, 390, 291, 405)
        return self.ocr_int(*at, screen)

    def next_char(self, screen=None):
        # at = (483, 119, 760, 141)
        at = (180, 75, 314, 97)
        self.lock_change(at, threshold=0.84, similarity=0.01, elseclick=(929, 269), elsedelay=3, is_raise=True,
                         screen=screen)


class CharZhuangBei(CharBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "CharZhuangBei"
        # 检测角色强化装备页
        self.feature = self.fun_feature_exist(JUESE_BTN["equip_selected"])

    def get_six_clothes(self, screen=None):
        if screen is None: screen = self.getscreen()
        Six_Points = [
            (101, 111),
            (336, 112),
            (65, 198),
            (371, 199),
            (101, 284),
            (336, 286),
        ]
        sc = cv2.cvtColor(screen, cv2.COLOR_RGB2HSV)
        value = sc[:, :, 1]
        out = []  # 从左到右，从上到下
        for p in Six_Points:
            w, h = 60, 30
            pic = UIMatcher.img_cut(value, (p[0], p[1], p[0] + w, p[1] + h))
            if debug:
                self.log.write_log('debug', pic.max())
            if pic.max() > 150:
                out += [True]
            else:
                out += [False]
        if debug:
            self.log.write_log('debug', out)
        return out

    def get_char_lv_status(self, screen=None):
        if screen is None:
            screen = self.getscreen()
        fc = [69, 123, 247]  # G B R:红点
        bc = [243, 247, 239]  # G B R:面板白
        xcor = 615
        ycor = 60
        a = self.check_color(fc, bc, xcor, ycor, color_type="gbr", screen=screen)
        return a

    def get_auto_upgrade_status(self, screen=None):
        if screen is None:
            screen = self.getscreen()
        fc = [73, 132, 247]  # G B R:红点
        bc = [182, 247, 90]  # G B R:面板蓝
        xcor = 425
        ycor = 415
        a = self.check_color(fc, bc, xcor, ycor, color_type="gbr", screen=screen)
        return a

    def get_equip_status(self, screen=None):
        # 返回值： 0-槽位满了强化也满了 1-槽位满了没强化满; 2-槽位满了，可升Rank; 3-槽位没满，有库存;4-槽位没满，有库存，还能升rank;
        #         5-槽位没满，没库存;
        if screen is None:
            screen = self.getscreen()
        # 判断1：先升rank
        if self.is_exists(JUESE_BTN["rank_on"], screen=screen):
            if self.is_exists(JUESE_BTN["yjzb"], screen=screen):
                # 没穿满，但可以升rank
                return 4
            else:
                # 穿满了，可升rank
                return 2
        # 判断2：再看装备是否能穿
        if self.is_exists(JUESE_BTN["red_small"], at=(287, 313, 309, 339)):
            # 有装备可穿
            return 3
        if self.is_exists(JUESE_BTN["reachable"].img, at=(71, 136, 435, 349)):
            return 5
        # 判断3: 穿满再看强化状态
        if self.is_exists(JUESE_BTN["red_small"].img, at=(372, 89, 437, 300)) \
                or self.is_exists(JUESE_BTN["red_small"].img, at=(101, 89, 176, 292)):
            return 1
        else:
            return 0

    def get_rank(self, screen=None):
        if screen is None:
            screen = self.getscreen()
        if use_pcrocr_to_detect_rank:
            rank_at_1 = (201, 110, 295, 135)
            rank_at_2 = (410, 389, 431, 403)
            # out1 = self.ocr_center(*rank_at_1,screen,custom_ocr="pcr",allowstr="品级0123456789")
            # out1 = int(make_it_as_number_as_possible(out1))
            out2 = self.ocr_center(*rank_at_2, screen, custom_ocr="pcr", allowstr="0123456789")
            out2 = int(make_it_as_number_as_possible(out2))
            out = out2
            return out
        out = self.check_dict_id(RANKS_DICT, screen, diff_threshold=0.001)
        for _ in range(3):
            if out is None:
                self.click(525, 71, post_delay=1)
                out = self.check_dict_id(RANKS_DICT, screen, diff_threshold=0.001)
        if out is None:
            self.log.write_log("warning", "获取Rank失败！")
            return None
        return int(out)

    def do_rankup(self, tomax=True):
        self.click_btn(JUESE_BTN["rank_on"], until_appear=JUESE_BTN["rank_up_ok"])
        if tomax:
            if self.is_exists(JUESE_BTN["rank_max"]):
                self.click(649, 242)  # click max
        out = self.click_btn(JUESE_BTN["zdqh_ok"], until_appear={
            JUESE_BTN["rank_up_complete"]: 1,
            JUESE_BTN["pjtsqr"]: 2,
        })
        if out == 2:
            self.click_btn(JUESE_BTN["pjtsqr_ok"], until_appear=JUESE_BTN["pjtswb"])
        self.fclick(1, 1)

    @PCRRetry(name="re_qianghua")
    def do_zidongqianghua(self, buy_sucai=True, do_shuatu=True, do_tuitu=False, teamorder="zhanli", getzhiyuan=False):
        # Return 1: 因为没体力而终止了
        # Return 2: 因为没次数而终止了
        self.fclick(1, 1)
        es = self.get_equip_status()
        if es == 0 or es == 1:
            self.log.write_log("info", "已经不能再自动强化了。")
            return
        out = self.click_btn(JUESE_BTN["zdqh_1"], until_appear={
            JUESE_BTN["zdqh_ok"]: 1,
            JUESE_BTN["tuijiancaidan"]: 2,
        }, retry=3, is_raise=False)
        if out is False:
            self.log.write_log("info", "尝试点了自动强化，但好像没有反应？")
            self.fclick(1, 1)
            return
        if out == 1:
            self.log.write_log("info", "进行等级、穿衣的升级。")
            self.click_btn(JUESE_BTN["zdqh_ok"], until_appear=JUESE_BTN["equip_selected"])
            raise ContinueNow(name="re_qianghua")
        if out == 2:
            sc = self.getscreen()
            A = self.img_prob(JUESE_BTN["tjqh_zb"], screen=sc)  # 装备、专武升星
            B = self.img_prob(JUESE_BTN["tjqh_gq"], screen=sc)  # 刷关
            if A < 0.1 and B < 0.1:
                self.log.write_log("warning", "为什么啥都没有呢……跳过该角色……")
                self.fclick(1, 1)
                return
            if A > B:
                self.log.write_log("info", "进行装备升星或专武升级。")
                out2 = self.lock_img({
                    JUESE_BTN["zdzbqhqr"]: 1,
                    JUESE_BTN["scgm_and_zdzbqhqr"]: 2
                }, elseclick=(477, 201), elsedelay=8, retry=3, is_raise=False)  # 点第一个
                if out2 is False:
                    self.log.write_log("warning", "为什么什么都点不到呢……跳过该角色……")
                    self.fclick(1, 1)
                    return

                if out2 == 1:

                    self.click_btn(JUESE_BTN["zdzbqhqr_ok"], until_disappear=JUESE_BTN["zdzbqhqr"])
                else:
                    # 要购买素材
                    if buy_sucai:
                        self.log.write_log("info", "强化素材不够，确认购买素材！")
                        self.click_btn(JUESE_BTN["zdzbqhqr_ok"], until_disappear=JUESE_BTN["scgm_and_zdzbqhqr"])

                time.sleep(1)
                raise ContinueNow(name="re_qianghua")
            else:
                if do_shuatu:
                    if not self.check_shuatu():
                        self.log.write_log("info", "装备不足，但没体力刷了。")
                        self.fclick(1, 1)
                        return 1
                    else:
                        self.log.write_log("info", "装备不足，准备刷取。")
                    fi: FightInfoBase = self.goto(FightInfoBase, gotofun=self.fun_click(477, 201))
                    stars = fi.get_upperright_stars()
                    if stars == 3:
                        out = fi.easy_saodang(target_cishu=6, one_tili=-1, check_cishu=True)
                        if out == 2:
                            self.log.write_log("info", "没有挑战次数了，放弃这个角色的装备刷取……")
                            self.fclick(1, 1)
                            return 2
                        elif out == 1:
                            self.log.write_log("info", "体力不足了，跳过该角色。")
                            self.fclick(1, 1)
                            return 1
                        else:
                            self.fclick(1, 1)
                            raise ContinueNow(name="re_qianghua")
                    else:
                        if do_tuitu:
                            self.log.write_log("info", "需要推图，准备推图")
                            out = fi.easy_shoushua(team_order=teamorder, one_tili=-1, check_cishu=True,
                                                   max_speed=2, get_zhiyuan=getzhiyuan)
                            if out == 1:
                                self.log.write_log("info", "由于挑战失败了，跳过这个角色的装备升级。")
                                self.fclick(1, 1)
                                return
                            elif out == 2:
                                self.log.write_log("info", "没有挑战次数了，放弃这个角色的装备刷取……")
                                self.fclick(1, 1)
                                return 2
                            elif out == 3:
                                self.log.write_log("info", "体力不足了，跳过该角色。")
                                self.fclick(1, 1)
                                return 1
                            else:
                                self.fclick(1, 1)
                                raise ContinueNow(name="re_qianghua")  # 再次强化看看能不能直接穿了

                        else:
                            self.log.write_log("info", "需要推图，但是不推图")
                            self.fclick(1, 1)
                            return
                else:
                    self.log.write_log("info", "装备不足，但并不刷取。")
                    self.fclick(1, 1)
                    return


class CharKaihua(CharBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "CharKaihua"
        # 检测角色开花页
        self.feature = self.fun_feature_exist(JUESE_BTN["kaihua_selected"])

    def get_starup_status(self, screen=None):
        if screen is None:
            screen = self.getscreen()
        if self.is_exists(JUESE_BTN["kaihua_enough"], screen=screen):
            return True
        else:
            return False

    def get_stars(self, screen=None):
        # TODO: Can not recognize Changed Stars
        if screen is None: screen = self.getscreen()
        from core.constant import PCRelement as p
        if self.is_exists(JUESE_BTN["liuxing_info"], screen=screen):
            return 5  # 尚不能六星开花
        if self.is_exists(JUESE_BTN["sixth_star_off"], screen=screen):
            # 六星模式
            five_stars = {
                1: p(153, 335),
                2: p(191, 336),
                3: p(228, 336),
                4: p(266, 334),
                5: p(302, 335),
            }
        else:
            five_stars = {
                1: p(170, 337),
                2: p(209, 337),
                3: p(243, 335),
                4: p(281, 336),
                5: p(320, 335),
            }
        if self.is_exists(JUESE_BTN["sixth_star"], screen=screen):
            return 6
        else:
            return int(self._a.count_stars(five_stars, screen))

    def cainengkaihua(self):
        def kh_sideclick(screen):
            self.fclick(611, 143)
            return False

        self.click_btn(JUESE_BTN["do_kaihua"], until_appear=JUESE_BTN["kaihua_confirm"])
        self.click(402, 230)  # MAX
        time.sleep(0.5)
        self.click_btn(JUESE_BTN["kaihua_confirm"], until_disappear=JUESE_BTN["kaihua_confirm"])
        self.lock_img(JUESE_BTN["kaihua_complete"], side_check=kh_sideclick)  # 加速加速
        self.fclick(1, 1)  # 跳过剧情等
        self.fclick(1, 1)

    def get_name(self, screen=None):
        if screen is None:
            screen = self.getscreen()
        at = (483, 119, 760, 141)
        ori_out = self.ocr_center(*at, screen)
        out = make_it_as_juese_as_possible(ori_out)
        if out == "公主宝珠":
            for _ in range(5):
                self.click(121, 172)
            time.sleep(1)
            return self.get_name()
        out = self._a._check_img_in_list_or_dir(out, (482, 114, 750, 261), "ocrfix/juese", "C_ID", screen)
        return out


class CharZhuanwu(CharBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_name = "CharZhuanwu"
        # 检测角色开花页
        self.feature = self.fun_feature_exist(JUESE_BTN["zhuanwu_selected"])

    def get_zhuanwu_status(self, screen=None):
        # return: 0-未开放 1-资源不足 2-可穿戴 3-可解锁上限 4-可升级 5-可解锁可升级
        if screen is None:
            screen = self.getscreen()
        if self.is_exists(JUESE_BTN["zhuanwu_lock"], screen=screen):
            return 0
        else:
            if self.is_exists(JUESE_BTN["zhuanwu_equipable"], method="sq", threshold=0.95, screen=screen):
                return 2
            else:
                if self.is_exists(img="img/juese/red_mid.bmp", at=(747, 409, 755, 418), screen=screen):
                    # 解放红点亮
                    if self.is_exists(img="img/juese/red_mid.bmp", at=(892, 409, 901, 418), screen=screen, method="sq"):
                        # 强化红点亮
                        return 5
                    else:
                        return 3
                else:
                    if self.is_exists(img="img/juese/red_mid.bmp", at=(892, 409, 901, 418), screen=screen, method="sq"):
                        # 强化红点亮
                        return 4
                    else:
                        return 1

    def wear_zhuanwu(self):
        self.click_btn(JUESE_BTN["wear"], until_appear=JUESE_BTN["wear_confirm"])
        self.click_btn(JUESE_BTN["wear_confirm"])
        time.sleep(2)

    def unlock_ceiling(self, tozhuanwulv=100):
        self.click_btn(JUESE_BTN["unlock_ceiling"], until_appear=JUESE_BTN["unlock_ceiling_confirm"])
        while True:
            screen = self.getscreen()
            a = self.get_zhuanwu_uplimit_during_unlock(screen)
            if self.is_exists(JUESE_BTN["sucaibuzu"], screen=screen):
                self.log.write_log('info', "提升专武的素材不足")
                self.fclick(1, 1)
                break

            if a <= tozhuanwulv:
                if self.is_exists(JUESE_BTN["unlock_ceiling_need_lv"], screen=screen):
                    self.fclick(1, 1)
                    break
                self.log.write_log('info', "解锁专武上限")
                self.click(585, 476)
                # 点击解锁上限
                time.sleep(5)
                if self.is_exists(JUESE_BTN["unlock_ceiling_off"], method="sq"):
                    self.fclick(1, 1)
                    break
                continue
            else:
                self.fclick(1, 1)
                self.log.write_log('info', "已达到目标专武等级")
                return 2

    def yijianqianghua(self):
        self.click_btn(JUESE_BTN["yijianqianghua"], until_appear=JUESE_BTN["wear_confirm"])
        self.click(655, 230)  # 点击MAX
        if not self.is_exists(JUESE_BTN["ticked"]):
            self.click(386, 410)  # 勾上
        self.click_btn(JUESE_BTN["wear_confirm"])
        time.sleep(3)  # 等动画

    def levelup_zhuanwu(self):
        while True:
            if self.is_exists(img="img/juese/red_mid.bmp", at=(892, 409, 901, 418), method="sq"):
                self.click_btn(JUESE_BTN["levelup_zhuanwu"], until_appear=JUESE_BTN["qhscxz"])
                at = (615, 389, 694, 412)
                sc1 = self.getscreen()
                handle = self._a.d.touch.down(200, 200)
                time.sleep(1)
                while True:
                    time.sleep(1)
                    sc2 = self.getscreen()
                    p = self.img_equal(sc1, sc2, at=at)
                    if p > 0.95:
                        break
                    sc1 = sc2
                handle.up(200, 200)
                # 由于按钮点击认为没点到，只能workround
                self.fclick(810, 470)
                time.sleep(2)
                self.fclick(1, 1)
                continue
            else:
                break

    def get_zhuanwu_uplimit_during_unlock(self, screen=None):
        # OCR获得专武上限目标等级，可靠
        self.check_ocr_running()
        if screen is None:
            screen = self.getscreen()
        at = (569, 80, 601, 99)
        out = self.ocr_int(*at, screen_shot=screen)
        return out
