# coding:utf-8

from flask_restful import reqparse, abort, Resource, fields, request

import json
from ..utils import helper
from .. import logger
from facelib import dbport, utils
from config.settings import MAX_IMAGE_SIZE

logger = logger.get_logger(__name__)

# 人脸注册
class DbFaceReg(Resource):
    @helper.signature_required
    def post(self): 
        try:
            # 获取入参
            body_data = request.get_data().decode('utf-8') # bytes to str
            json_data = json.loads(body_data)

            group_id = json_data.get('group_id', 'DEFAULT')
            user_id = json_data.get('user_id', '')
            name = json_data.get('name', '')
            mobile = json_data.get('mobile', '')
            memo = json_data.get('memo', '')
            image = json_data.get('image', '')

            logger.info("入参: %s %s %s %s %s %d"%(group_id, user_id, name, mobile, memo, len(image)))

            # 检查参数
            if '' in (image, user_id, name):
                return {"code": 9001, "msg": "缺少参数"}

            if len(image)>MAX_IMAGE_SIZE:
                return {"code": 9002, "msg": "图片数据太大"}

            # 定位人脸

            # 准备发队列消息
            request_id = helper.gen_request_id()

            request_msg = {
                'api'          : 'face_locate',
                'image'        : image,
                'max_face_num' : 10,
            }

            # 在发redis消息前注册, 防止消息漏掉
            ps = helper.redis_subscribe(request_id)

            # 发布消息给redis
            r = helper.redis_publish_request(request_id, request_msg)
            if r is None:
                logger.error("消息队列异常")
                return {"code": 9099, "msg": "消息队列异常"}

            # 通过redis订阅等待结果返回
            ret = helper.redis_sub_receive(ps, request_id)               
            ret2 = json.loads(ret['data'].decode('utf-8'))
            if ret2['code']!=200:
                return ret2

            face_num = ret2['data']['face_num']

            if face_num==0:
                return {"code": 9003, "msg": "未定位到人脸"}

            # 注册用户信息
            r = dbport.user_new(group_id, user_id, name=name, mobile=mobile, memo=memo)
            if r==-1:
                return {"code": 9004, "msg": "用户组不存在"}
            if r==-2:
                return {"code": 9005, "msg": "user_id已存在"}

            # 添加人脸信息
            face_id = dbport.face_new("vgg_evo", [])
            dbport.user_add_face(group_id, user_id, face_id)

            # 异步生成特征值、训练
            request_msg = {
                'api'      : 'face_features',
                'image'    : image,
                'face_id'  : face_id,
                'group_id' : group_id,
                'user_id'  : user_id,
            }
            # 发布消息给redis
            r = helper.redis_publish_request('NO_RECIEVER', request_msg)
            if r is None:
                logger.error("消息队列异常")
                return {"code": 9099, "msg": "消息队列异常"}


            return { "code" : 200, "msg" : "success", 'data' : { 'face_id'  : face_id } }

        except Exception as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }


# 人脸更新
class DbFaceUpdate(Resource):
    @helper.signature_required
    def post(self): 
        try:
            # 获取入参
            body_data = request.get_data().decode('utf-8') # bytes to str
            json_data = json.loads(body_data)

            group_id = json_data.get('group_id', 'DEFAULT')
            user_id = json_data.get('user_id', '')
            name = json_data.get('name', '')
            mobile = json_data.get('mobile', '')
            memo = json_data.get('memo', '')
            image = json_data.get('image', '')

            logger.info("入参: %s %s %s %s %s %d"%(group_id, user_id, name, mobile, memo, len(image)))

            # 检查参数
            if user_id=='':
                return {"code": 9001, "msg": "缺少参数"}

            if len(image)>MAX_IMAGE_SIZE:
                return {"code": 9002, "msg": "图片数据太大"}

            if len(image)>0:
                # 定位人脸

                # 准备发队列消息
                request_id = helper.gen_request_id()

                request_msg = {
                    'api'          : 'face_locate',
                    'image'        : image,
                    'max_face_num' : 10,
                }

                # 在发redis消息前注册, 防止消息漏掉
                ps = helper.redis_subscribe(request_id)

                # 发布消息给redis
                r = helper.redis_publish_request(request_id, request_msg)
                if r is None:
                    logger.error("消息队列异常")
                    return {"code": 9099, "msg": "消息队列异常"}

                # 通过redis订阅等待结果返回
                ret = helper.redis_sub_receive(ps, request_id)               
                ret2 = json.loads(ret['data'].decode('utf-8'))
                if ret2['code']!=200:
                    return ret2

                face_num = ret2['data']['face_num']

                if face_num==0:
                    return {"code": 9003, "msg": "未定位到人脸"}


            # 更新用户信息
            r = dbport.user_update(group_id, user_id, name=name, mobile=mobile, memo=memo)
            if r==-1:
                return {"code": 9004, "msg": "user_id不存在"}

            if len(image)>0:
                # 添加人脸信息
                face_id = dbport.face_new("vgg_evo", [])
                dbport.user_add_face(group_id, user_id, face_id)

                # 异步生成特征值、训练
                request_msg = {
                    'api'      : 'face_features',
                    'image'    : image,
                    'face_id'  : face_id,
                    'group_id' : group_id,
                    'user_id'  : user_id,
                }
                # 发布消息给redis
                r = helper.redis_publish_request('NO_RECIEVER', request_msg)
                if r is None:
                    logger.error("消息队列异常")
                    return {"code": 9099, "msg": "消息队列异常"}

            else:
                face_id = 0

            return { "code" : 200, "msg" : "success", 'data' : { 'face_id'  : face_id } }

        except Exception as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }


# 人脸删除
class DbFaceRemove(Resource):
    @helper.signature_required
    def post(self): 
        try:
            # 获取入参
            body_data = request.get_data().decode('utf-8') # bytes to str
            json_data = json.loads(body_data)

            group_id = json_data.get('group_id', 'DEFAULT')
            user_id = json_data.get('user_id', '')
            face_id = json_data.get('face_id', '')

            logger.info("入参: %s %s %s"%(group_id, user_id, face_id))

            # 检查参数
            if '' in (user_id, face_id):
                return {"code": 9001, "msg": "缺少参数"}

            # 检查用户信息
            r2 = dbport.user_face_list(group_id, user_id)
            if r2==-1:
                return {"code": 9002, "msg": "user_id不存在"}

            if face_id in r2:
                # 删除人脸数据
                dbport.user_remove_face(group_id, user_id, face_id)
                dbport.face_remove(face_id)
            else:
                return {"code": 9003, "msg": "用户没有face_id人脸数据"}

            return { "code" : 200, "msg" : "success", 'data' : { 'type'  : 'SUCCESS' } }

        except Exception as e:
            logger.error("未知异常: %s" % e, exc_info=True)
            return {"code": 9999, "msg": "%s : %s" % (e.__class__.__name__, e) }
