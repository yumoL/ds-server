from config import *
import json


class ResponseProtocol(object):
    """format response"""

    @staticmethod
    def response_login(result, username):
        data = {'type': RESPONSE_LOGIN, 'result':result, 'username': username}
        return json.dumps(data)

    @staticmethod
    def response_chat(username, msg, send_time):
        data = {'type': RESPONSE_CHAT, 'username': username, 'msg': msg, 'send_time': send_time}
        return json.dumps(data)

   