
import sys
import os

import datetime


BASE_URL = 'http://www.swpc.noaa.gov/ftpdir/lists/xray/'
TARGET_DIR = 'goes'


def getUrl(year, month, day, resolution = 1):
    year  = '%d' % year
    month = '%s%d' % ('0'*(month < 10), month)
    day   = '%s%d' % ('0'*(day < 10), day)
    if resolution not in [1, 5]:
        sys.exit('Invalid resolution, abort.')
    return '%s%s%s%s_Gp_xr_%dm.txt' %\
        (BASE_URL, year, month, day, resolution)

def downloadFile(date, resolution = 1):
    url = getUrl(date.year, date.month, date.day, resolution)
    cmd = 'cd %s; wget %s' % (TARGET_DIR, url)
    targetPath = os.path.join(TARGET_DIR, os.path.basename(url))
    if os.path.exists(targetPath):
        print '%s exists. Skipping.' % targetPath
    else:
        print 'About to execute %s...' % cmd
        os.system(cmd)
        print 'Done.'

def download(startDate, stopDate):
    delta = datetime.timedelta(days = 1)
    date = startDate
    while date <= stopDate:
        downloadFile(date)
        date += delta


    


if __name__ == '__main__':
    if not os.path.exists(TARGET_DIR):
        print 'Creating folder %s' % TARGET_DIR
        os.makedirs(TARGET_DIR)
    download(datetime.date(2009, 12, 1), datetime.date(2010, 1, 27))
    
