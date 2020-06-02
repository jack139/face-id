# coding:utf-8

from flask_restful import reqparse, abort, Resource, fields, request

import json
from ..utils import helper
from .. import logger
from facelib import dbport

logger = logger.get_logger(__name__)

# api测试
class DbUserInfo(Resource):
    # curl -X POST --data '{"group_id":"test","user_id":"obama"}' http://127.0.0.1:5000/facedb/user/info
    #@helper.token_required
    def post(self): 
        try:
            # 获取入参
            body_data = request.get_data().decode('utf-8') # bytes to str
            json_data = json.loads(body_data)

            group_id = json_data.get('group_id', 'DEFAULT')
            user_id = json_data.get('user_id')

            logger.info("入参: %s %s"%(group_id, user_id))

            # 检查参数
            if user_id is None:
                return {"code": 9001, "msg": "缺少参数"}

            r = dbport.user_info(group_id, user_id)

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

