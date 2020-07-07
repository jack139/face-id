# -*- coding: utf-8 -*-

import os, shutil
import face_recognition
from PIL import Image
import numpy as np

ratio = 0.5  # train/total
max_person = 50 # 人脸数量
max_images = 20 # 使用的照片数量


input_dir = 'data/train2b'
output_dir = 'data/train2bx'


def _HorizontalEyes(PILImg, pts):
    x1, y1 = pts[0]
    x2, y2 = pts[1]
    k = (y2-y1) / (x2-x1)
    angle = np.arctan(k)/np.pi*180
    #print('rotate angle:', angle)
    return PILImg.rotate(angle)


# 获取能取得人脸的照片
def get_face_image(path, file_list, output_path): 
    for i in file_list:
        # 复制原始文件
        shutil.copy(os.path.join(path, i), output_path)

        # 修正人脸角度
        image = face_recognition.load_image_file(os.path.join(path, i))
        # 调整人脸角度， 按第一个人的角度调整
        face_landmarks_list = face_recognition.face_landmarks(image)
        pil_image = Image.fromarray(image)
        if len(face_landmarks_list)>0:
            pil_image = _HorizontalEyes(pil_image, [face_landmarks_list[0]['left_eye'][0]] + [face_landmarks_list[0]['right_eye'][0]])
            #pil_image.show()
            
        pil_image.save(os.path.join(output_path, i+'.align.jpg'), quality=95)

        # 镜像人脸
        pil_image = pil_image.transpose(Image.FLIP_LEFT_RIGHT)
        pil_image.save(os.path.join(output_path, i+'.mirror.jpg'), quality=95)


if __name__ == "__main__":
    dir_list = os.listdir(input_dir)
    dir_list = sorted(dir_list)

    n = 0
    for d in dir_list:

        # 建输出目录
        output_path = os.path.join(output_dir, d) 
        if not os.path.exists(output_path):
            os.mkdir(output_path)

        # 所以文件
        file_list = os.listdir(os.path.join(input_dir, d))
        file_list = sorted(file_list)

        # 生成修正人脸和镜像
        get_face_image(os.path.join(input_dir, d), file_list, os.path.join(output_dir, d))

        print(d, len(file_list))
        n += 1
            
