# coding:utf-8

import os, time, json
from flask_restful import reqparse, abort, Resource, fields, request

from ..utils import helper
from .. import logger

logger = logger.get_logger(__name__)

# api测试
class SyncTest(Resource):
    def post(self):  #  request --> redis --> dispatcher --> redis --> return
        try:
            #time.sleep(1) # for test

            # 准备发队列消息
            request_id = helper.gen_request_id()
            request_msg = {
                'api' : 'sync_test',
                'txt' : 'Hello',
            }

            # 异步处理

            # 在发redis消息前注册, 防止消息漏掉
            ps = helper.redis_subscribe(request_id)

            # 发布消息给redis
            r = helper.redis_publish_request(request_id, request_msg)
            if r is None:
                logger.error("消息队列异常")
                return {"code": 9099, "msg": "消息队列异常"}

            # 通过redis订阅等待结果返回
            ret = helper.redis_sub_receive(ps, request_id)               
            ret2 = json.loads(ret['data'].decode('utf-8'))
            if ret2['code']!=200:
                return ret2

            print(ret)
            return {'code': 200, 'msg' : 'success', 'data' : ret2['data'] }

        except BaseException as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }

