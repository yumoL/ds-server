
class SocketWrapper(object):
    
    def __init__(self, soc):
        self.soc = soc

    def recv_data(self):
        return self.soc.recv(512).decode('utf-8')

    def send_data(self, message):
        return self.soc.send(message.encode('utf-8'))

    def close(self):
        self.soc.close()