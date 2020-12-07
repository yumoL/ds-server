# server address
SERVER_IP = '127.0.0.1'
SERVER_PORT = 8070


# redis config
REDIS_HOST = '192.168.1.164'
REDIS_PORT = 6379
CHANNEL = 'chat'
ALIVE_CHANNEL = 'alive'
WAIT = 3 #report aliveness condition every 3s
RECONNECT_REDIS_WAIT = 3 #try to reconnect to redis every 3 s
MSG_LIST = 'msg'