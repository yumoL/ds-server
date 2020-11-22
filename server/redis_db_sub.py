import redis
import json
host = '192.168.0.106' # redis server IP address
port = 6379            # redis server port
pool = redis.ConnectionPool(host=host, port=port)
ps = redis.Redis(connection_pool=pool)
p_s = ps.pubsub()
p_s.subscribe(['chat'])
msgs = []

import pymysql
conn = pymysql.connect(host= '127.0.0.1', user= 'root', password= 'password', db= 'dsp')
cur = conn.cursor()

for item in p_s.listen():
    if type(item["data"]) == int:
        continue
    else:
        msg_json = str(item["data"],encoding='utf-8')
        user_id = json.loads(msg_json)["user_id"]
        room_id = 1
        timestamp = json.loads(msg_json)["npt_time"]
        content = json.loads(msg_json)["content"]
#         print(user_id,room_id,timestamp,content)
        insert_sqli = "insert into chat_logs_info value({},{},'{}','{}');".format(user_id,room_id,str(timestamp),content)
#         print(insert_sqli)
        cur.execute(insert_sqli)
        conn.commit()

# shutdown necessary connections after finishing the jobs
# p_s.connection_pool.disconnect()
# # 4. 关闭游标
# cur.close()
# # 5. 关闭连接
# conn.close()
