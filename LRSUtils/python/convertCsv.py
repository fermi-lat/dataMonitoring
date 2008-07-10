#! /usr/bin/env python

import os
import commands
import sys

from lrsCalConverter import lrsCalConverter
from lrsTkrConverter import lrsTkrConverter
from lrsAcdConverter import lrsAcdConverter

LRS_DATA_PATH = '/nfs/farm/g/glast/u42/ISOC-flight/FswDumps/reports/nonEvent/'
TELEMETRY_DIR_PATH = '/nfs/slac/g/glast/users/glground/lbaldini/saa/telemetry'
OUTPUT_DIR_PATH = '/nfs/slac/g/glast/users/glground/lbaldini/saa/output'

calFilesList = commands.getoutput('ls %s*/f1001*' % LRS_DATA_PATH).split('\n')
tkrFilesList = commands.getoutput('ls %s*/f1002*' % LRS_DATA_PATH).split('\n')
acdFilesList = commands.getoutput('ls %s*/f1003*' % LRS_DATA_PATH).split('\n')

print '%d tracker files found.' % len(tkrFilesList)
print '%d calorimeter files found.' % len(calFilesList)
print '%d acd files found.' % len(acdFilesList)

numFilesLeft = len(calFilesList)
for filePath in calFilesList:
    numFilesList -= 1
    converter = lrsCalConverter(filePath, OUTPUT_DIR_PATH, TELEMETRY_DIR_PATH)
    del converter
    print '%d CAL files left to look at.' % numFilesLeft
    
numFilesLeft = len(tkrFilesList)
for filePath in calFilesList:
    numFilesList -= 1
    converter = lrsTkrConverter(filePath, OUTPUT_DIR_PATH, TELEMETRY_DIR_PATH)
    del converter
    print '%d TKR files left to look at.' % numFilesLeft

numFilesLeft = len(acdFilesList)
for filePath in acdFilesList:
    numFilesList -= 1
    converter = lrsAcdConverter(filePath, OUTPUT_DIR_PATH, TELEMETRY_DIR_PATH)
    del converter
    print '%d ACD files left to look at.' % numFilesLeft

