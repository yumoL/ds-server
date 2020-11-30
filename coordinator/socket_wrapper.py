import json

class SocketWrapper(object):
    
    def __init__(self, soc):
        self.soc = soc

    def recv_data(self):
        data = self.soc.recv(512).decode('utf-8')
        if data == '':
            return None
        return json.loads(data)

    def send_data(self, message):
        return self.soc.send(message.encode('utf-8'))

    def close(self):
        self.soc.close()