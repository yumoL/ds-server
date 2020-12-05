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
from log import Log
import pickle


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
        self.redis = redis.Redis(
            connection_pool=self.pool, socket_keepalive=True)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe([CHANNEL])

        self.log = Log('server.log')
        self.log.log_c_and_f('INFO', 'start logging')

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
                self.log.log_c_and_f(
                    'DBEUG', f'Accepted connection from client {addr}')

                client_soc = SocketWrapper(soc)

                req_handler_thread = Thread(
                    target=self.request_handler, args=(client_soc,))
                req_handler_thread.daemon = True
                req_handler_thread.start()

        except KeyboardInterrupt:
            self.log.log_c_and_f('DEBUG', 'server existed')
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

        for username, info in self.clients.items():
            if info['soc'] == client_soc:
                self.log.log_c_and_f('DEBUG', f'user {username} left')
                del self.clients[username]
                break

    def request_login_handler(self, client_soc, req_data):
        self.log.log_c_and_f('DEBUG', 'processing login request')

        # obtain username and pwd
        username = req_data['username']
        pwd = req_data['pwd']
        relogin = req_data['relogin']

        # check credentials
        result, user_id, username = self.check_credential(username, pwd)

        # existing user=>save user info
        if result == '1':
            self.clients[username] = {'user_id': user_id, 'soc': client_soc}
            self.log.log_c_and_f(
                'DEBUG', f'Accepted login request from {username}')

        # generate response
        response_text = ResponseProtocol.response_login(result, username)

        # response to user whether login succeeded or not
        client_soc.send_data(response_text)

        # send chat history (do not send history when user is redirected here due to failure of another chat server)
        if result == '1' and relogin == False:
            self.redirect_history(client_soc)

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
            self.redis.publish(CHANNEL, json.dumps(pub_msg))
            self.log.log_c_and_f(
                'DEBUG', f'publish {msg} from {username} to {CHANNEL}')

        except redis.ConnectionError:
            self.log.log_c_and_f(
                'ERROR', 'error when publishing messages, could not connect to redis')
            self.send_error_msg_to_clients()

    def sub_and_redirect(self):
        """
        subscribe messages from redis and redirect them to clients
        """
        while True:
            try:
                self.log.log_c_and_f('DEBUG', f'listening on {CHANNEL}')
                for item in self.pubsub.listen():
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
                            self.log.log_c_and_f(
                                'DEBUG', f'redirect {msg} to {u_name}')
                            info['soc'].send_data(response_text)
            except redis.ConnectionError:
                self.log.log_c_and_f(
                    'ERROR', 'error when subcribing, could not connect to redis')
                self.send_error_msg_to_clients()

                # try to resubcribe the channel after reconnection
                while True:
                    try:
                        self.log.log_c_and_f(
                            'DEBUG', 'try to reconnect to redis')
                        self.redis.ping()
                    except redis.ConnectionError:
                        print('not yet...')
                        sleep(RECONNECT_REDIS_WAIT)
                    else:
                        #self.redis = redis.Redis(connection_pool=self.pool,socket_keepalive=True)
                        self.pubsub = self.redis.pubsub()
                        self.pubsub.subscribe([CHANNEL])
                        self.log.log_c_and_f(
                            'DEBUG', 'reconnected to redis and re-subscribed the heartbeat channel')
                        print('channels', self.redis.pubsub_channels())
                        break

    def redirect_history(self, client_soc):
        """
        get chat history from redis queue and send them to user who just logs in
        """
        msg_list = []
        history_data = self.redis.lrange(MSG_LIST, 0, -1)
        for data_json in history_data:
            data_json = json.loads(data_json)
            username = data_json['username']
            msg = data_json['msg']
            send_time = data_json['ntp_time']

            response_data = {'username': username,
                             'msg': msg, 'send_time': send_time}
            msg_list.append(response_data)
        data_json = ResponseProtocol.response_chat_history(repr(msg_list))
        client_soc.send_data(data_json)

    def pub_condition(self):
        """
        publish heartbeat and the number of clients to redis
        """
        while True:
            try:
                while True:
                    condition = {'ip': SERVER_IP, 'clients': len(self.clients)}
                    self.log.write_log(
                        'f', 'DEBUG', f'publish heartbeat {condition}')
                    self.redis.publish(ALIVE_CHANNEL, json.dumps(condition))
                    sleep(WAIT)
            except redis.ConnectionError:
                self.log.log_c_and_f(
                    'ERROR', 'error when publishing heartbeat, could not connect to redis')
                sleep(RECONNECT_REDIS_WAIT)

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
