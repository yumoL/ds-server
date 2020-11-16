import socket
from config import *
import json

# not really work, try to 

def fake_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 8070))

    while True:
        username = input('username: ')
        pwd = input('password: ')
        data = {'type': REQUEST_LOGIN, 'username': username,
                'pwd': pwd}
        client_socket.send(json.dumps(data).encode('utf-8'))
        recv_data = client_socket.recv(512)
        parse_data = json.loads(recv_data.decode('utf-8'))
        if (parse_data['result']=='1'):
            while True:
                msg = input('message: ')
                msg_data = {'type': REQUEST_CHAT, 'username':parse_data['username'], 'msg':msg}
                client_socket.send(json.dumps(msg_data).encode('utf-8'))
                recv_data = client_socket.recv(512)
                parse_data = json.loads(recv_data.decode('utf-8'))
                print(parse_data)

    client_socket.close()

if __name__ == "__main__":
    fake_client()
