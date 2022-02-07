from cnocr import gen_model
import torch.nn as nn
def pcr_basic_model(model_name="densenet_lite_136-gru",cuda=True,voc_dir="."):
    V = []
    with open(f"{voc_dir}/label_basic.txt","r",encoding="utf-8") as f:
        for v in f:
            V.append(v.strip())
    model = gen_model(model_name,V)
    # model.encoder.features.conv0 =  nn.Conv2d(
    #         3, model.encoder.features.conv0.out_channels, kernel_size=(3,3), stride=(1,1), padding=1, bias=False
    #     )   # Enable 3 channels.
    # model.forward = lambda x:model.forward(*x)
    return model if not cuda else model.cuda()

class MyLoss(nn.Module):
    def __init__(self):
        super().__init__()
    def forward(self,x,y=None):
        return x["loss"]
