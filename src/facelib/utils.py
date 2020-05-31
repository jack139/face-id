# -*- coding: utf-8 -*-`
import time
from io import BytesIO
import base64
import numpy as np
from PIL import Image
import face_recognition


# 时间函数
ISOTIMEFORMAT=['%Y-%m-%d %X', '%Y-%m-%d', '%Y%m%d%H%M', '%Y-%m-%d %H:%M']
def time_str(t=None, format=0):
    return time.strftime(ISOTIMEFORMAT[format], time.localtime(t))


# 将 base64 编码的图片转为Image 数组
def load_image_b64(b64_data, mode='RGB'):
    data = base64.b64decode(b64_data) # Bytes
    tmp_buff = BytesIO()
    tmp_buff.write(data)
    tmp_buff.seek(0)
    img = Image.open(tmp_buff)
    if mode:
        img = img.convert(mode)
    pixels =  np.array(img)
    tmp_buff.close()
    return pixels


# 从照片中获取人脸数据，返回所有能识别的人脸， 图片输入为 base64 编码
def extract_face_b64(b64_data, required_size=(224, 224)):
    # load image from file
    pixels = load_image_b64(b64_data)
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
        face_array = np.asarray(image, 'float32')
        face_list.append(face_array)

    return face_list, face_bounding_boxes