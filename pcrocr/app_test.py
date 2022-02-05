# -*- coding:utf-8 -*-
import base64

import cv2
import requests

part = cv2.imread("../../Princess-connection-farm-master/dxc2.png")
img_binary = cv2.imencode('.jpg', part)[1].tostring()  # 转成base64编码（误）
img_binary = base64.b64encode(img_binary)
print(img_binary)
data = {
    'file': img_binary,
    'voc': 'None',
    'do_pre': 'True',
}
local_ocr_text = requests.post(url="http://127.0.0.1:5000/ocr/pcrocr_ocr/", data=data)
print(local_ocr_text.text)