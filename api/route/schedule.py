import os

from flask import Blueprint, jsonify, request

from api.constants.errors import NotFoundError, BadRequestError
from api.constants.reply import Reply, ListReply
from core.usercentre import list_all_users, AutomatorRecorder, list_all_schedules
from CreateUser import create_schedule as service_create_schedule, edit_schedule, del_schedule

schedule_api = Blueprint('schedule', __name__)


@schedule_api.route('/schedule', methods=['GET'])
def list_schedule():
    """
    获取账号列表
    ---
    tags:
      - 账号
    description:

    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """
    data = []
    count = 0

    all_users = list_all_users()
    count = len(all_users)

    for username in all_users:
        try:
            user = AutomatorRecorder(username).getuser()
        except Exception as e:
            return NotFoundError(e)
        if user is not None:
            data.append({
                'username': user.get('schedule'),
                'password': '********',
                'tags': '-'
            })

    return ListReply(data, count)


@schedule_api.route('/schedule/<username>', methods=['GET'])
def retrieve_schedule(username):
    """
    获取单条账号
    ---
    tags:
      - 账号
    description:

    parameters:
          - name: username
            in: path
            type: string
            required: true
            description: 用户名
    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """
    if username == '':
        return BadRequestError(f'参数不合法, 用户名:{username}')

    data = {
        'username': '',
        'password': '********',
        'taskname': '',
        'tags': '-'
    }

    try:
        user = AutomatorRecorder(username).getuser()
        if user is not None:
            data['username'] = user.get('schedule')
            data['taskname'] = user.get('taskfile')
        return Reply(data)

    except Exception as e:
        return NotFoundError(f"获取用户 {username} 失败, {e}")


@schedule_api.route('/schedule', methods=['POST'])
def create_schedule():
    """
    添加账号
    ---
    tags:
      - 账号
    description:

    parameters:
      - name: body
        in: body
        required: true
        schema:
          id:  账号添加
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: 账户
            password:
              type: string
              description: 密码
            taskname:
              type: string
              description: 任务
    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """
    body = request.form or request.get_json()
    if body is None:
        return BadRequestError(f'参数不合法')
    username = body.get('username', '')
    password = body.get('password', '')
    # taskname = body.get('taskname', '')
    # taskname已经被废弃不再需要
    try:
        if username == '':
            return BadRequestError(f'参数 username 不为空')
        if password == '':
            return BadRequestError(f'参数 password 不为空')

        service_create_schedule(schedule=username, password=password)

        return Reply({'username': username, 'password': password})

    except Exception as e:
        return NotFoundError(f"添加用户 {username} 失败, {e}")


@schedule_api.route('/schedule/<username>', methods=['PUT'])
def update_schedule(username):
    """
    更新账号
    ---
    tags:
      - 账号
    description:

    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: 主键
      - name: body
        in: body
        required: true
        schema:
          id:  账号更新
          properties:
            password:
              type: string
              description: 密码
            taskname:
              type: string
              description: 任务
    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """
    if username == '':
        return BadRequestError(f'参数 username 不为空')

    body = request.form or request.get_json()
    if body is None:
        return BadRequestError(f'参数不合法')
    password = body.get('password', None)
    # taskname = body.get('taskname', None)

    edit_schedule(schedule=username, password=password)
    return Reply({'username': username, 'password': password})


@schedule_api.route('/schedule/<username>', methods=['DELETE'])
def delete_schedule(username):
    """
    删除账号
    ---
    tags:
      - 账号
    description:

    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: 主键
    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """
    if username == '':
        return BadRequestError(f'参数 username 不为空')

    del_schedule(username)

    return Reply({'username': username})


@schedule_api.route('/schedules', methods=['GET'])
def get_list_all_schedules():
    try:
        count = 0
        schedules = list_all_schedules()
        count = len(schedules)
        return ListReply(schedules, count)
    except Exception as e:
        return 500


@schedule_api.route('/get_schedules/<filename>', methods=['GET'])
def get_schedules_info(filename):
    try:
        r = AutomatorRecorder.getschedule(filename)
        return ListReply(r, 0)
    except Exception as e:
        return 500


@schedule_api.route('/schedules_save', methods=['POST'])
def save_schedules():
    schedules = request.get_data()
    AutomatorRecorder.setschedule(ScheduleName, obj)
