from server_socket import ServerSocket
from socket_wrapper import SocketWrapper
from threading import Thread
from config import *
from response_protocol import *
import json
from db import DB

class Server(object):

    def __init__(self):
        self.server_socket = ServerSocket()

        #request id and its corresponding handler function
        self.req_handler_functions = {}
        self.register(REQUEST_LOGIN, self.request_login_handler)
        self.register(REQUEST_CHAT, self.request_chat_handler)
       
        #save info of logged in user 
        self.clients = {}

        #init db
        self.db = DB()

    def register(self, req_id, handler):
        #for each req type, register handler for it a dictionary
        self.req_handler_functions[req_id] = handler


    def startup(self):
        """accept connection from client"""
        while True:
            print('waiting connection from client...')
            soc, addr = self.server_socket.accept()
            print('Accepted connection from client')

            client_soc = SocketWrapper(soc)
            
            Thread(target=lambda: self.request_handler(client_soc)).start()
 

    def request_handler(self, client_soc):
        """handle client requests""" 
        while True:
            #receive and send data
            recv_data = client_soc.recv_data()

            #receiving nothing means user left
            if not recv_data:
                self.remove_offline_user(client_soc)
                client_soc.close()
                break

            #get request type and call corresponding handler
            handler_function = self.req_handler_functions.get(recv_data['type'])
            if handler_function:
                handler_function(client_soc, recv_data)


    def remove_offline_user(self, client_soc):
        print('user left')
        for username, info in self.clients.items():
            if info['soc'] == client_soc:
                print(self.clients)
                del self.clients[username]
                print(self.clients)
                break


    def request_login_handler(self, client_soc, req_data):
        print('received longin req, processing')

        #obtain username and pwd
        username = req_data['username']
        pwd = req_data['pwd']

        #check credentials
        result, username = self.check_credential(username, pwd)

        #existing user=>save user info
        if result == '1':
            print('client soc')
            print(client_soc)
            self.clients[username] = {'soc': client_soc}

        #generate response
        response_text = ResponseProtocol.response_login(result, username)

        #response to user whether login succeeded or not
        client_soc.send_data(response_text)


    def check_credential(self, username, pwd):
        """
        check if the given user existed
        result:
            0: no such a user
            1: user is existing
        return (result, username)
        """
        print('checking user credentials')
        result = self.db.get_user(username, pwd)
        
        if not result:
            return '0',''
        return '1', result['user_name']


    def request_chat_handler(self, client_soc, req_data):
        print('received chat req, processing')

        #get message content
        username = req_data['username']
        msg = req_data['msg']

        #TODO: publish to pub/sub middleware?
        
        #generate response
        response_text = ResponseProtocol.response_chat(username, msg)

        #send response to users
        for u_name, info in self.clients.items():
            if username == u_name:
                continue
            info['soc'].send_data(response_text)
        print(req_data)



if __name__ == '__main__':
    Server().startup()
