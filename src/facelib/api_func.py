# -*- coding: utf-8 -*-`

import os
#from datetime import datetime
from facelib import utils
from facelib.dbport import user_info, user_face_list, face_info
from config.settings import ALGORITHM, TRAINED_MODEL_PATH

#FACE_MODEL = 'para'
#
#if FACE_MODEL=='vgg':
#    from models.vggface import verify
#elif FACE_MODEL=='evo':
#    from models.face_evoLVe import verify
#else:
#    from models.parallel import verify

from models.parallel import verify
from models.predict_plus import predict_parallel, predict_thread_db
from models.knn_db import predict

# 人脸定位
def face_locations(b64_data, max_face_num=1):
    #start_time = datetime.now()
    face_bounding_boxes = utils.face_locations_b64(b64_data) # (top, right, bottom, left)
    face_num = min(len(face_bounding_boxes), max_face_num)
    #print('[Time taken: {!s}]'.format(datetime.now() - start_time))
    return face_num, face_bounding_boxes[:face_num]


# 人脸对比
def face_verify(b64_data1, b64_data2):
    #start_time = datetime.now()
    is_match, score = verify.is_match_b64(b64_data1, b64_data2)
    #print('[Time taken: {!s}]'.format(datetime.now() - start_time))
    if type(score)!=type([]):
        score = score.tolist() # np.array
    return is_match, score


# 人脸对比, 使用特征库人脸
def face_verify_db(b64_data, group_id, user_id):
    # 获取已知用户的特征数据
    face_list = user_face_list(group_id, user_id)
    if face_list==-1: # user_id 不存在
        return None, -1
    face_encodings = [face_info(i)['encodings'] for i in face_list]
    # 进行比较验证
    #start_time = datetime.now()
    is_match, score = verify.is_match_b64_2(face_encodings, b64_data)
    #print('[Time taken: {!s}]'.format(datetime.now() - start_time))
    if type(score)!=type([]):
        score = score.tolist() # np.array
    return is_match, score


# 人脸搜索， face_algorithm 取值： 'parallel' , 'vgg', 'evo'
def face_search(b64_data, group_id='DEFAULT', max_user_num=5, face_algorithm='parallel'):
    # 最多返回5个相似用户
    max_user_num = min(5, max_user_num)

    #start_time = datetime.now()
    if face_algorithm=='parallel':
        predictions = predict_parallel(predict_thread_db, b64_data, group_id)
    elif face_algorithm in ('evo', 'vgg'):
        predictions = predict(b64_data, group_id,
            model_path=TRAINED_MODEL_PATH,
            distance_threshold=ALGORITHM[face_algorithm]['distance_threshold'],
            face_algorithm=face_algorithm)
    else:
        return []
    #print('[Time taken: {!s}]'.format(datetime.now() - start_time))

    #print(predictions)

    if len(predictions)==0 or predictions[0][0]=='unknown':
        # 未识别
        return []

    # 准备返回结果
    user_list = []
    for i in range(min(max_user_num, len(predictions))):
        user_id, box, score, _ = predictions[i]
        info = user_info(group_id, user_id)
        user_list.append({
            'user_id'     : user_id,
            'mobile_tail' : info['mobile'][:-4], # 手机后4位
            'name'        : info['name'], # 用户姓名
            'location'    : box,
            'score'       : score,
        })

    return user_list


# 计算特征值
def face_features(b64_data):
    #start_time = datetime.now()
    encodings, boxes = verify.get_features_b64(b64_data)
    encodings = [i.tolist() if type(i)!=type([]) else i for i in encodings]
    #print('[Time taken: {!s}]'.format(datetime.now() - start_time))
    return encodings, boxes



