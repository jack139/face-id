# -*- coding: utf-8 -*-

from importlib import import_module

ALGORITHM = {
    'rec'   : { 'index': 2, 'distance_threshold' : 0.6,  'ext' : '.rec.clf',  'module' : 'models.face_rec.verify' },
    'vgg'   : { 'index': 0, 'distance_threshold' : 0.8,  'ext' : '.vgg.clf',  'module' : 'models.vggface.verify' },
    'evo'   : { 'index': 1, 'distance_threshold' : 1.25, 'ext' : '.evo.clf',  'module' : 'models.face_evoLVe.verify' },
    'plus'  : { 'index': 3, 'distance_threshold' : 1.4,  'ext' : '.plus.clf', 'module' : 'models.verify_plus' },
}

# 并行算法设置
algorithm_settings = {
    1 : [ 'vgg', 'data/model/train9.vgg.clf' ], # 优先返回
    2 : [ 'evo', 'data/model/train9.evo.clf' ],
    #1 : [ 'rec', 'data/model/train.rec.clf' ],
    #2 : [ 'vgg', 'data/model/train_senet50.vgg.clf' ],
}

def import_verify(face_algorithm):
    module = import_module(ALGORITHM[face_algorithm]['module'])
    #print('imported: ', module)
    return module
