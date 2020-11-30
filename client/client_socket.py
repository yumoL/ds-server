import socket
from config import *
import json

class ClientSocket(socket.socket):

    def __init__(self):
        super(ClientSocket, self).__init__(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, server_ip, server_port=SERVER_PORT):
        """
        connect server
        """
        super(ClientSocket, self).connect((server_ip, server_port))

    def recv_data(self):
        """
        receive data from server
        """
        data = self.recv(512).decode('utf-8')
        if data == '':
            return None
        return json.loads(data)

    def send_data(self, data):
        """
        send data
        """
        return self.send(data.encode('utf-8'))