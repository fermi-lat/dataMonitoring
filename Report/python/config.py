#!/afs/slac/g/glast/isoc/flightOps/rhel3_gcc32/ISOC_PROD/bin/shisoc python2.5

"""@brief Configuration.
@author M.E. Monzani <monzani@slac.stanford.edu>
"""

import os
import sys

taskName = "launchReport"
taskVersion = "1.4"
ReportMainDir = '/afs/slac.stanford.edu/g/glast/ground/releases/volume03/Report'

doCleanup = True

reportDuration = {
    'daily' : '24',
    #'weekly' : '168',
    'weekly' : '72',
    'telemetry' : '24',
}

reportOutType = {
    'daily' : 'Report-24h',
    #'weekly' : 'Report-168h',
    'weekly' : 'Report-72h',
    'telemetry' : 'Telemetry-Report',
}

reportFileTypes = {
    'daily' : 'DailyReport',
    'weekly' : 'WeeklyReport',
    'telemetry' : 'TelemetryReport',
}

reportConfigFile = {
    'daily' : 'summaryReport.xml',
    'weekly' : 'summaryReport.xml',
    'telemetry' : 'telemetryReport.xml',
}

applicationName = {
    'daily' : 'pReportGenerator.py',
    'weekly' : 'pReportGenerator.py',
    'telemetry' : 'pTelemetryGenerator.py',
}

paddingSeconds = 1
ReportInstallDir = os.path.join(ReportMainDir,'python')
reportXml = os.path.join(ReportMainDir, 'xml')

dataCatBase = '/SRep/'
reportOutBase = '/nfs/slac/g/glast/ground/links/Documentation/SummaryReport' 
reportTempBase = '/afs/slac.stanford.edu/g/glast/ground/PipelineStaging6'

# Used to distinguish our variable names from the hoi polloi
nameManglingPrefix = 'SR'

python = sys.executable

if __name__ == "__main__":
    print ReportMainDir
