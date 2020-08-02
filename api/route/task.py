from flask import Blueprint, jsonify, request

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
    return jsonify({})


@task_api.route('/task/<pk>', methods=['GET'])
def retrieve_task(pk):
    """
    获取单条任务
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
    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """
    return jsonify({})


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
            task_type
            params
          properties:
            task_type:
              type: string
              description: 任务类型
            params:
              type: string
              description: 任务参数
            title:
              type: string
              description: 任务标题
            desc:
              type: string
              description: 任务描述
    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """

    task_type = request.form.get('task_type')
    params = request.form.get('params')
    title = request.form.get('title')
    desc = request.form.get('desc')

    return jsonify({})


@task_api.route('/task/<pk>', methods=['PUT'])
def update_task(pk):
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
            task_type
            params
          properties:
            task_type:
              type: string
              description: 任务类型
            params:
              type: string
              description: 任务参数
            title:
              type: string
              description: 任务标题
            desc:
              type: string
              description: 任务描述
    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """

    task_type = request.form.get('task_type')
    params = request.form.get('params')
    title = request.form.get('title')
    desc = request.form.get('desc')

    return jsonify({})


@task_api.route('/task/<pk>', methods=['POST'])
def delete_task(pk):
    """
    删除任务
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
    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """

    return jsonify({})
