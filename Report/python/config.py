#!/afs/slac/g/glast/isoc/flightOps/rhel3_gcc32/ISOC_PROD/bin/shisoc python2.5

"""@brief Configuration.
@author M.E. Monzani <monzani@slac.stanford.edu>
"""

import os
import sys

taskName = "launchReport"
taskVersion = "1.0"
fullTaskName = '-'.join([taskName, taskVersion])
ReportMainDir = '/afs/slac.stanford.edu/g/glast/ground/releases/volume03/Report'

doCleanup = True

reportDuration = {
    'daily' : '24',
    'weekly' : '168',
}

reportOutType = {
    'daily' : 'Report-24h',
    'weekly' : 'Report-72h',
}

shiftHours = {
    'A' : '00',
    'B' : '08',
    'C' : '16',
}

ReportInstallDir = os.path.join(ReportMainDir,'python')
reportXml = os.path.join(ReportMainDir, 'xml')
reportConfig = os.path.join(reportXml,'summaryReport.xml')

dataCatBase = '/Reports'
reportOutBase = '/nfs/slac/g/glast/ground/links/Documentation/SummaryReport' 
reportTempBase = '/afs/slac.stanford.edu/g/glast/ground/PipelineStaging6'

#dataSource = os.environ.get('DATASOURCE', 'LPA')
#dataCatDir = '/'.join([dataCatBase, dataSource])

python = sys.executable

if __name__ == "__main__":
    print ReportMainDir
