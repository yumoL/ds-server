import time
import datetime
import ntplib

def get_ntp_time():
    '''get_ntp_time'''
    recv = False    # ntp response flag
    attmpt = 0      # number of attempts
    while recv == False and attmpt <= 3:
        try:
            ntp_pool = 'pool.ntp.org'
            call = ntplib.NTPClient()
            response = call.request(ntp_pool, version=3)
            t = datetime.datetime.fromtimestamp(response.orig_time)
            recv=True
        except:
            # when no response from ntp server => wait a bit and retry
            time.sleep(2)   
            #print("wrong") could be used for testing 
        attmpt += 1
        
    if recv:
        return t.strftime("%Y-%m-%d %H:%M:%S")
    else:
        # None returning should be taken care of
        return None
