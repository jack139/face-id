# -*- coding: utf-8 -*-

import sys
import os
import os.path
import face_recognition
from face_recognition.face_recognition_cli import image_files_in_folder
from config.settings import ALGORITHM
from facelib.utils import import_verify
from facelib import dbport


'''
     Structure:
        <train_dir>/
        ├── <person1>/
        │   ├── <somename1>.jpeg
        │   ├── <somename2>.jpeg
        │   ├── ...
        ├── <person2>/
        │   ├── <somename1>.jpeg
        │   └── <somename2>.jpeg
        └── ...
'''

# 导入图片特征： vgg evo rec deep

if __name__ == "__main__":
    if len(sys.argv)<3:
        print("usage: python3 %s <train_data_dir> <group_id>" % sys.argv[0])
        sys.exit(2)

    train_dir = sys.argv[1]
    group_id = sys.argv[2]

    # 新建分组，有可能已存在
    dbport.group_new(group_id)

    # 动态载入 verify库
    module_verify = [ 
        import_verify('vgg'), 
        import_verify('evo'), 
        import_verify('rec'), 
        #import_verify('deep') 
    ]

    # Loop through each person in the training set
    for class_dir in os.listdir(train_dir):
        if not os.path.isdir(os.path.join(train_dir, class_dir)):
            continue

        print('import: ', class_dir)

        # 新建用户
        dbport.user_new(group_id, class_dir, name=class_dir)


        # Loop through each training image for the current person
        for img_path in image_files_in_folder(os.path.join(train_dir, class_dir)):
            face_encodings_vgg, _ = module_verify[0].get_features(img_path)
            face_encodings_evo, _ = module_verify[1].get_features(img_path)
            face_encodings_rec, _ = module_verify[2].get_features(img_path)
            #face_encodings_deep, _ = module_verify[3].get_features(img_path)

            if len(face_encodings_vgg) != 1:
                # If there are no people (or too many people) in a training image, skip the image.
                print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(face_encodings) < 1 else "Found more than one face"))
            else:
                # Add face encoding for current image to the training set
                encoding_vgg = face_encodings_vgg[0]
                encoding_evo = face_encodings_evo[0]
                encoding_rec = face_encodings_rec[0]
                #encoding_deep = face_encodings_deep[0]
                if type(encoding_vgg)!=type([]):
                    encoding_vgg = encoding_vgg.tolist()
                if type(encoding_evo)!=type([]):
                    encoding_evo = encoding_evo.tolist()
                if type(encoding_rec)!=type([]):
                    encoding_rec = encoding_rec.tolist()
                #if type(encoding_deep)!=type([]):
                #    encoding_deep = encoding_deep.tolist()

                # 添加人脸特征
                filepath, filename = os.path.split(img_path)
                #face_id = dbport.face_new('vgg_evo_rec_deep', [ encoding_vgg, encoding_evo, encoding_rec, encoding_deep], filename)
                face_id = dbport.face_new('vgg_evo_rec_x', [ encoding_vgg, encoding_evo, encoding_rec, [] ], filename)
                # 人脸数据添加到用户信息
                dbport.user_add_face(group_id, class_dir, face_id)

