from pcrocr.model import pcr_basic_model
from pcrocr.utils import base64_decode, img_preprocess
import torch
import numpy as np


class PCROCRBasic:
    """
    PCR的基础OCR模块
    包括0~9,冒号，逗号，斜杠，叉号(x)
    载入模型目录，config.ini设置使用的模型，多模型投票决定结果。
    """

    def __init__(self, models_dir="pcrocr/model/basic", voc_dir="pcrocr"):
        """
        models_dir: 包含模型的目录，内含config.ini
        voc_dir: 包含词汇表的txt文件的目录
        """
        self.models = []
        self.models_dir = models_dir
        self.voc_dir = voc_dir
        self.initialize()

    def initialize(self):
        config = np.genfromtxt(f"{self.models_dir}/model_config.ini", comments='#', delimiter='\t', dtype='str')
        for filename, modelname in config:
            model = pcr_basic_model(model_name=modelname, cuda=False, voc_dir=self.voc_dir)
            param = torch.load(f"{self.models_dir}/{filename}", map_location="cpu")
            model.load_state_dict(param)
            model.eval()
            self.models.append(model)

    def ocr(self, x, voc=None, do_pre=True):
        # voc: 考虑的字符集，None则全部字符。
        # x: str,ndarray
        # do_pre: 是否预处理
        if isinstance(x, str):
            x = base64_decode(x)
        if do_pre:
            x = img_preprocess(x, cuda=False)
        # X:  1x32xW
        x = x.unsqueeze(0)
        score_dict = {}
        for model in self.models:
            out = model.forward(x, torch.Tensor([x.size(3)]).long(), return_preds=True, candidates=voc)
            preds = ''.join(out['preds'][0][0])
            conf = out['preds'][0][1]
            if preds not in score_dict:
                score_dict[preds] = [conf]
            else:
                score_dict[preds] += [conf]
        text = max(score_dict, key=lambda x: sum(score_dict[x]))
        conf = np.mean(score_dict[text])
        return dict(text=text, conf=conf)

    def ocr_int(self, x, do_pre=True):
        return self.ocr(x, voc="0123456789", do_pre=do_pre)

    def ocr_A_B(self, x, do_pre=True):
        return self.ocr(x, voc="0123456789/", do_pre=do_pre)

    def ocr_xA(self, x, do_pre=True):
        return self.ocr(x, voc="0123456789x", do_pre=do_pre)

    def ocr_mana(self, x, do_pre=True):
        return self.ocr(x, voc="0123456789,", do_pre=do_pre)
