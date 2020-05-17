# coding:utf-8

import os, time, hashlib
from flask_restful import reqparse, abort, Api, Resource, fields, marshal, request

from utils import helper
import logger

logger = logger.get_logger(__name__)

# api测试
class SyncTest(Resource):
    #@helper.token_required
    def post(self): 
        try:
            #time.sleep(1) # for test
            rid = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()

            # 发消息给 kafka
            helper.kafka_send_msg(rid, 'Hello')

            # 通过redis订阅等待结果返回
            ret = helper.redis_subscribe(rid)

            print(ret)
            return {'code': 200, 'msg' : 'success', 'data' : ret['data'].decode('utf-8') }

        except BaseException as e:
            logger.error("未知异常: %s" % e.message, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e.message) }

