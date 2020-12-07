import os
import redis
from config import *
from base64 import b64encode
import time
from threading import Thread, Lock
import socket

class MultipleFakeServer(object):
    """
    spawn multiple servers and let them subscibe to the same redis channel
    """

    def __init__(self, server_num, msg_num):

        #redis
        self.pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT)

        self.lock = Lock()
        self.time_sep = []

        self.server_num = server_num
        self.msg_num = msg_num

    def append_to_time(self, time_value):
        """
        record used time of a single server to a list
        """
        while self.lock.locked():
            continue
            
        self.lock.acquire()
        self.time_sep.append(time_value)
        self.lock.release()

        

    def subscribe(self):
             
        r = redis.Redis(
            connection_pool=self.pool, socket_keepalive=True)
        pubsub = r.pubsub()
        pubsub.subscribe([CHANNEL]) 
        print('thread started')
        start = 0
        end = 0
        for item in pubsub.listen():
            data = item['data']
            if type(item['data']) == int:
                continue
            if item['data'].decode('utf-8')=='ready':
                start = time.perf_counter()
            if item['data'].decode('utf-8')=='finish':
                end = time.perf_counter()
                break
        
        if end-start < 1000:
            self.append_to_time(end - start)


    def strat(self):
        threads = []
        for i in range(self.server_num):
            server_thread = Thread(target=self.subscribe)
            threads.append(server_thread)
            server_thread.start()
        [thread.join() for thread in threads]

        with open(f'{self.server_num}_{self.msg_num}.txt', "a+") as file:
            file.write('\n'.join([str(content) for content in self.time_sep]))
            file.close()
           

if __name__ == "__main__":
    mfs = MultipleFakeServer(50, 10000)
    mfs.strat()
