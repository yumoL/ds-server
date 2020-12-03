from socket import socket
import redis
from config import *
import json
from time import time, sleep
from threading import Thread
import sys
from coor_socket import CoorSocket
from socket_wrapper import SocketWrapper
from response_protocol import ResponseProtocol


class Coordinator:

    def __init__(self):
        self.beat_dict = {}

        self.coor_socket = CoorSocket()

        pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT)
        self.publisher = redis.Redis(connection_pool=pool)
        self.subscriber = self.publisher.pubsub()
        self.subscriber.subscribe([ALIVE_CHANNEL])

    def startup(self):
        try:
            update_thread = Thread(target=self.update)
            remove_silent_thread = Thread(target=self.remove_silent_servers)
            update_thread.daemon = True
            remove_silent_thread.daemon = True
            update_thread.start()
            remove_silent_thread.start()

            while True:
                print('waiting connection from client...')
                soc, addr = self.coor_socket.accept()
                print('Accepted connection from client')

                client_soc = SocketWrapper(soc)
                ip_thread = Thread(
                    target=self.send_valid_ip, args=(client_soc,))
                ip_thread.daemon = True
                ip_thread.start()

        except KeyboardInterrupt:
            sys.exit(0)

    def send_valid_ip(self, client_soc):
        """
        send a valid chat server ip to client 
        """
        while True:
            # receive and send data
            recv_data = client_soc.recv_data()

            # receiving nothing means user left
            if not recv_data:
                print('client left')
                client_soc.close()
                break

            # parse data
            request_type = recv_data['type']
            invalid_ip = recv_data['invalid_ip']

            # select the ip with the least clients
            if request_type == REQUEST_IP:
                server_ip = self.ip_with_least_clients(invalid_ip)

                # send a valid server ip
                response_text = ResponseProtocol.response_ip(server_ip)
                print('response')
                print(response_text)
                client_soc.send_data(response_text)

    def ip_with_least_clients(self, invalid_ip):
        """
        return ip of the server that has the least clients
        """
        if invalid_ip != '' and invalid_ip in self.beat_dict:
            """
            remove the invalid chat server ip immediately if the client asks for reconnection 
            by reporting an invalid ip
            """
            print('remove invalid ' + invalid_ip)
            del self.beat_dict[invalid_ip]
        return list(self.beat_dict)[0]
        

    def update(self):
        """
        update the last-checked time and client number of received ips
        """
        for item in self.subscriber.listen():
            if type(item['data']) == int:
                continue
            else:
                data_json = str(item["data"], encoding='utf-8')
                data = json.loads(data_json)
                server_ip = data['ip']
                clients = data['clients']
                self.beat_dict[server_ip] = {
                    'checked': time(), 'clients': clients}

    def remove_silent_servers(self):
        """
        remove invalid servers and sort the remaining servers based on their clients
        """
        print('start to remove...')
        while True:
            when = time() - CHECK_WAIT
            copy = self.beat_dict.copy()
            for ip in copy.keys():
                if copy[ip]['checked'] < when:
                    if self.beat_dict.get(ip) != None:
                        print('remove ' + ip)
                        del self.beat_dict[ip]
            
            # sort dict by the number of clients
            self.beat_dict = dict(sorted(self.beat_dict.items(), key=lambda item: item[1]['clients']))
            
            sleep(CHECK_WAIT)


if __name__ == "__main__":
    coor = Coordinator()
    coor.startup()
