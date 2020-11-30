import socket
from config import *

class CoorSocket(socket.socket):

    def __init__(self):
        super(CoorSocket, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((CO_IP, CO_PORT))
        self.listen(128) #maximum number of clients