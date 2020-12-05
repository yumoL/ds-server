import time
import os
import sys

start_time = sys.argv[1]  
timeArray = time.strptime(start_time, "%Y-%m-%d %H:%M:%S")
start = int(time.mktime(timeArray))

#back up time lag: 100 (s)
backup_timelag = 100

while True:
    try:
        cur = time.time()
        if cur - start >= backup_timelag:
            os.system("mysqldump -u root -ppassword dsp > ~/dsp_backup/dsp.sql")
            start = time.time()

        else:
            time.sleep(backup_timelag)
    except:
        print("backup error...check!")
        time.sleep(5)
        
# usage: type in command line like this:
# python3 backup.py "2020-12-4 19:36:00"
