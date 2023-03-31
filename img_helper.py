from screencut import AutomatorDebuger, WindowMode, ImgBox


def trycopy(text):
    try:
        import pyperclip
        pyperclip.copy(text)
        print("已复制到剪贴板！")
    except:
        print("复制到剪贴板失败，可能没装pyperclip依赖。")


if __name__ == "__main__":
    self = AutomatorDebuger()
    WindowMode()
    print("！！！必须要先连接模拟器！！！")
    while True:
        try:
            print("------ 图片坐标编辑小助手 -------")
            print("1: 新增Rank图标 (img/ranks)")
            print("2a: 新增新图图名 (img/zhuxian)")
            print("2b: 录入Normal坐标")
            print("2c: 录入Hard坐标")
            print("2d: 录入VH坐标")
            print("------------------------------")
            print("exit 退出")
            print("connect [series]  连接到模拟器，若不指定series，则默认连接第一个检测到的模拟器。")
            cmd = input("> ")
            cmds = cmd.split(" ")
            order = cmds[0]
            if order == "connect":
                if len(cmds) == 1:
                    self.Connect()
                else:
                    self.Connect(cmds[1])
                print("连接到：", self.address)
            elif order == "1":
                print("------- 新增Rank图标 -------")
                rank = input("请输入要添加的Rank： （请输入整数，输入-1 退出）").strip()
                if rank == "-1": continue
                rank = int(rank)
                print(f"请打开PCR，进入：角色，选择一个Rank为{rank}的角色并进入。")
                input("按下回车继续")
                print("正在截图……为了避免信息丢失，强制使用慢速截图。")
                self.Shot(force_slow=True, show=False, file="rank_window.bmp")
                print("请用右键框选 [品级 X] 区域，双击左键可重置框选。")
                print("按下a键记录当前选取，关闭窗口继续下一步。")
                click = self.Show(file="rank_window.bmp", verbose=False, return_click=True)
                img = ImgBox(filepath="rank_window.bmp")
                at = click['at'][-1]
                addr = f"img/ranks/{rank}.bmp"
                img.cut(*at).save(addr)
                print("图片已经保存到：", addr)
                print("请将以下代码粘贴到：core/constant.py 的RANKS_DICT字典中。")
                print()
                CODE = f"""    {rank}: p(img="{addr}", at={at}),"""
                print()
                print(CODE)
                trycopy(CODE)
            elif order == "2a":
                print("------- 新增图名 -------")
                IDX = input("请输入新添加图的图号： （请输入整数，输入-1 退出）").strip()
                if IDX == "-1": continue
                print(f"请前往图{IDX}，并确保左上角的图名出现。")
                input("输入回车继续")
                print("正在截图……为了避免信息丢失，强制使用慢速截图。")
                self.Shot(force_slow=True, show=False, file="zhuxian_title.bmp")
                print("注意：有一部分图名格式为 XXX - X部，它们的特点是有多个图共用同一个前缀，这增加了区分难度。")
                print("为了提高检测率，这类图将经过二次比较，只有左右两部分均通过，才算判断成功。")
                print("如果你还不理解，请去img/zhuxian中看一看。")
                print()
                MODE = input("新图图名是否由两部分组成？ 0 - 否；  1 - 是；  -1 退出 ")
                if MODE == "-1": continue
                MODE = int(MODE)
                IDX = int(IDX)
                EXIST = 0
                PRE = ""
                if MODE == 1:
                    print("请前往core/constant.py，搜索字典：ZHUXIAN_SECOND_ID")
                    t = input("你是否能找到同名前缀已经被录入过？ 0 - 否； 1 - 是； -1 退出 ")
                    if t == "-1": continue
                    EXIST = int(t)
                    if EXIST == 0:
                        PRE = input("请输入大写的前缀拼音首字母缩写，如：小行星原野->XXXYY ").strip().upper()

                    print("请用右键框选 [前缀] 区域，尽量避免背景部分框入。")
                    print("框选区域需要稍微向下，避免庆典图标遮挡。")
                    print("双击左键可重置框选，按下a键记录框选，关闭窗口继续。")
                    click = self.Show(file="zhuxian_title.bmp", verbose=False, return_click=True)
                    img = ImgBox(filepath="zhuxian_title.bmp")
                    at = click['at'][-1]
                    addr = f"img/zhuxian/{IDX}L.bmp"
                    img.cut(*at).save(addr)
                    AT_LEFT = at
                    print("图片已经保存到：", addr)

                    print("请用右键框选 [后缀] 区域，尽量避免背景部分框入。")
                    print("框选区域需要稍微向下，避免庆典图标遮挡。")
                    print("双击左键可重置框选，按下a键记录框选，关闭窗口继续。")
                    click = self.Show(file="zhuxian_title.bmp", verbose=False, return_click=True)
                    img = ImgBox(filepath="zhuxian_title.bmp")
                    at = click['at'][-1]
                    addr = f"img/zhuxian/{IDX}R.bmp"
                    img.cut(*at).save(addr)
                    AT_RIGHT = at
                    print("图片已经保存到：", addr)

                    CODE = f"""    {IDX}: p(img="img/zhuxian/{IDX}L.bmp", at={AT_LEFT}),"""
                    print("请将以下代码粘贴到：core/constant.py 的ZHUXIAN_ID字典中。")
                    print()
                    print(CODE)
                    print()
                    trycopy(CODE)
                    input("输入回车继续")

                    if EXIST == 0:
                        CODE = f"""ZHUXIAN_{PRE}_ID = {{\n""" \
                               f"""    {IDX}: p(img="img/zhuxian/{IDX}R.bmp", at={AT_RIGHT}),\n""" \
                               f"""}}"""
                        print("请将以下代码粘贴到：core/constant.py 的注释# ZHUXIAN_SUB_ID下方，注意图号顺序。")
                        print()
                        print(CODE)
                        print()
                        trycopy(CODE)
                        input("输入回车继续")

                        CODE = f"""    {(IDX,)}: ZHUXIAN_{PRE}_ID,"""
                        print("请将以下代码粘贴到：core/constant.py 的字典ZHUXIAN_SECOND_ID中。")
                        print()
                        print(CODE)
                        print()
                        trycopy(CODE)
                        input("输入回车继续")
                    else:
                        CODE = f"""    {IDX}: p(img="img/zhuxian/{IDX}R.bmp", at={AT_RIGHT}),"""
                        print("请将以下代码粘贴到：core/constant.py 的注释# ZHUXIAN_SUB_ID下方已有前缀字典中。")
                        print()
                        print(CODE)
                        print()
                        trycopy(CODE)
                        input("输入回车继续")

                        print("请找到core/constant.py 的字典ZHUXIAN_SECOND_ID中对应前缀的条目。")
                        print("并向对应字典的键中加入该图的图号。例如： (31, ):.... -> (31,32): ...")
                        input("输入回车继续")

                else:
                    print("请用右键框选 [地图名] 区域，尽量避免背景部分框入。")
                    print("框选区域需要稍微向下，避免庆典图标遮挡。")
                    print("双击左键可重置框选，按下a键记录框选，关闭窗口继续。")
                    click = self.Show(file="zhuxian_title.bmp", verbose=False, return_click=True)
                    img = ImgBox(filepath="zhuxian_title.bmp")
                    at = click['at'][-1]
                    addr = f"img/zhuxian/{IDX}.bmp"
                    img.cut(*at).save(addr)
                    AT = at
                    print("图片已经保存到：", addr)

                    CODE = f"""    {IDX}: p(img="img/zhuxian/{IDX}L.bmp", at={AT}),"""
                    print("请将以下代码粘贴到：core/constant.py 的ZHUXIAN_ID字典中。")
                    print()
                    print(CODE)
                    print()
                    trycopy(CODE)
                    input("输入回车继续")
                print("最后，请修改core/constant.py中的整数MAX_MAP为当前最新图的图号。")
            elif order == "2b":
                print("------- 新增NORMAL坐标 -------")
                IDX = input("请输入要录入的图号：（如26，则表示更新26图中的某些小图的坐标） （请输入整数，输入-1 退出）").strip()
                if IDX == "-1": continue
                IDX = int(IDX)
                print(f"请进入图{IDX}的NORMAL状态。")
                input("按下回车继续")
                TOTAL = input("请输入该图一共有多少小关： （请输入整数，输入-1退出） ").strip()
                if TOTAL == "-1": continue
                TOTAL = int(TOTAL)
                print()
                print("NORMAL图通常较长，因此需要左右拖动定位，通常取中间值为中心点左右分割。")
                MID = input(f"请输入分割值（推荐：{TOTAL // 2}；输入-1退出） ").strip()
                if MID == "-1": continue
                MID = int(MID)
                print("正在定位left……")
                self.Drag_Left()
                print("正在截图……为了避免信息丢失，强制使用慢速截图。")
                self.Shot(force_slow=True, show=False, file="zhuxian_select.bmp")
                print(f"请按照从小到大的顺序，依次点击：", end=" ")
                for j in range(1, MID + 1):
                    print(f"{IDX}-{j}", end=",")
                print()
                print("每个点点击完成后，按下x键记录当前坐标，然后点击下一个点。在按x键前你可以一直调整点位置。")
                print(f"按过{MID}次x后，关闭窗口继续。")
                click = self.Show(file="zhuxian_select.bmp", verbose=False, return_click=True)
                xy_left = click["xy"][-MID:]

                print("正在定位right……")
                self.Drag_Right()
                print("正在截图……为了避免信息丢失，强制使用慢速截图。")
                self.Shot(force_slow=True, show=False, file="zhuxian_select.bmp")
                print(f"请按照从小到大的顺序，依次点击：", end=" ")
                for j in range(MID + 1, TOTAL + 1):
                    print(f"{IDX}-{j}", end=",")
                print()
                print("每个点点击完成后，按下x键记录当前坐标，然后点击下一个点。在按x键前你可以一直调整点位置。")
                print(f"按过{TOTAL - MID}次x后，关闭窗口继续。")
                click = self.Show(file="zhuxian_select.bmp", verbose=False, return_click=True)
                xy_right = click["xy"][:MID]
                xy = xy_left + xy_right

                CODEs = []
                CODEs.append(f"""    {IDX}: {{""")
                CODEs.append(f"""        "right": {{""")
                for j in range(TOTAL, MID, -1):
                    xx, yy = xy[j - 1]
                    CODEs.append(f"""            {j}: p({xx}, {yy}, name="{IDX}-{j}"),""")
                CODEs.append(f"""        }},""")
                CODEs.append(f"""        "left": {{""")
                for j in range(MID, 0, -1):
                    xx, yy = xy[j - 1]
                    CODEs.append(f"""            {j}: p({xx}, {yy}, name="{IDX}-{j}"),""")
                CODEs.append(f"""        }},""")
                CODEs.append(f"""    }},""")
                CODE = "\n".join(CODEs)

                print("请将以下代码粘贴到：core/constant.py 的NORMAL_COORD字典中。")
                print()
                print(CODE)
                print()
                trycopy(CODE)
            elif order == "2c":
                print("------- 新增HARD坐标 -------")
                IDX = input("请输入要录入的图号：（如26，则表示更新26图中的某些小图的坐标）（请输入整数，输入-1 退出）").strip()
                if IDX == "-1": continue
                IDX = int(IDX)
                print(f"请进入图{IDX}的HARD状态。")
                input("按下回车继续")
                print("正在截图……为了避免信息丢失，强制使用慢速截图。")
                self.Shot(force_slow=True, show=False, file="zhuxian_select.bmp")
                print(f"请按照从小到大的顺序，依次点击：", end=" ")
                for j in range(1, 4):
                    print(f"{IDX}-{j}", end=",")
                print()
                print("每个点点击完成后，按下x键记录当前坐标，然后点击下一个点。在按x键前你可以一直调整点位置。")
                print(f"按过3次x后，关闭窗口继续。")
                click = self.Show(file="zhuxian_select.bmp", verbose=False, return_click=True)
                xy = click["xy"][-3:]
                CODEs = []
                CODEs.append(f"""    {IDX}: {{""")
                for j in range(1, 4):
                    xx, yy = xy[j - 1]
                    CODEs.append(f"""        {j}: p({xx}, {yy}, name="H{IDX}-{j}"),""")
                CODEs.append(f"""    }},""")
                CODE = "\n".join(CODEs)

                print("请将以下代码粘贴到：core/constant.py 的HARD_COORD字典中。")
                print()
                print(CODE)
                print()
                trycopy(CODE)
            elif order == "2d":
                print("------- 新增VH坐标 -------")
                IDX = input("请输入要录入的图号：（如26，则表示更新26图中的某些小图的坐标） （请输入整数，输入-1 退出）").strip()
                if IDX == "-1": continue
                IDX = int(IDX)
                print(f"请进入图{IDX}的VH状态。")
                input("按下回车继续")
                AA, BB = input(f"请输入两个整数a b，用空格隔开，分别代表即将录入的图号为 VH{IDX}-a 至 VH{IDX}-b：").split(" ")
                AA = int(AA)
                BB = int(BB)
                print("正在截图……为了避免信息丢失，强制使用慢速截图。")
                self.Shot(force_slow=True, show=False, file="zhuxian_select.bmp")
                print(f"请按照从小到大的顺序，依次点击：", end=" ")
                for j in range(AA, BB + 1):
                    print(f"{IDX}-{j}", end=",")
                print()
                print("每个点点击完成后，按下x键记录当前坐标，然后点击下一个点。在按x键前你可以一直调整点位置。")
                print(f"按过{BB - AA + 1}次x后，关闭窗口继续。")
                click = self.Show(file="zhuxian_select.bmp", verbose=False, return_click=True)
                xy = click["xy"][-3:]
                CODEs = []
                CODEs.append(f"""    {IDX}: {{""")
                for j in range(AA, BB + 1):
                    xx, yy = xy[j - AA]
                    CODEs.append(f"""        {j}: p({xx}, {yy}, name="VH{IDX}-{j}"),""")
                CODEs.append(f"""    }},""")
                CODE = "\n".join(CODEs)

                print("请将以下代码粘贴到：core/constant.py 的VH_COORD字典中。请注意字典的合并！")
                print()
                print(CODE)
                print()
                trycopy(CODE)
            elif order == "exit":
                break
            else:
                print("指令错误！")
        except Exception as e:
            print("发生错误：", e)
