import pymysql
import redis
import json
from config import *

pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT)
ps = redis.Redis(connection_pool=pool)
p_s = ps.pubsub()
p_s.subscribe([CHANNEL])
#msgs = []

conn = pymysql.connect(host=DB_HOST, port=DB_PORT,
                       user=DB_USER, password=DB_PWD, db=DB_NAME)
cur = conn.cursor()

for item in p_s.listen():
    print("dumping data to mysql...")
    if type(item["data"]) == int:
        continue
    else:
        data_json = str(item["data"], encoding='utf-8')
        user_id = json.loads(data_json)["user_id"]

        # currently only one room, may expand to multiple rooms in the future
        room_id = 1
        timestamp = json.loads(data_json)["ntp_time"]
        msg = json.loads(data_json)["msg"]
#         print(user_id,room_id,timestamp,content)
        insert_sqli = "insert into chat_logs_info value({},{},'{}','{}');".format(
            user_id, room_id, str(timestamp), msg)
#         print(insert_sqli)
        cur.execute(insert_sqli)
        conn.commit()
