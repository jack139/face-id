# -*- coding: utf-8 -*-

# 特征值分类器训练

import numpy as np
from sklearn import preprocessing

from keras import models
from keras import layers
from keras import optimizers

from tqdm import tqdm

from facelib import dbport


# 1. 取得训练集 features(从db)
# 2. 取得测试集 features
# 3. 构建网络
# 4. 训练 softmax

#有标签索引对应的元素为 1。其代码实现如下。
def to_one_hot(labels, dimension):
    results = np.zeros((len(labels), dimension))
    for i, label in enumerate(labels):
        results[i, label] = 1.
    return results

def get_encodings(encodings_set, method):
    if method=='vgg':
        return encodings_set['vgg'].values()
    elif method=='evo':
        return encodings_set['evo'].values()
    #elif method=='rec':
    #    return encodings_set[2]
    elif method=='plus': # vgg+evo
        plus = []
        for i in encodings_set['vgg'].keys()
            plus.append(encodings_set['vgg'][i]+encodings_set['evo'][i])
        return plus
    #elif method=='tri':
    #    return encodings_set[0]+encodings_set[1]+encodings_set[2]
    return []

def load_data(group_id, ratio=0.8, face_num=10, max_user=500, method='vgg'):

    X_train = []
    y_train = []
    X_test = []
    y_test = []

    # 按用户分组从db装入特征数据, 装入所有数据
    start = 0
    max_length = 1000
    total = 0
    while 1:
        user_list = dbport.user_list_by_group(group_id, start=start, length=max_length)
        for i in tqdm(range(len(user_list))):
            if total>max_user:
                break

            X = []
            y = []

            faces = dbport.user_face_list(group_id, user_list[i])
            for f in faces[:face_num]: # 使用指定数量人脸 
                r = dbport.face_info(f)
                if r:
                    e_list = get_encodings(r['encodings'], method)
                    X.extend(e_list)
                    y.extend([user_list[i]]*len(e_list))

            # 划分训练集和测试集
            train_num = int(len(X)*ratio)
            X_train.extend(X[:train_num])
            y_train.extend(y[:train_num])
            X_test.extend(X[train_num:])
            y_test.extend(y[train_num:])

            total += 1

        if total>max_user:
            break

        if len(user_list)<max_length: 
            break
        else: # 未完，继续
            start += max_length

    # y标签规范化
    label_y = preprocessing.LabelEncoder()
    label_y.fit(y_train)
    y_train = label_y.transform(y_train)
    y_train = to_one_hot(y_train, total)
    y_test = label_y.transform(y_test)
    y_test = to_one_hot(y_test, total)

    return np.array(X_train), np.array(y_train), np.array(X_test), np.array(y_test), label_y



# 模型参数
epochs_num = 120
batch_size = 50


# 创建模型
def get_model(input_dim, output_dim):
    # 三层网络 模型定义
    model = models.Sequential()
    model.add(layers.Dense(1024, activation = 'relu', input_dim = input_dim))
    #model.add(layers.Dense(512, activation = 'relu'))
    model.add(layers.Dropout(0.2))
    model.add(layers.Dense(output_dim, activation = 'softmax'))
    #编译模型
    model.compile(optimizer=optimizers.RMSprop(lr=2e-4), 
        loss='categorical_crossentropy', metrics=['accuracy']) 
    return model


if __name__ == '__main__':
    X_train, y_train, X_test, y_test, label_y = load_data('test8y', ratio=0.3, max_user=400, method='plus')

    input_dim = len(X_train[0])
    output_dim = len(y_train[0])

    model = get_model(input_dim, output_dim)
    model.summary()

    print('input_dim=', input_dim, 'output_dim=', output_dim, ' batch_size=', batch_size, ' epochs_num=', epochs_num)

    history = model.fit(X_train, y_train, epochs=epochs_num, batch_size=batch_size, verbose=1,
        validation_data=(X_test, y_test))

    # 评估预测结果
    results = model.evaluate(X_test, y_test, verbose=1)
    print('predict: ', results)


    # 保存模型 和 标签数据
    import pickle
    with open('ft_test.h5', 'wb') as f:
        pickle.dump((model, label_y), f)

    # 读取模型，并识别
    with open('ft_test.h5', 'rb') as f:
        model, label_y = pickle.load(f)

    result = model.predict_classes(X_test[:1])
    name = label_y.inverse_transform(result)
    print(name[0])
