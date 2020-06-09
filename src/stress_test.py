# -*- coding: utf-8 -*-
#
import time, hashlib, json, sys, random, base64
import threading
import urllib3

urllib3.disable_warnings()

TEST_SERVER = [
    '127.0.0.1:5000'
]

with open('../data/me/2.jpg', 'rb') as f:
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

def main_loop(tname, test_server):

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

        if r.status!=200:
            print(tname, test_server, '!!!!!! HTTP ret=', r.status, 'time_used=', time_used)
        else:
            print(tname, test_server, '200', 'time_used=', time_used, 'in_data_len=', len(body), 'out_data_len=', len(r.data))
    except Exception as e:
        print('Exception: ', type(e))

class MainLoop(threading.Thread):
    def __init__(self, rounds):
        threading.Thread.__init__(self)
        self._tname = None
        self._round = rounds

    def run(self):
        global count, mutex
        self._tname = threading.currentThread().getName()
        
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

    #线程池
    threads = []
        
    # 创建线程对象
    for x in range(0, int(sys.argv[1])):
        threads.append(MainLoop(int(sys.argv[2])))
    
    # 启动线程
    for t in threads:
        t.start()

    # 等待子线程结束
    for t in threads:
        t.join()  

    print("STRESS TEST exited: ", time.ctime())
