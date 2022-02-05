import os
from tqdm import tqdm
import pandas as pd
import random
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 生成数据集，包含数字，x，逗号，斜杠的数据集。
from matplotlib.patches import BoxStyle
import matplotlib


def result_filter(text: str):
    return " ".join(text.replace(" ", ""))


def generate_from_text(text, pic, board, fontname, fontsize, fontcolor, spacing):
    current_pic = pic.copy()
    current_pic = current_pic // 2 + 126
    img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(fontname, fontsize)
    x = 1
    y = 1
    if board:
        shallow = (255, 255, 255)
        # thin border
        d.text((x - 1, y), text, font=font, fill=shallow)
        d.text((x + 1, y), text, font=font, fill=shallow)
        d.text((x, y - 1), text, font=font, fill=shallow)
        d.text((x, y + 1), text, font=font, fill=shallow)

        # thicker border
        d.text((x - 1, y - 1), text, font=font, fill=shallow)
        d.text((x + 1, y - 1), text, font=font, fill=shallow)
        d.text((x - 1, y + 1), text, font=font, fill=shallow)
        d.text((x + 1, y + 1), text, font=font, fill=shallow)
    d.text((1, 1), text, fill=(*fontcolor, 255), font=font, spacing=spacing)
    text_width, text_height = d.textsize(text, font, spacing=spacing)
    text_width += 2
    text_height += 2
    img = img.crop((0, 0, text_width, text_height))
    img = np.array(img)
    mask = img[:, :, 3]
    mask = mask > 0
    # mask = np.stack([mask, mask, mask], axis=-1)
    img = img[:, :, :3]
    # Random Place Text To Image
    ava_x = current_pic.shape[0] - img.shape[0]
    ava_y = current_pic.shape[1] - img.shape[1]
    put_x = random.randint(0, ava_x)
    put_y = random.randint(0, ava_y)
    # mask = img.sum(axis=-1)>0
    x1 = put_x
    x2 = put_x + text_height
    y1 = put_y
    y2 = put_y + text_width
    region = current_pic[x1:x2, y1:y2]
    img[~mask] = 0
    region[mask] = 0
    region = region + img
    current_pic[x1:x2, y1:y2] = region
    y1 -= np.random.randint(0, 50)
    y2 += np.random.randint(0, 50)
    if y1 < 0:
        y1 = 0
    x1 -= np.random.randint(0, 5)
    x2 += np.random.randint(0, 5)
    if x1 < 0:
        x1 = 0
    return current_pic[x1:x2, y1:y2]


def generate_random_mana():
    mana = random.randint(0, 999999999)
    mana_str = f"{mana:,}"
    return mana_str


def generate_random_slash():
    A = random.randint(0, 999)
    B = random.randint(0, 999)
    return f"{A}/{B}"


def generate_random_time():
    tim = random.randint(0, 90)
    m = tim // 60
    s = tim % 60
    return f"{m}:{str(s).zfill(2)}"


def generate_random_x_int():
    n = random.randint(0, 9999999)
    return f"x{n}"


def generate_random():
    length = random.randint(1, 12)
    MODE = random.choice([0, 1])
    lst = []
    if MODE == 0:
        for ind in range(length):
            if ind > length // 6 and ind < length // 6 * 5:
                lst.append(
                    random.choice(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'x', '/', ':', ','] + ['1'] * 5))
            else:
                lst.append(random.choice(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']))
    else:
        lst = random.choice(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] + ['1'] * 5) * (length // 4) + \
              random.choice(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] + ['1'] * 5) * (length // 4) + \
              random.choice(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] + ['1'] * 5) * (length // 4) + \
              random.choice(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] + ['1'] * 5) * (length // 4 + 1)
    return ''.join(lst)


def generate_everything():
    funcs = [
        generate_random,
        generate_random,
        generate_random,
        generate_random,
        generate_random,
        generate_random,
        generate_random,
        generate_random,
        generate_random_time,
        generate_random_x_int,
        generate_random_mana,
        generate_random_slash,
    ]
    mode = random.randint(0, len(funcs) - 1)
    return funcs[mode]()


if __name__ == "__main__":
    # 人造数据生成
    DIR = "artifact"

    os.makedirs(f"{DIR}", exist_ok=True)
    # 读取img/juese/plate作为随机背景
    scan = os.scandir("../img/juese/plate")
    pic_names = [pic.name for pic in scan]  # noqa
    pics = [plt.imread(f"../img/juese/plate/{nam}") for nam in pic_names]
    C = 0

    # 读取字体
    all_fonts = []
    with open("all_fonts.txt", "r") as f:
        for n in f:
            all_fonts.append(n.strip().lower())

    # 验证字体
    lsts = [ImageFont.truetype(font) for font in all_fonts]
    del lsts

    # 生成数据集
    n_samples = 20000
    RECs = {
        "filename": [],
        "result": [],
    }
    for ind in tqdm(range(n_samples)):
        # 随机文字
        text = generate_everything()
        # 随机背景
        bc = random.choice(pics)
        # 随机字号
        font_size = random.randint(15, 35)
        # 随机间距
        spacing = random.randint(4, 8)
        # 随机字体
        font_type = random.choice(all_fonts)
        # 随机颜色
        font_color = tuple(random.randint(0, 128) for _ in range(3))
        # 生成图片
        pic = generate_from_text(
            text=text,
            pic=bc,
            board=random.choice([True, False, False]),
            fontname=font_type,
            fontsize=font_size,
            fontcolor=font_color,
            spacing=spacing,
        )
        # 保存图片
        Image.fromarray(pic).save(f"{DIR}/{ind}.jpg")
        # 增加记录
        RECs["filename"].append(f"{DIR}/{ind}.jpg")
        RECs["result"].append(result_filter(text))

    df = pd.DataFrame(RECs)
    df.to_csv(f"{DIR}/train.tsv", sep="\t", header=False, index=False)
