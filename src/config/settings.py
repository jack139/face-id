# -*- coding: utf-8 -*-
from pymongo import MongoClient


############ mongodb 设置
db_serv_list='172.17.0.1'
# db_serv_list='mongodb://10.168.11.151:27017,10.252.95.145:27017,10.252.171.8:27017/?replicaSet=rs0'

cli = {
    'web' : MongoClient(db_serv_list),
}
# MongoClient('10.168.11.151', replicaset='rs0', readPreference='secondaryPreferred') # 使用secondary 读
# MongoClient('mongodb://10.168.11.151:27017,10.252.95.145:27017,10.252.171.8:27017/?replicaSet=rs0')

db_web = cli['web']['face_db']
db_web.authenticate('ipcam','ipcam')

db_primary = db_web

############# 算法相关设置

'''
                        train2  train3  train8  train9
    rec                 0.43    0.58    0.38    0.52
    vgg     senet50     0.79    0.92    0.73    0.85
    vgg     resnet50    0.86    0.99
    evo     ir152       1.15    1.22
    evo     bh-ir50     1.12    1.14
    plus                1.45    1.56
    fnet                0.78    1.0
    deep                0.84    1.03
'''
ALGORITHM = {
    'rec'   : { 'index': 2, 'distance_threshold' : 0.58, 'ext' : '.rec.clf',  'module' : 'models.face_rec.verify' },  # 0.6,
    'vgg'   : { 'index': 0, 'distance_threshold' : 0.92, 'ext' : '.vgg.clf',  'module' : 'models.vggface.verify' },   # 0.86
    'evo'   : { 'index': 1, 'distance_threshold' : 1.22, 'ext' : '.evo.clf',  'module' : 'models.face_evoLVe.verify' },  # 1.2,
    'plus'  : { 'index': 5, 'distance_threshold' : 1.45, 'ext' : '.plus.clf', 'module' : 'models.verify_plus' },  # 1.4,
    'fnet'  : { 'index': 4, 'distance_threshold' : 0.78, 'ext' : '.fnet.clf', 'module' : 'models.facenet.verify' },  # 0.9,
    'deep'  : { 'index': 3, 'distance_threshold' : 1.03, 'ext' : '.deep.clf', 'module' : 'models.deepface.verify' },  # 0.9,
}

# 并行算法设置
algorithm_settings = {
    1 : [ 'vgg', '../data/model/train2_senet.vgg.clf' ], # 优先返回
    #2 : [ 'evo', '../data/model/train2_ir152.evo.clf' ],
    2 : [ 'deep', '../data/model/train2.deep.clf' ],
    #2 : [ 'rec', '../data/model/train2.rec.clf' ],
}

# 特征值训练模型保存路径
TRAINED_MODEL_PATH = '../data/model'

# face.evoLVe 模型l路径
#EVO_MODEL_BASE = '/opt/data/face_model/face.evoLVe.PyTorch/'
EVO_MODEL_BASE = '/home/gt/Codes/yhtech/face_model/face.evoLVe.PyTorch/'

# faceNET 模型l路径
#FACENET_MODEL_BASE = '/opt/data/face_model/20180402-114759/'
FACENET_MODEL_BASE = '/home/gt/Codes/yhtech/face_model/20180402-114759/'

############  app server 相关设置

APP_NAME = 'face-id'
APP_NAME_FORMATED = 'Face-ID'

# 参数设置
DEBUG_MODE = False
BIND_ADDR = '0.0.0.0'
BIND_PORT = '5000'


# dispatcher 中 最大线程数
MAX_DISPATCHER_WORKERS = 8



############# appid - 私钥

SECRET_KEY = {
    'THISISTEST' : 'F9OAZ4nbxYmz8NkLKJwivR5ZUasmePq7sL27v5HvHpY3wSHo',
    'uScwXmfq0S' : 'MeBYr9HDqxhXxrJ6yw7fmOL0S2gwpsbOMDOK4kUYSlwgqOlj',
    'HRdxkDxMls' : 'hSZ45OB44dLoNmgW7A8iuR5i8Ui7rRB2y54AKXuM5FVBDAvv',
    'Xl5Bp9Y5g9' : 'Ne9GO9IQT0gkJkVpN9TZGIupZlHkoVxT8zKqTmKT7HTJvdzV',
}


############# 消息中间件设置

KAFKA_CONFIG = {
    'SERVER' : ['172.17.0.1:9092'],
    'REQUEST-QUEUE' : 'synchronous-asynchronous-queue',
    'REQUEST-QUEUE-NUM' : 1,
    'RETURN-QUEUE' : 'synchronous-asynchronous-return',
    'MESSAGE_TIMEOUT' : 10000, # 结果返回消息超时，单位：毫秒
    'MAX_MESSAGE_SIZE' : 5242880,  # 消息最大尺寸 5MB
}

# 图片数据最大尺寸
MAX_IMAGE_SIZE = 2097152  # 2MB
