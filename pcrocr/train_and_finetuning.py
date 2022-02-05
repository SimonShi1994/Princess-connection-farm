import torch
from tqdm import tqdm
import random

from pcrocr.model import pcr_basic_model,MyLoss
from pcrocr.utils import MyNeuralNet, batch_padding,imshow, both_shuffle
from skorch.callbacks.training import Checkpoint
from skorch.callbacks.lr_scheduler import LRScheduler,WarmRestartLR
from pcrocr.dataset import load_from_tsv,MyDataLoader,MyDataset

img_list_1, label_list_1 = load_from_tsv("realB/data.tsv")   # 10001
img_list_2, label_list_2 = load_from_tsv("realA/data.tsv")   # 7554
img_list_3, label_list_3 = load_from_tsv("realA2/data.tsv")  # 3459
img_list_4, label_list_4 = load_from_tsv("realB2/data.tsv")   # 19220

tv_img_list = img_list_1[:9000] + img_list_2[:6500] + img_list_3[:2000] + img_list_4[:18000]
tv_label_list = label_list_1[:9000] + label_list_2[:6500] + label_list_3[:2000] + label_list_4[:18000]
test_img_list = img_list_1[9000:] + img_list_2[6500:] + img_list_3[2000:] + img_list_4[18000:]
test_label_list = label_list_1[9000:] + label_list_2[6500:] + label_list_3[2000:] + label_list_4[18000:]

tv_img_list, tv_label_list = both_shuffle(tv_img_list,tv_label_list)

# batch,lengths = batch_padding(img_list[:10])
# out = model.forward(batch,lengths,label_list[:10],return_preds=True,return_logits=True)
# model.calculate_loss((batch,))
train_ratio = 0.9
train_samples = int(len(tv_img_list)*train_ratio)

train_dataset = MyDataset(tv_img_list[:train_samples],tv_label_list[:train_samples],aug=True)
valid_dataset = MyDataset(tv_img_list[train_samples:],tv_label_list[train_samples:])

model_names = [
    "densenet_lite_136-lstm",
    "densenet_lite_136-fc",
    "densenet_lite_136-gru",
    "mobilenetv3_tiny-lstm",
    "mobilenetv3_tiny-gru",
]
fine_tuning = [
    "model/basic/basic_DL136_lstm.pt",
    "model/basic/basic_DL136_fc.pt",
    "model/basic/basic_DL136_gru.pt",
    "model/basic/basic_MNT_lstm.pt",
    None,
]
for name,ft in zip(model_names,fine_tuning):
    print("CURRENT:",name)
    model = pcr_basic_model(name)
    model.train()
    if fine_tuning is not None:
        params = torch.load(ft)
        model.load_state_dict(params)
    clf = MyNeuralNet(
        module=model,
        criterion=MyLoss,
        optimizer=torch.optim.AdamW,
        optimizer__weight_decay=1e-4,
        lr=3e-3,
        max_epochs=40,
        batch_size=100,
        iterator_train=MyDataLoader,
        iterator_valid=MyDataLoader,
        device="cuda",
        warm_start=False,
        callbacks=[('cp',Checkpoint(dirname=f"cp_{name}")),
                   ('sch',LRScheduler(min_lr=1e-5,max_lr=3e-3,period_mult=3))],
    )
    clf.fit(train_dataset)


# print("TEST!")
# params = torch.load("cp_mnt_fc/params.pt")
# model.cpu().eval()
# model.load_state_dict(params)

# Use CPU?
# test_img_list = [x.cpu() for x in test_img_list]
#
#
# with torch.no_grad():
#     error_imgs = []
#     error_preds = []
#     error_labels = []
#     true_count = 0
#     all_count = 0
#     for img,label in tqdm(zip(test_img_list,test_label_list)):
#         all_count+=1
#         x = img.unsqueeze(0)
#         out = model.forward(x,torch.Tensor([x.size(3)]).long(),target=[label],return_preds=True)
#         preds = ''.join(out['preds'][0][0])
#         target = ''.join(label)
#         if preds == target:
#             true_count+=1
#         else:
#             error_imgs.append(img)
#             error_preds.append(preds)
#             error_labels.append(target)
#             print(all_count,"ERROR:","PREDS",preds,"TARGET",target)
#
