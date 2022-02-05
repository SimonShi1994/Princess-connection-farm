from pcrocr.model import pcr_basic_model
from tqdm import tqdm
from pcrocr.dataset import MyDataset,MyDataLoader,load_from_tsv
import torch

MODEL_SETTINGS = [
    dict(model="densenet_lite_136-fc",file="basic_DL136_fc.pt"),
    dict(model="densenet_lite_136-lstm",file="basic_DL136_lstm.pt"),
    dict(model="densenet_lite_136-gru",file="basic_DL136_gru.pt"),
    dict(model="mobilenetv3_tiny-lstm",file="basic_MNT_lstm.pt"),
    dict(model="mobilenetv3_tiny-fc",file="basic_MNT_fc.pt"),
]
DATA_LIST = [
    "realA","realA2","realB","realB2"
]

print("==== Loading models ====")
models = []
model_names = [m['model'] for m in MODEL_SETTINGS]

for setting in MODEL_SETTINGS:
    print("Loading",setting['file'],"...")
    model = pcr_basic_model(setting['model']).eval()
    param_addr = f"model/basic/{setting['file']}"
    param = torch.load(param_addr,map_location="cuda")
    model.load_state_dict(param)
    models.append(model)

RESULTS = {}
torch.set_grad_enabled(False)
for data in DATA_LIST:
    print(f"==== DATA: {data} ====")
    print("Loading data...")
    img_list, label_list = load_from_tsv(f"{data}/data.tsv")
    all_count = 0
    true_count = 0
    error_imgs = []
    error_preds = []
    error_estr = []
    error_targets = []
    dataset = MyDataset(img_list,label_list)
    dataloader = MyDataLoader(dataset,batch_size=200,do_shuffle=False)
    model_scores = {}
    print("Testing models...")
    for X,Y in tqdm(dataloader):
        models_preds = {}
        models_confs = {}
        targets = X['target']
        for model,name in zip(models,model_names):
            out = model(**X,return_preds=True)
            models_preds[name]=[i[0] for i in out['preds']]
            models_confs[name]=[i[1] for i in out['preds']]

        for ind in range(len(targets)):
            score_dict = {}
            t_str = ''.join(targets[ind])
            for name in model_names:
                pp = models_preds[name][ind]
                cc = models_confs[name][ind]
                p_str = ''.join(pp)
                if p_str == t_str:
                    flag = 1
                else:
                    flag = 0
                if p_str not in score_dict:
                    score_dict[p_str] = cc
                else:
                    score_dict[p_str] += cc
                model_scores.setdefault(name,0)
                model_scores[name]+=flag

            e_str = max(score_dict,key=lambda x:score_dict[x])
            all_count += 1
            if e_str == t_str:
                true_count+=1
            else:
                error_imgs.append(X['x'][ind])
                error_preds.append({name:
                        (''.join(models_preds[name][ind]),
                         models_confs[name][ind])
                     for name in model_names})
                error_estr.append(e_str)
                error_targets.append(t_str)

    RESULTS[data] = {
        "acc":true_count/all_count,
        "true_count":true_count,
        "all_count":all_count,
        "errors":[{
            "img":error_imgs[i],
            "preds":error_preds[i],
            "e_str":error_estr[i],
            "t_str":error_targets[i]
        } for i in range(len(error_imgs))],
        "scores":model_scores,
    }

    # raise Exception("pause")

RESULTS2 ={k:{k2:v2 if k2!='errors' else
             [{k3:v3 for k3,v3 in err.items() if k3 in ['e_str','t_str']} for err in v2]
    for k2,v2 in v.items()}
for k,v in RESULTS.items()}