import torch
from tqdm import tqdm
import random

from pcrocr.model import pcr_basic_model, MyLoss, pcr_normal_model
from pcrocr.utils import MyNeuralNet, batch_padding,imshow, both_shuffle
from skorch.callbacks.training import Checkpoint
from skorch.callbacks.lr_scheduler import LRScheduler,WarmRestartLR
from pcrocr.dataset import load_from_tsv,MyDataLoader,MyDataset

DATA_LIST = [
    "realA","realA2","realB","realB2","artifactA","artifactB","realC","artifactC"
]
DATA_LAST = [
    6500,2000,9000,18000,18000,8000,8000,8000
]
print("Loading data... ")
DATASET_LIST = [load_from_tsv(f"{DIR}/data.tsv",top=num) for DIR,num in zip(DATA_LIST,DATA_LAST)]
tv_img_list = sum([x[0] for x in DATASET_LIST],[])
tv_label_list = sum([x[1] for x in DATASET_LIST],[])

tv_img_list, tv_label_list = both_shuffle(tv_img_list,tv_label_list)

# batch,lengths = batch_padding(img_list[:10])
# out = model.forward(batch,lengths,label_list[:10],return_preds=True,return_logits=True)
# model.calculate_loss((batch,))
train_ratio = 0.9
train_samples = int(len(tv_img_list)*train_ratio)

train_dataset = MyDataset(tv_img_list[:train_samples],tv_label_list[:train_samples],aug=True)
valid_dataset = MyDataset(tv_img_list[train_samples:],tv_label_list[train_samples:])

model_names = [
    # "densenet_lite_136-lstm",
    # "densenet_lite_136-fc",
    "densenet_lite_136-gru",
    "mobilenetv3_tiny-lstm",
    # "mobilenetv3_tiny-gru",
]
fine_tuning = [
    # "model/normal/normal_DL136_lstm.pt",
    # "model/normal/normal_DL136_fc.pt",
    "model/normal/normal_DL136_gru.pt",
    "model/normal/normal_MNT_lstm.pt",
    # None,
]
for name,ft in zip(model_names,fine_tuning):
    print("CURRENT:",name)
    model = pcr_normal_model(name)
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
        max_epochs=20,
        batch_size=100,
        iterator_train=MyDataLoader,
        iterator_valid=MyDataLoader,
        device="cuda",
        warm_start=True,
        callbacks=[('cp',Checkpoint(dirname=f"cp_{name}")),
                   ('sch',LRScheduler(min_lr=1e-5,max_lr=1e-3,period_mult=1,base_period=20))],
    )
    clf.fit(train_dataset)
#
#
# print("TEST!")
# params = torch.load("cp_mnt_fc/params.pt")
# model.cpu().eval()
# model.load_state_dict(params)
#
# # Use CPU?
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
