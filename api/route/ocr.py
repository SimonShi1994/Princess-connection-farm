from flask import Blueprint, jsonify, request
import muggle_ocr

import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

ocr_api = Blueprint('ocr', __name__)

sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.OCR)


@ocr_api.route('/', methods=['POST'])
def ocr():
    # 接收图片
    upload_file = request.files.get('file')
    # 获取图片名
    file_name = upload_file.filename
    if upload_file:
        result = sdk.predict(upload_file.read())
        print(result)
        return result
    return 400
