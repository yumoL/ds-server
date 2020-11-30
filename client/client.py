from client_socket import ClientSocket
from request_protocol import RequestProtocol
from threading import Thread
from config import *
from window_login import WindowLogin
from tkinter.messagebox import showinfo
from window_chat import WindowChat
import sys


class Client(object):

    def __init__(self):

        # init login window
        self.window_login = WindowLogin()
        self.window_login.on_login_button_click(self.send_login_data)
        self.window_login.on_window_closed(self.exit)

        # init chat window
        self.window_chat = WindowChat()
        self.window_chat.withdraw()
        self.window_chat.on_send_button_click(self.send_chat_data)
        self.window_chat.on_window_closed(self.exit)

        self.conn = ClientSocket()

        # response id and its corresponding handler function
        self.response_handler_functions = {}
        self.register(RESPONSE_LOGIN, self.response_login_handler)
        self.register(RESPONSE_CHAT, self.response_chat_handler)

        #logged in user
        self.username = None
        self.pwd = None

        # whether client is running or not
        self.is_running = True

        self.server_ip = ''
        #self.get_chat_server_ip()

    def register(self, response_id, handler):
        """
        for each response type, register handler for it a dictionary
        """
        self.response_handler_functions[response_id] = handler

    def get_chat_server_ip(self, reconnect=False):
        """
        request chat server ip from coordinator. In the case of the original chat 
        server becomes invalid, send the invalid ip to the coordinator
        """
        conn = ClientSocket()
        conn.connect(CO_IP, CO_PORT)
        if reconnect:
            request_text = RequestProtocol.request_ip(self.server_ip)
        else:
            request_text = RequestProtocol.request_ip()
        conn.send_data(request_text)
        server_ip = conn.recv_data().get('server_ip')
        print('received ip '+server_ip)
        conn.close()
        self.server_ip = server_ip

    def connect_chat_server(self, reconnect=False):
        """
        connect to chat server using ip received from coordinator
        """
        self.get_chat_server_ip(reconnect)
        self.conn = ClientSocket()
        self.conn.connect(self.server_ip)


    def startup(self):
         #self.conn.connect(self.server_ip)

        thread = Thread(target=self.response_handler)
        thread.daemon = True
        thread.start()
        self.window_login.mainloop()

    def send_login_data(self):
        username = self.window_login.get_username()
        self.pwd = self.window_login.get_pwd()

        request_text = RequestProtocol.request_login(username, self.pwd)

        self.conn.send_data(request_text)

    def send_chat_data(self):
        msg = self.window_chat.get_input()
        self.window_chat.clear_input()

        request_text = RequestProtocol.request_chat(self.username, msg)

        self.conn.send_data(request_text)

    def response_handler(self):
        """
        establish connection and continuously receive data from server
        """
        self.connect_chat_server()
        while self.is_running:
            response_data = self.conn.recv_data()

            #if server is dead, create connection again
            if response_data == None:
                self.connect_chat_server(reconnect=True)

                #re-login to new server
                relogin_request_text = RequestProtocol.request_login(
                    self.username, self.pwd)
                self.conn.send_data(relogin_request_text)
                response_data = self.conn.recv_data()

            # handle data based on response type
            handler_function = self.response_handler_functions[response_data['type']]

            if handler_function:
                handler_function(response_data)

    def response_login_handler(self, response_data):

        print('receive login result: ', response_data)
        result = response_data['result']
        if result == '1':
            self.username = response_data['username']

            # show chat window
            self.window_chat.set_title(self.username)
            self.window_chat.update()
            self.window_chat.deiconify()

            # hide login window
            self.window_login.withdraw()

        else:
            showinfo('Ohoo', 'Login failed, please try again')
            return

    def response_chat_handler(self, response_data):
        print('receive chat result: ', response_data)
        sender = response_data['username']
        msg = response_data['msg']
        send_time = response_data['send_time']
        self.window_chat.append_msg(sender, msg, send_time)

    def exit(self):
        """
        exit and release resource
        """
        self.is_running = False
        self.conn.close()
        self.window_login.destroy()

        sys.exit()


if __name__ == "__main__":
    Client().startup()
