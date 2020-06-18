# -*- coding: utf-8 -*-

import cv2
from PIL import Image
import numpy as np
import tensorflow.compat.v1 as tf
import face_recognition
from .extract_embeddings import extract_embeddings
from facelib.utils import extract_face_b64
from config.settings import FACENET_MODEL_BASE as MODEL_BASE
from config.settings import ALGORITHM
from .facenet import load_model, load_data, load_data_array


INPUT_SIZE = [160, 160]

MODEL_ROOT = MODEL_BASE+'20180402-114759.pb'

#print('Model path: ', MODEL_ROOT)

G = tf.Graph()
with G.as_default():
    # 装入 model 文件
    load_model(MODEL_ROOT)


# 从照片中获取人脸数据，返回所有能识别的人脸
def extract_face(filename, required_size=INPUT_SIZE):
    # load image from file
    pixels = face_recognition.load_image_file(filename)
    # extract the bounding box from the first face
    face_bounding_boxes = face_recognition.face_locations(pixels)

    # 可能返回 >0, 多个人脸
    if len(face_bounding_boxes) == 0:
        return [], []

    face_list = []
    for face_box in face_bounding_boxes:
        top, right, bottom, left = face_box
        x1, y1, width, height = left, top, right-left, bottom-top
        x2, y2 = x1 + width, y1 + height
        # extract the face
        face = pixels[y1:y2, x1:x2]
        # resize pixels to the model size
        image = Image.fromarray(face)
        image = image.resize(required_size)
        # transfer to opencv image
        open_cv_image = np.array(image) 
        face_list.append(open_cv_image)

        # show face
        #from PIL import ImageDraw
        #draw = ImageDraw.Draw(image)
        #del draw
        #image.show()
        #image.save('test.bmp')

    return face_list, face_bounding_boxes


# 定位人脸，然后人脸的特征值列表，可能不止一个脸
def get_features(filename):
    face_list, face_boxes = extract_face(filename, required_size=INPUT_SIZE)
    images = load_data_array(face_list, False, False, INPUT_SIZE[0])
    encoding_list = extract_embeddings(G, images)
    return encoding_list, face_boxes

# 直接返回特征值
def get_features2(filename):
    images = load_data([ filename ], False, False, INPUT_SIZE[0])
    face_encodings = extract_embeddings(G, images)
    return face_encodings


# 定位人脸，然后人脸的特征值列表，可能不止一个脸, 输入图片为 base64 编码
def get_features_b64(base64_data):
    face_list, face_boxes = extract_face_b64(base64_data, required_size=INPUT_SIZE)
    images = load_data_array(face_list, False, False, INPUT_SIZE[0])
    encoding_list = extract_embeddings(G, images)
    return encoding_list, face_boxes


# 特征值距离
def face_distance(face_encodings, face_to_compare):
    return face_recognition.face_distance(np.array(face_encodings), np.array(face_to_compare))


# 比较两个人脸是否同一人
def is_match_b64(b64_data1, b64_data2):
    # calculate distance between embeddings
    encoding_list1, face_boxes1 = get_features_b64(b64_data1)
    encoding_list2, face_boxes2 = get_features_b64(b64_data2)

    if len(face_boxes1)==0 or len(face_boxes2)==0:
        return False, [999]

    distance = face_distance([encoding_list1[0]], encoding_list2[0])
    return distance <= ALGORITHM['fnet']['distance_threshold'], distance

'''
# 比较两个人脸是否同一人, encoding_list1来自已知db用户
def is_match_b64_2(encoding_list_db, b64_data):
    encoding_list1 = [[], []]
    for i in range(len(encoding_list_db)):
        encoding_list1[0].append(encoding_list_db[i][0])
        encoding_list1[1].append(encoding_list_db[i][1])

    # calculate distance between embeddings
    encoding_list2, face_boxes = get_features_b64(b64_data)

    if len(face_boxes)==0:
        return False, [999]

    distance_evo = face_distance(encoding_list1[1], encoding_list2[1])
    x = distance_evo <= ALGORITHM['fnet']['distance_threshold']
    return x.any(), distance_evo
'''