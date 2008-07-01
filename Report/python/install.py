#!/afs/slac/g/glast/isoc/flightOps/rhel3_gcc32/ISOC_PROD/bin/shisoc python2.5

import os
import sys

import expandTemplate
import config

taskName = config.taskName

taskFile = os.path.join(config.reportXml, taskName + '-' + config.taskVersion + '.xml')
template = os.path.join(config.reportXml, taskName + '.xml.template')

configuration = dict(config.__dict__)

registerScript = os.path.join(config.ReportInstallDir, 'registerStuff.py')
configuration['registerBody'] = open(registerScript).read()

expandTemplate.expand(template, taskFile, configuration)

taskFile = os.path.abspath(taskFile)
print >> sys.stderr, "Now upload:"
print >> sys.stderr, taskFile


