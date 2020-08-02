from flask import Blueprint, jsonify, request

clan_api = Blueprint('clan', __name__)


@clan_api.route('/clan', methods=['GET'])
def list_clan():
    """
    获取行会列表
    ---
    tags:
      - 行会
    description:

    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """
    return jsonify({})


@clan_api.route('/clan/<pk>', methods=['GET'])
def retrieve_clan(pk):
    """
    获取单条行会
    ---
    tags:
      - 行会
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


@clan_api.route('/clan', methods=['POST'])
def create_clan():
    """
    添加行会
    ---
    tags:
      - 行会
    description:

    parameters:
      - name: body
        in: body
        required: true
        schema:
          id:  行会添加
          required:
            - clan_name
          properties:
            clan_name:
              type: string
              description: 行会名称
    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """

    clan_name = request.form.get('clan_name')

    return jsonify({})


@clan_api.route('/clan/<pk>', methods=['PUT'])
def update_clan(pk):
    """
    更新行会
    ---
    tags:
      - 行会
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
          id:  行会更新
          required:
            - clan_name
          properties:
            clan_name:
              type: string
              description: 行会名称
    responses:
      2xx:
        description: 成功
      4xx:
        description: 参数有误等
    """

    clan_name = request.form.get('clan_name')

    return jsonify({})


@clan_api.route('/clan/<pk>', methods=['POST'])
def delete_clan(pk):
    """
    删除行会
    ---
    tags:
      - 行会
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
