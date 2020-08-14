from flask import Blueprint, jsonify, request
from api.constants.errors import NotFoundError, BadRequestError
from api.constants.reply import Reply, ListReply
from CreateUser import list_all_tasks, AutomatorRecorder, create_task as service_create_task, del_task
task_api = Blueprint('task', __name__)


@task_api.route('/task', methods=['GET'])
def list_task():
    """
    获取任务列表
    ---
    tags:
      - 任务
    description:

    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """
    res = []
    tasks: [] = list_all_tasks()
    for task in tasks:
        res.append({
            'taskname': task,
            'accounts': '-',
        })
    return ListReply(res, len(res))


@task_api.route('/task/<taskname>', methods=['GET'])
def retrieve_task(taskname):
    """
    获取单条任务
    ---
    tags:
      - 任务
    description:

    parameters:
          - name: taskname
            in: path
            type: string
            required: true
            description: 任务名
    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """
    if taskname == '':
        return BadRequestError(f'参数不合法, 任务名:{taskname}')

    data = {
        'taskname': '',
        'accounts': '-',
        'subtask': {},
    }

    try:
        subtask = AutomatorRecorder(None).gettask(taskname)
        if subtask is not None:
            data['taskname'] = taskname
            data['subtask'] = subtask
        return Reply(data)

    except Exception as e:
        return NotFoundError(f"获取任务 {taskname} 失败, {e}")


@task_api.route('/task', methods=['POST'])
def create_task():
    """
    添加任务
    ---
    tags:
      - 任务
    description:

    parameters:
      - name: body
        in: body
        required: true
        schema:
          id:  任务添加
          required:
            taskname
          properties:
            taskname:
              type: string
              description: 任务名
    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """

    body = request.form or request.get_json()
    if body is None:
        return BadRequestError(f'参数不合法')
    taskname = body.get('taskname', '')
    if taskname == '':
        return BadRequestError(f'参数 taskname 不为空')

    service_create_task(taskname)
    return Reply({'taskname': taskname})


@task_api.route('/task/<taskname>', methods=['PUT'])
def update_task(taskname):
    """
    更新任务
    ---
    tags:
      - 任务
    description:

    parameters:
      - name: pk
        in: path
        type: string
        required: true
        description: 主键
      - name: body
        in: body
        required: true
        schema:
          id:  任务添加
          required:
            taskname
          properties:
            taskname:
              type: string
              description: 任务名
    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """
    return jsonify({})


@task_api.route('/task/<taskname>', methods=['DELETE'])
def delete_task(taskname):
    """
    删除任务
    ---
    tags:
      - 任务
    description:

    parameters:
      - name: taskname
        in: path
        type: string
        required: true
        description: 任务名
    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """
    if taskname == '':
        return BadRequestError(f'参数 taskname 不为空')

    del_task(taskname)

    return Reply({'taskname': taskname})
