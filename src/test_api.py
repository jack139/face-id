# coding:utf-8
from datetime import datetime
import urllib3, json, base64

urllib3.disable_warnings()

with open('../data/me/3.jpg', 'rb') as f:
    img_data = f.read()

with open('../data/me/2.jpg', 'rb') as f:
    img_data2 = f.read()


if __name__ == '__main__':

    body = {
        'image'    : base64.b64encode(img_data2).decode('utf-8'),
        #'image2'    : base64.b64encode(img_data2).decode('utf-8'),
        'group_id' : 'test',
        'user_id'  : 'gt',
        #'max_face_num' : 10
    }

    body = json.dumps(body)
    #print(body)

    pool = urllib3.PoolManager(num_pools=2, timeout=180, retries=False)
    #url = 'http://127.0.0.1:5000/face/verify'
    #url = 'http://127.0.0.1:5000/face/locate'
    url = 'http://127.0.0.1:5000/face/search'

    start_time = datetime.now()
    r = pool.urlopen('POST', url, body=body)
    print('[Time taken: {!s}]'.format(datetime.now() - start_time))

    print(r.status)
    print(json.loads(r.data.decode('utf-8')))
