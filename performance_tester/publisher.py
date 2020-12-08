import os
import redis
from config import *
from base64 import b64encode
import time
from threading import Thread
import socket

class Publisher(object):
    """
    publish random messages (100 bytes) to redis for performance evaluation
    """

    def __init__(self):
        #redis
        self.pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT)
        self.redis = redis.Redis(
            connection_pool=self.pool, socket_keepalive=True)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe([CHANNEL]) 
        self.msg_num = 10000


    def publish(self):
        self.redis.publish(CHANNEL, 'ready')
        for i in range(self.msg_num):
            msg_bytes = os.urandom(100)
            self.redis.publish(CHANNEL, b64encode(msg_bytes).decode('utf-8'))
            time.sleep(0.02) #sleep 0.02s to avoid package loss because of the full socket buffer
            print(i)
        self.redis.publish(CHANNEL, 'finish')
        print('publish finished')



    def stratup(self):
        self.publish()
        

if __name__ == "__main__":
    publisher = Publisher()
    publisher.stratup()
