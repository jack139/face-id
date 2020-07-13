# -*- coding: utf-8 -*-

from flask import Flask
from flask_restful import Api

from async_api.resources import *
from config.settings import BIND_ADDR, BIND_PORT, DEBUG_MODE

app = Flask(__name__)
api = Api(app)

@app.route('/')
def hello_world():
    return 'Hello World!'

# 对外同步api 测试
#api.add_resource(SyncTest, '/test')

# 人脸识别api，同步调用，异步处理（使用消息队列）
api.add_resource(FaceLocate, '/face/locate')
api.add_resource(FaceVerify, '/face/verify')
api.add_resource(FaceSearch, '/face/search')
api.add_resource(Feedback, '/face/feedback')

# 人脸特征库管理api，同步调用，同步处理
api.add_resource(DbFaceReg,    '/facedb/face/reg')  # 异步处理（使用消息队列）
api.add_resource(DbFaceUpdate, '/facedb/face/update')
api.add_resource(DbFaceRemove, '/facedb/face/remove')

api.add_resource(DbUserInfo,   '/facedb/user/info')
api.add_resource(DbUserFaceList,  '/facedb/user/face_list')
api.add_resource(DbUserCopy,   '/facedb/user/copy')
api.add_resource(DbUserRemove, '/facedb/user/remove')
api.add_resource(DbUserList,   '/facedb/user/list')

api.add_resource(DbGroupNew,    '/facedb/group/new')
api.add_resource(DbGroupRemove, '/facedb/group/remove')
api.add_resource(DbGroupList,   '/facedb/group/list')


if __name__ == '__main__':
    # 外部可见，出错时带调试信息（debug=True）
    # 转生产时，接口需要增减校验机制，避免非授权调用 ！！！！！！
    app.run(host=BIND_ADDR, port=BIND_PORT, debug=DEBUG_MODE)
