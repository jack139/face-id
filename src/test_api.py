# coding:utf-8
from datetime import datetime
import urllib3, json, base64

urllib3.disable_warnings()

with open('../data/me/photo_s.jpg', 'rb') as f:
    img_data = f.read()


if __name__ == '__main__':

    body = {
        'image'    : base64.b64encode(img_data).decode('utf-8'),
        'group_id' : 'test',
    }

    body = json.dumps(body)
    #print(body)

    pool = urllib3.PoolManager(num_pools=2, timeout=180, retries=False)
    url = 'http://127.0.0.1:5000/face/search'

    start_time = datetime.now()
    r = pool.urlopen('POST', url, body=body)
    print('[Time taken: {!s}]'.format(datetime.now() - start_time))

    print(r.status)
    print(json.loads(r.data.decode('utf-8')))