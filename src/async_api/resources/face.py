# coding:utf-8

import os, time, hashlib
import json
from flask_restful import reqparse, abort, Resource, fields, request

from ..utils import helper
from .. import logger

logger = logger.get_logger(__name__)

# 人脸识别 1:N
class FaceSearch(Resource):
    #@helper.token_required
    def post(self): 
        try:
            # 获取入参
            body_data = request.get_data().decode('utf-8') # bytes to str
            json_data = json.loads(body_data)
 
            group_id = json_data.get('group_id', 'DEFAULT')
            user_id = json_data.get('user_id')
            image = json_data.get('image')
            max_user_num = json_data.get('max_user_num', '5')

            logger.info("入参: %s %s %s %d"%(group_id, user_id, max_user_num, len(image)))

            # 检查参数
            if image is None:
                return {"code": 9001, "msg": "缺少参数"}

            if not max_user_num.isdigit():
                max_user_num = 5
            else:
                # 最多返回5个
                max_user_num = min(5, int(max_user_num))

            # 准备发队列消息
            request_id = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()

            request_msg = {
                'api'          : 'face_search',
                'image'        : image,
                'group_id'     : group_id,
                'user_id'      : user_id,
                'max_user_num' : max_user_num,
            }

            # 发消息给 kafka
            helper.kafka_send_msg(request_id, request_msg)

            # 通过redis订阅等待结果返回
            ret = helper.redis_subscribe(request_id)

            ret = json.loads(ret['data'].decode('utf-8'))

            return {'code': 200, 'msg' : 'success', 'data' :  ret}

        except BaseException as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }

