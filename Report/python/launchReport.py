#!/afs/slac/g/glast/isoc/flightOps/rhel3_gcc32/ISOC_PROD/bin/shisoc python2.5

import os
import sys
import time

import config
import runner
import registerPrep
from pTimeConverter import convert2msec
from pTimeConverter import utc2met
from pReportGenerator import getPdfFileName

InstallDir = config.ReportInstallDir
 
reportType = os.environ['REPORT_TYPE']
timeStamp = os.environ['TIMESTAMP']

dateStruct = time.strptime(timeStamp,'%a %b %d %H:%M:%S UTC %Y')
shiftYear = dateStruct.tm_year
shiftDoy = dateStruct.tm_yday - 1
workDir = config.ReportMainDir
padSeconds = config.paddingSeconds

app = os.path.join(InstallDir,'pReportGenerator.py')
duration = config.reportDuration[reportType] 
endTime = '%s-%s 23:59:59' %(shiftYear,shiftDoy)
endTimeMs = convert2msec(endTime)
tStop = utc2met(endTimeMs/1000.)
tStart = tStop-float(duration)*3600 + padSeconds

configFile = config.reportConfig
tempDir = os.path.join(config.reportTempBase,'Report')

outDir = os.path.join(config.reportOutBase,config.reportOutType[reportType])
shiftYear = '%s' %(shiftYear)
outDir = os.path.join(outDir,shiftYear)

cmd = '''
cd %(workDir)s
%(app)s -c %(configFile)s -d %(tempDir)s -e "%(endTime)s" -s %(duration)s -p %(padSeconds)s
''' % locals()

status = runner.run(cmd)

if not status:
    fileName = getPdfFileName(endTimeMs,float(duration),configFile)
    fpath = os.path.join(tempDir,fileName)
    fullName = os.path.join(outDir,fileName)
    shortName = fileName.strip('.pdf').strip('summaryReport_')
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    cpCmd = '''
    cp %(fpath)s %(fullName)s 
    ''' % locals()
    cpStatus = runner.run(cpCmd)
    if not cpStatus:
        registerPrep.prep(fullName, shortName, tStart, tStop)
        pass
    pass
    
sys.exit(status or cpStatus)
