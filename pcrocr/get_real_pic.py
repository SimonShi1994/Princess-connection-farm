import cv2
from random import randint
import numpy as np

from screencut import AutomatorDebuger,WindowMode
import matplotlib.pyplot as plt
from core.cv import UIMatcher
from tqdm import tqdm
import os
from pcrocr.test_getocrpic import result_filter, generate_everything
import pandas as pd
import time

def shot_items(self:AutomatorDebuger):
    # 进入道具，点开某一个道具
    at_cys = (639,267,695,283)  # 持有数
    at_mid = (449,307,513,329)  # 中间的道具数
    at_axb = (451, 347, 568, 371)  # mana x number
    at_mana_cur = (590, 348, 695, 369)  # all consume mana
    at_mana_left = (597,383,697,402)  # left mana

    path = input("请输入存放目录 ")
    CUR = 0

    df_dict = {
        "file":[],
        "label":[],
    }
    if os.path.exists(path):
        print("目录已经存在！",end=" ")
        CUR = max([int(j.name[:-4]) for j in os.scandir(path) if j.name.endswith(".jpg")])+1  # noqa
        print("从",CUR,"开始！")
        df = pd.read_csv(f"{path}/data.tsv", sep='\t', header=None, names=['file', 'label'], encoding="gbk")
    else:
        os.makedirs(path)
        df = pd.DataFrame(dict(file=[],label=[]))

    total_num = int(input("请输入道具总数 "))
    one_mana = int(input("请输入单个能卖mana "))
    all_mana = int(input("请输入当前总mana "))
    step = int(input("请输入截图间隔 "))

    print("开始操作！")
    # 点击max
    self.click(638,312,post_delay=0.5)
    lsts = list(range(total_num,0,-step))
    last_sc = None
    for now in tqdm(lsts):
        sc = self.getscreen()
        for _ in range(10):
            if last_sc is not None:
                if self.img_equal(sc,last_sc,at=at_mana_left)>0.95:
                    time.sleep(0.2)
                    sc = self.getscreen()
                else:
                    break
            else:
                break
        else:
            print("截图大错误！")
            break
        last_sc = sc

        item_list = []
        item_list.append(dict(
            img=UIMatcher.img_cut(sc,at_cys),
            label=str(total_num-now)
        ))
        item_list.append(dict(
            img=UIMatcher.img_cut(sc, at_mid),
            label=str(now)
        ))
        item_list.append(dict(
            img=UIMatcher.img_cut(sc, at_axb),
            label=f"{one_mana}x{now}"
        ))
        item_list.append(dict(
            img=UIMatcher.img_cut(sc, at_mana_cur),
            label=f"{one_mana*now:,}"
        ))
        item_list.append(dict(
            img=UIMatcher.img_cut(sc, at_mana_left),
            label=f"{all_mana + one_mana * now:,}"
        ))
        for item in item_list:
            addr = f"{path}/{CUR}.jpg"
            cv2.imwrite(addr, item["img"])
            df_dict['file'].append(addr)
            df_dict['label'].append(result_filter(item['label']))
            CUR+=1

        for _ in range(step):
            self.click(394, 316)
        time.sleep(0.2)
    print("完成！")
    df = pd.concat([df,pd.DataFrame(df_dict)])
    df.to_csv(f"{path}/data.tsv", sep='\t',header=False,index=False)

def shot_hanghui(self:AutomatorDebuger):
    # 进入行会编辑，准备编辑行会说明
    at_lines = [(272, 230, 424, 251),
                (272, 249, 424, 264),
                (272, 265, 424, 283)
                ]
    all_ats = (272,230,424,283)

    path = input("请输入存放目录 ")
    CUR = 0

    df_dict = {
        "file":[],
        "label":[],
    }
    if os.path.exists(path):
        print("目录已经存在！",end=" ")
        CUR = max([int(j.name[:-4]) for j in os.scandir(path) if j.name.endswith(".jpg")])+1  # noqa
        print("从",CUR,"开始！")
        df = pd.read_csv(f"{path}/data.tsv", sep='\t', header=None, names=['file', 'label'], encoding="gbk")
    else:
        os.makedirs(path)
        df = pd.DataFrame(dict(file=[],label=[]))

    total_num = int(input("请输入生成总数 "))
    print("开始操作！")
    # 点击输入框
    self.click(361, 238,post_delay=1.)
    self.input(clear=True)
    pbar = tqdm(desc="Shotting... ",total=total_num)
    pbar.update(CUR)
    last_sc = None
    try:
        while CUR < total_num:
            if os.path.exists(f"{path}/stop.txt"):
                break
            # 输入文字
            texts = [generate_everything(),
                     generate_everything(),
                     generate_everything()]
            texts = [s.center(12) for s in texts]
            self.input('\n'.join(texts),clear=True)
            # Make sure the screen is not empty
            for _ in range(100):
                sc = self.getscreen()
                at = (272, 230, 414, 251)
                img = UIMatcher.img_cut(sc, at)
                img2 = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                if np.sum(img2 > 220)>0:
                    break
            else:
                continue
            # Make sure the screen is not the same
            if last_sc is not None:
                if self.img_equal(sc,last_sc,at=all_ats)>0.9:
                    print("Same sceen, repick.")
                    continue
            last_sc = sc
            item_list = []
            for at,text in zip(at_lines,texts):
                img = UIMatcher.img_cut(sc, at)
                img2 = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                mask = img2 > 220
                if np.sum(mask)==0:
                    continue
                mask_c = np.cumsum(np.max(mask, axis=0))
                mask_r = np.cumsum(np.max(mask, axis=1))
                x2 = mask_c.argmax()
                x1 = (mask_c > 0).argmax()
                y2 = mask_r.argmax()
                y1 = (mask_r > 0).argmax()
                real_x1 = randint(0, x1)
                real_x2 = randint(x2, len(mask_c))
                real_y1 = randint(0, y1)
                real_y2 = randint(y2, len(mask_r))
                img3 = img[real_y1:real_y2,real_x1:real_x2]


                item_list.append(dict(
                    img=img3,
                    label=text,
                ))
            for item in item_list:
                addr = f"{path}/{CUR}.jpg"
                cv2.imwrite(addr, item["img"])
                df_dict['file'].append(addr)
                df_dict['label'].append(result_filter(item['label']))
                CUR+=1
                pbar.update(1)
    except KeyboardInterrupt:
        pass
    pbar.close()
    print("完成！")
    df = pd.concat([df,pd.DataFrame(df_dict)])
    df.to_csv(f"{path}/data.tsv", sep='\t',header=False,index=False)


if __name__ == "__main__":
    WindowMode()
    self = AutomatorDebuger()
    self.Connect()
    # shot_items(self)
    shot_hanghui(self)
    # df = pd.read_csv(f"realB2/data.tsv",sep='\t',header=None)
    # label = df[1]
    # def doimg(img):
    #     img2 = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    #     mask = img2 > 220
    #     mask_c = np.cumsum(np.max(mask, axis=0))
    #     mask_r = np.cumsum(np.max(mask, axis=1))
    #     x2 = mask_c.argmax()
    #     x1 = (mask_c > 0).argmax()
    #     y2 = mask_r.argmax()
    #     y1 = (mask_r > 0).argmax()
    #     img = img[y1:y2,x1:x2]
    #     return img
    # REC = []
    # relu = lambda x:0 if x<0 else x
    # for i in range(11310):
    #     for j in range(i+1,i+4):
    #         if j>=11310:
    #             continue
    #         A = doimg(UIMatcher._get_template(f"realB2/{i}.jpg"))
    #         B = doimg(UIMatcher._get_template(f"realB2/{j}.jpg"))
    #         # if A.shape!=B.shape:
    #         #     continue
    #         xx = relu(A.shape[0]-B.shape[0])
    #         yy = relu(A.shape[1]-B.shape[1])
    #         B = np.pad(B,((0,xx),(0,yy),(0,0)))
    #         xx = relu(B.shape[0] - A.shape[0])
    #         yy = relu(B.shape[1] - A.shape[1])
    #         A = np.pad(A, ((0, xx), (0, yy), (0, 0)))
    #         if self.img_equal(A,B,similarity=0.1)>0.9 and label[j]!=label[i]:
    #             REC.append((i,j))
    #             print("Sim:",i,j,self.img_equal(A,B))
    # pre_inds = [xx[0] for xx in REC]
    # ALL_IND = []
    # for inds in pre_inds:
    #     if inds not in ALL_IND:
    #         ALL_IND.append(inds)
    #         ALL_IND.append(inds+1)
    #         ALL_IND.append(inds+2)
    #
    # df = df.drop(index=ALL_IND)
    # df.to_csv("realB2/data.tsv",sep='\t',header=False,index=False)
    #
    # REC = []
    # for i in range(3470-5):
    #     A = UIMatcher._get_template(f"real2/{i}.jpg")
    #     B = UIMatcher._get_template(f"real2/{i+5}.jpg")
    #     if self.img_equal(A,B,similarity=0.05)>0.95:
    #         REC.append((i,i+5))
    #         print("Sim:", i, i+5, self.img_equal(A, B))
    # pre_inds = [xx[0] for xx in REC]
    # ALL_IND = []
    # for inds in pre_inds:
    #     if inds not in ALL_IND:
    #         ALL_IND.append(inds)
    #         ALL_IND.append(inds + 1)
    #         ALL_IND.append(inds + 2)
    #         ALL_IND.append(inds + 3)
    #         ALL_IND.append(inds + 4)
    #
    # df = pd.read_csv(f"real2/data.tsv",sep='\t',header=None)
    # df = df.drop(index=[660,661,662,663,664])
    # df.to_csv("real2/data.tsv", sep='\t', header=False, index=False)
    # shot_hanghui(self)
    # img = cv2.imread("realB/46.jpg")
    # img2 = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # mask = img2>220
    # mask_c = np.cumsum(np.max(mask,axis=0))
    # mask_r = np.cumsum(np.max(mask,axis=1))
    # x2 = mask_c.argmax()
    # x1 = (mask_c>0).argmax()
    # y2 = mask_r.argmax()
    # y1 = (mask_r>0).argmax()
    # real_x1 = randint(0,x1)
    # real_x2 = randint(x2,len(mask_c))
    # real_y1 = randint(0,y1)
    # real_y2 = randint(y2,len(mask_r))
