from server_socket import ServerSocket
from socket_wrapper import SocketWrapper
from threading import Thread
from config import *
from response_protocol import *
import json
from db import DB
import redis
from utils import get_current_time
import sys
from time import sleep

class Server(object):

    def __init__(self):
        self.server_socket = ServerSocket()

        # request id and its corresponding handler function
        self.req_handler_functions = {}
        self.register(REQUEST_LOGIN, self.request_login_handler)
        self.register(REQUEST_CHAT, self.request_chat_handler)

        # save info of logged in user
        self.clients = {}

        # init db
        self.db = DB()

        # init redis
        self.pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT)
        self.redis = redis.Redis(connection_pool=self.pool,socket_keepalive=True)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe([CHANNEL])

    def register(self, req_id, handler):
        # for each req type, register handler for it a dictionary
        self.req_handler_functions[req_id] = handler

    def startup(self):
        """accept connection from client"""
        try:
            pub_condition_thread = Thread(target=self.pub_condition)
            sub_thread = Thread(target=self.sub_and_redirect)
            pub_condition_thread.daemon = True
            sub_thread.daemon = True
            pub_condition_thread.start()
            sub_thread.start()

            while True:  
                print('waiting connection from client...')
                soc, addr = self.server_socket.accept()
                print('Accepted connection from client')

                client_soc = SocketWrapper(soc)

                req_handler_thread = Thread(target=self.request_handler,args=(client_soc,))
                req_handler_thread.daemon = True
                req_handler_thread.start()
                
        except KeyboardInterrupt:
            sys.exit(0)


    def request_handler(self, client_soc):
        """handle client requests"""
        while True:
            # receive and send data
            recv_data = client_soc.recv_data()

            # receiving nothing means user left
            if not recv_data:
                self.remove_offline_user(client_soc)
                client_soc.close()
                break

            # get request type and call corresponding handler
            handler_function = self.req_handler_functions.get(
                recv_data['type'])
            if handler_function:
                handler_function(client_soc, recv_data)

    def remove_offline_user(self, client_soc):
        print('user left')
        for username, info in self.clients.items():
            if info['soc'] == client_soc:
                del self.clients[username]
                break

    def request_login_handler(self, client_soc, req_data):
        print('received longin req, processing')

        # obtain username and pwd
        username = req_data['username']
        pwd = req_data['pwd']

        # check credentials
        result, user_id, username = self.check_credential(username, pwd)

        # existing user=>save user info
        if result == '1':
            print('client soc')
            print(client_soc)
            self.clients[username] = {'user_id': user_id, 'soc': client_soc}

        # generate response
        response_text = ResponseProtocol.response_login(result, username)

        # response to user whether login succeeded or not
        client_soc.send_data(response_text)

    def check_credential(self, username, pwd):
        """
        check if the given user existed
        result:
            0: no such a user
            1: user is existing
        return (result, user_id, username)
        """
        print('checking user credentials')
        result = self.db.get_user(username, pwd)

        if not result:
            return '0', ''
        return '1', result['user_id'], result['user_name']

    def request_chat_handler(self, client_soc, req_data):
        print('received chat req, processing')

        # get message content
        username = req_data['username']
        msg = req_data['msg']

        # pub to redis
        ntp_time = get_current_time()
        pub_msg = {'user_id': self.clients[username]['user_id'],
                   "username": username, "msg": msg, 'ntp_time': ntp_time}
        try:
            recvd = self.redis.publish(CHANNEL, json.dumps(pub_msg))
            print('recvd', recvd)
        except redis.ConnectionError:
            print('error when publishing messages, could not connect to redis')
            self.send_error_msg_to_clients()

    def sub_and_redirect(self):
        """
        subscribe messages from redis and redirect them to clients
        """
        while True:
            try:
                for item in self.pubsub.listen():         
                    print('data',item['data'])
                    if type(item["data"]) == int:
                        continue
                    else:
                        data_json = str(item["data"], encoding='utf-8')
                        data = json.loads(data_json)
                        print('subscribed message')
                        print(data)
                        username = data['username']
                        msg = data['msg']
                        send_time = data['ntp_time']

                        response_text = ResponseProtocol.response_chat(
                            username, msg, send_time)
                        for u_name, info in self.clients.items():
                            info['soc'].send_data(response_text)
            except redis.ConnectionError:
                print('error when subcribing, could not connect to redis')
                self.send_error_msg_to_clients()

                # try to resubcribe the channel after reconnection
                while True:
                    try:
                        self.redis.ping()
                    except redis.ConnectionError:
                        print('not yet...')
                        sleep(RECONNECT_REDIS_WAIT)
                    else:
                        #self.redis = redis.Redis(connection_pool=self.pool,socket_keepalive=True)
                        self.pubsub = self.redis.pubsub()
                        self.pubsub.subscribe([CHANNEL])
                        print('resubscribe...')
                        print('channels', self.redis.pubsub_channels())
                        break
                
    

    def pub_condition(self):
        """
        publish heartbeat and the number of clients to redis
        """
        while True:
            try:
                while True:
                    condition = {'ip': SERVER_IP, 'clients': len(self.clients)}   
                    print(condition)       
                    self.redis.publish(ALIVE_CHANNEL, json.dumps(condition))
                    sleep(WAIT)
            except redis.ConnectionError:
                print('error when publishing heartbeat, could not connect to redis')
                sleep(10)



    def send_error_msg_to_clients(self):
        error_msg = ResponseProtocol.response_chat(
            username='System Admin', 
            msg='There are some problems in our servers, please wait...\n',
            send_time=get_current_time()
        )
        for u_name, info in self.clients.items():
            info['soc'].send_data(error_msg)
           

if __name__ == '__main__':
    Server().startup()
