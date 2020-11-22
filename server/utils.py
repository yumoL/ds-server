import time
import datetime
import ntplib

def get_ntp_time():
    '''get_ntp_time'''
    ntp_pool = 'uk.pool.ntp.org'
    call = ntplib.NTPClient()
    response = call.request(ntp_pool, version=3)
    t = datetime.datetime.fromtimestamp(response.orig_time)
    return t.strftime("%Y-%m-%d %H:%M:%S")