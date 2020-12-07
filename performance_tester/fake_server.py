import os
import redis
from config import *
from base64 import b64encode
import time
from threading import Thread
import socket

class FakeServer(object):
    """
    publish to redis for performance evaluation
    """

    def __init__(self):

        #redis
        self.pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT)
        self.redis = redis.Redis(
            connection_pool=self.pool, socket_keepalive=True)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe([CHANNEL]) 

        #socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((SERVER_IP, SERVER_PORT))
        self.server_socket.listen(128) #maximum number of clients

        self.client_socs = []


    def subscribe_and_redirect(self):
        # while True:
        #     for soc in self.client_socs:
        #         soc.send('ready to redirect'.encode('utf-8'))
        for item in self.pubsub.listen():
            for soc in self.client_socs:
                soc.send(item['data'])
                #print(item['data'])


    def stratup(self):
        sub_thread = Thread(target=self.subscribe_and_redirect)
        sub_thread.start()

        while True:       
            print('ready to accept connection...')
            client_soc, addr = self.server_socket.accept()
            self.client_socs.append(client_soc)
            print(len(self.client_socs))
            
            




if __name__ == "__main__":
    fs = FakeServer()
    fs.stratup()