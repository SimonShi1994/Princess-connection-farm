import os

from flask import Blueprint, jsonify, request

from api.constants.errors import NotFoundError, BadRequestError
from api.constants.reply import Reply, ListReply
from core.usercentre import list_all_users, AutomatorRecorder, list_all_schedules
from CreateUser import create_schedule as service_create_schedule, edit_schedule, del_schedule

schedule_api = Blueprint('schedules', __name__)

@schedule_api.route('/schedules', methods=['GET'])
def get_list_all_schedules():
    schedules = list_all_schedules()
    count = len(schedules)
    if schedules and count != 0:
        return ListReply(schedules, count)
    else:
        return NotFoundError(f"读取总数为{count}的日程表配置文件夹失败")


@schedule_api.route('/schedules_save', methods=['POST'])
def save_schedules():
    schedules = request.get_data()
    AutomatorRecorder.setschedule(ScheduleName, obj)
