# coding:utf-8

import os, time, hashlib, json
from flask_restful import reqparse, abort, Api, Resource, fields, marshal, request

from ..utils import helper
from .. import logger

logger = logger.get_logger(__name__)

# api测试
class SyncTest(Resource):
    #@helper.token_required
    def post(self):  #  request --> kafka --> dispatcher --> redis --> return
        try:
            #time.sleep(1) # for test
            request_id = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()

            request_msg = {
                'api' : 'sync_test',
                'txt' : 'Hello',
            }

            # 发消息给 kafka
            r = helper.kafka_send_msg(request_id, request_msg)
            if r is None:
                logger.error("消息队列异常")
                return {"code": 9099, "msg": "消息队列异常"}

            # 通过redis订阅等待结果返回
            ret = helper.redis_subscribe(request_id)
            ret2 = json.loads(ret['data'].decode('utf-8'))
            if ret2['code']!=200:
                return ret2

            print(ret)
            return {'code': 200, 'msg' : 'success', 'data' : ret2['data'] }

        except BaseException as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }


    def put(self):  #  request --> kafka --> dispatcher --> kafka --> return
        try:
            #time.sleep(1) # for test
            request_id = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()

            request_msg = {
                'api' : 'sync_test',
                'txt' : 'Hello',
            }

            # 在发kafka消息前生成 consumer, 防止消息漏掉
            consumer = helper.kafka_get_return_consumer()

            # 发消息给 kafka
            r = helper.kafka_send_msg(request_id, request_msg)
            if r is None:
                logger.error("消息队列异常")
                return {"code": 9099, "msg": "消息队列异常"}

            # 通过kafka 等待结果返回
            ret = helper.kafka_recieve_return(consumer, request_id)
            ret2 = ret['data']
            if ret2['code']!=200:
                return ret2

            print(ret)
            return {'code': 200, 'msg' : 'success', 'data' : ret2['data'] }

        except BaseException as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }


