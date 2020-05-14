# -*- coding: utf-8 -*-

import os, shutil

#path = 'data/face_data/AFDB_face_dataset'
#train = 'data/train2'
#test = 'data/test2'

path = 'data/face_data/CASIA-maxpy-clean'
train = 'data/train3'
test = 'data/test3'


dir_list = os.listdir(path)
dir_list = sorted(dir_list)

ratio = 0.5  # train/total

for d in dir_list[:50]:
    # 所以文件
    file_list = os.listdir(os.path.join(path, d))
    file_list = sorted(file_list)
    print(d, len(file_list))

    if len(file_list)<2: # 至少需要两张照片
        continue

    # 建输出目录
    output_train = os.path.join(train, d) 
    output_test = os.path.join(test, d) 
    if not os.path.exists(output_train):
        os.mkdir(output_train)
    if not os.path.exists(output_test):
        os.mkdir(output_test)

    # 计算训练图片数量
    train_c = int(len(file_list)*ratio)

    # 生成train的数据
    for i in file_list[:train_c]: 
        shutil.copy(os.path.join(path,d,i), output_train)
        
    # 生成test的数据
    for i in file_list[train_c:]: 
        shutil.copy(os.path.join(path,d,i), output_test)

