from pymysql import connect, err
from config import *
import time

class DB(object):
    """
    maintain db
    """

    def __init__(self):
        self.conn = connect(host=DB_HOST, database=DB_NAME, port=DB_PORT,user=DB_USER,password=DB_PWD)
        print('database connection', self.conn.open)
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def get_user(self, username, pwd):
        while True:
            try:
                self.conn.ping(reconnect=True)
            except (ConnectionRefusedError, err.OperationalError):
                print('mysql error')
                time.sleep(3)
            else:
                break

        self.cursor.execute("select * from user_info where user_name=%s and pwd=%s", (username, pwd))
        query_result = self.cursor.fetchone()
        if not query_result:
            return None

        fields = [field[0] for field in self.cursor.description]

        user = dict()
        for field, value in zip(fields, query_result):
            user[field] = value
        
        return user

# if __name__ == '__main__':
#     db = DB()
#     data = db.get_user("test1", "111")
#     print(data)
#     db.close()