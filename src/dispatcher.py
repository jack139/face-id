# -*- coding: utf-8 -*-

# 后台调度程序，轮询kafka，异步执行，redis返回结果

import sys, json, time
from kafka import KafkaConsumer

from async_api.utils import helper
from async_api import logger


if __name__ == '__main__':
    while 1:
        consumer = KafkaConsumer('synchronous-asynchronous-queue', bootstrap_servers=['localhost:9092'])
        for message in consumer:
            # message value and key are raw bytes -- decode if necessary
            msg_body = json.loads(message.value.decode('utf-8'))
            print(msg_body)

            time.sleep(1)

            # 收到消息
            helper.redis_publish(msg_body['rid'], 'Hello world.')
