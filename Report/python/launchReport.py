#!/afs/slac/g/glast/isoc/flightOps/rhel3_gcc32/ISOC_PROD/bin/shisoc python2.5

import os
import sys
import time

import config
import runner
#import registerPrep
from pTimeConverter import convert2msec
from pReportGenerator import getPdfFileName

InstallDir = config.ReportInstallDir
 
reportType = os.environ['REPORT_TYPE']
shiftType = os.environ['SHIFT_TYPE']
timeStamp = os.environ['TIMESTAMP']

dateStruct = time.strptime(timeStamp,'%a %b %d %H:%M:%S UTC %Y')
shiftYear = dateStruct.tm_year
shiftDoy = dateStruct.tm_yday
workDir = config.ReportMainDir

app = os.path.join(InstallDir,'pReportGenerator.py')
duration = config.reportDuration[reportType] 
endHour = config.shiftHours[shiftType]
endTime = '%s-%s %s:00:00' %(shiftYear,shiftDoy,endHour)
endTimeMs = convert2msec(endTime)
dirDate = '%s-%s' %(shiftYear,shiftDoy)

configFile = config.reportConfig
tempDir = os.path.join(config.reportTempBase,'Report')

outDir = os.path.join(config.reportOutBase,config.reportOutType[reportType])
shiftYear = '%s' %(shiftYear)
outDir = os.path.join(outDir,shiftYear)
outDir = os.path.join(outDir,dirDate)

cmd = '''
cd %(workDir)s
%(app)s -c %(configFile)s -d %(tempDir)s -e "%(endTime)s" -s %(duration)s
''' % locals()

status = runner.run(cmd)

if not status:
    fname = getPdfFileName(endTimeMs,float(duration),configFile)
    fpath = os.path.join(tempDir,fname)
    cpCmd = '''
    cp %(fpath)s %(outDir)s 
    ''' % locals()
    cpStatus = runner.run(cpCmd)
    if not cpStatus:
        #registerPrep.prep(reportType, realVerifyHistoFile)
        pass
    pass
    
sys.exit(status or cpStatus)
