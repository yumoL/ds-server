import redis
import time
import datetime
import ntplib
import json

host = '192.168.0.106' # redis server IP address
port = 6379            # redis server port
pool = redis.ConnectionPool(host=host, port=port)
r = redis.Redis(connection_pool=pool)
r.pubsub()

def get_ntp_time():
    '''get_ntp_time'''
    ntp_pool = 'uk.pool.ntp.org'
    call = ntplib.NTPClient()
    response = call.request(ntp_pool, version=3)
    t = datetime.datetime.fromtimestamp(response.orig_time)
    return t.strftime("%Y-%m-%d %H:%M:%S")

# publish a message
# I assume a loop is needed here
user_id = 1
user_name = "testX"
content = "blahblahblah"
msg = {"user_id":user_id,"user_name":user_name,"content":content,"npt_time":get_ntp_time()}
r.publish('chat',json.dumps(msg))

# disconnect the pool (logout)
# r.connection_pool.disconnect()
