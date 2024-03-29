# coding:utf-8

import sys, time, os, shutil, json, random, hashlib
import threading
import functools

import redis

from config.settings import REDIS_CONFIG
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

# 生成request_id
def gen_request_id():
    return '%s%s'%(time_str(format=3)[2:],hashlib.md5(ranstr(10).encode('utf-8')).hexdigest())

# redis订阅
def redis_subscribe(queue_id):
    rc = redis.StrictRedis(host=REDIS_CONFIG['SERVER'], 
            port=REDIS_CONFIG['PORT'], db=1, password=REDIS_CONFIG['PASSWD'])
    ps = rc.pubsub()
    ps.subscribe(queue_id)  #从liao订阅消息
    logger.info('subscribe to : '+str((queue_id))) 
    return ps


# 从订阅接收, 值收一条
def redis_sub_receive(pubsub, queue_id):
    #for item in pubsub.listen():        #监听状态：有消息发布了就拿过来
    #    logger.debug('subscribe 2: '+str((queue_id, item))) 
    #    if item['type'] == 'message':
    #        #print(item)
    #        break

    start = time.time()
    while 1:
        item = pubsub.get_message()
        if item:
            logger.info('reveived: type='+item['type']) 
            if item['type'] == 'message':
                break

        # 检查超时
        if time.time()-start > REDIS_CONFIG['MESSAGE_TIMEOUT']:
            item = { 'data' : json.dumps({"code": 9997, 'data': {"msg": "消息队列超时"}}).encode('utf-8') }
            break

        # 释放cpu
        time.sleep(0.001)

    return item


# redis发布
def redis_publish(queue_id, data):
    logger.info('publish: '+queue_id) 

    if queue_id=='NO_RECIEVER': # 无接收的消息，不发送
        return None

    msg_body = json.dumps(data)

    rc = redis.StrictRedis(host=REDIS_CONFIG['SERVER'], 
            port=REDIS_CONFIG['PORT'], db=1, password=REDIS_CONFIG['PASSWD'])
    return rc.publish(queue_id, msg_body)


# 返回　请求队列　随机id
def choose_queue_redis():
    # 随机返回
    return random.randint(1, REDIS_CONFIG['REQUEST-QUEUE-NUM'])

# redis发布到请求队列
def redis_publish_request(request_id, data):
    msg_body = {
        'request_id' : request_id, # request id
        'data' : data,
    }

    # 设置发送的queue
    queue = REDIS_CONFIG['REQUEST-QUEUE']+str(choose_queue_redis())
    print('queue:', queue)

    return redis_publish(queue, msg_body)
