import os

from flask import Blueprint, jsonify, request

from api.constants.errors import NotFoundError, BadRequestError
from api.constants.reply import Reply, ListReply
from core.usercentre import list_all_users, AutomatorRecorder
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


@schedule_api.route('/batches', methods=['GET'])
def list_all_batches(verbose=0):
    def check_valid_batch(batch: dict, is_raise=True) -> bool:
        try:
            assert "batch" in batch
            B = batch["batch"]
            assert type(B) is list
            for i in B:
                f1 = "account" in i
                f2 = "group" in i
                if f1 + f2 == 0:
                    return BadRequestError(f"必须至少含有account,group中的一个！")
                if f1 + f2 == 2:
                    return BadRequestError(f"account和group键只能出现其中一个！")
                assert "taskfile" in i
                assert type("taskfile") is str
                assert "priority" in i

        except Exception as e:
            if is_raise:
                raise e
            else:
                return False
        return True
    batch_addr = "batches"  # 存放批任务的文件夹
    if not os.path.exists(batch_addr):
        os.makedirs(batch_addr)
    ld = os.listdir(batch_addr)
    batches = []
    count = 0
    for i in ld:
        if not os.path.isdir(i) and i.endswith(".txt"):
            nam = ""
            try:
                nam = i[:-4]
                batch = AutomatorRecorder.getbatch(nam)
                check_valid_batch(batch)
                batches += [nam]
                if verbose:
                    pass
                    # print("批配置", nam, "加载成功！")
                count += 1
            except Exception as e:
                if verbose:
                    pass
                    # print("打开批配置", nam, "失败！", e)
    if verbose:
        pass
        # print("加载完成，一共加载成功", count, "个批配置。")
    return ListReply(batches, count)
