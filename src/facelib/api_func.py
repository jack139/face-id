# -*- coding: utf-8 -*-`

from datetime import datetime
from facelib import utils
from facelib.dbport import user_info

#FACE_MODEL = 'para'
#
#if FACE_MODEL=='vgg':
#    from models.vggface import verify
#elif FACE_MODEL=='evo':
#    from models.face_evoLVe import verify
#else:
#    from models.parallel import verify

from models.parallel import verify
from models.predict_plus import predict_parallel, predict_thread_db


# 人脸定位
def face_locations(b64_data, max_face_num=1):
    start_time = datetime.now()
    face_bounding_boxes = utils.face_locations_b64(b64_data) # (top, right, bottom, left)
    face_num = min(len(face_bounding_boxes), max_face_num)
    print('[Time taken: {!s}]'.format(datetime.now() - start_time))
    return face_num, face_bounding_boxes[:face_num]


# 人脸对比
def face_verify(b64_data1, b64_data2):
    start_time = datetime.now()
    is_match, score = verify.is_match_b64(b64_data1, b64_data2)
    print('[Time taken: {!s}]'.format(datetime.now() - start_time))
    if type(score)!=type([]):
        score = score.tolist()[0] # np.array
    return is_match, score


# 人脸搜索
def face_search(b64_data, group_id='DEFAULT', max_user_num=5):
    # 最多返回5个相似用户
    max_user_num = min(5, max_user_num)

    start_time = datetime.now()
    predictions = predict_parallel(predict_thread_db, b64_data, group_id)
    print('[Time taken: {!s}]'.format(datetime.now() - start_time))

    #print(predictions)

    if len(predictions)==0 or predictions[0][0]=='unknown':
        # 未识别
        return []

    # 准备返回结果
    user_list = []
    for i in range(min(max_user_num, len(predictions))):
        user_id, box, score, _ = predictions[i]
        info = user_info(group_id, user_id)
        user_list.append({
            'user_id'     : user_id,
            'mobile_tail' : info['mobile'][:-4], # 手机后4位
            'name'        : info['name'], # 用户姓名
            'location'    : box,
            'score'       : score,
        })

    return user_list

