# -*- coding: utf-8 -*-`

import os
#from datetime import datetime
import numpy as np
from facelib import utils
from facelib.dbport import user_info, user_face_list, face_info, face_update, user_list_by_group
from config.settings import ALGORITHM

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
    is_match, score = verify.verify_vgg.is_match_b64(b64_data1, b64_data2)
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
    is_match, score = verify.verify_vgg.is_match_b64_2(face_encodings, b64_data)
    if type(score)!=type([]):
        score = score.tolist() # np.array
    return is_match, score


# 人脸搜索， face_algorithm 取值： 'parallel' , 'vgg', 'evo'
def face_search(b64_data, group_id='DEFAULT', max_user_num=5, face_algorithm='parallel'):
    # 最多返回5个相似用户
    max_user_num = min(5, max_user_num)

    if face_algorithm=='parallel':
        predictions = predict_parallel(predict_thread_db, b64_data, group_id)
    elif face_algorithm in ('evo', 'vgg'):
        predictions = predict(b64_data, group_id,
            model_path=TRAINED_MODEL_PATH,
            distance_threshold=ALGORITHM[face_algorithm]['distance_threshold'],
            face_algorithm=face_algorithm)
    else:
        return []

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
def face_features(b64_data, face_id, group_id):
    encodings_result = {'vgg':{}, 'evo':{}}
    face_image = []

    # 保存特征值：1. 原始，2. 水平后镜像
    for angle in [None, 360]:
        encodings, boxes, face_list = verify.get_features_b64(b64_data, angle)
        if len(boxes)==0: # 未检测到人脸
            return False

        encodings_result['vgg'][str(angle)] = encodings['vgg'].tolist()
        encodings_result['evo'][str(angle)] = encodings['evo'].tolist()

        if angle==None:
            face_image = np.uint8(face_list[0]).tolist()

    # 更新数据库：特征值、人脸图片
    r = face_update(face_id, encodings=encodings_result, image=face_image)

    # 重新训练模型
    r2 = user_list_by_group(group_id)
    if len(r2)>0: 
        # 重新训练模型, 至少需要1个用户
        utils.train_by_group(group_id)

    return r


