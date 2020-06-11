# -*- coding: utf-8 -*-
from pymongo import MongoClient

#####
debug_mode = True   # Flase - production, True - staging
#####



############ mongodb 设置
db_serv_list='127.0.0.1'
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


ALGORITHM = {
    'rec'   : { 'index': 2, 'distance_threshold' : 0.6, 'ext' : '.rec.clf',  'module' : 'models.face_rec.verify' },
    'vgg'   : { 'index': 0, 'distance_threshold' : 0.8, 'ext' : '.vgg.clf',  'module' : 'models.vggface.verify' },
    'evo'   : { 'index': 1, 'distance_threshold' : 1.2, 'ext' : '.evo.clf',  'module' : 'models.face_evoLVe.verify' },
    'plus'  : { 'index': 3, 'distance_threshold' : 1.4, 'ext' : '.plus.clf', 'module' : 'models.verify_plus' },
}

# 并行算法设置
algorithm_settings = {
    1 : [ 'vgg', '../data/model/train9.vgg.clf' ], # 优先返回
    2 : [ 'evo', '../data/model/train9.evo.clf' ],
    #1 : [ 'rec', 'data/model/train2.rec.clf' ],
    #2 : [ 'vgg', 'data/model/train2_senet50.vgg.clf' ],
    #1 : [ 'rec', 'data/model/train2.rec.clf' ],
    #2 : [ 'evo', 'data/model/train2_5.evo.clf' ],
}

# 特征值训练模型保存路径
TRAINED_MODEL_PATH = '../data/model'

# face.evoLVe 模型l路径
EVO_MODEL_BASE = '/home/gt/Codes/yhtech/face_model/face.evoLVe.PyTorch/'

############  app server 相关设置

APP_NAME = 'face-id'
APP_NAME_FORMATED = 'Face-ID'

# 私钥
SECRET_KEY = {
    'localhost' : 'V4cCI6MTU4NTAzNDcxMCwiaWF0IjoxNTg1MDMxMT',
} 

# 参数设置
DEBUG_MODE = False
BIND_ADDR = '127.0.0.1'
BIND_PORT = '5000'


# 消息最大尺寸
MAX_MESSAGE_SIZE = 5242880  # 5MB
# 图片数据最大尺寸
MAX_IMAGE_SIZE = 2097152  # 2MB

# dispatcher 中 最大线程数
MAX_DISPATCHER_WORKERS = 8

# 结果返回消息超时，单位：毫秒
MESSAGE_TIMEOUT = 10000
