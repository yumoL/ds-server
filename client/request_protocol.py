from config import *
import json


class RequestProtocol(object):
    """format response"""

    @staticmethod
    def request_login(username, pwd):
        data = {'type': REQUEST_LOGIN, 'username': username, 'pwd':pwd}
        return json.dumps(data)

    @staticmethod
    def response_chat(username, msg):
        data = {'type': REQUEST_CHAT, 'username': username, 'msg': msg}
        return json.dumps(data)

   