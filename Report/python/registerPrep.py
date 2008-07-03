
import os
import sys

import config
import pipeline

def prep(fullName, shortName, tStart, tStop):
    """
    Deal with batch-side prep to register a file with the data catalog.
    Actual registration is done by a scriptlet (in registerStuff.py).
    This sets up some pipeline variables so the scriptlet knows what to do.
    """
    reportType = os.environ['REPORT_TYPE']
    fileType = config.reportFileTypes[reportType]
    dcGroup = fileType.upper()

    taskName = config.taskName
    taskVersion =  config.taskVersion
    creator = '-'.join([taskName, taskVersion])

    attributes = ':'.join([
        "nMetStart=%f" % tStart,
        "nMetStop=%f" % tStop,
        "sCreator=%s" % creator
    ])
    
    logiPath = '%s/%s:%s' % (config.dataCatBase, dcGroup, shortName)

    pipeline.setVariable('REGISTER_LOGIPATH', logiPath)
    pipeline.setVariable('REGISTER_FILETYPE', dcGroup)
    pipeline.setVariable('REGISTER_FILEPATH', fullName)
    pipeline.setVariable('REGISTER_ATTRIBUTES', attributes)
 
    return
