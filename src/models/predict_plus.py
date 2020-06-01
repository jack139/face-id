# -*- coding: utf-8 -*-

# 使用两个算法模型并行识别

import os, sys
import concurrent.futures
from datetime import datetime
from config.settings import ALGORITHM, algorithm_settings
from . import knn
from . import knn_db

# 用于文件图片的预测线程
def predict_thread(face_algorithm, model_name, image_file, group_id='', data_type='base64'):
    # https://discuss.streamlit.io/t/attributeerror-thread-local-object-has-no-attribute-value/574/3
    import keras.backend.tensorflow_backend as tb
    tb._SYMBOLIC_SCOPE.value = True
    return knn.predict(image_file, 
        model_path=model_name, 
        distance_threshold=ALGORITHM[face_algorithm]['distance_threshold'],
        face_algorithm=face_algorithm)

# 用于db和base64图片的预测线程
# data_type: 'base64', 'encodings'
def predict_thread_db(face_algorithm, model_name, image_data, group_id, data_type='base64'): 
    # https://discuss.streamlit.io/t/attributeerror-thread-local-object-has-no-attribute-value/574/3
    import keras.backend.tensorflow_backend as tb
    tb._SYMBOLIC_SCOPE.value = True
    model_path, _ = os.path.split(model_name) # 取得模型所在路径
    if data_type!='base64': # 不是base64时，是db里的特征值对，根据算法取相应特征值
        image_data = [image_data[ALGORITHM[face_algorithm]['index']]]
    return knn_db.predict(image_data, group_id,
        model_path=model_path, 
        distance_threshold=ALGORITHM[face_algorithm]['distance_threshold'],
        face_algorithm=face_algorithm,
        data_type=data_type)

# 启动并行算法
def predict_parallel(thread_func, image_data, group_id='', data_type='base64'):
    all_predictions = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future1 = executor.submit(thread_func, algorithm_settings[1][0], algorithm_settings[1][1], 
                image_data, group_id, data_type)
        future2 = executor.submit(thread_func, algorithm_settings[2][0], algorithm_settings[2][1], 
                image_data, group_id, data_type)
        for future in concurrent.futures.as_completed([future1, future2]):
            predictions = future.result()
            if future==future1:
                all_predictions[1] = predictions
            else:
                all_predictions[2] = predictions
    
    #print(all_predictions)
    return merge_results(all_predictions)


# 合并两个算法的结果为最终结果
def merge_results(all_predictions):
    # 综合结果判断：
    # 1. 如果两个结果唯一且相同，则无异议
    # 2. 如果都为unkonw，则无结果
    # 3. 如果有一个为unknown， 则返回非unknown的
    # 4. 如果有一个为multi, 则返回非multi的
    # 5. 如果都是multi, 优先返回算法1的
    # 6. 如果两个都有唯一结果，优先返回算法1的
    # 7. 如果结果都为0，则无结果
    # 8. 如果有一个为0， 则返回非0的
    # 9. 最后优先返回算法1的结果
    final_result=[]
    len1 = len(all_predictions[1])
    len2 = len(all_predictions[2])
    name1=name2=''
    if len1>0:
        name1 = all_predictions[1][0][0]
    if len2>0:
        name2 = all_predictions[2][0][0]

    # 条件 7
    if len1==len2==0:
        final_result=[]
    # 条件 8
    elif 0 in (len1, len2):
        if len2==0:
            final_result = all_predictions[1]
        else:
            final_result = all_predictions[2]
    # 条件 2
    elif name1==name2=='unknown': 
        final_result = all_predictions[1]
    # 条件 3
    elif 'unknown' in (name1, name2): 
        if name1=='unknown':
            final_result = all_predictions[2]
        else:
            final_result = all_predictions[1]
    # 条件 1, 6
    elif len1==len2==1: 
        final_result = all_predictions[1]
    # 条件 4, 5
    elif len1>1 or len2>1:
        if len2==1:
            final_result = all_predictions[2]
        else:
            final_result = all_predictions[1]
    # 条件 9
    else:
        final_result = all_predictions[1]
    return final_result

