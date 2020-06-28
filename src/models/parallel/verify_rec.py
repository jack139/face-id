# -*- coding: utf-8 -*-

from datetime import datetime
import cv2
from PIL import Image
import numpy as np
import concurrent.futures
import face_recognition
from config.settings import ALGORITHM

# 双算法： vggface + face-rec
from models.vggface import verify as verify_vgg
from models.face_rec import verify as verify_rec


def get_features_b64_thread(face_algorithm, b64_data):
    start_time = datetime.now()
    # https://discuss.streamlit.io/t/attributeerror-thread-local-object-has-no-attribute-value/574/3
    #import keras.backend.tensorflow_backend as tb
    #tb._SYMBOLIC_SCOPE.value = True

    if face_algorithm=='vgg':
        encoding_list, face_boxes = verify_vgg.get_features_b64(b64_data)
    else:
        encoding_list, face_boxes = verify_rec.get_features_b64(b64_data)
    print('[{} - Time taken: {!s}]'.format(face_algorithm, datetime.now() - start_time))
    return encoding_list, face_boxes


# 比较两个人脸是否同一人 --------- 不会被knn_db调用, 多线程实现 获取特征值
def is_match_b64(b64_data1, b64_data2):
    results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_list = [
            executor.submit(get_features_b64_thread, 'vgg', b64_data1), # 0
            executor.submit(get_features_b64_thread, 'rec', b64_data1), # 1
            executor.submit(get_features_b64_thread, 'vgg', b64_data2), # 2
            executor.submit(get_features_b64_thread, 'rec', b64_data2), # 3
        ]
        for future in concurrent.futures.as_completed(future_list):
            pos = future_list.index(future)
            results[pos] = future.result()

    if len(results[0][1])==0 or len(results[2][1])==0:
        return False, [999]

    distance_vgg = face_distance([results[0][0][0]], results[2][0][0])
    if distance_vgg <= ALGORITHM['vgg']['distance_threshold']:
        return True, distance_vgg/ALGORITHM['vgg']['distance_threshold']

    distance_rec = face_distance([results[1][0][0]], results[3][0][0])
    if distance_rec <= ALGORITHM['rec']['distance_threshold']:
        return True, distance_rec/ALGORITHM['rec']['distance_threshold']

    # 均为匹配
    return False, distance_vgg/ALGORITHM['vgg']['distance_threshold'] # 只返回 vgg 结果


# 定位人脸，然后人脸的特征值列表，可能不止一个脸, 只取最大的一个脸(第1个脸)
def get_features_b64(b64_data):
    encoding_list1, face_boxes1 = verify_vgg.get_features_b64(b64_data)
    encoding_list2, face_boxes2 = verify_rec.get_features_b64(b64_data)

    if len(face_boxes1) == 0:
        return [], []
    else:
        # 返回4个，第2个位置留给evo，第4个留给deep，保持一直， 2020-06-23
        return [encoding_list1[0], [], encoding_list2[0], []], face_boxes1


# 特征值距离
def face_distance(face_encodings, face_to_compare):
    return face_recognition.face_distance(np.array(face_encodings), np.array(face_to_compare))


# 比较两个人脸是否同一人，--------- 顺序执行
def is_match_b64_serial(b64_data1, b64_data2):
    start_time = datetime.now()
    # calculate distance between embeddings
    encoding_list1, face_boxes1 = get_features_b64(b64_data1)
    encoding_list2, face_boxes2 = get_features_b64(b64_data2)

    print('[Time taken: {!s}]'.format(datetime.now() - start_time))

    if len(face_boxes1)==0 or len(face_boxes2)==0:
        return False, [999]

    distance_vgg = face_distance([encoding_list1[0]], encoding_list2[0])
    if distance_vgg <= ALGORITHM['vgg']['distance_threshold']:
        return True, distance_vgg

    distance_rec = face_distance([encoding_list1[1]], encoding_list2[1])
    if distance_rec <= ALGORITHM['rec']['distance_threshold']:
        return True, distance_rec

    # 均为匹配
    return False, distance_vgg # 只返回 vgg 结果


# 比较两个人脸是否同一人, encoding_list1来自已知db用户, 多对1, db里可能有多个脸，base64只取一个脸， 多线程处理
def is_match_b64_2(encoding_list_db, b64_data):
    encoding_list1 = [[], []]  # [ vgg, rec ]
    for i in range(len(encoding_list_db)):
        encoding_list1[0].append(encoding_list_db[i][0]) # vgg index=0
        encoding_list1[1].append(encoding_list_db[i][2]) # rec index=2  2020-06-23

    # calculate distance between embeddings
    #encoding_list2, face_boxes = get_features_b64(b64_data)
    #if len(face_boxes)==0:
    #    return False, [999]

    results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_list = [
            executor.submit(get_features_b64_thread, 'vgg', b64_data), # 0
            executor.submit(get_features_b64_thread, 'rec', b64_data), # 1
        ]
        for future in concurrent.futures.as_completed(future_list):
            pos = future_list.index(future)
            results[pos] = future.result()

    if len(results[0][1])==0:
        return False, [999]

    distance_vgg = face_distance(encoding_list1[0], results[0][0][0])
    x = distance_vgg <= ALGORITHM['vgg']['distance_threshold']
    if x.any():
        return True, distance_vgg/ALGORITHM['vgg']['distance_threshold']

    distance_rec = face_distance(encoding_list1[1], results[1][0][0])
    x = distance_rec <= ALGORITHM['rec']['distance_threshold']
    if x.any():
        return True, distance_rec/ALGORITHM['rec']['distance_threshold']

    # 均未匹配
    return False, distance_vgg/ALGORITHM['vgg']['distance_threshold'] # 只返回 vgg 结果
