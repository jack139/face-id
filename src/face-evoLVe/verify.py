# -*- coding: utf-8 -*-

from backbone.model_resnet import ResNet_50, ResNet_101, ResNet_152
from backbone.model_irse import IR_50, IR_101, IR_152, IR_SE_50, IR_SE_101, IR_SE_152
import face_recognition

INPUT_SIZE = [112, 112]

if False:
    #======= model & loss & optimizer =======#
    BACKBONE_DICT = {'ResNet_50': ResNet_50(INPUT_SIZE), 
                     'ResNet_101': ResNet_101(INPUT_SIZE), 
                     'ResNet_152': ResNet_152(INPUT_SIZE),
                     'IR_50': IR_50(INPUT_SIZE), 
                     'IR_101': IR_101(INPUT_SIZE), 
                     'IR_152': IR_152(INPUT_SIZE),
                     'IR_SE_50': IR_SE_50(INPUT_SIZE), 
                     'IR_SE_101': IR_SE_101(INPUT_SIZE), 
                     'IR_SE_152': IR_SE_152(INPUT_SIZE)}
    BACKBONE = BACKBONE_DICT[BACKBONE_NAME]
    print("=" * 60)
    print(BACKBONE)


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
        open_cv_image = numpy.array(pil_image) 
        face_list.append(open_cv_image)
        #face_array = np.asarray(image, 'float32')
        #face_list.append(face_array)

        # show face
        #from PIL import ImageDraw
        #draw = ImageDraw.Draw(image)
        #del draw
        #image.show()

    return face_list, face_bounding_boxes

INPUT_SIZE = [112, 112]

def get_features(filename):
    faces = extract_face(filename, required_size=INPUT_SIZE)
        
    backbone = IR_50(INPUT_SIZE)
    model_root = '/home/gt/Codes/yhtech/face_model/face.evoLVe.PyTorch/bh-ir50/backbone_ir50_asia.pth'
    face_encodings = extract_feature(filename, backbone, model_root)
    return face_encodings