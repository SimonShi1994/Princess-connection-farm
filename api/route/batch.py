import os

from flask import Blueprint, jsonify, request

from api.constants.errors import NotFoundError, BadRequestError
from api.constants.reply import Reply, ListReply
from core.usercentre import AutomatorRecorder, list_all_batches
from CreateUser import create_schedule as service_create_schedule, edit_schedule, del_schedule

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