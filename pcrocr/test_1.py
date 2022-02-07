import torch
from tqdm import tqdm
import random

from pcrocr.model import pcr_basic_model,MyLoss
from pcrocr.utils import MyNeuralNet, batch_padding,imshow
from skorch.callbacks.training import Checkpoint
from pcrocr.dataset import load_from_tsv,MyDataLoader,MyDataset
model = pcr_basic_model(cuda=False)
img_list_1, label_list_1 = load_from_tsv("realA/data.tsv",cuda=False)
img_list = img_list_1
label_list = label_list_1
print("START TEST! ")
params = torch.load("cp/params.pt",map_location="cpu")
model.load_state_dict(params)
#
# Use CPU?
test_img_list = img_list
test_label_list = label_list
model.cpu().eval()

with torch.no_grad():
    error_imgs = []
    error_preds = []
    error_labels = []
    error_inds = []
    true_count = 0
    all_count = 0
    for ind,(img,label) in enumerate(tqdm(zip(test_img_list,test_label_list))):
        all_count+=1
        x = img.unsqueeze(0)
        out = model.forward(x,torch.Tensor([x.size(3)]).long(),target=[label],return_preds=True,)
        preds = ''.join(out['preds'][0][0])
        target = ''.join(label)
        if preds == target:
            true_count+=1
        else:
            error_imgs.append(img)
            error_preds.append(preds)
            error_inds.append(ind)
            error_labels.append(target)
            print("ERROR: Preds:",preds,"Target",target,"IND:",ind)

