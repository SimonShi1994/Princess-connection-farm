import os

from flask import Blueprint, jsonify, request

from api.constants.reply import ListReply
from core.usercentre import AutomatorRecorder, list_all_batches

batches_api = Blueprint('batches', __name__)


@batches_api.route('/batches', methods=['GET'])
def get_list_all_batches():
    try:
        count = 0
        batches = list_all_batches()
        count = len(batches)
        return ListReply(batches, count)
    except Exception as e:
        return 500


@batches_api.route('/get_batches/<filename>', methods=['GET'])
# 查
def get_batches_info(filename):
    try:
        r = AutomatorRecorder.getbatch(filename)
        if r:
            return ListReply(r, 0)
        else:
            return 500
    except Exception as e:
        return 500


@batches_api.route('/batches_save', methods=['POST'])
# 增 改
def save_batches():
    # '{"batch": [{"group": "\u88c5\u5907\u519c\u573a","taskfile": "n11\u88c5\u5907\u519c\u573a","priority": 0}]}'
    try:
        obj = request.json
        BatchesFileName = request.json.get("filename")
        obj.pop("filename")
        save_dict = {"batch": [obj]}
        if check_valid_batch(save_dict, is_raise=False):
            AutomatorRecorder.setbatch(BatchName, save_dict)
            old_batch = AutomatorRecorder.getbatch(BatchesFileName)
            return jsonify({"code": 200, "msg": f"{old_batch}-保存成功"})
        else:
            return jsonify({"code": 500, "msg": f"{save_dict}-保存失败"})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"{e}-保存失败"})


@batches_api.route('/batches_del/<filename>', methods=['GET'])
# 删
def del_schedule(filename):
    batch_addr = "batches"
    target = "%s/%s.json" % (batch_addr, filename)
    if os.path.exists(target):
        os.remove(target)
        return 200
    else:
        return 500
