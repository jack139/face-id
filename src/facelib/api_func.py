# -*- coding: utf-8 -*-`

import os
#from datetime import datetime
import numpy as np
from facelib import utils
from facelib.dbport import user_info, user_face_list, face_info, face_update, \
    user_list_by_group, user_list_by_mobile_tail, face_save_to_temp, user_update
from config.settings import ALGORITHM, IMPORT_ANGLE

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
def face_verify_db(request_id, b64_data, group_id, user_id):
    # 获取已知用户的特征数据
    face_list = user_face_list(group_id, user_id)
    if face_list==-1: # user_id 不存在
        return None, -1
    face_encodings = [face_info(i)['encodings'] for i in face_list]
    # 进行比较验证
    is_match, score, face_array = verify.verify_vgg.is_match_b64_2(face_encodings, b64_data)
    if type(score)!=type([]):
        score = score.tolist() # np.array

    # 只记录结果正确的人脸数据，用于后面数据增强
    if is_match>0:
        face_image = np.uint8(face_array[0]).tolist()
        face_save_to_temp(group_id, request_id, 'face_verify_db', [user_id], face_image)

    return is_match, score


# 人脸搜索
def face_search(request_id, b64_data, group_id='DEFAULT', max_user_num=5):
    # 最多返回5个相似用户
    max_user_num = min(5, max_user_num)

    # 先使用knn分类器搜索（临时特征库）
    predictions = predict_parallel(predict_thread_db, b64_data, group_id, 
            request_id=request_id, classifier='knn')
    # 如果未找到，再使用深度网络分类器（全量特征库）
    if len(predictions)==0 or predictions[0][0]=='unknown':
        print('search using keras classifier')
        predictions = predict_parallel(predict_thread_db, b64_data, group_id, 
                request_id=request_id, classifier='keras')
        # 如果仍未识别，返回空
        if len(predictions)==0 or predictions[0][0]=='unknown':
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

    # 只记录有结果的人脸数据，用于后面数据增强, 图片在预测时已保存
    if len(user_list)>0:
        face_save_to_temp(group_id, request_id, 'face_search', user_list)

    return user_list


# 计算特征值
def face_features(b64_data, face_id, group_id, user_id):
    encodings_result = {'vgg':{}, 'evo':{}}
    face_image = []

    # 保存特征值：1. 原始，2. 水平后镜像
    for angle in IMPORT_ANGLE:
        encodings, boxes, face_list = verify.get_features_b64(b64_data, angle)
        if len(boxes)==0: # 未检测到人脸
            return False

        encodings_result['vgg'][str(angle)] = encodings['vgg'].tolist()
        encodings_result['evo'][str(angle)] = encodings['evo'].tolist()

        if angle==None:
            face_image = np.uint8(face_list[0]).tolist()

    # 更新数据库：特征值、人脸图片
    r = face_update(face_id, encodings=encodings_result, image=face_image)
    r3 = user_update(group_id, user_id, need_train=1) # 标记需要重新训练

    # 重新训练模型: TODO： 需要修改为集中训练，在这可能会频繁训练！！！
    utils.train_by_group(group_id)

    return r


# 双因素识别：人脸+手机号后4位 
def face_search_mobile_tail(request_id, b64_data, mobile_tail, group_id='DEFAULT', max_user_num=5):
    # 获取手机尾号的用户列表
    user_list = user_list_by_mobile_tail(mobile_tail, group_id)

    # 获取已知用户的特征数据
    face_X = []
    face_y = []
    user_dict = {}
    for user in user_list:
        user_dict[user['user_id']] = user
        face_list = user_face_list(group_id, user['user_id'])
        if face_list==-1: # user_id 不存在
            continue

        for x in face_list:
            ec = face_info(x)['encodings']['vgg'].values()
            face_X.extend(ec)
            face_y.extend([user['user_id']]*len(ec))

    # 进行识别: 与给定的用户人脸进行比较
    r, face_boxes, face_array = verify.verify_vgg.is_match_b64_3((face_X, face_y), b64_data)

    user_list = []
    for i in r[:max_user_num]:
        user_id = i[0]
        user_list.append({
            'user_id'     : user_id,
            'mobile_tail' : mobile_tail, # 手机后4位
            'name'        : user_dict[user_id]['name'], # 用户姓名
            'location'    : face_boxes,
            'score'       : i[1], # 距离
        })

    # 只记录有结果的人脸数据，用于后面数据增强
    if len(user_list)>0:
        face_image = np.uint8(face_array[0]).tolist()
        face_save_to_temp(group_id, request_id, 'face_search_mobile_tail', user_list, face_image)

    return user_list
