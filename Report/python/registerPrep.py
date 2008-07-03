
import os
import sys

import config
import variables

def prep(fullName, shortName, tStart, tStop):
    """
    Deal with batch-side prep to register a file with the data catalog.
    Actual registration is done by a scriptlet (in registerStuff.py).
    This sets up some pipeline variables so the scriptlet knows what to do.
    """

    taskName = config.taskName
    taskVersion =  config.taskVersion
    creator = '-'.join([taskName, taskVersion])

    reportType = os.environ['REPORT_TYPE']
    fileType = config.reportFileTypes[reportType]

    variables.setVar(reportType, 'format', 'pdf')
    variables.setVar(reportType, 'fileType', fileType)
    variables.setVar(reportType, 'path', config.dataCatBase)
    variables.setVar(reportType, 'group', fileType.upper())
    variables.setVar(reportType, 'site', 'SLAC')
    variables.setVar(reportType, 'fullName', fullName)
    variables.setVar(reportType, 'creator', creator)
    variables.setVar(reportType, 'shortName', shortName)
    variables.setVar(reportType, 'tStart', tStart)
    variables.setVar(reportType, 'tStop', tStop)

    return
