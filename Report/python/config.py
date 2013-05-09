#!/afs/slac/g/glast/isoc/flightOps/rhel3_gcc32/ISOC_PROD/bin/shisoc python2.5

"""@brief Configuration.
@author M.E. Monzani <monzani@slac.stanford.edu>
"""

import os
import sys

taskName = "launchReport"
taskVersion = "1.8"
ReportMainDir = '/afs/slac.stanford.edu/g/glast/ground/releases/volume03/Report'

doCleanup = True

reportDuration = {
    'daily' : '24',
    'weekly' : '72',
    'telemetry' : '24',
    'trending' : '168',
}

reportOutType = {
    'daily' : 'SummaryReport/Report-24h',
    'weekly' : 'SummaryReport/Report-72h',
    'telemetry' : 'TelemetryReport/Report-24h',
    'trending' : 'WeeklyTrending/Report-168h',
}

reportFileTypes = {
    'daily' : 'DailyReport',
    'weekly' : 'WeeklyReport',
    'telemetry' : 'TelemetryReport',
    'trending' : 'WeeklyTrending',
}

reportConfigFile = {
    'daily' : 'summaryReport.xml',
    'weekly' : 'summaryReport.xml',
    'telemetry' : 'telemetryReport.xml',
    'trending' : 'weeklyTrending.xml',
}

applicationName = {
    'daily' : 'pReportGenerator.py',
    'weekly' : 'pReportGenerator.py',
    'telemetry' : 'pTelemetryGenerator.py',
    'trending' : 'pTelemetryGenerator.py',
}

paddingSeconds = 1
ReportInstallDir = os.path.join(ReportMainDir,'python')
reportXml = os.path.join(ReportMainDir, 'xml')

dataCatBase = '/SRep/'
reportOutBase = '/nfs/slac/g/glast/ground/links/Documentation' 

# Used to distinguish our variable names from the hoi polloi
nameManglingPrefix = 'SR'

python = sys.executable

if __name__ == "__main__":
    print ReportMainDir
