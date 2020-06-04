# -*- coding: utf-8 -*-

import cv2
from PIL import Image
import numpy as np
#from .backbone.model_irse import IR_50, IR_152, IR_SE_50, IR_SE_152
from .backbone.model_irse import IR_50, IR_101, IR_152, IR_SE_50, IR_SE_101, IR_SE_152
import face_recognition
from .extract_feature_v2 import extract_feature, load_model
from facelib.utils import extract_face_b64

# 当前使用模型的索引，选择数据模型只需要修改这里
CURRENT_MODEL = 5

INPUT_SIZE = [112, 112]
MODEL_BASE = '/home/gt/Codes/yhtech/face_model/face.evoLVe.PyTorch/'
MODEL_LIST = [
    ('ir50', 'bh-ir50/backbone_ir50_asia.pth'), # 0
    ('ir50', 'ms1m-ir50/backbone_ir50_ms1m_epoch63.pth'), # 1
    ('ir50', 'ms1m-ir50/backbone_ir50_ms1m_epoch120.pth'), # 2
    ('ir152', 'ms1m-ir152/Backbone_IR_152_Epoch_37_Batch_841528_Time_2019-06-06-02-06_checkpoint.pth'), # 3
    ('ir152', 'ms1m-ir152/Backbone_IR_152_Epoch_59_Batch_1341896_Time_2019-06-14-06-04_checkpoint.pth'), # 4
    ('ir152', 'ms1m-ir152/Backbone_IR_152_Epoch_112_Batch_2547328_Time_2019-07-13-02-59_checkpoint.pth'), # 5
    # 用于 HEAD，不能用于 backbone
    #('ir152', 'ms1m-ir152/Head_ArcFace_Epoch_37_Batch_841528_Time_2019-06-06-02-06_checkpoint.pth'), # 6
    #('ir152', 'ms1m-ir152/Head_ArcFace_Epoch_59_Batch_1341896_Time_2019-06-14-06-04_checkpoint.pth'), # 7
    #('ir152', 'ms1m-ir152/Head_ArcFace_Epoch_112_Batch_2547328_Time_2019-07-13-02-59_checkpoint.pth'), # 8
]

if MODEL_LIST[CURRENT_MODEL][0]=='ir152':
    BACKBONE = IR_152(INPUT_SIZE)
else:
    BACKBONE = IR_50(INPUT_SIZE)

MODEL_ROOT = MODEL_BASE+MODEL_LIST[CURRENT_MODEL][1]

print('Model: ', MODEL_LIST[CURRENT_MODEL][0])
#print('Model path: ', MODEL_ROOT)

# 装入 model 文件
BACKBONE = load_model(BACKBONE, MODEL_ROOT)

# 从照片中获取人脸数据，返回所有能识别的人脸
def extract_face(filename, required_size=[112, 112]):
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

    return face_list, face_bounding_boxes


# 定位人脸，然后人脸的特征值列表，可能不止一个脸
def get_features(filename):
    face_list, face_boxes = extract_face(filename, required_size=INPUT_SIZE)
    encoding_list = []
    for face in face_list:
        open_cv_face = face[:, :, ::-1].copy() 

        face_encodings = extract_feature(open_cv_face, BACKBONE, MODEL_ROOT)
        encoding_list.append(face_encodings.numpy()[0]) # torch.tensor to numpy.array

    return encoding_list, face_boxes

# 直接返回特征值
def get_features2(filename):
    img = cv2.imread(filename)
    face_encodings = extract_feature(img, BACKBONE, MODEL_ROOT)
    return face_encodings

# 定位人脸测试
def test(filename):
    face_list, face_boxes = extract_face(filename, required_size=INPUT_SIZE)
    print(face_boxes)

    n=0
    for face in face_list:
        open_cv_face = face[:, :, ::-1].copy() 
        cv2.imwrite(str(n)+'.jpg', open_cv_face)
        n+=1



# 定位人脸，然后人脸的特征值列表，可能不止一个脸, 输入图片为 base64 编码
def get_features_b64(base64_data):
    face_list, face_boxes = extract_face_b64(base64_data, required_size=INPUT_SIZE)
    encoding_list = []
    for face in face_list:
        open_cv_face = face[:, :, ::-1].copy() 

        face_encodings = extract_feature(open_cv_face, BACKBONE, MODEL_ROOT)
        encoding_list.append(face_encodings.numpy()[0]) # torch.tensor to numpy.array

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
    return distance <= ALGORITHM['evo']['distance_threshold'], distance

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
    x = distance_evo <= ALGORITHM['evo']['distance_threshold']
    return x.any(), distance_evo
