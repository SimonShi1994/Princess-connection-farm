import random

import numpy as np
import matplotlib.pyplot as plt
from pcrocr.utils import rescale_img,batch_padding,img_preprocess
import torch
from torch.utils.data import DataLoader,Dataset
from screencut import ImgBox
from tqdm import tqdm
from cnocr.data_utils.aug import RandomStretchAug
import cv2


def load_from_tsv(filename,top=None,tail=None,cuda=True):
    out = np.genfromtxt(filename,delimiter='\t',dtype=str,encoding="utf-8")
    label_list = []
    img_list = []

    for path,ans in tqdm(out):
        if top is not None:
            top -= 1
            if top<0:
                break
        if tail is not None:
            tail -= 1
            if tail>=0:
                continue
        img = cv2.imread(path)
        img = img_preprocess(img,cuda)
        if img.shape[2]<20:
            continue
        label_list.append(ans.split(" "))
        img_list.append(img)

    return img_list, label_list

class FgBgFlipAug():
    def __init__(self, p):
        self.p = p

    def __call__(self, src):
        if random.random() < self.p:
            src = 1 - src
        return src

class MyDataset(Dataset):
    def __init__(self,img_list,label_list,aug=False):
        self.img_list = img_list
        self.label_list = label_list
        self.aug = aug
        self.RSA = RandomStretchAug(0.8,1.2)
        self.FGA = FgBgFlipAug(p=0.5)

    def __len__(self):
        return len(self.img_list)

    def __getitem__(self, item):
        if self.aug:
            img = self.FGA(self.RSA(self.img_list[item]))
        else:
            img = self.img_list[item]

        return img, self.label_list[item]

def collate_fn(x):
    img_list, labels_list = zip(*x)
    # label_lengths = torch.tensor([len(labels) for labels in labels_list])
    imgs,img_lengths = batch_padding(img_list)
    return {
        "x":imgs,
        "input_lengths":img_lengths,
        "target":labels_list,
    }, None

class MyDataLoader(DataLoader):
    def __init__(self,dataset,batch_size,do_shuffle=True,**kwargs):
        super().__init__(
            dataset,
            batch_size,
            shuffle=do_shuffle,
            collate_fn=collate_fn,
        )
