import pymysql
import redis
import json
from config import *
from time import sleep
from log import Log
from threading import Thread

class Persist():

    def __init__(self):
        self.log = Log('dump.log')

        self.pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT)
        self.ps = redis.Redis(connection_pool=self.pool)
        self.p_s = self.ps.pubsub()
        self.p_s.subscribe([CHANNEL])
    #msgs = []

        self.conn = pymysql.connect(host=DB_HOST, port=DB_PORT,
                        user=DB_USER, password=DB_PWD, db=DB_NAME)
        self.cur = self.conn.cursor()

    def add_to_queue(self):
        """
        add published messages to redis list
        """
        while True:
            try:
                for item in self.p_s.listen():
                    self.log.log_c_and_f('DEBUG', 'caching data to redis queue...')
                    if type(item["data"]) == int:
                        continue
                    else:
                        data_json = str(item["data"], encoding='utf-8')
                        self.ps.rpush(MSG_LIST, data_json)
            except redis.ConnectionError:
                self.log.log_c_and_f('ERROR', 'could not connect to redis')

                # try to resubcribe the channel after reconnection
                while True:
                    try:
                        self.log.log_c_and_f('DEBUG', 'try to reconnect to redis')
                        self.ps.ping()
                    except redis.ConnectionError:
                        print('not yet...')
                        sleep(RECONNECT_REDIS_WAIT)
                    else:
                        self.p_s = self.ps.pubsub()
                        self.p_s.subscribe([CHANNEL])
                        self.log.log_c_and_f('DEBUG','reconnected to redis and re-subscribed the heartbeat channel')
                        print('channels', self.ps.pubsub_channels())
                        break

    def dump_to_db(self):
        """
        pop out messages and save them to mysql
        """
       
        while True:
            length = self.ps.llen(MSG_LIST)
            if length < 2:
                sleep(30)
                continue

            while True:
                try:
                    self.conn.ping(reconnect=True)
                except (ConnectionRefusedError, pymysql.err.OperationalError):
                    self.log.log_c_and_f('ERROR', 'mysql error')
                    sleep(10)
                else:
                    break

            for i in range(length-1):
                data = self.ps.lpop(MSG_LIST)
                data_json = json.loads(data)
                room_id = 1
                user_id = data_json['user_id']
                timestamp = data_json["ntp_time"]
                msg = data_json["msg"]
                #print(user_id,room_id,timestamp,content)
                insert_sqli = "insert into chat_logs_info value({},{},'{}','{}');".format(
                    user_id, room_id, str(timestamp), msg)
                self.log.log_c_and_f('DEBUG', insert_sqli)
                self.cur.execute(insert_sqli)
                self.conn.commit()

    def startup(self):
        try:
            dump_thread = Thread(target=self.dump_to_db) 
            dump_thread.daemon = True
            dump_thread.start()
            self.add_to_queue()
        except KeyboardInterrupt:
            self.log.log_c_and_f('DEBUG', 'server existed')


if __name__ == "__main__":
    persist = Persist()
    persist.startup()
        


