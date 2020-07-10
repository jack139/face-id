# -*- coding: utf-8 -*-

import tensorflow.compat.v1 as tf
import tensorlayer as tl
import cv2
from PIL import Image
import numpy as np
from .nets.L_Resnet_E_IR_fix_issue9 import get_resnet
import face_recognition
from facelib.utils import extract_face_b64
#from config.settings import FACENET_MODEL_BASE as MODEL_BASE
from config.settings import ALGORITHM

from .extract_embeddings import extract_embeddings
from .initializer import xavier_initializer


INPUT_SIZE = [112, 112]


# 初始化tensorflow
def init_nets():
    image_size = INPUT_SIZE
    net_depth = 50
    num_output = 85164
    ckpt_index_list = ['710000.ckpt']
    ckpt_file = '/home/gt/Codes/yhtech/face_model/ckpt_model_d/InsightFace_iter_best_'

    tf.disable_eager_execution()

    images = tf.placeholder(name='img_inputs', shape=[None, *image_size, 3], dtype=tf.float32)
    labels = tf.placeholder(name='img_labels', shape=[None, ], dtype=tf.int64)
    dropout_rate = tf.placeholder(name='dropout_rate', dtype=tf.float32)

    w_init_method = xavier_initializer(uniform=False)
    net = get_resnet(images, net_depth, type='ir', w_init=w_init_method, trainable=False, keep_rate=dropout_rate)
    embedding_tensor = net.outputs
    # mv_mean = tl.layers.get_variables_with_name('resnet_v1_50/bn0/moving_mean', False, True)[0]
    # 3.2 get arcface loss
    #logit = arcface_loss(embedding=net.outputs, labels=labels, w_init=w_init_method, out_num=num_output)

    sess = tf.Session()
    saver = tf.train.Saver()

    result_index = []
    file_index = ckpt_index_list[0]
    feed_dict_test = {}
    path = ckpt_file + file_index
    saver.restore(sess, path)
    print('ckpt file %s restored!' % file_index)
    feed_dict_test.update(tl.utils.dict_to_one(net.all_drop))
    feed_dict_test[dropout_rate] = 1.0

    #data = load_image(image_path)
    #data = face_list

    #results = extract_embeddings(sess, np.array(data), embedding_tensor, feed_dict=feed_dict_test, input_placeholder=images)

    #result_index.append(results)

    return sess, embedding_tensor, feed_dict_test, images

_sess, _embedding_tensor, _feed_dict_test, _input_placeholder = init_nets()

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
        np_img = np.array(image) 
        np_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
        face_list.append(np.array(np_img, dtype=np.float32))

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
    encoding_list = extract_embeddings(_sess, np.array(face_list), 
        _embedding_tensor, feed_dict=_feed_dict_test, input_placeholder=_input_placeholder)
    return encoding_list, face_boxes


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

