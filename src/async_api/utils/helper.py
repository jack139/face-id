# coding:utf-8

import sys, time, os, shutil, json, random, hashlib
import threading
import functools

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
#import redis

from config.settings import KAFKA_CONFIG
from .. import logger

logger = logger.get_logger(__name__)


# 检查文件类型是否可接受上传
ALLOWED_EXTENSIONS = [
    set(['jpg', 'jpeg', 'png']), # 图片文件
]
def allowed_file(filename, category=0):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS[category]

# 返回指定长度的随机字符串
def ranstr(num):
    H = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    salt = ''
    for i in range(num):
        salt += random.choice(H)
    return salt

# 按格式输出时间字符串
ISOTIMEFORMAT=['%Y-%m-%d %X', '%Y-%m-%d', '%Y%m%d', '%Y%m%d%H%M%S']
def time_str(t=None, format=0):
    return time.strftime(ISOTIMEFORMAT[format], time.localtime(t))


###### about 签名

# 生成参数字符串
def gen_param_str(param):
    name_list = sorted(param.keys())
    return ''.join([str(param[i]) for i in name_list])


# 检查signature修饰器
def signature_required(view_func):
    from config.settings import SECRET_KEY, DEBUG_MODE
    
    @functools.wraps(view_func)
    def verify_signature(*args,**kwargs):
        if DEBUG_MODE:
            return view_func(*args,**kwargs)  ## !!!!!!!!!!!!!!!!!!!!!!!! 测试时，关闭签名校验

        from flask_restful import request

        try:
            # 获取入参
            body_data = request.get_data().decode('utf-8') # bytes to str
            json_data = json.loads(body_data)

            #print(json_data)

            appid = json_data['appid']
            unixtime = json_data['unixtime']
            signature = json_data['signature']

            # 调用时间不能超过前后5分钟
            if abs(int(time.time())-int(unixtime))>300:
                logger.error("verify_signature: 调用时间错误") 
                return {'code': 9802, 'msg' : '调用时间错误' }

            # 三个固定参数不参与计算参数字符串
            json_data.pop('appid')
            json_data.pop('unixtime')
            json_data.pop('signature')

            # 获取私钥
            secret = SECRET_KEY[appid]

        except Exception as e:
            logger.error("verify_signature: 异常: %s : %s" % (e.__class__.__name__, e))
            return {'code': 9801, 'msg' : '签名参数有错误' }

        # 生成参数字符串
        param_str = gen_param_str(json_data)

        sign_str = '%s%s%s%s' % (appid, str(unixtime), secret, param_str)
        signature_str =  hashlib.sha256(sign_str.encode('utf-8')).hexdigest().upper()
        #print(signature_str, signature)

        if signature==signature_str:
            return view_func(*args,**kwargs)
        else:
            logger.error("verify_signature: 无效signature") 
            return {'code': 9800, 'msg' : '无效签名' }            

    return verify_signature


########## 异步接口调用

# 返回　请求队列　随机id
def choose_queue():
    # 随机返回
    return random.randint(1, KAFKA_CONFIG['REQUEST-QUEUE-NUM'])

# 向kafka发消息
def kafka_send_msg(request_id, data):
    msg_body = {
        'request_id' : request_id, # request id
        'data' : data,
    }
    #msg_body = json.dumps(msg_body).encode('utf-8')

    logger.info('send to kafka: ' + request_id) 

    producer = KafkaProducer(bootstrap_servers=KAFKA_CONFIG['SERVER'], 
        value_serializer = lambda v: json.dumps(v).encode('utf-8'),
        max_request_size=KAFKA_CONFIG['MAX_MESSAGE_SIZE'])

    # 设置发送的queue
    queue = KAFKA_CONFIG['REQUEST-QUEUE']+str(choose_queue())
    print('queue:', queue)

    future = producer.send(queue, msg_body)

    # Block for 'synchronous' sends
    try:
        record_metadata = future.get(timeout=10)
    except KafkaError as e:
        # Decide what to do if produce request failed...
        logger.error("send Kafka message fail: %s"%e) 
        return None

    return record_metadata



# redis订阅
def redis_subscribe(request_id):
    rc = redis.StrictRedis(host='localhost', port='6379', db=1, password=None)
    ps = rc.pubsub()
    ps.subscribe(request_id)  #从liao订阅消息
    logger.info('subscribe to : '+str((request_id))) 
    for item in ps.listen():        #监听状态：有消息发布了就拿过来
        logger.debug('subscribe 2: '+str((request_id, item))) 
        if item['type'] == 'message':
            #print(item)
            logger.info('subscribe: '+request_id) 
            break
    return item

# redis发布
def redis_publish(request_id, data):
    msg_body = json.dumps(data)

    rc = redis.StrictRedis(host='localhost', port='6379', db=1, password=None)
    rc.publish(request_id, msg_body)
    logger.info('publish: '+request_id) 



# 向kafka发返回结果
def kafka_send_return(request_id, data):
    msg_body = {
        'request_id' : request_id, # request id
        'data' : data,
    }
    #msg_body = json.dumps(msg_body).encode('utf-8')

    #logger.info(data) 

    producer = KafkaProducer(bootstrap_servers=KAFKA_CONFIG['SERVER'], 
        value_serializer = lambda v: json.dumps(v).encode('utf-8'),
        max_request_size=KAFKA_CONFIG['MAX_MESSAGE_SIZE'])

    future = producer.send(KAFKA_CONFIG['RETURN-QUEUE'], msg_body)

    # Block for 'synchronous' sends
    try:
        record_metadata = future.get(timeout=10)
        logger.info('sent RETURN to kafka: ' + request_id) 
    except KafkaError as e:
        # Decide what to do if produce request failed...
        logger.error("send RETURN to Kafka FAIL: %s"%e) 
        return None

    return record_metadata


# 返回kafka消费者
def kafka_get_return_consumer():
    return KafkaConsumer(KAFKA_CONFIG['RETURN-QUEUE'], bootstrap_servers=KAFKA_CONFIG['SERVER'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')), 
        # auto_offset_reset='earliest',
        consumer_timeout_ms=KAFKA_CONFIG['MESSAGE_TIMEOUT'], # 超时返回错误结果
        fetch_max_bytes=KAFKA_CONFIG['MAX_MESSAGE_SIZE'])


# 从kafka取返回结果
def kafka_recieve_return(consumer, request_id):
    # To consume latest messages and auto-commit offsets
    message_list = []
    msg_body = {
        'request_id' : request_id,
        'data'       : {"code": 9997, "msg": "消息队列超时"},
    }   
    for message in consumer:
        # message value and key are raw bytes -- decode if necessary
        msg_body = message.value

        if msg_body['request_id'] == request_id:
            break

        #logger.info('kafka RETURN recieved: ' + msg_body['request_id'])

    return msg_body


# 生成request_id
def gen_request_id():
    return '%s%s'%(time_str(format=3)[2:],hashlib.md5(ranstr(10).encode('utf-8')).hexdigest())
