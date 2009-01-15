#!/usr/bin/env python

import os
import sys


DATAMONROOT = os.environ['DATAMONROOT']


class pAlarmUnitTest:

    def joinPath(self, p):
        return os.path.join(DATAMONROOT, p)

    def run(self, inputFilePath, options = 'r', group = None,
            outputFilePath = None):
        print
        print 'Running test on %s...' % inputFilePath
        if not os.path.exists(inputFilePath):
            sys.exit('Could not find input file %s.' % inputFilePath)
        if group is None:
            print 'Try guessing the group from the name of the input file...'
            if 'calhist' in inputFilePath:
                group = 'calhist'
            elif 'acdpedsanalyzer' in inputFilePath:
                group = 'acdpeds_eor'
            elif 'calpedsanalyzer' in inputFilePath:
                group = 'calpeds_eor'
            elif 'calgainsanalyzer' in inputFilePath:
                group = 'calgains_eor'
            elif 'tkrtrend' in inputFilePath:
                group = 'trackermon_trend'
            else:
                group = os.path.basename(inputFilePath).split('_')[-1]
                group = group.replace('.root', '')
                group = group.replace('hist', '_eor')
                group = group.replace('trend', '_trend')
            print 'Detected group is "%s".' % group
        if outputFilePath is None:
            outputFilePath = os.path.join(os.curdir, group, 'alarms.xml')
        outputFolderPath = os.path.dirname(outputFilePath)
        if not os.path.exists(outputFolderPath):
            print 'Creating the output folder %s...' % outputFolderPath
            os.makedirs(outputFolderPath)
        cmd = 'pAlarmHandler.py -c %s -x %s -o %s %s %s' %\
              (self.joinPath('AlarmsCfg/xml/%s_alarms.xml' % group),
               self.joinPath('AlarmsCfg/xml/%s_alarms_exceptions.xml' % group),
               outputFilePath, options, inputFilePath)
        print 'About to execute command "%s"...' % cmd
        os.system(cmd)

    def runAll(self, inputFolderPath = None, options = '-r', wait = False):
        if inputFolderPath is None:
            inputFolderPath = os.path.curdir
        for fileName in os.listdir(inputFolderPath):
            if '.root' in fileName and ('hist' in fileName or \
                                        'trend' in fileName or \
                                        'analyzer' in fileName):
                filePath = os.path.join(inputFolderPath, fileName)
                self.run(filePath, options)
                if wait:
                    raw_input('Press enter to continue.')

                
if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options] rootFilePath')
    parser.add_option('-d', '--directory', dest = 'd',
                      default = False, action = 'store_true',
                      help = 'loop over the files in the folder')
    parser.add_option('-o', '--options', dest = 'o',
                      default = '-r', type = str,
                      help = 'options to be passed to the alarm handler.')
    (opts, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('Exactly one argument required.')
    inputPath = args[0]
    test = pAlarmUnitTest()
    if opts.d:
        test.runAll(inputPath, opts.o)
    else:
        test.run(inputPath, opts.o)
