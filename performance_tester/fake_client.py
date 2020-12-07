import socket
import time
from threading import Thread, Lock

class FakeClient(object):

    def __init__(self, client_num, msg_num):
        """
        spawn multiple clients that connect to the same server
        client_num: client number
        msg_num: message number
        """
       
        self.lock = Lock()
        self.time_sep = []
        self.client_num = client_num
        self.msg_num = msg_num

    def append_to_time(self, time_value):
        while self.lock.locked():
            continue
            
        self.lock.acquire()
        self.time_sep.append(time_value)
        self.lock.release()

    def fake_client(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 8070))
        client_socket.send('I am here'.encode('utf-8'))
     
        i=1
        start = 0
        while True:
            recv_data = client_socket.recv(1024)
            if recv_data.decode('utf-8') == 'ready':
                start = time.perf_counter()
            i=i+1 
            if i == self.msg_num + 1:
                break
        end = time.perf_counter()
        if end-start < 1000:
            self.append_to_time(end-start)

    def start(self):
    
        threads = []
        for i in range(self.client_num):
            client_thread = Thread(target=self.fake_client)
            threads.append(client_thread)
            client_thread.start()
        [thread.join() for thread in threads]

        with open(f'{self.client_num}_{self.msg_num}.txt', "a+") as file:
            file.write('\n'.join([str(content) for content in self.time_sep]))
            file.close()
        

if __name__ == "__main__":
    fc = FakeClient(100, 10000)
    fc.start()
