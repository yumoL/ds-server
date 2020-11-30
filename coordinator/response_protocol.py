from config import *
import json


class ResponseProtocol(object):
    """format response"""

    @staticmethod
    def response_ip(server_ip):
        data = {'type': RESPONSE_IP, 'server_ip': server_ip}
        return json.dumps(data)


   