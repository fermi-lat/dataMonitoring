#!/afs/slac/g/glast/isoc/flightOps/rhel3_gcc32/ISOC_PROD/bin/shisoc python2.5

import os
import sys
import time

timeStamp = os.environ['TIMESTAMP']

dateStruct = time.strptime(timeStamp,'%a %b %d %H:%M:%S UTC %Y')
shiftYear = dateStruct.tm_year
shiftDoy = dateStruct.tm_yday - 1
if  dateStruct.tm_yday == 1:
    shiftYear = shiftYear-1
    newDateStr = 'Dec 31 %s' % shiftYear  
    newDate = time.strptime(newDateStr,'%b %d %Y')
    shiftDoy = newDate.tm_yday

print shiftYear
print shiftDoy
