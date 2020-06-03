# -*- coding: utf-8 -*-

# 后台调度程序，轮询kafka，异步执行，redis返回结果

import sys, json, time
import concurrent.futures
from kafka import KafkaConsumer

from async_api.utils import helper
from async_api import logger

from facelib import api_func
from config.settings import MAX_MESSAGE_SIZE

import binascii

logger = logger.get_logger(__name__)

def process_thread(request):
    import keras.backend.tensorflow_backend as tb
    tb._SYMBOLIC_SCOPE.value = True

    try:
        if request['api']=='face_search': # 人脸识别
            if request['user_id'] is None: # 1:N
                r = api_func.face_search(request['image'], request['group_id'], request['max_user_num'])
                # 准备结果
                result = { 'code' : 200, 'data' : { 'user_list' : r } }

            else: # 1:1 
                r = api_func.face_verify_db(request['image'], request['group_id'], request['user_id'])
                # 准备结果
                result = { 'code' : 200, 'data' : { 'is_match' : r[0], 'score' : r[1] } }

        elif request['api']=='face_verify': # 人脸验证
            r = api_func.face_verify(request['image1'], request['image2'])
            # 准备结果
            result = { 'code' : 200, 'data' : { 'is_match' : r[0], 'score' : r[1] } }

        elif request['api']=='face_locate': # 人脸定位
            r = api_func.face_locations(request['image'], request['max_face_num'])
            # 准备结果
            result = { 'code' : 200, 'data' : { 'face_num' : r[0], 'locations' : r[1] } }

        elif request['api']=='face_features': # 计算特征值
            encodings, boxes = api_func.face_features(request['image'])
            # 准备结果
            result = { 'code' : 200, 'data' : { 'encodings' : encodings, 'boxes' : boxes } }

        else: # 未知 api
            logger.error('Unknown api: '+request['api']) 

            result = { 'code' : 9900, 'msg' : '未知 api 调用'}

        # 发送消息
        helper.redis_publish(msg_body['request_id'], result)

    except binascii.Error as e:
        logger.error("编码转换异常: %s" % e)
        helper.redis_publish(msg_body['request_id'], { 'code' : 9901, 'msg' : 'base64编码异常: '+str(e)})

    except Exception as e:
        logger.error("未知异常: %s" % e, exc_info=True)
        helper.redis_publish(msg_body['request_id'], { 'code' : 9998, 'msg' : '未知错误: '+str(e)})


if __name__ == '__main__':
    while 1:
        consumer = KafkaConsumer('synchronous-asynchronous-queue', bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')), 
            fetch_max_bytes=MAX_MESSAGE_SIZE)

        for message in consumer:
            # message value and key are raw bytes -- decode if necessary
            #msg_body = json.loads(message.value.decode('utf-8'))
            msg_body = message.value
            request = msg_body['data']
            #print(request.keys())
            logger.info('Calling api: '+request['api']) 

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(process_thread, request)
                logger.info('Thread future: '+str(future)) 

            time.sleep(1)

