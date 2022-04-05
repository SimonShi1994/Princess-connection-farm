import base64
import random
import time
import os

import requests
from flask import Blueprint, jsonify, request
from retrying import retry
from PIL import Image
from io import BytesIO

from aip import AipOcr
from core.pcr_config import ocr_mode_main, ocr_mode_secondary, baidu_apiKey, baidu_secretKey, baidu_QPS, \
    ocrspace_ocr_apikey
from pcrocr.ocr import PCROCRBasic

ocr_list = [x for x in ocr_mode_secondary.split(',')]
ocr_list.insert(0, ocr_mode_main)
for ocr_mode in ocr_list:
    try:
        if len(ocr_mode) == 0:
            continue

        # 强制加载
        pcr_ocr = PCROCRBasic().ocr

        if ocr_mode[:2] != "网络":
            if ocr_mode == "本地1":
                # 这一行代码用于关闭tensorflow的gpu模式（如果使用，内存占用翻几倍）
                os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

                import muggle_ocr

                # 初始化；model_type 包含了 ModelType.OCR/ModelType.Captcha 两种
                sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.OCR)

            if ocr_mode == "本地2":
                import tr

            if ocr_mode == "本地3":
                import ddddocr

                ocr = ddddocr.DdddOcr(show_ad=False, old=True)
            if ocr_mode == "本地4":
                import easyocr

                # 'ch_tra' 中文繁体
                easyocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False,
                                                verbose=False)  # this needs to run only once to load the model into memory
        else:
            if ocr_mode == "网络1":
                import queue

                # 这一行创建了发包队列
                baidu_queue = queue.Queue(baidu_QPS)
                config = {
                    'appId': 'PCR',
                    'apiKey': baidu_apiKey,
                    'secretKey': baidu_secretKey
                }
                client = AipOcr(**config)
            if ocr_mode == "网络2":
                ocrspace_ocr_config = {
                    'isOverlayRequired': False,
                    'apikey': ocrspace_ocr_apikey,
                    'language': 'chs',
                    'scale': True,
                }
    except ModuleNotFoundError as e:
        print("OCR初始化启动，模块缺失：", e)
        os.system("pause")
    except Exception as e:
        print("如果cannot import name '_registerMatType' from 'cv2.cv2'，检查opencv-python和opencv-contrib-python版本是否一致\n"
              "一致还是不行，可以试试pip uninstall opencv-python-headless")
        print("OCR初始化启动，失败未知错误：", e)
        os.system("pause")

ocr_api = Blueprint('ocr', __name__)


@ocr_api.route('/', methods=['GET'])
def ocr_is_work():
    return {'code': 200}


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


@ocr_api.route('/local_ocr3/', methods=['POST'])
def local_ocr3():
    # 接收图片
    upload_file = request.files.get('file')
    # print(upload_file)
    if upload_file:
        result = ocr.classification(upload_file.read())
        # print(result)
        return result
    return 400


@ocr_api.route('/local_ocr4/', methods=['POST'])
def local_ocr4():
    # 接收图片
    upload_file = base64.b64decode(request.form.get('file'))
    # print(upload_file)
    allowstr = request.form.get('allowstr')
    if allowstr != 'null' and allowstr != 'None':
        allowstr = allowstr
    else:
        allowstr = None
    if upload_file:
        result = easyocr_reader.readtext(upload_file, allowlist=allowstr, detail=0)
        # print(result)
        if type(result) is list:
            return str(result).replace("'", '').replace('[', '').replace(']', '')
        return str(result)
    return 400


@ocr_api.route('/baidu_ocr/', methods=['POST'])
def baidu_ocr():
    lay_sw = False
    # 接收图片
    img = request.files.get('file')
    baidu_queue.put((img.read()))
    if img:
        # time.sleep(random.uniform(1.5, 2.05))
        part = baidu_queue.get()

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


@ocr_api.route('/ocrspace_ocr/<language>', methods=['POST'])
def ocrspace_ocr(language='chs'):
    # 接收图片
    img = request.files.get('file')
    if language:
        ocrspace_ocr_config['language'] = language
    # ocrspace_ocr_config['base64Image'] = img.read()
    try:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={'test.png': img.read()},
                          data=ocrspace_ocr_config,
                          )
        if type(r) is list:
            return str(r).replace("'", '').replace('[', '').replace(']', '')
    except Exception as e:
        raise Exception('ocrspace_ocr发生了错误，原因为:{}'.format(e))
    return r.content.decode()


@ocr_api.route('/pcrocr_ocr/', methods=['POST'])
def pcrocr_ocr():
    # 接收图片
    img = request.form.get('file')
    # print(request.form.get('voc'))
    voc = request.form.get('voc')
    do_pre = request.form.get('do_pre')
    # print("VOC:",voc,type(voc))
    # print("DO_PRE:",do_pre,type(do_pre))
    # from pcrocr.utils import base64_decode
    # print(base64_decode(img))

    if voc != 'null' and voc != 'None':
        voc = voc
    else:
        voc = None

    if do_pre != 'True' and do_pre != 'true':
        do_pre = False
    else:
        do_pre = True
    if img:
        try:
            result = pcr_ocr(x=img, voc=voc, do_pre=do_pre)
            return result['text']
        except FileNotFoundError as e:
            raise Exception('PCR特化OCR发生了错误，原因为:{}'.format(e))
    return 400
