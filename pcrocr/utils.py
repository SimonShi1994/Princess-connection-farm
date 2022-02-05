import random
import torch
import torch.nn.functional as F
import torchvision.transforms.functional as TVF
from typing import List
from cnocr.dataset import pad_img_seq
from skorch import NeuralNet
from skorch.utils import to_numpy
import numpy as np
import matplotlib.pyplot as plt
import cv2
import base64

def base64_decode(code):
    b64_de_img = str(base64.b64decode(code))
    np_arr = np.fromstring(b64_de_img, np.uint8)  # 把字符串转ndarray
    c_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return c_img

def imshow(img):
    plt.imshow(np.moveaxis(to_numpy(img),0,-1));plt.show()

def rescale_img(img,IMG_STANDARD_HEIGHT=32) -> torch.Tensor:
    """
    rescale an image tensor with [Channel, Height, Width] to the given height value, and keep the ratio
    :param img: np.ndarray; should be [c, height, width]
    :return: image tensor with the given height. The resulting dim is [C, height, width]
    """
    ori_height, ori_width = img.shape[1:]
    ratio = ori_height / IMG_STANDARD_HEIGHT
    if img.size(1) != IMG_STANDARD_HEIGHT:
        img = TVF.resize(img, [IMG_STANDARD_HEIGHT, int(ori_width / ratio)])
    return img

def img_preprocess(img:np.ndarray,cuda=False):
    # To Grey:
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    assert img.ndim==2
    # Unsqueeze
    img = np.reshape(img, (1, *img.shape))
    # Normalize
    img = img/255
    # To Tensor
    img = torch.Tensor(img)
    if cuda:
        img = img.cuda()
    # Rescale
    img = rescale_img(img)
    # # Padding, if to small
    # if img.shape[2] < 20:
    #     img = F.pad(img,[10,10,0,0,0,0])
    return img

def batch_padding(batch:List[torch.Tensor]):
    out = pad_img_seq(batch)
    img_lengths = torch.tensor([img.size(2) for img in batch])  # C H W
    return out,img_lengths

class MyNeuralNet(NeuralNet):
    def infer(self, x, **fit_params):
        return self.module_(**x)
    def get_loss(self, y_pred, y_true, X=None, training=False):
        return self.criterion_(y_pred, y_true)
    def run_single_epoch(self, dataset, training, prefix, step_fn, **fit_params):
        if dataset is None:
            return
        batch_count = 0
        for batch in self.get_iterator(dataset, training=training):
            self.notify("on_batch_begin", batch=batch, training=training)
            step = step_fn(batch, **fit_params)
            self.history.record_batch(prefix + "_loss", step["loss"].item())
            batch_size = len(batch[0]['x'])
            self.history.record_batch(prefix + "_batch_size", batch_size)
            self.notify("on_batch_end", batch=batch, training=training, **step)
            batch_count += 1

        self.history.record(prefix + "_batch_count", batch_count)

def both_shuffle(a,b):
    c = list(zip(a, b))
    random.shuffle(c)
    a, b = zip(*c)
    return a,b
