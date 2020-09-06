from flask import Blueprint, jsonify, request

from core.pcr_config import ocr_mode

import os
# 这一行代码用于关闭tensorflow的gpu模式（如果使用，内存占用翻几倍）
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

if ocr_mode != "网络" and len(ocr_mode) != 0:
    import muggle_ocr
    # 初始化；model_type 包含了 ModelType.OCR/ModelType.Captcha 两种
    sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.OCR)



ocr_api = Blueprint('ocr', __name__)


@ocr_api.route('/', methods=['POST'])
def ocr():
    # 接收图片
    upload_file = request.files.get('file')
    # print(upload_file)
    if upload_file:
        result = sdk.predict(upload_file.read())
        # print(result)
        return result
    return 400
