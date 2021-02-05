import os
import sqlite3
import time
from collections import defaultdict


def update():
    import brotli
    import requests
    if not os.path.isdir("pcrdata/data"):
        os.makedirs("pcrdata/data")

    print("正在下载最新数据包……")
    re = requests.get("https://redive.estertion.win/db/redive_cn.db.br")
    db = brotli.decompress(re.content)
    with open("pcrdata/data.db", "wb") as f:
        f.write(db)
    print("下载完毕！")


conn = sqlite3.connect("pcrdata/data.db")
cur = conn.cursor()

"""
Table Name
<equipment_data>        装备信息
    - equipment_id
    - equipment_name

<equipment_craft>       装备合成信息
    - equipment_id
    - condition_equipment_id_(N)
    - consume_num_(N)
    .. (10)

<unit_data>             角色信息
    - unit_id
    - unit_name
    - kana
    - atk_type 1:物理 2:魔法
    - rarity 1~3
    - 
    where comment<>'' and unit_id < 400000

<unit_promotion> Rank数据
    - unit_id
    - promotion_level
    - equip_slot_(N)
    .. (6)

<quest_data>
    - quest_id
    - area_id
    - quest_name
    - stamina
    - team_exp

"""

"""
DEBUG TOOLS
"""


def get_all_tables(filter=None):
    out = cur.execute("select name from sqlite_master order by name").fetchall()
    if filter is not None:
        out = [e for e in out if filter in e[0]]
    return out


def get_table_head(table):
    return cur.execute(f"pragma table_info({table})").fetchall()


def preview(table, *heads, where="", limit=1, with_title=True):
    if len(heads) == 0:
        heads = ["*"]
    if where != "":
        where = "where " + where
    return cur.execute(f"select {','.join(heads)} from {table} {where} limit {limit}").fetchall()


"""
Get Data
"""


def get_item_id_name():
    out = cur.execute("select item_id,item_name from item_data").fetchall()
    EQU_ID = {}
    ID_EQU = {}
    for id, nam in out:
        EQU_ID[nam] = id
        ID_EQU[id] = nam
    return EQU_ID, ID_EQU


def get_equip_id_name():
    out = cur.execute("select equipment_id,equipment_name from equipment_data").fetchall()
    EQU_ID = {}
    ID_EQU = {}
    for id, nam in out:
        EQU_ID[nam] = id
        ID_EQU[id] = nam
    return EQU_ID, ID_EQU


def get_chara_id_name():
    out = cur.execute("select unit_id,unit_name from unit_data where comment<>'' and unit_id < 400000").fetchall()
    CHARA_ID = {}
    ID_CHARA = {}
    for id, nam in out:
        CHARA_ID[nam] = id
        ID_CHARA[id] = nam
    return CHARA_ID, ID_CHARA


def create_CInfo(ID_CHARA):
    CInfo = {i: {} for i in ID_CHARA}
    return CInfo


def get_rank_need(CInfo):
    mid_str = ','.join([f"equip_slot_{i}" for i in range(1, 7)])
    out = cur.execute(f"select unit_id,promotion_level,{mid_str} from unit_promotion where unit_id<400000").fetchall()
    for id, rank, *zb in out:
        if id not in CInfo:
            continue
        CInfo[id].setdefault("rank", {})
        CInfo[id]["rank"][rank] = list(zb)


def get_chara_info(CInfo):
    """
    <unit_data>             角色信息
    - unit_id
    - unit_name
    - kana
    - atk_type 1:物理 2:魔法
    - rarity 1~3
    -
    where comment<>'' and unit_id < 400000
    :param CInfo:
    :return:
    """
    out = cur.execute(
        f"select unit_id,atk_type,rarity from unit_data where comment<>'' and unit_id < 400000").fetchall()
    for id, atk_type, rarity in out:
        if id not in CInfo:
            continue
        CInfo[id]["atk_type"] = atk_type
        CInfo[id]["rarity"] = rarity


def create_MInfo():
    """
    <quest_data>
    - quest_id
    - area_id
    - quest_name
    - stamina
    - team_exp

    11AAABBB - N-AAA-BBB关
    12AAABBB - H-AAA-BBB关
    18001BBB - 调查BBB等级
    """
    out = cur.execute("select quest_id,quest_name,stamina,team_exp from quest_data")
    MInfo = {}
    for qid, qnam, tili, exp in out:
        MInfo[qid] = {
            "nam": qnam,
            "tili": tili,
            "exp": exp
        }
    return MInfo


def get_map_enemy_group(MInfo):
    mid_str = ','.join([f"wave_group_id_{i}" for i in range(1, 4)])
    out = cur.execute(f"select quest_id,{mid_str} from quest_data")
    for id, gp1, gp2, gp3 in out:
        if id not in MInfo:
            continue
        MInfo[id].setdefault("wave", {})
        MInfo[id]["wave"][1] = gp1
        MInfo[id]["wave"][2] = gp2
        MInfo[id]["wave"][3] = gp3


def create_equip_info(ID_EQU):
    EInfo = {i: {"craft": []} for i in ID_EQU}
    return EInfo


def get_craft_info(EInfo):
    """
    <equipment_craft>       装备合成信息
    - equipment_id
    - condition_equipment_id_(N)
    - consume_num_(N)
    .. (10)
    """
    mid_str = ','.join([f"condition_equipment_id_{i},consume_num_{i}" for i in range(1, 11)])
    out = cur.execute(f"select equipment_id,{mid_str} from equipment_craft")
    for id, *p in out:
        if id not in EInfo:
            continue
        for a, b in zip(p[::2], p[1::2]):
            if a == 0:
                break
            EInfo[id]["craft"] += [(a, b)]


def get_equip_base_info(EInfo):
    out = cur.execute(f"select equipment_id,promotion_level from equipment_data")
    for id, plevel in out:
        if id not in EInfo:
            continue
        EInfo[id]["plevel"] = plevel


def create_wave_info():
    WInfo = {}
    mid_str = ','.join([f"enemy_id_{i},drop_gold_{i},drop_reward_id_{i}" for i in range(1, 6)])
    out = cur.execute(f"select wave_group_id,{mid_str} from wave_group_data")
    for wgid, *p in out:
        WInfo[wgid] = []
        for a, b, c in zip(p[::3], p[1::3], p[2::3]):
            if a == 0:
                continue
            WInfo[wgid] += [
                {"eid": a,
                 "rid": c}
            ]
    return WInfo


def create_reward_info():
    RInfo = {}
    mid_str = ','.join([f"reward_type_{i},reward_id_{i},reward_num_{i},odds_{i}" for i in range(1, 6)])
    out = cur.execute(f"select drop_reward_id,{mid_str} from enemy_reward_data")
    for rid, *p in out:
        RInfo[rid] = []
        for a, b, c, d in zip(p[::4], p[1::4], p[2::4], p[3::4]):
            if a == 0:
                continue
            RInfo[rid] += [
                {
                    "typ": a,
                    "rid": b,
                    "num": c,
                    "odds": d
                }
            ]
    return RInfo


def dict_plus(d1, d2, is_copy=True):
    if is_copy:
        d = d1.copy()
    else:
        d = d1
    for k, v in d2.items():
        if k in d:
            d[k] += v
        else:
            d[k] = v
    return d


class PCRData:
    def __init__(self):
        # INITING>>>
        self.EQU_ID, self.ID_EQU = get_equip_id_name()
        self.ITEM_ID, self.ID_ITEM = get_item_id_name()
        self.MInfo = create_MInfo()
        self.WInfo = create_wave_info()
        self.RInfo = create_reward_info()
        self.EInfo = create_equip_info(self.ID_EQU)
        get_craft_info(self.EInfo)
        get_equip_base_info(self.EInfo)
        self.C_ID, self.ID_C = get_chara_id_name()
        self.CInfo = create_CInfo(self.ID_C)
        get_map_enemy_group(self.MInfo)
        get_chara_info(self.CInfo)
        get_rank_need(self.CInfo)
        self.last_update_time = time.time()

    @staticmethod
    def dict_plus(d1, d2, is_copy=True):
        dict_plus(d1, d2, is_copy)

    def get_waves(self, quest_id):
        return self.MInfo[quest_id]["wave"]

    def get_wave_rewards(self, wave_id):
        return [obj['rid'] for obj in self.WInfo[wave_id] if obj['rid'] != 0]

    def parse_reward(self, reward_id, ):
        # Only TYPE 4 REWARD!
        reward_list = []
        for cur in self.RInfo[reward_id]:
            reward_list += [cur]
        return reward_list

    def _calc_quest_reward(self, quest_id):
        rewards = []
        waves = self.get_waves(quest_id)
        for _, wave_id in waves.items():
            reward = self.get_wave_rewards(wave_id)
            for rew in reward:
                rewards.extend(self.parse_reward(rew))
        return rewards

    def calc_normal_reward(self, A, B):
        # Only 装备
        normal_quest = 11000000 + A * 1000 + B
        rewards = self._calc_quest_reward(normal_quest)
        rewards = [r for r in rewards if r['typ'] == 4]
        return rewards

    def calc_hard_reward(self, A, B):
        # Only 装备+碎片
        hard_quest = 12000000 + A * 1000 + B
        rewards = self._calc_quest_reward(hard_quest)
        rewards = [r for r in rewards if r['typ'] == 4 or str(r['rid'])[0] == 3]
        return rewards

    def make_normal_map_prob(self, maxtu=None):
        choose = []
        EQUIP_PROB = {}
        for quest_id in self.MInfo.keys():
            if str(quest_id).startswith("11"):
                choose += [((quest_id // 1000) % 1000, quest_id % 1000)]
        for A, B in choose:
            if maxtu is not None:
                if A > maxtu:
                    continue
            rewards = self.calc_normal_reward(A, B)
            for rew in rewards:
                eid = rew["rid"]
                odd = rew["odds"]
                EQUIP_PROB.setdefault(eid, [])
                EQUIP_PROB[eid] += [(odd, (A, B))]
        # Sort
        for key in EQUIP_PROB:
            EQUIP_PROB[key].sort(reverse=True)
        return EQUIP_PROB

    def equip_name(self, equip_id):
        return self.ID_EQU[equip_id]

    def item_name(self, item_id):
        return self.ID_ITEM[item_id]

    def get_name(self, id):
        if id in self.ID_C:
            return self.ID_C[id]
        elif id in self.ID_EQU:
            return self.ID_EQU[id]
        elif id in self.ID_ITEM:
            return self.ID_ITEM[id]
        else:
            return None

    def get_id(self, name):
        if name in self.C_ID:
            return self.C_ID[name]
        elif name in self.EQU_ID:
            return self.EQU_ID[name]
        elif name in self.ITEM_ID:
            return self.ITEM_ID[name]
        else:
            return None

    def calc_equip_decompose(self, equip_id, num=1, store={}, copy=True):
        """
        store中有的部分会被事先消耗。
        store会被copy，不用担心数据丢失。
        """
        if copy:
            store = store.copy()
        need = {}

        def fun(eid, num):
            if eid in store and store[eid] > 0:
                store[eid] -= num
                if store[eid] <= 0:
                    num = -store[eid]
                    del store[eid]
                else:
                    num = 0
            if num > 0:
                clist = self.EInfo[eid]['craft']
                if len(clist) == 0:
                    need.setdefault(eid, 0)
                    need[eid] += num
                else:
                    for i, n in clist:
                        fun(i, n * num)

        fun(equip_id, num)
        return need

    def calc_equips_decompose(self, equip_dict, store={}):
        store = store.copy()
        need = {}
        for k, v in equip_dict.items():
            next_need = self.calc_equip_decompose(k, v, store, False)
            need = dict_plus(need, next_need)
        return need

    def calc_rankup_equip(self, chara_id, old_rank, old_zb, new_rank, new_zb):
        ranks = self.CInfo[chara_id]['rank']
        need_zb = []

        def fun(z):
            if z == 0:
                return [False] * 6
            elif z == 6:
                return [True] * 6
            elif z == 5:
                return [True, True, True, False, True, True]
            elif z == 1:
                return [False, True, True, True, True, True]
            elif z == 2:
                return [True, True, False, False, False, False]
            else:
                return z

        old_zb = fun(old_zb)
        new_zb = fun(new_zb)
        if old_rank == new_rank:
            for i in range(6):
                if not old_zb[i] and new_rank[i]:
                    need_zb += [ranks[old_rank][i]]
        else:
            for i in range(6):
                if not old_zb[i]:
                    need_zb += [ranks[old_rank][i]]

        if new_rank > old_rank:
            for i in range(6):
                if not new_zb[i]:
                    need_zb += [ranks[new_rank][i]]

        for now_rank in range(old_rank + 1, new_rank):
            for i in range(6):
                need_zb += [ranks[now_rank][i]]
        zb_dict = {}

        for zb in need_zb:
            if zb != 999999:  # ???
                zb_dict.setdefault(zb, 0)
                zb_dict[zb] += 1
        return zb_dict

    @staticmethod
    def make_map_advice(lack_equip: dict, prob_map: dict, num_w=0):
        # 整数规划问题
        import cvxpy as cp
        can_maps = defaultdict(list)
        for equ in lack_equip:
            if equ in prob_map:
                for prob, (A, B) in prob_map[equ]:
                    can_maps[f"{A}-{B}"] += [(equ, prob)]
        map_id = {}
        for ind, k in enumerate(can_maps):
            map_id[ind] = k
        x = cp.Variable(len(map_id), name="x")
        xflag = cp.Variable(len(map_id), name="xflag", boolean=True)
        cons = [x >= 0]
        equ_x = defaultdict(list)
        for mid in map_id:
            lst = can_maps[map_id[mid]]
            for equ, prob in lst:
                equ_x[equ] += [x[mid] * (prob / 100)]
        for c, exps in equ_x.items():
            cons += [cp.sum(exps) >= lack_equip[c]]
        if num_w > 0:
            cons += [x <= xflag * 100000]
            obj = cp.Minimize(cp.sum(x) + cp.sum(xflag) * num_w)
        else:
            obj = cp.Minimize(cp.sum(x))
        prob = cp.Problem(obj, cons)
        result = prob.solve(verbose=True)
        out_map = {}
        int_result = 0
        for ind, a in enumerate(x):
            v = round(a.value)
            if v == 0:
                continue
            out_map[map_id[ind]] = int(v)
            int_result += v
        return out_map, int_result
