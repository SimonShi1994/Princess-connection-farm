import base64
import datetime
import gzip
import json
import os
import pickle
import time
from collections import defaultdict
from io import BytesIO
from typing import Optional, TYPE_CHECKING

from rich.table import Table as RTable

from core.constant import USER_DEFAULT_DICT as UDD
from core.usercentre import AutomatorRecorder
from core.utils import get_time_str, WowSearch

if TYPE_CHECKING:
    from pcrdata.pcrdata import PCRData
    from core.utils import WowSearch
import rich.box as rbox
from core.richutils import RText, ROrderGrid, ROneTable, RValue, RComment, RLRProgress

JSNameWow: Optional[WowSearch] = None
ZBNameWow: Optional[WowSearch] = None


def LoadPCRData() -> "PCRData":
    global data, JSNameWow, ZBNameWow
    if not os.path.isdir("pcrdata"):
        os.makedirs("pcrdata")
    if not os.path.exists("pcrdata/data.dat"):
        return None
    try:
        data = pickle.load(open("pcrdata/data.dat", "rb"))
        try:
            JSNameWow = WowSearch(data.C_ID)
            JSNameWow.parse()
        except Exception as e:
            print("角色搜索模块加载失败！", e)
            JSNameWow = None
        try:
            ZBNameWow = WowSearch(data.EQU_ID)
            ZBNameWow.parse()
        except Exception as e:
            print("角色搜索模块加载失败！", e)
            ZBNameWow = None

        return data
    except Exception as e:
        print("读取数据发生错误！", e)
        return None


def UpdateData():
    global data
    if not os.path.isdir("pcrdata"):
        os.makedirs("pcrdata")
    try:
        import pcrdata.pcrdata as pcrdata
        pcrdata.update()
        data = pcrdata.PCRData()
        pickle.dump(data, open("pcrdata/data.dat", "wb"))
        return data
    except Exception as e:
        print("更新数据发生错误：", e)
        return None


last_account = ""
AR: Optional[AutomatorRecorder] = None


def GetLastAccount():
    global last_account, AR
    if not os.path.exists("bind_account.txt"):
        last_account = ""
        AR = None
        return
    with open("bind_account.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        if len(lines) > 0:
            last_account = lines[0]
            AR = AutomatorRecorder(last_account)


def UnBind():
    global last_account, AR
    last_account = ""
    AR = None
    with open("bind_account.txt", "w", encoding="utf-8") as f:
        f.write("")


def BindAccount(account):
    global last_account, AR
    if account != "":
        last_account = account
        AR = AutomatorRecorder(account)
    with open("bind_account.txt", "w", encoding="utf-8") as f:
        f.write(account)
    print("account绑定成功：", account)


def ZB_KC_FIX():
    # 修复装备库存
    global AR
    kc = AR.get("zhuangbei_kucun", UDD["zhuangbei_kucun"])
    bad_k = []
    for k in kc:
        if k not in data.EQU_ID:
            bad_k += [k]
    if len(bad_k) == 0:
        print("装备库存无需修复。")
        return
    print("检测到有", len(bad_k), "个条目需要修复：")
    print("装备 库存 修复 ----------------------")
    print("接下来每行会输出一个名称不符的条目，并给出它的最近更新时间。")
    print("请输入它的正确名称，则该条目将会被替换为此名称。")
    print("若存在较新条目已经存在该名称，则此项会被舍弃。")
    print("若存在较旧条目已经存在该名称，此项将替换之。")
    print("输入 0 表示舍弃该项。")
    print("您可以在/ocrfix文件夹中找到出错的条目的截图以便于识别。")
    print("您可以手动把错误截图的文件名改为正确的名称，则下次再次识别出错时会自动修复。")
    total = len(bad_k)
    for ind, k in enumerate(bad_k):
        while True:
            v = kc[k]
            num, tim, bz = v
            print("[", ind + 1, "/", total, "] 上次更新:", get_time_str(tim), "数量", num, "备注", bz)
            new_k = input(f"{k}   ->   ")
            if new_k == "0":
                del kc[k]
                AR.set("zhuangbei_kucun", kc)
                break
            elif new_k not in data.EQU_ID:
                print("该名称不存在！")
            elif new_k in kc:
                if kc[new_k][1] > tim:
                    print("存在较新记录，此项作废。")
                else:
                    print("存在较旧记录，此项替换。")
                    kc[new_k] = kc.pop(k)
                    AR.set("zhuangbei_kucun", kc)
                break
            else:
                kc[new_k] = kc.pop(k)
                AR.set("zhuangbei_kucun", kc)
                break
    print("修复已完成！")


def JS_FIX():
    # 修复角色信息
    global AR
    kc = AR.get("juese_info", UDD["juese_info"])
    bad_k = []
    for k in kc:
        if k not in data.C_ID:
            bad_k += [k]
    if len(bad_k) == 0:
        print("角色名称无需修复。")
        return
    print("检测到有", len(bad_k), "个条目需要修复：")
    print("角色 修复 ---------------------------")
    print("接下来每行会输出一个名称不符的条目，并给出它的最近更新时间。")
    print("请输入它的正确名称，则该条目将会被替换为此名称。")
    print("若存在较新条目已经存在该名称，则此项会被舍弃。")
    print("若存在较旧条目已经存在该名称，此项将替换之。")
    print("输入 0 表示舍弃该项。")
    print("您可以在/ocrfix文件夹中找到出错的条目的截图以便于识别。")
    print("您可以手动把错误截图的文件名改为正确的名称，则下次再次识别出错时会自动修复。")
    total = len(bad_k)
    for ind, k in enumerate(bad_k):
        while True:
            v = kc[k]
            print("[", ind + 1, "/", total, "] 上次更新:", get_time_str(v['last_update']))
            new_k = input(f"{k}   ->   ")
            if new_k == "0":
                del kc[k]
                AR.set("juese_info", kc)
                break
            elif new_k not in data.C_ID:
                print("该名称不存在！")
            elif new_k in kc:
                if kc[new_k]['last_update'] > v['last_update']:
                    print("存在较新记录，此项作废。")
                else:
                    print("存在较旧记录，此项替换。")
                    kc[new_k] = kc.pop(k)
                    AR.set("juese_info", kc)
                break
            else:
                kc[new_k] = kc.pop(k)
                AR.set("juese_info", kc)
                break
    print("修复已完成！")


def ToLibrary():
    # 角色
    from functools import reduce
    List1 = []
    js = AR.get("juese_info", UDD["juese_info"])
    for j, v in js.items():
        if j not in data.C_ID:
            continue
        cur = {}
        # e: equip 000000
        cur['e'] = reduce(lambda x, y: x + str(int(y)), v['zb'], "")
        # p: Rank
        cur['p'] = int(v["rank"])
        # r: Star
        cur['r'] = int(v["star"])
        # u: id
        cur['u'] = hex(data.C_ID[j] // 100)[2:]
        # t: track
        cur['t'] = v.get("track", False)
        # q: special
        cur['q'] = v.get("special", "")
        List1 += [cur]

    List2 = []
    # zb
    zb = AR.get("zhuangbei_kucun", UDD["zhuangbei_kucun"])
    for z, v in zb.items():
        if z not in data.EQU_ID:
            continue
        cur = {}
        # c: num
        num, _, _ = v
        cur['c'] = str(num)
        # e: id
        cur['e'] = hex(data.EQU_ID[z])[2:]
        # a: hide
        cur['a'] = '1'
        List2 += [cur]

    print("CODE------------------------------")
    print(base64.b64encode(gzip.compress(bytes(json.dumps([List1, List2]), encoding='utf-8'))).decode("utf-8"))
    print("----------------------------------")
    print("https://pcredivewiki.tw/Armory")


def FromLibrary(all=False):
    code = input("请粘贴Code： ")
    output = json.load(BytesIO(gzip.decompress(base64.b64decode(code))))
    js_info = output[0]
    zb_info = output[1]
    # js
    js = AR.get("juese_info", UDD["juese_info"])
    for cur in js_info:
        uid = int(cur['u'], 16) * 100 + 1
        key = data.ID_C[uid]
        js.setdefault(key, {})
        if all:
            equ = [i == '1' for i in cur['e']]
            rank = cur['p']
            star = cur['r']
            js[key]['zb'] = equ
            js[key]['rank'] = rank
            js[key]['star'] = star
        track = cur['t']
        js[key]['track'] = track
        if track not in ["false", "true"]:
            if '.' in track:
                A, B = track.split(".")
                A = int(A)
                B = int(B)
                ZBLABLE = {
                    3: [False, True, False, True, False, True],
                    4: [False, True, False, True, True, True],
                    5: [False, True, True, True, True, True]
                }
                js[key]['track_rank'] = A
                js[key]['track_zb'] = ZBLABLE[B]
            else:
                A = int(track)
                js[key]["track_rank"] = A
                js[key]["track_zb"] = [True] * 6
        elif track == "false":
            if "track_rank" in js[key]:
                del js[key]["track_rank"]
            if "track_zb" in js[key]:
                del js[key]["track_zb"]

        special = cur['q']
        js[key]['special'] = special
    AR.set("juese_info", js)
    # zb
    zb = AR.get("zhuangbei_kucun", UDD["zhuangbei_kucun"])
    if all:
        for cur in zb_info:
            eid = int(cur['e'], 16)
            if eid in data.ID_EQU:
                key = data.ID_EQU[eid]
            else:
                continue
            comment = "From Lib"
            update_time = time.time()
            num = int(cur['c'])
            zb[key] = (num, update_time, comment)
        AR.set("zhuangbei_kucun", zb)


def SearchJSName(name: str) -> int:
    global JSNameWow
    if name.isnumeric():
        n = int(name)
        if n in data.ID_C:
            return n
        elif n * 100 + 1 in data.ID_C:
            return n * 100 + 1
        elif (n // 100) * 100 + 1 in data.ID_C:
            return (n // 100) * 100 + 1
        else:
            return -1
    if name in data.C_ID:
        return data.C_ID[name]
    else:
        if JSNameWow is None:
            return -1
        else:
            name = JSNameWow.get_all_by_tree(name)
            if len(name) == 0:
                return -1
            elif name[0] in data.C_ID:
                return data.C_ID[name[0]]
            else:
                return -1


def JS_SHOW(name):
    ID = SearchJSName(name)
    if ID == -1:
        print("找不到该角色！")
        return
    obj = AR.get("juese_info", UDD["juese_info"])
    name = data.ID_C[ID]
    print("角色信息：", name, " 角色ID：", ID // 100)
    if name in obj:
        v = obj[name]
        if 'star' in v:
            print("星：", *['★'] * v['star'])
        if 'dengji' in v:
            print("等级：", v['dengji'])
        CELL = {}
        # (0,0) - (0,1)
        CELL[(0, 0)] = 'R'
        if 'rank' in v:
            CELL[(0, 1)] = str(v['rank'])
        else:
            CELL[(0, 1)] = "？"
        # (1,0) - (3,1)
        if 'zb' not in v:
            for i in range(6):
                CELL[(1 + i // 2, i % 2)] = "？"
        else:
            for i in range(6):
                CELL[(1 + i // 2, i % 2)] = '■' if v['zb'][i] else '□'
        CELL[(1, 2)] = "-->"
        # (0,3) - (3,4)
        if 'track_rank' in v and 'track_zb' in v:
            flag = True
            CELL[(0, 3)] = 'R'
            CELL[(0, 4)] = str(v['track_rank'])
            for i in range(6):
                CELL[(1 + i // 2, i % 2 + 3)] = '■' if v['track_zb'][i] else '□'
        else:
            flag = False
        if flag:
            max_c = 4
        else:
            max_c = 1
        max_r = 3
        for r in range(max_r + 1):
            for c in range(max_c + 1):
                if (r, c) in CELL:
                    print(CELL[(r, c)], end='\t')
                else:
                    print(end='\t')
            print()
        if 'haogan' in v:
            print("好感：", v['haogan'])
        if 'special' in v:
            print("专武：", v["special"])
    else:
        print("你并没有这个角色！")


def ParseZBStr(zb_str):
    for z in zb_str:
        assert z in ['0', '1'], "装备字符串一定为0或1！"
    assert len(zb_str) == 6
    return [z == '1' for z in zb_str]


def JS_TRACK(name, rank=0, zb_str="", track_str=None):
    # rank=-1: 不跟踪
    # track_str is not None

    ID = SearchJSName(name)
    if ID == -1:
        print("找不到该角色！")
        return
    name = data.ID_C[ID]
    obj = AR.get("juese_info", UDD["juese_info"])
    if name not in obj:
        print("你并没有获得这个角色。")
        return
    if rank == -1:
        obj[name]["track"] = False
        if "track_rank" in obj[name]:
            del obj[name]["track_rank"]
        if "track_zb" in obj[name]:
            del obj[name]["track_zb"]
        AR.set("juese_info", obj)
        JS_SHOW(name)
        return
    if track_str is not None:
        if '.' not in track_str:
            A = int(track_str)
            rank = A
            zb_str = "111111"
        else:
            A, B = track_str.split('.')
            A = int(A)
            B = int(B)
            rank = A
            if B == 3:
                zb_str = '010101'
            elif B == 4:
                zb_str = '010111'
            elif B == 5:
                zb_str = '011111'
            else:
                raise Exception("错误的lib_track_str！")
        obj[name]["track"] = track_str
    obj[name]["track_rank"] = int(rank)
    obj[name]["track_zb"] = ParseZBStr(zb_str)
    AR.set("juese_info", obj)
    JS_SHOW(name)


def has_arg(args, key):
    for k in args:
        if k == key:
            return True
    return False


def get_arg(args, key, default):
    for k in args:
        if k.startswith(key):
            return k[k.find("=") + 1:]
    return default


def JS_TRACKINFO():
    from rich import print
    obj = AR.get("juese_info", UDD["juese_info"])
    zb = AR.get("zhuangbei_kucun", UDD["zhuangbei_kucun"])
    store = {}
    for k, v in zb.items():
        num, _, _ = v
        if k in data.EQU_ID:
            store[data.EQU_ID[k]] = num
    table = RTable(title="练度追踪", caption="*当前可满：以目前的库存最高能满装Rank。\n"
                                         "*下一RANK：要在下一RANK上满装还需要的碎片。", caption_justify="left")
    table.add_column("角色", justify='center')
    table.add_column("进度", justify='center')
    table.add_column("当前可满", justify='center')
    table.add_column("下一RANK", justify='center')
    for k, v in obj.items():
        if not ('track_rank' in v and 'track_zb' in v and 'zb' in v and 'rank' in v):
            continue
        if k not in data.C_ID:
            continue
        cid = data.C_ID[k]
        need_equip_before = data.calc_rankup_equip(cid, v['rank'], [False] * 6, v['track_rank'], v['track_zb'])
        before_store = data.calc_equips_decompose(need_equip_before)
        need_equip_after = data.calc_rankup_equip(cid, v['rank'], v['zb'], v['track_rank'], v['track_zb'])
        after_store = data.calc_equips_decompose(need_equip_after, store=store)
        before_sum = sum(before_store.values())
        after_sum = sum(after_store.values())
        if before_sum == 0:
            continue
        if after_sum == 0:
            continue
        cur_rank = v['rank']
        cur_after_sum = 0
        while cur_rank <= v['track_rank']:
            cur_zb = [True] * 6 if cur_rank < v['track_rank'] else v['track_zb']
            cur_need = data.calc_rankup_equip(cid, v['rank'], v['zb'], cur_rank, cur_zb)
            cur_after = data.calc_equips_decompose(cur_need, store=store)
            cur_after_sum = sum(cur_after.values())
            if cur_after_sum > 0:
                break
            cur_rank += 1
        R = []
        R += [k]
        OG = ROrderGrid(2)
        OG.add(RLRProgress(before_sum - after_sum, before_sum, RValue("R%2d" % v['rank']),
                           RValue("R%2d" % v['track_rank']), width=20, percent=False))
        OG.add(RComment(''.join(['O' if p else '_' for p in v['track_zb']])))
        OG.finish()
        R += [OG]
        cur_rank -= 1
        R += ["Rank " + str(cur_rank)]
        R += ["x" + str(cur_after_sum)]
        table.add_row(*R)
    print(table)


def JS_SET(name, item, value):
    ID = SearchJSName(name)
    if ID == -1:
        print("找不到该角色！")
        return
    name = data.ID_C[ID]
    obj = AR.get("juese_info", UDD["juese_info"])
    if name not in obj:
        print("你并没有获得这个角色。")
        return
    obj[name][item] = value
    obj[name]["last_update"] = time.time()
    AR.set("juese_info", obj)
    JS_SHOW(name)


def JS_NEW(name):
    ID = SearchJSName(name)
    if ID == -1:
        print("找不到该角色！")
        return
    name = data.ID_C[ID]
    obj = AR.get("juese_info", UDD["juese_info"])
    if name in obj:
        print("你已经获得了该角色！")
        return
    obj[name] = {
        "dengji": 1,
        "rank": 1,
        "haogan": 1,
        "zb": [False] * 6,
        "star": 1,
        "last_update": time.time(),
    }
    AR.set("juese_info", obj)
    JS_SHOW(name)


def JS_DEL(name):
    ID = SearchJSName(name)
    if ID == -1:
        print("找不到该角色！")
        return
    name = data.ID_C[ID]
    obj = AR.get("juese_info", UDD["juese_info"])
    if name not in obj:
        print("你并没有该角色！")
        return
    del obj[name]
    AR.set("juese_info", obj)



def ZB_ST_LACK(args):
    from rich import print
    need_equip = {}
    juese = AR.get("juese_info", UDD["juese_info"])
    for k, v in juese.items():
        if k in data.C_ID and "track_rank" in v and "track_zb" in v \
                and "rank" in v and "zb" in v:
            ne = data.calc_rankup_equip(data.C_ID[k], v["rank"], v["zb"], v["track_rank"], v["track_zb"])
            data.dict_plus(need_equip, ne, False)
    if has_arg(args, "--item"):
        lack = need_equip
    else:
        if not has_arg(args, "--no-store"):
            store = {}
            zb = AR.get("zhuangbei_kucun", UDD["zhuangbei_kucun"])
            for k, v in zb.items():
                num, _, _ = v
                if k in data.EQU_ID:
                    store[data.EQU_ID[k]] = num
            lack = data.calc_equips_decompose(need_equip, store)
        else:
            lack = data.calc_equips_decompose(need_equip)
    show = defaultdict(list)
    for equ in lack:
        show[data.EInfo[equ]['plevel']] += [equ]
    LABEL = {
        1: '铁',
        2: '铜',
        3: '银',
        4: '金',
        5: '紫',
        6: '红',
    }
    min_rare = int(get_arg(args, "--min-rare", "0"))
    max_rare = int(get_arg(args, "--max-rare", "6"))
    max_tu = get_arg(args, "--max-tu", None)
    if max_tu is not None:
        max_tu = int(max_tu)
    normal = data.make_normal_map_prob(max_tu)
    for k in sorted(show, reverse=True):
        if k < min_rare or k > max_rare:
            continue
        table = RTable(title="稀有度：" + LABEL[k], show_lines=True, box=rbox.HEAVY_EDGE)
        table.add_column("装备", justify="center")
        table.add_column("缺失", justify="center")
        if has_arg(args, "--normal"):
            table.add_column("刷取区域", justify="center")
        for equ in show[k]:
            row = [data.ID_EQU[equ], f"x{lack[equ]}"]
            if has_arg(args, "--normal"):
                if equ not in normal:
                    row += ['']
                else:
                    RR = ROrderGrid(8)
                    lst = normal[equ]
                    for prob, (A, B) in lst:
                        RR.add(ROneTable(f"{A}-{B}", f"{prob}%"))
                    RR.finish()
                    row += [RR]
            table.add_row(*row)
        print(table)


def ZB_ST_ADVICE(args):
    from rich import print
    max_tu = get_arg(args, "--max-tu", None)
    if max_tu is not None:
        max_tu = int(max_tu)
    min_rare = int(get_arg(args, "--min-rare", "0"))
    max_rare = int(get_arg(args, "--max-rare", "6"))
    num_w = float(get_arg(args, "--num-w", "0.1"))
    need_equip = {}
    js_need = {}
    zb_js = {}
    juese = AR.get("juese_info", UDD["juese_info"])
    for k, v in juese.items():
        if k in data.C_ID and "track_rank" in v and "track_zb" in v \
                and "rank" in v and "zb" in v:
            ne = data.calc_rankup_equip(data.C_ID[k], v["rank"], v["zb"], v["track_rank"], v["track_zb"])
            for n in list(ne.keys()):
                lv = data.EInfo[n]['plevel']
                if lv < min_rare or lv > max_rare:
                    ne.pop(n)
            ne2 = data.calc_equips_decompose(ne)
            for n in ne2:
                js_need.setdefault(k, {})
                js_need[k].setdefault(n, 0)
                js_need[k][n] += ne2[n]
                zb_js.setdefault(n, {})
                zb_js[n].setdefault(k, 0)
                zb_js[n][k] += ne2[n]
            data.dict_plus(need_equip, ne, False)
    store = {}
    if not has_arg(args, "--no-store"):

        zb = AR.get("zhuangbei_kucun", UDD["zhuangbei_kucun"])
        for k, v in zb.items():
            num, _, _ = v
            if k in data.EQU_ID:
                store[data.EQU_ID[k]] = num
        lack = data.calc_equips_decompose(need_equip, store)
    else:
        lack = data.calc_equips_decompose(need_equip)

    prob_map = data.make_normal_map_prob(max_tu)
    map_js = {}
    for k, v in zb_js.items():
        if k not in prob_map:
            continue
        m = prob_map[k]
        for _, (A, B) in m:
            mid = f"{A}-{B}"
            map_js.setdefault(mid, {})
            data.dict_plus(map_js[mid], v, False)
    out_map = None
    try:
        out_map, result_int = data.make_map_advice(lack, prob_map, num_w)
    except Exception as e:
        print(e)
        if num_w > 0:
            print("可能是混合整数搜索失败！你可能需要安装cvxopt依赖")
            out_map, result_int = data.make_map_advice(lack, prob_map, 0)

    mul = int(get_arg(args, "--n", "1"))
    if mul > 1:
        result_int = 0
        keys = list(out_map.keys())
        for i in keys:
            out_map[i] = int(round(out_map[i] / 2))
            if out_map[i] == 0:
                out_map.pop(i)
                continue
            result_int += out_map[i]
    out_sorted = sorted(out_map, reverse=True, key=lambda x: out_map[x])

    table = RTable(title="刷取建议",
                   caption=RText("倍率：") + RValue("【", mul, "】") + RText(' 总次数：') + RValue(int(result_int)),
                   box=rbox.HEAVY_EDGE, show_lines=True)
    js_flag = has_arg(args, "--js")
    zb_flag = has_arg(args, "--zb")
    store_flag = has_arg(args, "--no-store")
    table.add_column("图号", justify="center")
    table.add_column("次数", justify="center")
    if js_flag or zb_flag:
        table.add_column("详细信息", justify="center")
    for out in out_sorted:
        row = []
        row += [out]
        row += [f"x{out_map[out]}"]
        if zb_flag:
            RR = ROrderGrid(4)
            A, B = out.split('-')
            A = int(A)
            B = int(B)
            rew = data.calc_normal_reward(A, B)
            for r in rew:
                if r["rid"] in lack:
                    col = []
                    col += [data.ID_EQU[r['rid']]]
                    col += [RValue(f"x{lack[r['rid']]}")]
                    if not store_flag:
                        col[-1] += f"\t库存：{store.get(r['rid'], 0)}"
                    col += ["----------"]
                    sss = []
                    if js_flag:
                        sss += []
                        cur = zb_js[r['rid']]
                        for nam in sorted(cur, reverse=True, key=lambda x: cur[x]):
                            sss += ["%s x%d" % (nam, cur[nam])]
                        col += ['\n'.join(sss)]
                    ROT = ROneTable(*col)
                    RR.add(ROT)
            RR.finish()
            row += [RR]
        elif js_flag:
            cur = map_js[out]
            cur_sort = sorted(cur, reverse=True, key=lambda x: cur[x])
            sss = []
            for p in cur_sort:
                sss += ["%s x%d" % (p, cur[p])]
            row += ["\n".join(sss)]
        table.add_row(*row)
    print(table)


if __name__ == "__main__":
    GetLastAccount()
    print("---  PCR数据中心  ---")
    data = LoadPCRData()
    if data is None:
        print("数据库未加载")
    else:
        print("数据库上次更新时间：", datetime.datetime.fromtimestamp(data.last_update_time).strftime("%Y-%m-%d %H:%M:%S"))

    print("help 帮助")
    print("exit 退出")
    precmd = ""
    while True:
        try:
            prompt = "[未绑定]>" if last_account == "" else f"[{last_account}]> "
            cmd = input(prompt + precmd + " ")
            if cmd == "":
                precmd = ""
                continue
            cmd = precmd + " " + cmd
            cmd = cmd.strip()
            cmds = cmd.split(" ")
            order = cmds[0]
            if order == "help":
                print("帮助----------------------------")
                print("update 更新数据库[需要sqlite3, brotli依赖]")
                print("bind (account) 绑定一个账号，可以查看它的数据")
                if last_account != "":
                    print("zb 查看装备相关帮助")
                    print("js 查看角色相关帮助")
                    print("lib 查看图书馆插件")
                    print("xls 查看xls导入导出操作帮助 [敬请期待]")
                    print("enter [cmd] 如果频繁地输入前缀很麻烦，可以输入enter cmd自带前缀")
                    print("unbind 解绑账号")
            elif precmd == "" and order == "enter":
                precmd = cmd.strip()[5:]
                print("已经绑定前缀", precmd, "！不输入直接回车取消绑定。")
                continue

            elif order == "unbind":
                UnBind()
            elif order == "bind" and len(cmds) == 2:
                BindAccount(cmds[1])
            elif order == "update":
                UpdateData()
                data = LoadPCRData()
            elif order == "exit":
                break
            elif cmd == "zb":
                print("帮助 装备-------------------------")
                print("zb kc 查看库存相关帮助")
                print("zb st 查看装备刷图建议相关帮助")
            elif cmd == "zb kc":
                print("帮助 装备 库存---------------------")
                print("zb kc clear 清空之前记录 （删库警告！）")
                print("zb kc fix 修复因为ocr失误引起的错误库存")
                # print("zb kc last_update 最近一次更新时间")
            elif order == "zb" and len(cmds) > 2 and cmds[1] == "kc":
                if len(cmds) == 3 and cmds[2] == "clear":
                    AR.set("zhuangbei_kucun", UDD["zhuangbei_kucun"])
                elif len(cmds) == 3 and cmds[2] == "fix":
                    ZB_KC_FIX()
            elif cmd == "zb st":
                print("帮助 装备 刷图---------------------")
                print("注：必须为角色设置了追踪后才可以使用刷图帮助功能！")
                print("zb st lack [--options] 查询装备缺口")
                print("    --min-rare=... 最低等级（至少为1）")
                print("    --max-rare=... 最高等级（至多为6 <-红）")
                print("    --no-store     不计算库存")
                print("    --item         以装备显示而不是图纸显示")
                print("    --normal       显示普通图刷图提示")
                print("    --max-tu=...   限制最高图数")
                print("zb st advice 查询刷图建议")
                print("    --min-rare=... 最低等级（至少为1）")
                print("    --max-rare=... 最高等级（至多为6 <-红）")
                print("    --no-store     不计算库存")
                print("    --max-tu=...   限制最高图数")
                print("    --js           显示角色详细信息")
                print("    --zb           显示装备详细信息")
                print("    --n=...        设置倍率")
                print("    --num-w=...    懒人权重（>=0实数）\n"
                      "\t\t\t越高则给出的刷图选项越少，默认0.1\n"
                      "\t\t\t大于0时使用混合规划，越大越慢。")
            elif order == "zb" and len(cmds) >= 2 and cmds[1] == 'st':
                if len(cmds) >= 3 and cmds[2] == 'lack':
                    ZB_ST_LACK(cmds[3:])
                elif len(cmds) >= 3 and cmds[2] == "advice":
                    ZB_ST_ADVICE(cmds[3:])
            elif cmd == "js":
                print("帮助 角色-------------------------")
                print("js namehelp 查看缩写查询帮助")
                print("js clear 清空之前记录 (删库警告！)")
                print("js fix 修复因为ocr失误引起的角色名称错误")
                print("js trackinfo 显示角色的养成（跟踪）状态")
                print("js (name) 或 js (name) show 查看某一个角色的信息")
                print("js (name) track 查看角色追踪帮助")
                print("js (name) set 查看修改信息帮助")
            elif order == "js" and len(cmds) >= 2:
                if len(cmds) == 2 and cmds[1] == "clear":
                    AR.set("juese_info", UDD["juese_info"])
                elif len(cmds) == 2 and cmds[1] == "fix":
                    JS_FIX()
                elif len(cmds) == 2 and cmds[1] == "trackinfo":
                    JS_TRACKINFO()
                elif len(cmds) == 2 and cmds[1] == "namehelp":
                    print("帮助 角色 缩写助手-------------------")
                    print("在查询某一个角色时，有以下查询方式：")
                    print("全名查询：如千歌（圣诞节）")
                    print("拼音查询：如qiange(shengdanjie)或qiangeshengdanjie")
                    print("部分拼音查询：如qg(sdj)或qgsdj")
                    print("ID查询：如1084或108401")
                elif len(cmds) == 3 and cmds[2] == 'track':  # cmds[1]=(name)
                    print("帮助 角色追踪-----------------------")
                    print("js (name) track false 关闭追踪")
                    print("js (name) track (rank) (ZB_STR)")
                    print("    设置追踪到rank，ZB_STR为六个或0或1的数字，")
                    print("    分别表示从上到下，从左到右，不穿0或穿1.")
                    print("js (name) track (lib_track_str)")
                    print("    按照兰德索尔图书馆的格式设置追踪目标，该追踪可以导出到图书馆。")
                    print("    格式：A或A.B,其中B只能为3,4,5")
                    print("    [EG] 8.3: [XOXOXO]")
                    print("         8.4: [XOXOOO]")
                    print("         8.5: [XOOOOO]")
                    print("         8 :  [OOOOOO]")
                elif len(cmds) == 4 and cmds[2] == "track":
                    if cmds[3] == "false":
                        JS_TRACK(cmds[1], -1)
                    else:
                        JS_TRACK(cmds[1], track_str=cmds[3])
                elif len(cmds) == 5 and cmds[2] == "track":
                    JS_TRACK(cmds[1], int(cmds[3]), cmds[4])
                elif len(cmds) == 3 and cmds[2] == "set":
                    print("帮助 角色设置----------------------")
                    print("js (name) set new  获得角色")
                    print("js (name) set rank (rank) 设置当前rank")
                    print("js (name) set zb (ZB_STR) 设置当前衣服")
                    print("    ZB_STR为六个或0或1的数字，")
                    print("    分别表示从上到下，从左到右，不穿0或穿1.")
                    print("js (name) set love (love) 设置好感度")
                    print("js (name) set special (special) 设置专武")
                    print("    * 此项对接图书馆的专武字符串，但我还没有研究过它的格式")
                    print("js (name) set star (star) 设置星级（1~5）")
                    print("js (name) set level (level) 设置等级")
                elif len(cmds) == 4 and cmds[2] == "set" and cmds[3] == "new":
                    JS_NEW(cmds[1])
                elif len(cmds) == 4 and cmds[2] == "set" and cmds[3] == "del":
                    JS_DEL(cmds[1])
                elif len(cmds) == 5 and cmds[2] == "set":
                    if cmds[3] == "rank":
                        JS_SET(cmds[1], "rank", int(cmds[4]))
                    elif cmds[3] == "zb":
                        JS_SET(cmds[1], "zb", ParseZBStr(cmds[4]))
                    elif cmds[3] == "love":
                        JS_SET(cmds[1], "haogan", int(cmds[4]))
                    elif cmds[3] == "special":
                        JS_SET(cmds[1], "special", cmds[4])
                    elif cmds[3] == "star":
                        JS_SET(cmds[1], "star", int(cmds[4]))
                    elif cmds[3] == "level":
                        JS_SET(cmds[1], "dengji", int(cmds[4]))

                elif len(cmds) == 2 or (len(cmds) == 3 and cmds[2] == 'show'):  # cmds[1]=(name)
                    JS_SHOW(cmds[1])

            elif cmd == "lib":
                print("帮助 图书馆-------------------------")
                print("注：请实现进行zb kc fix和js fix确保OCR正确性！")
                print("lib output 导出到图书馆")
                print("lib input [-all] 从图书馆导入\n"
                      "    （选择all：全部导入（不推荐）；否则：只导入专武和追踪信息）")
            elif order == "lib" and len(cmds) >= 2:
                if len(cmds) == 2 and cmds[1] == 'output':
                    ToLibrary()
                elif len(cmds) in [2, 3] and cmds[1] == 'input':
                    if len(cmds) == 3 and cmds[2] == '-all':
                        FromLibrary(True)
                    elif len(cmds) == 2:
                        FromLibrary(False)
            elif cmd == "xls":
                print("帮助 xls操作------------------------")
                print("xls output 导出到xls/account.xls [敬请期待]")
                print("xls input 从xls/account.xls导入 [敬请期待]")
        except Exception as e:
            print("输入错误！", e)
