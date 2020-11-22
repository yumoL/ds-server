from server_socket import ServerSocket
from socket_wrapper import SocketWrapper
from threading import Thread
from config import *
from response_protocol import *
import json
from db import DB
import redis
from utils import get_ntp_time


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
        pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT)
        self.publisher = redis.Redis(connection_pool=pool)
        self.subscriber = self.publisher.pubsub()
        self.subscriber.subscribe([CHANNEL])

    def register(self, req_id, handler):
        # for each req type, register handler for it a dictionary
        self.req_handler_functions[req_id] = handler

    def startup(self):
        """accept connection from client"""
        while True:
            print('waiting connection from client...')
            soc, addr = self.server_socket.accept()
            print('Accepted connection from client')

            client_soc = SocketWrapper(soc)

            Thread(target=lambda: self.request_handler(client_soc)).start()
            Thread(target=lambda: self.sub_and_redirect()).start()

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
                # print(self.clients)
                del self.clients[username]
                # print(self.clients)
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
        ntp_time = get_ntp_time()
        pub_msg = {'user_id': self.clients[username]['user_id'],
                   "username": username, "msg": msg, 'ntp_time': ntp_time}
        self.publisher.publish(CHANNEL, json.dumps(pub_msg))

    def sub_and_redirect(self):
        """
        subscribe messages from redis and redirect them to clients
        """
        for item in self.subscriber.listen():
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


if __name__ == '__main__':
    Server().startup()
