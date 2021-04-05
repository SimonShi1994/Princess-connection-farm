import queue
import random
import time
from flask import Blueprint, jsonify, request
from retrying import retry
from PIL import Image, ImageDraw
from io import BytesIO

from aip import AipOcr
from core.pcr_config import ocr_mode, baidu_apiKey, baidu_secretKey, baidu_QPS

import os

# 这一行创建了发包队列
queue = queue.Queue(baidu_QPS)

# 这一行代码用于关闭tensorflow的gpu模式（如果使用，内存占用翻几倍）
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

if ocr_mode != "网络" and len(ocr_mode) != 0:
    if ocr_mode == "本地" or ocr_mode == "混合" or ocr_mode == "智能":
        import muggle_ocr
        # 初始化；model_type 包含了 ModelType.OCR/ModelType.Captcha 两种
        sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.OCR)

    if ocr_mode == "本地2" or ocr_mode == "混合" or ocr_mode == "智能":
        import tr


config = {
    'appId': 'PCR',
    'apiKey': baidu_apiKey,
    'secretKey': baidu_secretKey
}
client = AipOcr(**config)

ocr_api = Blueprint('ocr', __name__)


@ocr_api.route('/local_ocr/', methods=['POST'])
def local_ocr():
    # 接收图片
    upload_file = request.files.get('file')
    # print(upload_file)
    if upload_file:
        result = sdk.predict(upload_file.read())
        # print(result)
        return result
    return 400


@ocr_api.route('/local_ocr2/', methods=['POST'])
def local_ocr2():
    # 接收图片 二进制流
    upload_file = request.files.get('file')
    # print(upload_file)
    if upload_file:
        upload_file = Image.open(BytesIO(upload_file.read()))
        upload_file = upload_file.convert("RGB")
        # print(tr.run(img.copy().convert("L"), flag=tr.FLAG_ROTATED_RECT))
        result = tr.recognize(upload_file.copy().convert("L"))
        # print(result)
        return {"res": result}
    return 400


@ocr_api.route('/baidu_ocr/', methods=['POST'])
def baidu_ocr():
    lay_sw = False
    # 接收图片
    img = request.files.get('file')
    queue.put((img.read()))
    if img:
        # time.sleep(random.uniform(1.5, 2.05))
        part = queue.get()

        @retry(stop_max_attempt_number=5)
        def sent_ocr():
            nonlocal lay_sw
            try:
                if lay_sw:
                    time.sleep(random.uniform(1.5, 2.05))
                ocr_result = client.basicGeneral(part)
                return ocr_result
            except Exception as e:
                lay_sw = True
                raise Exception('BaiDuOCR发生了错误，原因为:{}'.format(e))

        result = sent_ocr()
        return result

    return 400
