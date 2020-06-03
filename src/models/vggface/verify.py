# -*- coding: utf-8 -*-

import sys

if __name__ == '__main__':
    if len(sys.argv)<3:
        print("usage: python3 %s <img1> <img2>" % sys.argv[0])
        sys.exit(2)


# face verification with the VGGFace2 model
from PIL import Image
import numpy as np
from scipy.spatial.distance import cosine
from keras.preprocessing import image
from .keras_vggface.vggface import VGGFace
from .keras_vggface.utils import preprocess_input
import face_recognition
from facelib.utils import extract_face_b64


# 装入识别模型 # pooling: None, avg or max # model: vgg16, senet50, resnet50
model = VGGFace(model='senet50', include_top=False, input_shape=(224, 224, 3), pooling='avg') 
# https://stackoverflow.com/questions/40850089/is-keras-thread-safe
model._make_predict_function() # have to initialize before threading

# 从照片中获取人脸数据，返回所有能识别的人脸
def extract_face(filename, required_size=(224, 224)):
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
        face_array = np.asarray(image, 'float32')
        face_list.append(face_array)

        # show face
        #from PIL import ImageDraw
        #draw = ImageDraw.Draw(image)
        #del draw
        #image.show()

    return face_list, face_bounding_boxes


def load_face(filename, required_size=(224, 224)):
    img = image.load_img(filename, target_size=required_size)
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    return x


# 返回图片中所有人脸的特征
def get_features(filename):
    # extract faces
    faces, face_boxs = extract_face(filename)
    if len(faces) == 0:
        return [], []
    # convert into an array of samples
    samples = np.asarray(faces, 'float32')
    # prepare the face for the model, e.g. center pixels
    samples = preprocess_input(samples, version=2)
    # perform prediction
    yhat = model.predict(samples)
    yhat2 = yhat / np.linalg.norm(yhat)
    return yhat2, face_boxs


# determine if a candidate face is a match for a known face
def is_match(known_embedding, candidate_embedding, thresh=0.5):
    # calculate distance between embeddings
    score = cosine(known_embedding, candidate_embedding)
    if score <= thresh:
        print('>face is a Match (%.3f <= %.3f)' % (score, thresh))
    else:
        print('>face is NOT a Match (%.3f > %.3f)' % (score, thresh))


# 返回图片中所有人脸的特征
def get_features_b64(base64_data):
    # extract faces
    faces, face_boxs = extract_face_b64(base64_data, required_size=(224, 224))
    if len(faces) == 0:
        return [], []
    # convert into an array of samples
    samples = np.asarray(faces, 'float32')
    # prepare the face for the model, e.g. center pixels
    samples = preprocess_input(samples, version=2)
    # perform prediction
    yhat = model.predict(samples)
    yhat2 = yhat / np.linalg.norm(yhat)
    return yhat2, face_boxs


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
    return distance <= ALGORITHM['vgg']['distance_threshold'], distance


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

    distance_vgg = face_distance(encoding_list1[0], encoding_list2[0])
    x = distance_vgg <= ALGORITHM['vgg']['distance_threshold']
    return x.any(), distance_vgg
