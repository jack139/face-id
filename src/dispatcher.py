# -*- coding: utf-8 -*-

# 后台调度程序，轮询kafka，异步执行，redis返回结果

import sys, json, time
from kafka import KafkaConsumer

from async_api.utils import helper
from async_api import logger

from facelib import api_func

logger = logger.get_logger(__name__)

if __name__ == '__main__':
    while 1:
        consumer = KafkaConsumer('synchronous-asynchronous-queue', bootstrap_servers=['localhost:9092'])

        for message in consumer:
            # message value and key are raw bytes -- decode if necessary
            msg_body = json.loads(message.value.decode('utf-8'))
            request = msg_body['data']
            #print(request.keys())
            logger.info('Calling api: '+request['api']) 

            if request['api']=='face_search':
                if request['user_id'] is None: # 1:N
                    r = api_func.face_search(request['image'], request['group_id'], request['max_user_num'])
                else: # 1:1
                    r = []        

                # 准备结果
                result = { 'user_list' : r }

                # 发送消息
                helper.redis_publish(msg_body['request_id'], json.dumps(result))

            else:
                logger.error('Unknown api: '+request['api']) 

                # 发送消息
                helper.redis_publish(msg_body['request_id'], 'Hello world.')

            time.sleep(1)

