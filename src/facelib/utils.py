# -*- coding: utf-8 -*-`
import time
import base64
import numpy as np
from io import BytesIO
from PIL import Image
from config.settings import ALGORITHM
from importlib import import_module
import face_recognition
#from datetime import datetime


# 时间函数
ISOTIMEFORMAT=['%Y-%m-%d %X', '%Y-%m-%d', '%Y%m%d%H%M', '%Y-%m-%d %H:%M']
def time_str(t=None, format=0):
    return time.strftime(ISOTIMEFORMAT[format], time.localtime(t))


# 动态引入
def import_verify(face_algorithm):
    module = import_module(ALGORITHM[face_algorithm]['module'])
    #print('imported: ', module)
    return module


# 将 base64 编码的图片转为Image 数组
def load_image_b64(b64_data, mode='RGB'):
    data = base64.b64decode(b64_data) # Bytes
    tmp_buff = BytesIO()
    tmp_buff.write(data)
    tmp_buff.seek(0)
    img = Image.open(tmp_buff)
    if mode:
        img = img.convert(mode)
    if img.size>(500,500): # 处理的尺寸不超过500
        img.thumbnail((500, 500)) 
    pixels =  np.array(img)
    tmp_buff.close()
    #print('pixels size: ', pixels.nbytes)
    return pixels

# 人脸定位
def face_locations_b64(b64_data):
    # load image from file
    pixels = load_image_b64(b64_data)
    # extract the bounding box from the first face 
    face_bounding_boxes = face_recognition.face_locations(pixels)

    # 可能返回 >0, 多个人脸
    if len(face_bounding_boxes) == 0:
        return []

    # 按人脸面积从大到小排序
    face_bounding_boxes = sorted( face_bounding_boxes, key=lambda s: (s[1]-s[3])*(s[2]-s[0]), reverse=True )
    return face_bounding_boxes


# 从照片中获取人脸数据，返回所有能识别的人脸， 图片输入为 base64 编码
def extract_face_b64(b64_data, required_size=(224, 224)):
    #start_time = datetime.now()
    # load image from file
    pixels = load_image_b64(b64_data)
    #print('[1 Time taken: {!s}]'.format(datetime.now() - start_time))
    # extract the bounding box from the first face
    face_bounding_boxes = face_recognition.face_locations(pixels)
    #print('[2 Time taken: {!s}]'.format(datetime.now() - start_time))

    # 可能返回 >0, 多个人脸
    if len(face_bounding_boxes) == 0:
        return [], []

    # 按人脸面积从大到小排序
    face_bounding_boxes = sorted( face_bounding_boxes, key=lambda s: (s[1]-s[3])*(s[2]-s[0]), reverse=True )
    # 只处理面积最大的一个脸
    face_bounding_boxes = face_bounding_boxes[:1]
    
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
        face_array = np.asarray(image, 'float32')
        face_list.append(face_array)
        #print('[3 Time taken: {!s}]'.format(datetime.now() - start_time))

    return face_list, face_bounding_boxes




# 图片文件转base64编码
def load_image_to_base64(image_file):
    with open(image_file, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data)
