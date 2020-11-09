from server_socket import ServerSocket
from socket_wrapper import SocketWrapper
from threading import Thread

class Server(object):

    def __init__(self):
        self.server_socket = ServerSocket()

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
            msg = client_soc.recv_data()

            if not msg:
                client_soc.close()
                break

            print(msg)
            client_soc.send_data('Server received: '+msg)


if __name__ == '__main__':
    Server().startup()
