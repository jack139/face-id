# coding:utf-8

import json
from flask_restful import reqparse, abort, Resource, fields, request
from ..utils import helper
from facelib import dbport
from .. import logger

logger = logger.get_logger(__name__)

# 人脸定位
class Feedback(Resource):
    @helper.signature_required
    def post(self): 
        try:
            # 获取入参
            body_data = request.get_data().decode('utf-8') # bytes to str
            json_data = json.loads(body_data)
 
            group_id = json_data.get('group_id', '')
            request_id = json_data.get('request_id', '')
            is_correct = json_data.get('is_correct', 0)

            logger.info("入参: %s %s"%(request_id, is_correct))

            # 检查参数
            if len(request_id)==0 or len(group_id)==0:
                return {"code": 9001, "msg": "缺少参数"}

            if type(is_correct)!=type(1) and not is_correct.isdigit():
                return {"code": 9002, "msg": "参数格式错误"}

            # 登记反馈
            dbport.face_temp_update(group_id, request_id, int(is_correct))

            return {'code': 200, 'msg' : 'success'}

        except Exception as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }

