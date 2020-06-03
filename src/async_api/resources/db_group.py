# coding:utf-8

from flask_restful import reqparse, abort, Resource, fields, request

import json
from ..utils import helper
from .. import logger
from facelib import dbport

logger = logger.get_logger(__name__)


# 用户组新建
class DbGroupNew(Resource):
    #@helper.token_required
    def post(self): 
        try:
            # 获取入参
            body_data = request.get_data().decode('utf-8') # bytes to str
            json_data = json.loads(body_data)

            group_id = json_data.get('group_id', '')

            logger.info("入参: %s" % group_id)

            # 检查参数
            if group_id=='':
                return {"code": 9001, "msg": "缺少参数"}

            # 新建用户组
            r = dbport.group_new(group_id)
            if r==-1:
                return {"code": 9002, "msg": "group_id已存在"}

            return { "code" : 200, "msg" : "success", 'data' : { "type" : "SUCCESS" } }

        except Exception as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }


# 用户组删除
class DbGroupRemove(Resource):
    #@helper.token_required
    def post(self): 
        try:
            # 获取入参
            body_data = request.get_data().decode('utf-8') # bytes to str
            json_data = json.loads(body_data)

            group_id = json_data.get('group_id', '')

            logger.info("入参: %s" % group_id)

            # 检查参数
            if group_id=='':
                return {"code": 9001, "msg": "缺少参数"}

            # 删除用户组
            r = dbport.group_remove(group_id)
            if r==-1:
                return {"code": 9002, "msg": "group_id不存在"}

            return { "code" : 200, "msg" : "success", 'data' : { "type" : "SUCCESS" } }

        except Exception as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }

# 用户组列表
class DbGroupList(Resource):
    #@helper.token_required
    def post(self): 
        try:
            # 获取入参
            body_data = request.get_data().decode('utf-8') # bytes to str
            json_data = json.loads(body_data)

            start = json_data.get('start', 0)
            length = json_data.get('length', 100)

            logger.info("入参: %s %s"%(start, length))

            start = max(0, int(start))
            length = min(1000, int(length))

            # 用户组列表
            r = dbport.group_list(start=start, length=length)

            return { "code" : 200, "msg" : "success", 'data' : { "user_list" : r } }

        except Exception as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }


