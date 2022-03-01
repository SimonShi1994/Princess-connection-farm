import time

from automator_mixins._tools import ToolsMixin
from scenes.clan.clan_battle import ClanBattleMAP, ClanBattlePre, ClanBattleBianzu


class HuizhanMixin(ToolsMixin):

    def gonghuizhan(self, team_order="zhanli", zhiyuan_mode=0, kick=0):
        self.lock_home()
        self.get_zhuye().goto_maoxian().goto_hanghui()
        cbm = ClanBattleMAP(self).enter()
        while True:  # 用完会战次数大循环
            cishu = cbm.get_cishu()
            if cishu > 0:
                cbp = cbm.goto_battlepre()  # 点到BOSS
                cbp.make_formal()
                cbb = cbp.goto_battle()

                if zhiyuan_mode == 0:
                    cbb.select_team(team_order)  # 不使用支援
                elif abs(zhiyuan_mode) == 3:
                    # 任意支援
                    if zhiyuan_mode < 0:
                        cbb.clear_team()
                    else:
                        cbb.select_team(team_order)
                    code = cbb.get_zhiyuan(is_full=kick)
                    if code > 0:
                        self.log.write_log("warning", f"借人出现奇怪的错误 【CODE={code}】，不知所措，自己打BOSS！")
                        if cbb.get_fight_current_member_count() < 5:
                            cbb.select_team(team_order)  # 重选一次
                    else:
                        self.log.write_log("info", "任意借人成功！")
                else:
                    raise Exception("公会战zhiyuan_mode只能为0或3或-3！")
                continue
            else:
                break

        self.lock_home()

