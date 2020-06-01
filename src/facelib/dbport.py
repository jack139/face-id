# -*- coding: utf-8 -*-

# 使用 mongodb 作为存储，数据库操作

from bson.objectid import ObjectId
from . import utils
from config import settings

db = settings.db_web



########### 用户组操作

# 新建用户组，group_id要唯一，否则返回 None
def group_new(group_id, memo=''):
    r = db.groups.find({'group_id' : group_id})
    if r.count()>0: # group_id 已存在
        return -1
    else:
        r2 = db.groups.insert_one({
            'group_id' : group_id, 
            'memo'     : memo,
            'time_t'   : utils.time_str()
        })
        return str(r2.inserted_id)


# 用户组信息
def group_info(group_id):
    r = db.groups.find_one({'group_id' : group_id}, {'_id':0})
    if r:
        return r
    else:
        return -1


# 删除用户组, 慎用，会删除组下所有用户及特征数据
def group_remove(group_id):
    if group_info(group_id)==-1: # 组不存在
        return -1

    r2 = db.users.find({'group_id' : group_id}, {'user_id' : 1})
    user_deleted = face_deleted = 0
    for i in r2:
        # 删除用户数据
        r3 = user_remove(group_id, i['user_id'])
        if r3==-1: 
            pass # 数据不完整，要删除的用户不存在
        else:
            user_deleted += r3[0]
            face_deleted += r3[1]

    r = db.groups.delete_one({'group_id': group_id})
    return (r.deleted_count, face_deleted, face_deleted)


# 返回用户组列表
def group_list(start=0, length=100):
    length = 100 if length>100 else length
    r = db.groups.find({}, {'_id':0}, sort=[('_id', 1)], limit=length, skip=start)
    return [i for i in r]


##################### 用户操作

# 新建用户，user_id要唯一，否则返回 None
def user_new(group_id, user_id, name='', mobile='', memo=''):
    if group_info(group_id)==-1:
        return -1 # 用户组不存在

    if user_info(group_id, user_id)!=-1:
        return -2  # user_id 已存在
    else:
        r2 = db.users.insert_one({
            'group_id' : group_id, 
            'user_id'  : user_id, 
            'name'     : name, 
            'mobile'   : mobile, 
            'memo'     : memo,
            'face_list': [],
            'time_t'   : utils.time_str(),
            'last_t'   : utils.time_str(),
        })
        return str(r2.inserted_id)


# 更新用户信息，
def user_update(group_id, user_id, name=None, mobile=None, memo=None):
    if user_info(group_id, user_id)==-1:
        return -1  # 用户不存在
    update_set = {}
    if name:
        update_set['name'] = name
    if mobile:
        update_set['mobile'] = mobile
    if memo:
        update_set['memo'] = memo

    if len(update_set)>0: # 有数据更新
        update_set['last_t'] = utils.time_str()
        r = db.users.update_one({'group_id' : group_id, 'user_id' : user_id}, {'$set' : update_set})
        return r.modified_count
    else:
        return 0


# 用户信息
def user_info(group_id, user_id):
    r = db.users.find_one({'group_id' : group_id, 'user_id' : user_id}, {'_id' : 0})
    if r is None:
        return -1
    else:
        return r


# 删除用户， 慎用， 会删除用户的所有特征数据
def user_remove(group_id, user_id):
    r = user_face_list(group_id, user_id) 
    if r==-1:
        return -1  # 用户不存在

    face_deleted = 0
    for i in r:
        # 删除人脸数据
        r2 = face_remove(i)
        if r2==-1:
            pass  # 数据有问题， 要删除的人脸不存在
        else:
            face_deleted += r2 

    r = db.users.delete_one({'group_id':group_id, 'user_id':user_id})
    return (r.deleted_count, face_deleted)


# 用户组里所有用户 user_id， 返回列表
def user_list_by_group(group_id, start=0, length=100):
    length = 100 if length>100 else length
    r = db.users.find({'group_id' : group_id}, {'user_id' : 1}, sort=[('_id', 1)], limit=length, skip=start)
    return [i['user_id'] for i in r if i.get('user_id')]


# 复制用户到另一个group
def user_copy(user_id, src_group_id, dst_group_id):
    r = db.users.find_one({'group_id' : src_group_id, 'user_id' : user_id}, {'_id' : 0})
    if r is None:
        return -1 # 用户不存在

    if user_info(dst_group_id, user_id)!=-1:
        return -2 # 用户在目的组已存在

    # 添加用户数据
    r['group_id'] = dst_group_id
    r['time_t'] = r['last_t'] = utils.time_str()
    r2 = db.users.insert_one(r)

    # 人脸引用计数增加
    for i in r['face_list']:
        face_ref_inc(i)

    return str(r2.inserted_id)


# 用户注册的人脸数据列表
def user_face_list(group_id, user_id):
    r = db.users.find_one({'group_id' : group_id, 'user_id'  : user_id}, {'face_list' : 1})
    if r:
        return r['face_list']
    else:
        return -1 # 不存在


# 用户添加face_id
def user_add_face(group_id, user_id, face_id):
    r = db.users.update_one({'group_id':group_id, 'user_id':user_id},
        {'$push' : {'face_list' : face_id}})
    return r.modified_count


# 用户删除face_id
def user_remove_face(group_id, user_id, face_id):
    r = db.users.update_one({'group_id':group_id, 'user_id':user_id},
        {'$pull' : {'face_list' : face_id}})
    return r.modified_count


#################### 特征数据操作

# 新建人脸特征
def face_new(model_id, encodings):
    r2 = db.faces.insert_one({
        'model_id'  : model_id, 
        'encodings' : encodings, 
        'time_t'    : utils.time_str(),
        'ref_count' : 1,
    })
    face_id = str(r2.inserted_id)
    return face_id


# 删除人脸特征
def face_remove(face_id):
    # 检索 并 引用计数减一
    r = db.faces.find_one_and_update({'_id':ObjectId(face_id)}, {'$inc' : {'ref_count' : -1}})
    if r is None:
        return -1

    if r['ref_count']==1:
        # 实际删除
        r = db.faces.delete_one({'_id':ObjectId(face_id)})
        return r.deleted_count
    else:
        # 计数已减一，不删除
        return 0


# 人脸引用计数增加
def face_ref_inc(face_id):
    # 引用计数加一
    r = db.faces.update_one({'_id':ObjectId(face_id)}, {'$inc' : {'ref_count' : 1}})
    return r.modified_count

# 人脸数据
def face_info(face_id):
    # 引用计数加一
    r = db.faces.find_one({'_id':ObjectId(face_id)}, {'_id' : 0})
    return r


######################### 日志操作

# 添加日志
def log(api, param, result, extra=''):
    r2 = db.facelog.insert_one({
        'api'    : api,
        'param'  : param,
        'result' : result,
        'extra'  : extra,
    })
    return str(r2.inserted_id)
