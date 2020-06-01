# -*- coding: utf-8 -*-

import cv2
from PIL import Image
import numpy as np
import face_recognition
from config.settings import ALGORITHM

# 双算法： vggface + evoLVe
from models.vggface import verify as verify_vgg
from models.face_evoLVe import verify as verify_evo


# 定位人脸，然后人脸的特征值列表，可能不止一个脸, 只取最大的一个脸(第1个脸)
def get_features_b64(b64_data):
    encoding_list1, face_boxes1 = verify_vgg.get_features_b64(b64_data)
    encoding_list2, face_boxes2 = verify_evo.get_features_b64(b64_data)

    if len(face_boxes1) == 0:
        return [], []
    else:
        return [encoding_list1[0], encoding_list2[0]], face_boxes1


# 特征值距离
def face_distance(face_encodings, face_to_compare):
    return face_recognition.face_distance([np.array(face_encodings)], np.array(face_to_compare))


# 比较两个人脸是否同一人
def is_match_b64(b64_data1, b64_data2):
    # calculate distance between embeddings
    encoding_list1, face_boxes1 = get_features_b64(b64_data1)
    encoding_list2, face_boxes2 = get_features_b64(b64_data2)

    if len(face_boxes1)==0 or len(face_boxes2)==0:
        return False

    distance_vgg = face_distance(encoding_list1[0], encoding_list2[0])
    if distance_vgg <= ALGORITHM['vgg']['distance_threshold']:
        return True, distance_vgg

    distance_evo = face_distance(encoding_list1[1], encoding_list2[1])
    if distance_evo <= ALGORITHM['evo']['distance_threshold']:
        return True, distance_evo

    # 均为匹配
    return False, [-1]

