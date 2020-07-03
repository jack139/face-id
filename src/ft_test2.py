# -*- coding: utf-8 -*-

# vggface 数据增强训练, 
import time
import numpy as np
from sklearn import preprocessing

from keras import models
from keras import layers
from keras import optimizers
from keras.preprocessing.image import ImageDataGenerator

from tqdm import tqdm

from facelib import dbport
from models.vggface.keras_vggface.vggface import VGGFace

# 1. 取得训练集 features(从db)
# 2. 取得测试集 features
# 3. 构建网络
# 4. 训练 softmax


# 模型参数
epochs_num = 2
batch_size = 20
target_size = (224, 224)
output_dim = 412
train_dir = '../data/train2'
validation_dir = '../data/test2'

# 创建模型
def get_model(output_dim):
    vgg_model = VGGFace(model='senet50', include_top=False, input_shape=(224, 224, 3), pooling='avg') 
    last_layer = vgg_model.get_layer('avg_pool').output
    x = layers.Flatten(name='flatten_added')(last_layer) # 保持与 include_top=True 的定义一致
    out = layers.Dense(output_dim, activation='softmax', name='classifier')(x) 
    custom_vgg_model = models.Model(vgg_model.input, out)

    set_trainable = False
    for layer in custom_vgg_model.layers:
        if layer.name == 'conv5_3_1x1_reduce': # 'flatten_added' 确定冻结的位置， 此层以前都冻结
            set_trainable = True
        if set_trainable:
            layer.trainable = True
        else:
            layer.trainable = False

    #编译模型
    custom_vgg_model.compile(optimizer=optimizers.RMSprop(lr=2e-5), 
        loss='categorical_crossentropy', metrics=['accuracy']) 
    return custom_vgg_model


# 去掉分类器权重, 用于获取特征值
def extrace_weight(): 
    vgg_model = VGGFace(model='senet50', include_top=True, input_shape=(224, 224, 3), pooling='avg') 
    last_layer = vgg_model.get_layer('avg_pool').output
    no_classifier_model = models.Model(vgg_model.input, last_layer)
    no_classifier_model.summary()
    no_classifier_model.save('no_classifier.h5')

def extrace_weight2(weight_file): 
    #vgg_model = VGGFace(model='senet50', include_top=True, input_shape=(224, 224, 3), pooling='avg', weights=weight_file) 
    vgg_model = get_model(output_dim)
    vgg_model.load_weights(weight_file)
    last_layer = vgg_model.get_layer('avg_pool').output
    no_classifier_model = models.Model(vgg_model.input, last_layer)
    no_classifier_model.summary()
    no_classifier_model.save('no_classifier.h5')


if __name__ == '__main__':

    model = get_model(output_dim)
    model.summary()

    print('output_dim=', output_dim, ' batch_size=', batch_size, ' epochs_num=', epochs_num)


    train_datagen = ImageDataGenerator(
        rescale=None,
        rotation_range=0,
        width_shift_range=0.0,
        height_shift_range=0.0,
        shear_range=0.0,
        zoom_range=0.0,
        horizontal_flip=False,
        fill_mode='nearest')
    test_datagen = ImageDataGenerator(rescale=None)

    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=target_size,
        batch_size=batch_size,
        class_mode='categorical')
    validation_generator = test_datagen.flow_from_directory(
        validation_dir,
        target_size=target_size,
        batch_size=batch_size,
        class_mode='categorical')


    history = model.fit_generator(
        train_generator,
        steps_per_epoch=50,
        epochs=epochs_num,
        validation_data=validation_generator,
        validation_steps=50)


    # 评估预测结果
    #results = model.evaluate(X_test, y_test, verbose=1)
    #print('predict: ', results)


    # 保存权重
    model.save('trained_'+str(int(time.time()))+'.h5')

    # 保存模型 和 标签数据
    #import pickle
    #with open('ft_test.h5', 'wb') as f:
    #    pickle.dump((model, label_y), f)
    ## 读取模型，并识别
    #with open('ft_test.h5', 'rb') as f:
    #    model, label_y = pickle.load(f)
    #result = model.predict_classes(X_test[:1])
    #name = label_y.inverse_transform(result)
    #print(name[0])
