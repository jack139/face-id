# coding:utf-8

import os, time, hashlib
import json
from datetime import datetime
from flask_restful import reqparse, abort, Resource, fields, request
from config.settings import MAX_IMAGE_SIZE
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
            image = json_data.get('image', '')
            max_user_num = json_data.get('max_user_num', 5)

            logger.info("入参: %s %s %s %d"%(group_id, user_id, max_user_num, len(image)))

            # 检查参数
            if len(image)==0:
                return {"code": 9001, "msg": "缺少参数"}

            if len(image)>MAX_IMAGE_SIZE:
                return {"code": 9002, "msg": "图片数据太大"}

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

            start_time = datetime.now()

            if 0:
                # 同步处理 （用于对比测试）
                import dispatcher  # 调用时载入，第一轮时间会有点久

                ret2 = dispatcher.process_api(request_msg)

            else:
                # 异步处理

                # 在发kafka消息前生成 consumer, 防止消息漏掉
                consumer = helper.kafka_get_return_consumer()

                # 发消息给 kafka
                #print('-->', request_id, helper.time_str())
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

            #print('<--', request_id, helper.time_str(), datetime.now() - start_time)
            logger.info('[Time taken: {!s}]'.format(datetime.now() - start_time))
            
            if ret2['code']==200:
                return {'code': 200, 'msg' : 'success', 'data' : ret2['data']}
            else:
                return ret2

        except Exception as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }

