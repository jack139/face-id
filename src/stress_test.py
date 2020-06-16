# -*- coding: utf-8 -*-
#
import time, hashlib, json, sys, random, base64
import threading
import urllib3
from async_api.utils import helper

urllib3.disable_warnings()

TEST_SERVER = [
    '172.17.0.3:5000'
    #'10.10.6.197:5000',
]

with open('../data/me/idcard40.jpg', 'rb') as f:
    img_data = f.read()

with open('../data/me/3.jpg', 'rb') as f:
    img_data2 = f.read()

BODY = {
    'image'    : base64.b64encode(img_data).decode('utf-8'),
    #'image2'    : base64.b64encode(img_data2).decode('utf-8'),
    'group_id' : 'test',
    #'user_id'  : 'gt',
    #'max_face_num' : 10
}

appid = 'THISISTEST'
unixtime = int(time.time())
param_str = helper.gen_param_str(BODY)
sign_str = '%s%s%s%s' % (appid, str(unixtime), 'F9OAZ4nbxYmz8NkLKJwivR5ZUasmePq7sL27v5HvHpY3wSHo', param_str)
signature_str =  hashlib.sha256(sign_str.encode('utf-8')).hexdigest().upper()

BODY['unixtime'] = unixtime
BODY['appid'] = appid
BODY['signature'] = signature_str

SCORE = {}

def main_loop(tname, test_server):
    global SCORE

    body = json.dumps(BODY)
    #print(body)

    pool = urllib3.PoolManager(num_pools=2, timeout=180, retries=False)
    #url = 'http://%s/face/verify'%test_server
    #url = 'http://%s/face/locate'%test_server
    url = 'http://%s/face/search'%test_server
    #url = 'http://%s/test'%test_server

    tick_start = time.time()

    try:
        print(url)
        #print header

        r = pool.urlopen('POST', url, body=body)
        #print(r.data)
        #print(r.status)

        tick_end = time.time()

        time_used =  int((tick_end-tick_start)*1000)
        SCORE[tname] += time_used

        if r.status!=200:
            print(tname, test_server, '!!!!!! HTTP ret=', r.status, 'time_used=', time_used)
        else:
            print(tname, test_server, '200', 'time_used=', time_used, 'in_data_len=', len(body), 'out_data_len=', len(r.data))
    except Exception as e:
        print("异常: %s : %s" % (e.__class__.__name__, e))

class MainLoop(threading.Thread):
    def __init__(self, rounds):
        threading.Thread.__init__(self)
        self._tname = None
        self._round = rounds

    def run(self):
        global count, mutex, SCORE
        self._tname = threading.currentThread().getName()
        SCORE[self._tname] = 0        

        print('Thread - %s started.' % self._tname)

        #while 1:
        for x in range(0, self._round):
            for y in TEST_SERVER:
                main_loop(self._tname, y)

            # 周期性打印日志
            time.sleep(random.randint(0,1))
            sys.stdout.flush()


if __name__=='__main__':
    if len(sys.argv)<3:
        print("usage: python stress_test.py <thread_num> <round_per_thread>")
        sys.exit(2)

    print("STRESS TEST started: " , time.ctime())

    thread_num = int(sys.argv[1])
    round_per_thread = int(sys.argv[2])

    #线程池
    threads = []
        
    # 创建线程对象
    for x in range(0, thread_num):
        threads.append(MainLoop(round_per_thread))
    
    # 启动线程
    for t in threads:
        t.start()

    # 等待子线程结束
    for t in threads:
        t.join()  

    total = 0
    for i in SCORE.keys():
        total += SCORE[i]
        print('%s - %.3f'%( i, SCORE[i]/round_per_thread ))

    print('Average: %.3f'%(total/(thread_num*round_per_thread)) )

    print("STRESS TEST exited: ", time.ctime())
