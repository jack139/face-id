# coding:utf-8

from flask_restful import reqparse, abort, Resource, fields, request

import json
from ..utils import helper
from .. import logger
from facelib import dbport, utils

logger = logger.get_logger(__name__)

# 用户信息
class DbUserInfo(Resource):
    # curl -X POST --data '{"group_id":"test","user_id":"obama"}' http://127.0.0.1:5000/facedb/user/info
    #@helper.token_required
    def post(self): 
        try:
            # 获取入参
            body_data = request.get_data().decode('utf-8') # bytes to str
            json_data = json.loads(body_data)

            group_id = json_data.get('group_id', 'DEFAULT')
            user_id = json_data.get('user_id', '')

            logger.info("入参: %s %s"%(group_id, user_id))

            # 检查参数
            if user_id=='':
                return {"code": 9001, "msg": "缺少参数"}

            r = dbport.user_info(group_id, user_id)
            if r==-1:
                return {"code": 9002, "msg": "user_id不存在"}

            return { "code" : 200, "msg" : "success", 'data' : { 
                'group_id'  : r['group_id'],
                'user_id'   : r['user_id'],
                'name'      : r['name'],
                'mobile'    : r['mobile'],
                'memo'      : r['memo'],
                'ctime'     : r['time_t'],
                'image_num' : len(r['face_list']),
            } }

        except Exception as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }



# 用户人脸列表
class DbUserFaceList(Resource):
    #@helper.token_required
    def post(self): 
        try:
            # 获取入参
            body_data = request.get_data().decode('utf-8') # bytes to str
            json_data = json.loads(body_data)

            group_id = json_data.get('group_id', 'DEFAULT')
            user_id = json_data.get('user_id', '')

            logger.info("入参: %s %s"%(group_id, user_id))

            # 检查参数
            if user_id=='':
                return {"code": 9001, "msg": "缺少参数"}

            r = dbport.user_face_list(group_id, user_id)
            if r==-1:
                return {"code": 9002, "msg": "user_id不存在"}

            return { "code" : 200, "msg" : "success", 'data' : { "face_list" : r } }

        except Exception as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }


# 用户复制
class DbUserCopy(Resource):
    #@helper.token_required
    def post(self): 
        try:
            # 获取入参
            body_data = request.get_data().decode('utf-8') # bytes to str
            json_data = json.loads(body_data)

            src_group_id = json_data.get('src_group_id', '')
            dst_group_id = json_data.get('dst_group_id', '')
            user_id = json_data.get('user_id', '')

            logger.info("入参: %s %s %s"%(user_id, src_group_id, dst_group_id))

            # 检查参数
            if '' in (user_id, src_group_id, dst_group_id) :
                return {"code": 9001, "msg": "缺少参数"}

            # 复制用户到目的用户组
            r = dbport.user_copy(user_id, src_group_id, dst_group_id)
            if r==-1:
                return {"code": 9002, "msg": "user_id不存在"}
            if r==-2:
                return {"code": 9003, "msg": "user_id在目的用户组已存在"}

            # 重新训练模型
            utils.train_by_group(dst_group_id)

            return { "code" : 200, "msg" : "success", 'data' : { "type" : "SUCCESS" } }

        except Exception as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }


# 用户删除
class DbUserRemove(Resource):
    #@helper.token_required
    def post(self): 
        try:
            # 获取入参
            body_data = request.get_data().decode('utf-8') # bytes to str
            json_data = json.loads(body_data)

            group_id = json_data.get('group_id', 'DEFAULT')
            user_id = json_data.get('user_id', '')

            logger.info("入参: %s %s"%(group_id, user_id))

            # 检查参数
            if user_id=='':
                return {"code": 9001, "msg": "缺少参数"}

            # 删除用户
            r = dbport.user_remove(group_id, user_id)
            if r==-1:
                return {"code": 9002, "msg": "user_id不存在"}

            # 重新训练模型
            utils.train_by_group(group_id)

            return { "code" : 200, "msg" : "success", 'data' : { "type" : "SUCCESS" } }

        except Exception as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }

# 用户列表
class DbUserList(Resource):
    #@helper.token_required
    def post(self): 
        try:
            # 获取入参
            body_data = request.get_data().decode('utf-8') # bytes to str
            json_data = json.loads(body_data)

            group_id = json_data.get('group_id', 'DEFAULT')
            start = json_data.get('start', 0)
            length = json_data.get('length', 100)

            logger.info("入参: %s %s %s"%(group_id, start, length))

            start = max(0, int(start))
            length = min(1000, int(length))

            # 查询用户组下用户列表
            r = dbport.user_list_by_group(group_id, start=start, length=length)

            return { "code" : 200, "msg" : "success", 'data' : { "user_list" : r } }

        except Exception as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }


