import redis
import json
host = '192.168.0.106' # redis server IP address
port = 6379            # redis server port
pool = redis.ConnectionPool(host=host, port=port)
ps = redis.Redis(connection_pool=pool)
p_s = ps.pubsub()
p_s.subscribe(['chat'])

for item in p_s.listen():
    if type(item["data"]) == int:
        continue
    else:
        msg_json = str(item["data"],encoding='utf-8')
        # process msg_json as you want
        print(json.loads(msg_json))

# if needed to disconnect
# p_s.connection_pool.disconnect()
