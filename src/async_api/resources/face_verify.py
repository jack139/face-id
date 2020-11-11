# coding:utf-8

import json
from datetime import datetime
from flask_restful import reqparse, abort, Resource, fields, request
from config.settings import MAX_IMAGE_SIZE
from ..utils import helper
from .. import logger

logger = logger.get_logger(__name__)

# 人脸验证 1:1
class FaceVerify(Resource):
    @helper.signature_required
    def post(self): 
        try:
            # 获取入参
            body_data = request.get_data().decode('utf-8') # bytes to str
            json_data = json.loads(body_data)
 
            image1 = json_data.get('image1', '')
            image2 = json_data.get('image2', '')

            logger.info("入参: %d %d"%(len(image1), len(image2)))

            # 检查参数
            if len(image1)==0 or len(image2)==0:
                return {"code": 9001, "msg": "缺少参数"}

            if len(image1)>MAX_IMAGE_SIZE or len(image2)>MAX_IMAGE_SIZE:
                return {"code": 9002, "msg": "图片数据太大"}

            # 准备发队列消息
            request_id = helper.gen_request_id()

            request_msg = {
                'api'          : 'face_verify',
                'image1'        : image1,
                'image2'        : image2,
            }

            # 发消息给 redis
            start_time = datetime.now()

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

            logger.info('[Time taken: {!s}]'.format(datetime.now() - start_time))

            if ret2['code']==200:
                return {'code': 200, 'msg' : 'success', 'data' : ret2['data']}
            else:
                return ret2

        except Exception as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }

