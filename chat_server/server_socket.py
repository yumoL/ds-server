import socket
from config import *

class ServerSocket(socket.socket):

    def __init__(self):
        super(ServerSocket, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        super(ServerSocket, self).setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind((SERVER_IP, SERVER_PORT))
        self.listen(128) #maximum number of clients