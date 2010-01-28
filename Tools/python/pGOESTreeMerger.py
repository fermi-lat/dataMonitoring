#!/usr/bin/env python

import os

from pLongTermTrendMaker import *
from pMeritTrendMerger   import pMeritTrendMerger

VARIABLE_DICT = {'OutF_Normalized_AcdHit_AcdTile': (128, 'F'),
                 'TimeStampFirstEvt': (1, 'D')
                 }

BRYSON_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

def getTelemetry(filePath, startDate, stopDate):
    command = 'MnemRet.py --csv %s -b "%s" -e "%s" SACFLAGISINSUN'%\
        (filePath, startDate, stopDate)
    logging.info('About to execute command "%s".' % command)
    os.system(command)



class pGOESTreeMerger(pMeritTrendMerger):

    def __init__(self, fileListPath, outputFilePath, minStartDate,
                 maxStartDate):
        if not os.path.exists(fileListPath):
            print 'Creating the file list...'
            minStartTime = utc2met(convert2sec(minStartDate))
            maxStartTime = utc2met(convert2sec(maxStartDate))
            minRunDuration = 1000
            runIntent = 'nomSciOps_diagEna'
            query = pDataCatalogQuery('DIGITREND', minStartTime, maxStartTime,
                                      minRunDuration, runIntent)
            query.dumpList(fileListPath)
            logFilePath = outputFilePath.replace('.root', '.log')
            logFile = file(logFilePath, 'w')
            logFile.writelines('File created by pGOESTreeMerger.py on %s.' %\
                                   time.asctime())
            logFile.writelines('\n\n')
            logFile.writelines('Selections for histogram merging:\n')
            logFile.writelines('- Start run between %s and %s UTC.\n' %\
                               (minStartDate, maxStartDate))
            logFile.writelines('- Minimum run duration: %s s.\n' %\
                               minRunDuration)
            logFile.writelines('- Run intent: "%s".\n' % runIntent)
            logFile.writelines('\n')
            logFile.writelines('See the file lists for details. Bye.')
            logFile.close()
        else:
            print 'File list %s found.' % fileListPath
            print 'Delete the file if you want to recreate it.'
        self.FileList = [line.strip('\n') for line in file(fileListPath, 'r')]
        self.FileList.sort()
        self.OutputFilePath = outputFilePath
        self.VariableDict = VARIABLE_DICT
        print 'Done. %d file(s) found.' % len(self.FileList)




if __name__ == '__main__':
    startDate = 'Jan/17/2010 00:00:00'
    stopDate  = 'Jan/22/2010 00:00:00'
    merger = pGOESTreeMerger('goes_digi_filelist.txt', 'goes_digi.root',
                             startDate, stopDate)
    merger.run()
    merger = pMeritTrendMerger('goes_merit_filelist.txt', 'goes_merit.root',
                               stopDate, 5)
    merger.run()
    getTelemetry('2010-01-17 00:00:00', '2010-01-22 00:00:00')
