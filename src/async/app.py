# -*- coding: utf-8 -*-

from flask import Flask
from flask_restful import Api

from resources import *
from settings import *

app = Flask(__name__)
api = Api(app)

@app.route('/')
def hello_world():
    return 'Hello World!'

# 对外同步api
api.add_resource(SyncTest, '/test')

# 人脸识别内部api，异步调用
#api.add_resource(Face, '/face/search')

def run_server():
    # 外部可见，出错时带调试信息（debug=True）
    # 转生产时，接口需要增减校验机制，避免非授权调用 ！！！！！！
    app.run(host=BIND_ADDR, port=BIND_PORT, debug=DEBUG_MODE)

if __name__ == '__main__':
    run_server()
