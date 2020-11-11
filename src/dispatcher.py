# -*- coding: utf-8 -*-

# 后台调度程序，轮询redis，异步执行，redis返回结果

import sys, json, time, random
import concurrent.futures
from datetime import datetime

from async_api.utils import helper
from async_api import logger

from facelib import api_func, utils
from config.settings import REDIS_CONFIG, MAX_DISPATCHER_WORKERS

import binascii

logger = logger.get_logger(__name__)


def process_api(request_id, request_msg):
    request = request_msg
    try:
        if request['api']=='face_search': # 人脸识别
            if request['user_id'] is None and request['mobile_tail']=='': # 1:N
                r = api_func.face_search(request_id, request['image'], request['group_id'], request['max_user_num'])
                # 准备结果
                result = { 'code' : 200, 'data' : { 'user_list' : r, 'request_id' : request_id } }

            elif request['user_id'] is None: # 双因素识别: 人脸+手机号后4位
                r = api_func.face_search_mobile_tail(request_id, request['image'], request['mobile_tail'], 
                        request['group_id'], request['max_user_num'])
                # 准备结果
                result = { 'code' : 200, 'data' : { 'user_list' : r, 'request_id' : request_id } }

            else: # 1:1 
                r = api_func.face_verify_db(request_id, request['image'], request['group_id'], request['user_id'])
                # 准备结果
                result = { 'code' : 200, 'data' : { 'is_match' : r[0], 'score' : r[1], 'request_id' : request_id } }

        elif request['api']=='face_verify': # 人脸验证
            r = api_func.face_verify(request['image1'], request['image2'])
            # 准备结果
            result = { 'code' : 200, 'data' : { 'is_match' : r[0], 'score' : r[1] } }

        elif request['api']=='face_locate': # 人脸定位
            r = api_func.face_locations(request['image'], request['max_face_num'])
            # 准备结果
            result = { 'code' : 200, 'data' : { 'face_num' : r[0], 'locations' : r[1] } }

        elif request['api']=='face_features': # 计算特征值,  不返回结果
            ret = api_func.face_features(request['image'], request['face_id'], request['group_id'], request['user_id'])
            if ret==False:
                logger.info('face_features 未检测到人脸: '+request['face_id'])
            # 准备结果
            result = { 'code' : 200, 'data' : {} }

        elif request['api']=='train_by_group': # 重新训练模型,  不返回结果
            utils.train_by_group(request['group_id'])
            result = { 'code' : 200, 'data' : {} }

        elif request['api']=='sync_test': # 测试
            time.sleep(random.random())
            result = { 'code' : 200, 'data' : { 'txt' : request['txt']+' world!' } }


        else: # 未知 api
            logger.error('Unknown api: '+request['api']) 

            result = { 'code' : 9900, 'msg' : '未知 api 调用'}

    except binascii.Error as e:
        logger.error("编码转换异常: %s" % e)
        result = { 'code' : 9901, 'msg' : 'base64编码异常: '+str(e)}

    except Exception as e:
        logger.error("未知异常: %s" % e, exc_info=True)
        result = { 'code' : 9998, 'msg' : '未知错误: '+str(e)}

    return result



def process_thread(msg_body):
    try:
        # for keras 2.3
        import keras.backend.tensorflow_backend as tb
        tb._SYMBOLIC_SCOPE.value = True

        logger.info('{} Calling api: {}'.format(msg_body['request_id'], msg_body['data'].get('api', 'Unknown'))) 

        start_time = datetime.now()

        api_result = process_api(msg_body['request_id'], msg_body['data'])

        logger.info('1 ===> [Time taken: {!s}]'.format(datetime.now() - start_time))
        
        # 发布redis消息
        helper.redis_publish(msg_body['request_id'], api_result)
        
        logger.info('{} {} [Time taken: {!s}]'.format(msg_body['request_id'], msg_body['data']['api'], datetime.now() - start_time))

        sys.stdout.flush()

    except Exception as e:
        logger.error("process_thread异常: %s" % e, exc_info=True)


if __name__ == '__main__':
    if len(sys.argv)<2:
        print("usage: dispatcher.py <QUEUE_NO.>")
        sys.exit(2)

    queue_no = sys.argv[1]

    print('Request queue NO. ', queue_no)

    sys.stdout.flush()

    while 1:
        # redis queue
        ps = helper.redis_subscribe(REDIS_CONFIG['REQUEST-QUEUE']+queue_no)

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_DISPATCHER_WORKERS) # 建议与cpu核数相同

        for item in ps.listen():        #监听状态：有消息发布了就拿过来
            logger.info('reveived: type=%s running=%d pending=%d'% \
                (item['type'], len(executor._threads), executor._work_queue.qsize())) 
            if item['type'] == 'message':
                #print(item)
                msg_body = json.loads(item['data'].decode('utf-8'))

                future = executor.submit(process_thread, msg_body)
                logger.info('Thread future: '+str(future)) 

                sys.stdout.flush()
