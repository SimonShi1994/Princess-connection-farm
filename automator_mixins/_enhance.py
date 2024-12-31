import time

from automator_mixins._shuatu_base import ShuatuBaseMixin
from core.constant import JUESE_BTN, FIGHT_BTN, MAIN_BTN, HUODONG_BTN
from core.pcr_config import debug
from scenes.dxc.dxc_fight import FightBianzuDXC
from scenes.dxc.dxc_fight import FightingWinDXC, FightingLossDXC
from scenes.fight.fightinfo_zhuxian import FightInfoBase
from scenes.fight.fighting_zhuxian import FightingWinZhuXian2, HaoYouMsg
from scenes.root.juese import CharMenu, get_plate_img_path, CharBase, CharKaihua, CharZhuanwu, CharZhuangBei
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

    def zidongqianghua(self, do_rank=True, do_shuatu=True, do_kaihua=True, do_zhuanwu=True, do_loveplus=False,
                       charlist=None, team_order="zhanli", getzhiyuan=False, is_full=0, tozhuanwulv=150, torank=30,
                       sort="level", count=15):
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
        cm = self.get_zhuye().goto_juese()
        # 进入角色选择
        cm.sort_by(sort)
        cm.sort_down()

        while True:
            # 单页面循环

            sc = self.getscreen()
            for i in charlist[:]:
                plate_path = get_plate_img_path(i)
                for j in plate_path:
                    a = cm.click_plate(j, screen=sc)
                    if a is True:
                        cm.clear_initFC()
                        charlist.remove(i)
                        ecb = CharZhuangBei(self).enter()
                        ekh = ecb.goto_kaihua()
                        if do_kaihua:
                            if debug:
                                self.log.write_log('debug', "升星任务开始")
                            if ekh.get_starup_status():
                                ekh.cainengkaihua()
                        ecb = ekh.goto_zhuangbei()
                        if debug:
                            self.log.write_log('debug', "升星完成，前往base")

                        # 装备级等级强化
                        while True:
                            time.sleep(1)
                            ers = ecb.get_equip_status(char=i)
                            now_rank = ecb.get_rank()
                            if debug:
                                self.log.write_log('debug', "等级装备强化任务开始")
                                self.log.write_log('debug', '角色状态：%s' % ers)

                            # 能直接提升Rank的情况
                            if ers == 2 or ers == 4:
                                # 先处理升rank
                                if do_rank and (now_rank < torank):
                                    # rank提升开且小于目标rank
                                    if debug:
                                        self.log.write_log('debug', "rank提升开始")
                                    self.click_btn(JUESE_BTN["rank_on"], until_appear=JUESE_BTN["rank_up_ok"])
                                    self.click_btn(JUESE_BTN["zdqh_ok"], until_appear=JUESE_BTN["rank_up_complete"])
                                    for _ in range(2):
                                        self.fclick(1, 1)
                                        if debug:
                                            self.log.write_log('debug', "rank提升完成")
                                        continue
                                else:
                                    # rank提升关闭，那就有装备就穿，等级拉满。由于提示升rank，不会缺装备
                                    if ers == 4:
                                        self.click_btn(JUESE_BTN["zdqh_1"], until_appear=JUESE_BTN["zdqh_ok"])
                                        self.click_btn(JUESE_BTN["zdqh_ok"], until_appear=JUESE_BTN["equip_selected"])
                                    # 拉满了跑路
                                    if ers == 2:
                                        # 已经满了
                                        pass
                                    if debug:
                                        self.log.write_log('debug', "rank任务完成")
                                    break
                                continue

                            # 不能直接提升rank情况下：
                            # 先做升级动作
                            if ers == 3 or ecb.get_char_lv_status() is True:
                                # 由于上限突破加入，技能等级一直有红点，请自行进行突破后再使用
                                time.sleep(1)
                                self.click_btn(JUESE_BTN["zdqh_1"], until_appear=JUESE_BTN["zdqh_ok"])
                                self.click_btn(JUESE_BTN["zdqh_ok"], until_appear=JUESE_BTN["equip_selected"])
                                continue

                            # 情况1.穿满了，不缺，跑路
                            if ers == 0 or ers == 1:
                                # 穿满强化满等级满
                                if debug:
                                    self.log.write_log('debug', "穿满，无动作")
                                break

                            # 情况2.穿满，缺件，开打
                            if ers == 5:
                                if do_shuatu is True:
                                    time.sleep(2)
                                    self.click_btn(JUESE_BTN["zdqh_0"], until_appear=JUESE_BTN["tuijiancaidan"])
                                    time.sleep(2)
                                    self.click_btn(JUESE_BTN["enter_shuatu"], until_appear=FIGHT_BTN["baochou"])
                                    ecb.clear_initFC()
                                    fi = FightInfoBase(self).enter()
                                    sc = self.getscreen()
                                    stars = fi.get_upperright_stars(sc)
                                    if stars < 3:
                                        tili_left = fi.get_tili_left(sc)
                                        if tili_left < 12:
                                            self.stop_shuatu()
                                            self.log.write_log('info', "没有体力了，退出")
                                            for _ in range(6):
                                                self.click(1, 1)
                                            break
                                        # fb = fi.goto_tiaozhan()
                                        if debug:
                                            self.log.write_log('debug', "开始刷图补装备")

                                        # 支援
                                        if getzhiyuan:
                                            r = fi.easy_shoushua(team_order, check_cishu=True, max_speed=1,
                                                                 get_zhiyuan=True, if_full=is_full)
                                            if r == 2:
                                                break
                                            if r == 3:
                                                self.stop_shuatu()
                                                break
                                            if r == 1:
                                                self.log.write_log('info', "打不过，跑了")
                                                break
                                            time.sleep(2)
                                            self.fclick(1, 1)
                                            continue
                                        else:
                                            r = fi.easy_shoushua(team_order, check_cishu=True, max_speed=1,
                                                                 get_zhiyuan=False)
                                            if r == 2:
                                                break
                                            if r == 3:
                                                self.stop_shuatu()
                                                break
                                            if r == 1:
                                                self.log.write_log('info', "打不过，跑了")
                                                break
                                            time.sleep(2)
                                            self.fclick(1, 1)
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
                                                    self.log.write_log('info', "没有体力了，退出")
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
                                        #
                                        if debug:
                                            self.log.write_log('debug', "保险起见，4s")
                                        time.sleep(2)
                                        self.fclick(1, 1)
                                        time.sleep(2)
                                        self.fclick(1, 1)
                                        if debug:
                                            self.log.write_log('debug', "刷图/扫荡完毕")
                                    continue
                                else:
                                    break

                        # 解决部分卡推荐强化菜单的问题
                        time.sleep(0.5)
                        self.fclick(1, 1)

                        if debug:
                            self.log.write_log('debug', "等级装备强化任务完成")
                        # 好感度升级
                        if do_loveplus:
                            ecb.loveplus(read_story=True)
                        # 专武
                        if do_zhuanwu:
                            ezw = ecb.goto_zhuanwu()
                            if debug:
                                self.log.write_log('debug', "专武任务开始")
                            while True:
                                zws = ezw.get_zhuanwu_status()
                                if debug:
                                    self.log.write_log('debug', '专武状态：%s' % zws)
                                if zws == 2:
                                    ezw.wear_zhuanwu()
                                    continue
                                if zws == 3 or zws == 5:
                                    if tozhuanwulv == 999:
                                        ezw.yijianqianghua()
                                    else:
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
                            ecb = ezw.goto_zhuangbei()
                            if debug:
                                self.log.write_log('debug', "专武任务完成")
                        if debug:
                            self.log.write_log('debug', "此角色强化任务已完成")
                        cm = ecb.goto_juese()
                        time.sleep(1)

            if len(charlist) == 0:
                break

            if cm.check_buttom() is True:
                break
            else:
                cm.dragdown()
                if self.is_exists(JUESE_BTN["weijiesuo_w"], at=(21, 144, 167, 463)):
                    break
                continue
        self.lock_home()

    def starup_six(self, charname=None, cname_lst=None):
        # 六星开花
        self.lock_home()
        cm = self.get_zhuye().goto_juese()
        # 进入角色选择
        win_status = 0
        cm.sort_by("star")
        cm.sort_down()

        while True:
            sc = self.getscreen()
            plate_path = get_plate_img_path(charname)
            for j in plate_path:
                a = cm.click_plate(j, screen=sc)
                if a is True:
                    cm.clear_initFC()
                    ecb = CharZhuangBei(self).enter()
                    ekh = ecb.goto_kaihua()
                    while True:
                        if win_status == 1 or self.is_exists(JUESE_BTN["cnkh"]):
                            self.click_btn(JUESE_BTN["cnkh"])
                            cor = self.img_where_all(JUESE_BTN["six_star_confirm"])
                            self.click(cor[0], cor[1])
                            self.log.write_log('info', "成功升6星")
                            break
                        if win_status == -1:
                            break
                        if self.is_exists(JUESE_BTN["yijianpeizhi"]):
                            self.click_btn(JUESE_BTN["yijianpeizhi"], until_appear=JUESE_BTN["shezhi"])
                            self.click_btn(JUESE_BTN["shezhi"], until_appear=JUESE_BTN["shuxingzhitisheng"])
                            self.fclick(477, 435)
                            time.sleep(5)
                            if self.is_exists(HUODONG_BTN["speaker_box"]):
                                self.fclick(1, 1)
                            continue
                        if self.is_exists(JUESE_BTN["unlock"]):
                            self.log.write_log("debug", "开花准备完毕")
                            self.click_btn(JUESE_BTN["unlock"], until_appear=JUESE_BTN["fight6"])
                            self.click_btn(JUESE_BTN["fight6"])
                            fi = FightInfoBase(self)
                            fb = fi.goto_tiaozhan()
                            for i in [5, 4, 3, 2, 1]:
                                self.click(FIGHT_BTN["empty"][i], post_delay=0.5)
                            fb.select_by_namelst(cname_lst)
                            F = fb.goto_fight()
                            F.set_auto(1)
                            D = F.get_during()
                            while True:
                                out = D.check()
                                if isinstance(out, D.FightingWinZhuXian):
                                    self.log.write_log("info", f"战胜了！")
                                    out.next()
                                    A = out.get_after()
                                    while True:
                                        out = A.check()
                                        if isinstance(out, A.FightingWinZhuXian2):
                                            out.next()
                                            win_status = 1
                                            break
                                        elif isinstance(out, A.ChaoChuShangXianBox):
                                            out.OK()

                                elif isinstance(out, D.FightingLoseZhuXian):
                                    self.log.write_log("info", f"战败了！")
                                    win_status = -1
                                    self.fclick(1, 1)
                                    break
                                elif isinstance(out, D.FightingDialog):
                                    out.skip()
                        if self.is_exists(JUESE_BTN["already_six"]):
                            self.log.write_log("info", "已经6星了")
                            break
                    self.lock_home()
