# coding:utf-8

import os, time, hashlib
import json
from flask_restful import reqparse, abort, Resource, fields, request
from config.settings import MAX_IMAGE_SIZE
from ..utils import helper
from .. import logger

logger = logger.get_logger(__name__)

# 人脸定位
class FaceLocate(Resource):
    @helper.signature_required
    def post(self): 
        try:
            # 获取入参
            body_data = request.get_data().decode('utf-8') # bytes to str
            json_data = json.loads(body_data)
 
            image = json_data.get('image', '')
            max_face_num = json_data.get('max_face_num', 1)

            logger.info("入参: %s %d"%(max_face_num, len(image)))

            # 检查参数
            if len(image)==0:
                return {"code": 9001, "msg": "缺少参数"}

            if len(image)>MAX_IMAGE_SIZE:
                return {"code": 9002, "msg": "图片数据太大"}

            # 准备发队列消息
            request_id = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()

            request_msg = {
                'api'          : 'face_locate',
                'image'        : image,
                'max_face_num' : int(max_face_num),
            }

            # 在发kafka消息前生成 consumer, 防止消息漏掉
            consumer = helper.kafka_get_return_consumer()

            # 发消息给 kafka
            r = helper.kafka_send_msg(request_id, request_msg)
            if r is None:
                logger.error("消息队列异常")
                return {"code": 9099, "msg": "消息队列异常"}

            # 通过redis订阅等待结果返回
            #ret = helper.redis_subscribe(request_id)
            #ret2 = json.loads(ret['data'].decode('utf-8'))

            # 通过kafka 等待结果返回
            ret = helper.kafka_recieve_return(consumer, request_id)
            ret2 = ret['data']

            if ret2['code']==200:
                return {'code': 200, 'msg' : 'success', 'data' : ret2['data']}
            else:
                return ret2

        except Exception as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }

