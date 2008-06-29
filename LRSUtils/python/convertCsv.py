#! /usr/bin/env python

import os

from lrsCalConverter import lrsCalConverter
from lrsTkrConverter import lrsTkrConverter

LRS_DATA_PATH = '/nfs/farm/g/glast/u42/ISOC-flight/FswDumps/reports/nonEvent'
FILE_PATTERNS = ['f1001', 'f1002']
TELEMETRY_DIR_PATH = '/nfs/slac/g/glast/users/glground/lbaldini/saa/telemetry'
OUTPUT_DIR_PATH = '/nfs/slac/g/glast/users/glground/lbaldini/saa/output'

filesList = []
for fileName in os.listdir(LRS_DATA_PATH):
    if 'f1001' in fileName:
        filePath = os.path.join(LRS_DATA_PATH, fileName)
        converter = lrsCalConverter(filePath, OUTPUT_DIR_PATH,\
                                    TELEMETRY_DIR_PATH)
        converter.convert()
        converter.close()
        del converter
    elif 'f1002' in fileName:
        filePath = os.path.join(LRS_DATA_PATH, fileName)
        converter = lrsTkrConverter(filePath, OUTPUT_DIR_PATH,\
                                    TELEMETRY_DIR_PATH)
        converter.convert()
        converter.close()
        del converter
