# coding:utf-8

import sys, time, os, shutil, json
import threading
import functools

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
#import redis

from config.settings import MAX_MESSAGE_SIZE, MESSAGE_TIMEOUT
from .. import logger

logger = logger.get_logger(__name__)


# 检查文件类型是否可接受上传
ALLOWED_EXTENSIONS = [
    set(['jpg', 'jpeg', 'png']), # 图片文件
]
def allowed_file(filename, category=0):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS[category]


# 按格式输出时间字符串
ISOTIMEFORMAT=['%Y-%m-%d %X', '%Y-%m-%d', '%Y%m%d', '%Y%m%d%H%M%S']
def time_str(t=None, format=0):
    return time.strftime(ISOTIMEFORMAT[format], time.localtime(t))


###### about token

# 检查token修饰器
def token_required(view_func):
    from config.settings import SECRET_KEY
    
    @functools.wraps(view_func)
    def verify_token(*args,**kwargs):
        return view_func(*args,**kwargs)  ## 测试时，关闭token校验

        from flask_restful import request
        from itsdangerous.exc import BadSignature, SignatureExpired
        from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

        try:
            #在请求头上拿到token
            #print(request.headers)
            token = request.headers["faceid-token"]
        except Exception as e:
            #没接收的到token
            logger.error("verify_token: 异常: %s" % e.message) 
            return {'code': 9998, 'msg' : '缺少token' }
        
        token_pass = False
        for secret in SECRET_KEY.values():
            s = Serializer(secret)
            try:
                data = s.loads(token)
                logger.info("verify_token: login: %s %s"%(data['appid'],data['remote_addr']))
                if request.remote_addr!=data['remote_addr']: # 核对 remote_addr
                    logger.error("verify_token: 客户端ip异常")
                    return {'code': 9994, 'msg' : '客户端ip异常' }      
                token_pass = True
                break
            except SignatureExpired:
                # token 过期
                logger.error("verify_token: token过期")
                return {'code': 9997, 'msg' : 'token已过期' }
            except BadSignature:
                # secret不对，尝试下一个, 适应SECRET_KEY有多个私钥的情况
                #logger.warning("verify_token: BadSignature")
                continue
            except Exception as e:
                logger.error("verify_token: 异常: %s" % e.message) 
                return {'code': 9996, 'msg' : '其它异常' }
        if token_pass:
            return view_func(*args,**kwargs)
        else:
            logger.error("verify_token: 无效token") 
            return {'code': 9995, 'msg' : '无效token' }            

    return verify_token


########## 异步接口调用




# 向kafka发消息
def kafka_send_msg(request_id, data):
    msg_body = {
        'request_id' : request_id, # request id
        'data' : data,
    }
    #msg_body = json.dumps(msg_body).encode('utf-8')

    logger.info('send to kafka: ' + request_id) 

    producer = KafkaProducer(bootstrap_servers=['localhost:9092'], 
        value_serializer = lambda v: json.dumps(v).encode('utf-8'),
        max_request_size=MAX_MESSAGE_SIZE)

    future = producer.send('synchronous-asynchronous-queue', msg_body)

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

    logger.info('send RETURN to kafka: ' + request_id) 

    producer = KafkaProducer(bootstrap_servers=['localhost:9092'], 
        value_serializer = lambda v: json.dumps(v).encode('utf-8'),
        max_request_size=MAX_MESSAGE_SIZE)

    future = producer.send('synchronous-asynchronous-return', msg_body)

    # Block for 'synchronous' sends
    try:
        record_metadata = future.get(timeout=10)
    except KafkaError as e:
        # Decide what to do if produce request failed...
        logger.error("send RETURN to Kafka FAIL: %s"%e) 
        return None

    return record_metadata


# 返回kafka消费者
def kafka_get_return_consumer():
    return KafkaConsumer('synchronous-asynchronous-return', bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')), 
        # auto_offset_reset='earliest',
        consumer_timeout_ms=MESSAGE_TIMEOUT, # 超时返回错误结果
        fetch_max_bytes=MAX_MESSAGE_SIZE)


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

