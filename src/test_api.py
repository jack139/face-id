# coding:utf-8

import urllib3, json, base64, time, hashlib
from datetime import datetime
from async_api.utils import helper

urllib3.disable_warnings()

with open('../data/test/obama1.jpg', 'rb') as f:
    img_data = f.read()

with open('../data/test/obama1.jpg', 'rb') as f:
    img_data2 = f.read()


if __name__ == '__main__':

    body = {
        'image'    : base64.b64encode(img_data).decode('utf-8'),
        #'image2'    : base64.b64encode(img_data2).decode('utf-8'),
        'group_id' : 'debug',
        #'mobile_tail' : '1234',
        'user_id'  : 'obama2',
        #'name'     : 'obama',
        #'max_face_num' : 10,
        'request_id' : '93271821f9c74c1cf21b812fce29944e',
        'is_correct' : 1
    }

    appid = 'THISISTEST'
    unixtime = int(time.time())
    param_str = helper.gen_param_str(body)
    sign_str = '%s%s%s%s' % (appid, str(unixtime), 'F9OAZ4nbxYmz8NkLKJwivR5ZUasmePq7sL27v5HvHpY3wSHo', param_str)
    signature_str =  hashlib.sha256(sign_str.encode('utf-8')).hexdigest().upper()

    body['unixtime'] = unixtime
    body['appid'] = appid
    body['signature'] = signature_str

    body = json.dumps(body)
    #print(body)

    pool = urllib3.PoolManager(num_pools=2, timeout=180, retries=False)
    #url = 'http://172.17.0.3:5000/face/verify'
    #url = 'http://172.17.0.3:5000/face/locate'
    #url = 'http://172.17.0.3:5000/face/search'
    url = 'http://172.17.0.3:5000/face/feedback'
    #url = 'http://172.17.0.3:5000/facedb/face/reg'
    #url = 'http://172.17.0.3:5000/facedb/face/update'

    start_time = datetime.now()
    r = pool.urlopen('POST', url, body=body)
    print('[Time taken: {!s}]'.format(datetime.now() - start_time))

    print(r.status)
    if r.status==200:
        print(json.loads(r.data.decode('utf-8')))
    else:
        print(r.data)
