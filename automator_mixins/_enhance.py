import time

from automator_mixins._shuatu_base import ShuatuBaseMixin
from core.constant import JUESE_BTN, FIGHT_BTN, MAIN_BTN
from core.pcr_config import debug
from scenes.dxc.dxc_fight import FightBianzuDXC
from scenes.dxc.dxc_fight import FightingWinDXC, FightingLossDXC
from scenes.fight.fightinfo_zhuxian import FightInfoBase
from scenes.fight.fighting_zhuxian import FightingWinZhuXian2, HaoYouMsg
from scenes.juese.enhance import CharBase, CharKaihua, CharZhuanwu
from scenes.juese.juese_base import CharMenu, get_plate_img_path
from scenes.scene_base import PossibleSceneList


class DuringFighting(PossibleSceneList):
    def __init__(self, a):
        self.FightingWinDXC = FightingWinDXC
        self.FightingLossDXC = FightingLossDXC
        self.HaoYouMsg = HaoYouMsg
        scene_list = [
            FightingWinDXC(a),
            FightingLossDXC(a),
            HaoYouMsg(a),
        ]
        super().__init__(a, scene_list, double_check=0.)


class EnhanceMixin(ShuatuBaseMixin):

    def zidongqianghua(self, do_rank=True, do_shuatu=True, do_kaihua=True, do_zhuanwu=True, charlist=None,
                       team_order="zhanli", getzhiyuan=True, is_full=2, tozhuanwulv=150, count=15, sort="level"):
        '''
        角色升级任务，包含了装备、升星、专武
        do_rank:rank升级
        do_shuatu:刷图补装备
        do_kaihua:升星
        do_zhuanwu:处理专武，默认拉满
        charlist:list对象,需要执行该任务的角色
        team_order:刷图无法扫荡时，使用的挑战队伍。zhanli、dengji、队伍序号、星数，详见FightBianZuBase
        getzhiyuan:是否借人
        is_full:借人人满时换下的角色位置
        tozhuanwulv:专武提升上限
        '''
        # 计数器
        if charlist is None:
            charlist = []
        self.lock_home()
        self.clear_all_initFC()
        self.click_btn(MAIN_BTN["juese"], until_appear=JUESE_BTN["duiwu"])
        time.sleep(5)
        self.fclick(1,1)
        # 进入角色选择
        cm = CharMenu(self)
        cm.sort_by(sort)
        time.sleep(2)
        cm.sort_down()
        time.sleep(1)

        while True:
            # 单页面循环

            sc = self.getscreen()
            for i in charlist[:]:
                plate_path = get_plate_img_path(i)
                for j in plate_path:
                    a = cm.click_plate(j, screen=sc)
                    if a is True:
                        charlist.remove(i)
                        ecb = CharBase(self)
                        ekh = ecb.goto_kaihua()
                        if do_kaihua:
                            if debug:
                                print("升星任务开始")
                            if ekh.get_starup_status():
                                ekh.cainengkaihua()
                        ekh.goto_base()
                        if debug:
                            print("升星完成，前往base")

                        # 装备级等级强化
                        while True:
                            ecb = CharBase(self)
                            ers = ecb.get_equip_status()
                            ehs = ecb.get_enhance_status()
                            if debug:
                                print("等级装备强化任务开始")
                                print('角色状态：%s' % ehs)

                            if ers == 2:
                                # 先处理升rank
                                if do_rank:
                                    # rank提升开
                                    if debug:
                                        print("rank提升开始")
                                    self.click_btn(JUESE_BTN["rank_on"], until_appear=JUESE_BTN["rank_up_ok"])
                                    self.click_btn(JUESE_BTN["zdqh_ok"], until_appear=JUESE_BTN["rank_up_complete"])
                                    for _ in range(2):
                                        self.fclick(1, 1)
                                        if debug:
                                            print("rank提升完成")
                                        continue
                                else:
                                    # rank提升关闭，那就有装备就穿，等级拉满。由于提示升rank，不会缺装备
                                    if ehs > 1:
                                        self.click_btn(JUESE_BTN["zdqh_1"], until_appear=JUESE_BTN["zdqh_ok"])
                                        self.click_btn(JUESE_BTN["zdqh_ok"], until_appear=JUESE_BTN["equip_selected"])
                                        if ehs == 4:
                                            continue
                                    # 拉满了跑路
                                    if debug:
                                        print("rank任务完成")
                                    break
                                continue

                            if ehs == 0:
                                # 穿满强化满等级满
                                if debug:
                                    print("穿满，无动作")
                                break

                            if ehs == 1:
                                # 自动强化亮，判断是否缺装备。因为没强化满也会亮
                                if self.is_exists(img="img/juese/reachable.bmp", at=(82, 150, 434, 347)) and do_shuatu is True\
                                        and self.check_shuatu() is True:
                                    time.sleep(2)
                                    self.click_btn(JUESE_BTN["zdqh_0"], until_appear=JUESE_BTN["tuijiancaidan"])
                                    time.sleep(2)
                                    self.click_btn(JUESE_BTN["enter_shuatu"], until_appear=FIGHT_BTN["baochou"])
                                    fi = FightInfoBase(self)
                                    sc = self.getscreen()
                                    stars = fi.get_upperright_stars(sc)
                                    if stars < 3:
                                        tili_left = fi.get_tili_left(sc)
                                        if tili_left < 12:
                                            self.stop_shuatu()
                                            print("没有体力了，退出")
                                            for _ in range(6):
                                                self.click(1, 1)
                                            break
                                        fi.goto_tiaozhan()
                                        if debug:
                                            print("开始刷图补装备")

                                        # 支援
                                        fb = FightBianzuDXC(self)
                                        fb.select_team(team_order, change=3)
                                        if getzhiyuan:
                                            fb.get_zhiyuan(assist_num=1, force_haoyou=False, if_full=is_full)
                                        zd = fb.goto_zhandou()
                                        zd.set_auto(True)
                                        zd.set_speed(1, max_level=1)
                                        during = DuringFighting(self)
                                        while True:
                                            time.sleep(1)
                                            out = during.check(timeout=300, double_check=3)
                                            if isinstance(out, during.HaoYouMsg):
                                                out.exit_with_off()
                                                continue
                                            elif isinstance(out, during.FightingWinDXC):
                                                out.ok()
                                                fw = FightingWinZhuXian2(self).enter()
                                                time.sleep(5)
                                                fw.next()
                                                return True
                                            elif isinstance(out, during.FightingLossDXC):
                                                out.ok()
                                                return True
                                            # elif isinstance(out, next.TuanDuiZhanBox):
                                            #     out.OK()
                                            else:
                                                continue

                                    else:
                                        sc = self.getscreen()
                                        cishu = fi.get_cishu()
                                        if cishu == 0:
                                            for _ in range(6):
                                                self.click(1, 1)
                                            break
                                        if 3 >= cishu > 0:
                                            fi.set_saodang_to_max()
                                            self.stop_shuatu()
                                        if cishu > 3:
                                            tili_left = fi.get_tili_left(sc)
                                            if tili_left > 64:
                                                fi.set_saodang_cishu(6)
                                            if tili_left < 65:
                                                if tili_left < 13:
                                                    for _ in range(6):
                                                        self.click(1, 1)
                                                    print("没有体力了，退出")
                                                    break
                                                    # 这个break导致一直next_char
                                                fi.set_saodang_to_max()
                                                self.stop_shuatu()
                                        sd = fi.goto_saodang()
                                        sd = sd.OK()
                                        MsgList = sd.OK()  # 扫荡后的一系列MsgBox
                                        while True:
                                            out = MsgList.check()
                                            if out is None:  # 无msgbox
                                                break
                                            if isinstance(out, MsgList.XianDingShangDianBox):
                                                # 限定商店
                                                out.Cancel()
                                            if isinstance(out, MsgList.TuanDuiZhanBox):
                                                out.OK()
                                            if isinstance(out, MsgList.LevelUpBox):
                                                out.OK()
                                                self.start_shuatu()  # 体力又有了！
                                            if isinstance(out, MsgList.ChaoChuShangXianBox):
                                                out.OK()
                                        # 扫荡结束
                                        # 保险起见
                                        for _ in range(6):
                                            self.click(1, 1)
                                        if debug:
                                            print("刷图/扫荡完毕")
                                    continue
                                else:
                                    break

                            if ehs > 2:
                                # 自动强化有红点，等级不满或者没穿满，直接穿上且升级
                                time.sleep(1)
                                self.click_btn(JUESE_BTN["zdqh_1"], until_appear=JUESE_BTN["zdqh_ok"])
                                self.click_btn(JUESE_BTN["zdqh_ok"], until_appear=JUESE_BTN["equip_selected"])
                                continue
                        if debug:
                            print("等级装备强化任务开始")
                        # 专武
                        if do_zhuanwu:
                            ecb.goto_zhuanwu()
                            if debug:
                                print("专武任务开始")
                            ezw = CharZhuanwu(self)
                            while True:
                                zws = ezw.get_zhuanwu_status()
                                if debug:
                                    print('专武状态：%s' % zws)
                                if zws == 2:
                                    ezw.wear_zhuanwu()
                                    continue
                                if zws == 3 or zws == 5:
                                    c = ezw.unlock_ceiling(tozhuanwulv=tozhuanwulv)
                                    if c != 2:
                                        continue
                                    else:
                                        break
                                if zws == 4:
                                    ezw.levelup_zhuanwu()
                                    continue
                                if zws == 0 or zws == 1:
                                    break
                            ezw.goto_base()
                            if debug:
                                print("专武任务完成")
                        if debug:
                            print("此角色强化任务已完成")
                        ecb = CharBase(self)
                        ecb.goto_menu()

            if len(charlist) == 0:
                break

            if cm.check_buttom() is True:
                break
            else:
                cm.dragdown()
                if self.is_exists(img="img/juese/weijiesuo_w.bmp", at=(21, 144, 167, 463)):
                    break
                continue



        # 以下是旧方法
        # cm.click_first()
        # self.fclick(1,1)
        #
        # for charcount in range(0, count):
        #     # 全角色任务
        #     self.click_btn(JUESE_BTN["kaihua_unselected"])
        #     self.lock_img(JUESE_BTN["char_lv_unselected"], elseclick=(784,76), elsedelay=0.2)
        #     time.sleep(1)
        #     # 获取名称
        #     ekh = CharKaihua(self)
        #     charlist = set(charlist)
        #     charname = ekh.get_name()
        #     if debug:
        #         print(charname)
        #
        #     if charname in charlist:
        #         # 升星
        #         if do_kaihua:
        #             if debug:
        #                 print("升星任务开始")
        #             if ekh.get_starup_status():
        #                 ekh.cainengkaihua()
        #         ekh.goto_base()
        #         if debug:
        #             print("升星完成，前往base")
        #
        #         # 装备级等级强化
        #         while True:
        #             ecb = CharBase(self)
        #             ers = ecb.get_equip_status()
        #             ehs = ecb.get_enhance_status()
        #             if debug:
        #                 print("等级装备强化任务开始")
        #                 print('角色状态：%s' % ehs)
        #
        #             if ers == 2:
        #                 # 先处理升rank
        #                 if do_rank:
        #                     # rank提升开
        #                     if debug:
        #                         print("rank提升开始")
        #                     self.click_btn(JUESE_BTN["rank_on"], until_appear=JUESE_BTN["rank_up_ok"])
        #                     self.click_btn(JUESE_BTN["zdqh_ok"], until_appear=JUESE_BTN["rank_up_complete"])
        #                     for _ in range(2):
        #                         self.fclick(1, 1)
        #                         if debug:
        #                             print("rank提升完成")
        #                         continue
        #                 else:
        #                     # rank提升关闭，那就有装备就穿，等级拉满。由于提示升rank，不会缺装备
        #                     if ehs > 1:
        #                         self.click_btn(JUESE_BTN["zdqh_1"], until_appear=JUESE_BTN["zdqh_ok"])
        #                         self.click_btn(JUESE_BTN["zdqh_ok"], until_appear=JUESE_BTN["equip_selected"])
        #                         if ehs == 4:
        #                             continue
        #                     # 拉满了跑路
        #                     if debug:
        #                         print("rank任务完成")
        #                     break
        #                 continue
        #
        #             if ehs == 0:
        #                 # 穿满强化满等级满
        #                 if debug:
        #                     print("穿满，无动作")
        #                 break
        #
        #             if ehs == 1:
        #                 # 自动强化亮，判断是否缺装备。因为没强化满也会亮
        #                 if self.is_exists(img="img/juese/reachable.bmp", at=(82, 150, 434, 347)) and do_shuatu is True\
        #                         and self.check_shuatu() is True:
        #                     time.sleep(2)
        #                     self.click_btn(JUESE_BTN["zdqh_0"], until_appear=JUESE_BTN["tuijiancaidan"])
        #                     time.sleep(2)
        #                     self.click_btn(JUESE_BTN["enter_shuatu"], until_appear=FIGHT_BTN["baochou"])
        #                     fi = FightInfoBase(self)
        #                     sc = self.getscreen()
        #                     stars = fi.get_upperright_stars(sc)
        #                     if stars < 3:
        #                         tili_left = fi.get_tili_left(sc)
        #                         if tili_left < 12:
        #                             self.stop_shuatu()
        #                             print("没有体力了，退出")
        #                             for _ in range(6):
        #                                 self.click(1, 1)
        #                             break
        #                         fi.goto_tiaozhan()
        #                         if debug:
        #                             print("开始刷图补装备")
        #
        #                         # 支援
        #                         fb = FightBianzuDXC(self)
        #                         fb.select_team(team_order, change=3)
        #                         if getzhiyuan:
        #                             fb.get_zhiyuan(assist_num=1, force_haoyou=False, if_full=is_full)
        #                         zd = fb.goto_zhandou()
        #                         zd.set_auto(True)
        #                         zd.set_speed(1, max_level=1)
        #                         during = DuringFighting(self)
        #                         while True:
        #                             time.sleep(1)
        #                             out = during.check(timeout=300, double_check=3)
        #                             if isinstance(out, during.HaoYouMsg):
        #                                 out.exit_with_off()
        #                                 continue
        #                             elif isinstance(out, during.FightingWinDXC):
        #                                 out.ok()
        #                                 fw = FightingWinZhuXian2(self).enter()
        #                                 time.sleep(5)
        #                                 fw.next()
        #                                 return True
        #                             elif isinstance(out, during.FightingLossDXC):
        #                                 out.ok()
        #                                 return True
        #                             # elif isinstance(out, next.TuanDuiZhanBox):
        #                             #     out.OK()
        #                             else:
        #                                 continue
        #
        #                     else:
        #                         sc = self.getscreen()
        #                         cishu = fi.get_cishu()
        #                         if cishu == 0:
        #                             for _ in range(6):
        #                                 self.click(1, 1)
        #                             break
        #                         if 3 >= cishu > 0:
        #                             fi.set_saodang_to_max()
        #                             self.stop_shuatu()
        #                         if cishu > 3:
        #                             tili_left = fi.get_tili_left(sc)
        #                             if tili_left > 64:
        #                                 fi.set_saodang_cishu(6)
        #                             if tili_left < 65:
        #                                 if tili_left < 13:
        #                                     for _ in range(6):
        #                                         self.click(1, 1)
        #                                     print("没有体力了，退出")
        #                                     break
        #                                     # 这个break导致一直next_char
        #                                 fi.set_saodang_to_max()
        #                                 self.stop_shuatu()
        #                         sd = fi.goto_saodang()
        #                         sd = sd.OK()
        #                         MsgList = sd.OK()  # 扫荡后的一系列MsgBox
        #                         while True:
        #                             out = MsgList.check()
        #                             if out is None:  # 无msgbox
        #                                 break
        #                             if isinstance(out, MsgList.XianDingShangDianBox):
        #                                 # 限定商店
        #                                 out.Cancel()
        #                             if isinstance(out, MsgList.TuanDuiZhanBox):
        #                                 out.OK()
        #                             if isinstance(out, MsgList.LevelUpBox):
        #                                 out.OK()
        #                                 self.start_shuatu()  # 体力又有了！
        #                             if isinstance(out, MsgList.ChaoChuShangXianBox):
        #                                 out.OK()
        #                         # 扫荡结束
        #                         # 保险起见
        #                         for _ in range(6):
        #                             self.click(1, 1)
        #                         if debug:
        #                             print("刷图/扫荡完毕")
        #                     continue
        #                 else:
        #                     break
        #
        #             if ehs > 2:
        #                 # 自动强化有红点，等级不满或者没穿满，直接穿上且升级
        #                 time.sleep(1)
        #                 self.click_btn(JUESE_BTN["zdqh_1"], until_appear=JUESE_BTN["zdqh_ok"])
        #                 self.click_btn(JUESE_BTN["zdqh_ok"], until_appear=JUESE_BTN["equip_selected"])
        #                 continue
        #         if debug:
        #             print("等级装备强化任务开始")
        #         # 专武
        #         if do_zhuanwu:
        #             ecb.goto_zhuanwu()
        #             if debug:
        #                 print("专武任务开始")
        #             ezw = CharZhuanwu(self)
        #             while True:
        #                 zws = ezw.get_zhuanwu_status()
        #                 if debug:
        #                     print('专武状态：%s' % zws)
        #                 if zws == 2:
        #                     ezw.wear_zhuanwu()
        #                     continue
        #                 if zws == 3 or zws == 5:
        #                     c = ezw.unlock_ceiling(tozhuanwulv=tozhuanwulv)
        #                     if c != 2:
        #                         continue
        #                     else:
        #                         break
        #                 if zws == 4:
        #                     ezw.levelup_zhuanwu()
        #                     continue
        #                 if zws == 0 or zws == 1:
        #                     break
        #             ezw.goto_base()
        #             if debug:
        #                 print("专武任务完成")
        #         if debug:
        #             print("此角色强化任务已完成")
        #         ecb = CharBase(self)
        #         ecb.next_char()
        #         charcount = charcount + 1
        #         if debug:
        #             print('计数：%s' % charcount)
        #     else:
        #         if debug:
        #             print("此角色无动作")
        #         ekh.goto_base()
        #         ecb = CharBase(self)
        #         ecb.next_char()
        #         charcount = charcount + 1
        #         if debug:
        #             print('计数：%s' % charcount)

        self.lock_home()
