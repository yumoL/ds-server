# server address
SERVER_IP = '127.0.0.1'
SERVER_PORT = 8070

# protocol
REQUEST_LOGIN = '0001'
REQUEST_CHAT = '0002'
RESPONSE_LOGIN = '1001'
RESPONSE_CHAT = '1002'
RESPONSE_CHAT_HISTORY = '1003'

# database config
DB_HOST = '192.168.1.164'
DB_PORT = 3306
DB_NAME = 'dsp'
DB_USER = 'yumo'
DB_PWD = 'password'

# redis config
REDIS_HOST = '192.168.1.164'
REDIS_PORT = 6379
CHANNEL = 'chat'
ALIVE_CHANNEL = 'alive'
WAIT = 3 #report aliveness condition every 3s
RECONNECT_REDIS_WAIT = 3 #try to reconnect to redis every 3 s
MSG_LIST = 'msg'