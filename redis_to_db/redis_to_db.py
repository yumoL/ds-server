import pymysql
import redis
import json
from config import *
from time import sleep
from log import Log

log = Log('dump.log')

pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT)
ps = redis.Redis(connection_pool=pool)
p_s = ps.pubsub()
p_s.subscribe([CHANNEL])
#msgs = []

conn = pymysql.connect(host=DB_HOST, port=DB_PORT,
                       user=DB_USER, password=DB_PWD, db=DB_NAME)
cur = conn.cursor()

while True:
    try:
        for item in p_s.listen():
            log.log_c_and_f('DEBUG', 'dumping data to mysql...')
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
  
                cur.execute(insert_sqli)
                conn.commit()
    except redis.ConnectionError:
        log.log_c_and_f('ERROR', 'could not connect to redis')

        # try to resubcribe the channel after reconnection
        while True:
            try:
                log.log_c_and_f('DEBUG', 'try to reconnect to redis')
                ps.ping()
            except redis.ConnectionError:
                print('not yet...')
                sleep(RECONNECT_REDIS_WAIT)
            else:
                p_s = ps.pubsub()
                p_s.subscribe([CHANNEL])
                log.log_c_and_f('DEBUG','reconnected to redis and re-subscribed the heartbeat channel')
                print('channels', ps.pubsub_channels())
                break

