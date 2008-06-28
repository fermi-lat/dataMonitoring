
import os
import logging

import lrsUtils


class telemetryTrendingInterface:

    def __init__(self, inputCsvFilePath, outputDirPath, dataBlockSize):
        if not os.path.exists(inputCsvFilePath):
            sys.exit('Could not find %s. Abort.' % inputCsvFilePath)
        self.InputCsvFileName = os.path.basename(inputCsvFilePath)
        self.OutputDirPath = outputDirPath
        self.FirstTimestamp = lrsUtils.getFirstTimestamp(inputCsvFilePath)
        self.LastTimestamp = lrsUtils.getLastTimestamp(inputCsvFilePath,\
                                                       dataBlockSize)
        self.BeginDate = lrsUtils.utc2string(self.FirstTimestamp)
        self.EndDate = lrsUtils.utc2string(self.LastTimestamp)
        logging.info('Data found between %s and %s.' %\
                         (self.BeginDate, self.EndDate))
        self.retrieveNavigationInformation()
        self.retrieveSAAInformation()
    
    def retrieveNavigationInformation(self):
        navFileName = self.InputCsvFileName.replace('.csv', '_nav.txt')
        navFilePath = os.path.join(self.OutputDirPath, navFileName)
        command = 'DiagRet.py --nav -b "%s" -e "%s" >> %s' %\
            (self.BeginDate, self.EndDate, navFilePath)
        logging.info('About to execute command "%s".' % command)
        os.system(command)

    def retrieveSAAInformation(self):
        saaFileName = self.InputCsvFileName.replace('.csv', '_saa.txt')
        saaFilePath = os.path.join(self.OutputDirPath, saaFileName)
        command = 'MnemRet.py --csv %s -b "%s" -e "%s" SACFLAGLATINSAA'%\
            (saaFilePath, self.BeginDate, self.EndDate)
        logging.info('About to execute command "%s".' % command)
        os.system(command)


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options]')
    parser.add_option('-o', '--output-dir', dest = 'o',
                      default = '.', type = str,
                      help = 'path to the output dir')
    parser.add_option('-d', '--data-block-size', dest = 'd',
                      type = int,
                      help = 'path to the output dir')
    (opts, args) = parser.parse_args()
    interface = telemetryTrendingInterface(args[0], opts.o, opts.d)

