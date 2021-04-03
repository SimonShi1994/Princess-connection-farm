import os

from flask import Blueprint, jsonify, request

from api.constants.errors import NotFoundError, BadRequestError
from api.constants.reply import Reply, ListReply
from core.usercentre import AutomatorRecorder, list_all_schedules
from CreateUser import create_schedule as service_create_schedule, edit_schedule, del_schedule, check_valid_schedule

schedule_api = Blueprint('schedules', __name__)

@schedule_api.route('/schedules', methods=['GET'])
def get_list_all_schedules():
    try:
        count = 0
        schedules = list_all_schedules()
        count = len(schedules)
        if schedules:
            return ListReply(schedules, count)
        else:
            return 500
    except Exception as e:
        return 500


@schedule_api.route('/get_schedules/<filename>', methods=['GET'])
def get_schedules_info(filename):
    # x,y,z都为字典的拆分所产生出来的临时变量
    # 后面会优化
    try:
        r = AutomatorRecorder.getschedule(filename)
        if len(r['schedules']) > 1:
            count = 0
            for i in r['schedules']:
                x = list(i.values())
                y = list(i.keys())
                x[2] = [x[2]]
                y[2] = 'batchlist'
                r['schedules'][count] = [dict(zip(y, x))]
                if count < len(r['schedules']):
                    count = count + 1
        elif len(r['schedules']) == 1:
            x = list(r.values())
            y = list(x[0][0].keys())
            z = list(x[0][0].values())
            for i in range(len(y)):
                if y[i] == 'batchfile':
                    y[i] = 'batchlist'
                    # if not type(z[i]) is list:
                    z[i] = [z[i]]
                r['schedules'] = [dict(zip(y, z))]
        if r:
            return ListReply(r, 0)
        else:
            return 500
    except Exception as e:
        return 500


@schedule_api.route('/schedules_save', methods=['POST'])
def save_schedules():
    # '{"name":"test","batchlist":["zhuangbeirichang"],"condition":{},"type":"asap"}'
    try:
        obj = request.json
        ScheduleFileName = request.json.get("filename")
        # old_schedule = AutomatorRecorder.getschedule(ScheduleFileName)
        obj.pop("filename")
        save_dict = {"schedules": [obj]}
        if check_valid_schedule(save_dict, is_raise=False):
            AutomatorRecorder.setschedule(ScheduleFileName, save_dict)
            old_schedule = AutomatorRecorder.getschedule(ScheduleFileName)
            return jsonify({"code":200, "msg":f"{old_schedule}-保存成功"})
        else:
            return jsonify({"code":500, "msg":f"{save_dict}-保存失败"})
    except Exception as e:
        return jsonify({"code":500, "msg":f"{e}-保存失败"})
