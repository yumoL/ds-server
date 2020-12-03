import time
import datetime

def get_current_time():
    '''parse time'''
    t = datetime.datetime.now()
    return t.strftime("%Y-%m-%d %H:%M:%S")
