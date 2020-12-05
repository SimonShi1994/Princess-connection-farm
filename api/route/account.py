from flask import Blueprint, jsonify, request

from api.constants.errors import NotFoundError, BadRequestError
from api.constants.reply import Reply, ListReply
from core.usercentre import list_all_users, AutomatorRecorder
from CreateUser import create_account as service_create_account, edit_account, del_account

account_api = Blueprint('account', __name__)


@account_api.route('/account', methods=['GET'])
def list_account():
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
                'username': user.get('account'),
                'password': '********',
                'tags': '-'
            })

    return ListReply(data, count)


@account_api.route('/account/<username>', methods=['GET'])
def retrieve_account(username):
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
            data['username'] = user.get('account')
            data['taskname'] = user.get('taskfile')
        return Reply(data)

    except Exception as e:
        return NotFoundError(f"获取用户 {username} 失败, {e}")


@account_api.route('/account', methods=['POST'])
def create_account():
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
    print(body)
    if body is None:
        return BadRequestError(f'参数不合法')
    username = body.get('username', '')
    password = body.get('password', '')
    taskname = body.get('taskname', '')
    # taskname已经被废弃不再需要
    if username == '':
        return BadRequestError(f'参数 username 不为空')
    if password == '':
        return BadRequestError(f'参数 password 不为空')

    service_create_account(account=username, password=password)

    return Reply({'username': username, 'password': password})


@account_api.route('/account/<username>', methods=['PUT'])
def update_account(username):
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
    taskname = body.get('taskname', None)

    edit_account(account=username, password=password, taskfile=taskname)
    return Reply({'username': username, 'password': password, 'taskname': taskname})


@account_api.route('/account/<username>', methods=['DELETE'])
def delete_account(username):
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

    del_account(username)

    return Reply({'username': username})
