import time
import json
import requests
import datetime
import traceback
import urllib.request
from . import gold_price_monitor
from flask_cors import cross_origin
from flask import session, redirect, url_for, current_app, flash, Response, request, jsonify
from ..model.gold_price_model import gold_price as gold_price_table
from ..model.gold_price_model import gold_price_push_option
from ..login.login_funtion import User
from ..privilege.privilege_control import permission_required
from ..response import Response
from peewee import DoesNotExist

rsp = Response()

URL_PREFIX = '/gold'


@gold_price_monitor.route('/get', methods=['POST'])
@cross_origin()
def get():
    try:
        user_id = request.get_json()['user_id']
        try:
            _ = gold_price_push_option.get((gold_price_push_option.is_valid == 1) & (gold_price_push_option.user_id == user_id))
            threshold = eval(_.push_threshold)
        except DoesNotExist:
            threshold = []

        result = []
        _ = gold_price_table.select().limit(40).order_by(-gold_price_table.update_time).dicts()
        for boo in _:
            result.insert(0, {'price': boo['price'], 'update_time': boo['update_time'].strftime("%m-%d %H:%M")})
        return rsp.success({'price_list': result, 'threshold': threshold})
    except Exception as e:
        traceback.print_exc()
        return rsp.failed(e), 500


@gold_price_monitor.route('/edit', methods=['POST'])
@cross_origin()
def edit():
    try:
        user_id = request.get_json()['user_id']
        threshold_min = request.get_json()['threshold_min']
        threshold_max = request.get_json()['threshold_max']
        threshold = [threshold_min, threshold_max]
        try:
            _ = gold_price_push_option.get((gold_price_push_option.is_valid == 1) & (gold_price_push_option.user_id == user_id))
            _.is_valid = 0
            _.save()
        except DoesNotExist:
            pass
        gold_price_push_option.create(user_id=user_id, is_valid=1, push_threshold=threshold, update_time=dateyime.datetime.now())
        response = {'code': 200, 'msg': '成功！', 'data': []}
        return jsonify(response)
    except Exception as e:
        traceback.print_exc()
        return rsp.failed(e), 500
