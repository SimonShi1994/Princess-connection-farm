from flask import Blueprint, jsonify, request

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
    return jsonify({})


@account_api.route('/account/<pk>', methods=['GET'])
def retrieve_account(pk):
    """
    获取单条账号
    ---
    tags:
      - 账号
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
    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """

    username = request.form.get('username')
    password = request.form.get('password')

    return jsonify({})


@account_api.route('/account/<pk>', methods=['PUT'])
def update_account(pk):
    """
    更新账号
    ---
    tags:
      - 账号
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
          id:  账号更新
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
    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """

    username = request.form.get('username')
    password = request.form.get('password')

    return jsonify({})


@account_api.route('/account/<pk>', methods=['POST'])
def delete_account(pk):
    """
    删除账号
    ---
    tags:
      - 账号
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
