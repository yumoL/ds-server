from config import *
import json


class RequestProtocol(object):
    """format response"""

    @staticmethod
    def request_login(username, pwd, relogin=False):
        data = {'type': REQUEST_LOGIN, 'username': username, 'pwd': pwd, 'relogin': relogin}
        return json.dumps(data)

    @staticmethod
    def request_chat(username, msg):
        data = {'type': REQUEST_CHAT, 'username': username, 'msg': msg}
        return json.dumps(data)

    @staticmethod
    def request_ip(invalid_ip=''):
        data = {'type': REQUEST_IP, 'invalid_ip': invalid_ip}
        return json.dumps(data)
