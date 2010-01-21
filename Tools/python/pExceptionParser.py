#!/usr/bin/env python

from pLongTermTrendMaker import *
import time


GROUPS = ['FASTMONHISTALARM',
          'CALPEDSALARM',
          'CALGAINSALARM',
          'ACDPEDSALARM',
          'CALHISTALARM',
          'TKRTRENDALARM',
          'MERITHISTALARM',
          'RECONHISTALARM',
          'RECONTRENDALARM',
          'MERITTRENDALARM',
          'FASTMONTRENDALARM',
          'DIGITRENDALARM',
          'DIGIHISTALARM'
          ]


class pExceptionParser:

    def __init__(self, maxStartDate, daysSpanned):
        self.MaxStartDate = maxStartDate
        self.DaysSpanned = daysSpanned
        self.MaxStartTime = utc2met(convert2sec(self.MaxStartDate))
        self.MinStartTime = self.MaxStartTime - self.DaysSpanned*24*3600
        self.GroupDict = {}
        self.ViolationDict = {}

    def getFileList(self, group):
        fileListPath = '%s_filelist.txt' % group
        if not os.path.exists(fileListPath):
            print 'Creating the file list...'
            minRunDuration = 1000
            runIntent = 'nomSciOps_diagEna'
            query = pDataCatalogQuery(group, self.MinStartTime,
                                      self.MaxStartTime, minRunDuration,
                                      runIntent,
                                      site = 'SLAC /Data/Flight/Level1/LPA')
            query.dumpList(fileListPath)
        else:
            print 'File list %s found.' % fileListPath
            print 'Delete the file if you want to recreate it.'
        fileList = [line.strip('\n').strip()\
                    for line in file(fileListPath, 'r')]
        fileList.sort()
        print 'Done. %d file(s) found.' % len(fileList)
        return fileList

    def parseFile(self, group, filePath):
        print 'Parsing file %s...' % filePath
        for line in file(filePath):
            if line.strip().startswith('<plot'):
                plotName = line.split('name="')[-1].strip('">\n')
            elif line.strip().startswith('<alarm'):
               algorithm = line.split('function="')[-1].strip('">\n')
            elif 'violations' in line:
                baseKey = '%s_%s_%s' % (group, plotName, algorithm)
                if 'too much garbage following' in line:
                    line = line.replace(", '%s" % line.split(", '")[-1], ']')
                violationList = eval(line.split('value="')[-1].strip('"/>\n'))
                newViolationList = []
                for (i, violation) in enumerate(violationList):
                    if 'significance' in violation or \
                           ':' in violation or \
                           'value' in violation:
                        v = ''
                        for (j, piece) in enumerate(violation.split(',')):
                            if 'significance' not in piece and \
                                   ':' not in piece and \
                                   'value' not in piece:
                                v += '%s%s' % (','*(j!=0), piece)
                        v = v.lstrip(', ').rstrip(' ,')
                        if v not in newViolationList:
                            newViolationList.append(v)
                for (i, violation) in enumerate(newViolationList):
                    key = '%s -> "%s"' % (baseKey, violation)
                    if key in self.ViolationDict:
                        self.ViolationDict[key] += 1
                    else:
                        self.ViolationDict[key] = 1

    def run(self, outputFilePath):
        for group in GROUPS:
            print 'About to parse exceptions for group %s...' % group
            fileList = self.getFileList(group)
            self.GroupDict[group] = len(fileList)
            for filePath in fileList:
                self.parseFile(group, filePath)
        keys = self.ViolationDict.keys()
        keys.sort()
        outputFile = file(outputFilePath, 'w')
        print '** Parsing summary **'
        outputFile.writelines('** Parsing summary **\n')
        outputFile.writelines('\nCreated by pExceptionParser.py on %s.\n' %\
                              time.asctime())
        outputFile.writelines('Including runs over %d days before %s.\n\n' %\
                              (self.DaysSpanned, self.MaxStartDate))
        for key in keys:
            group = key.split('_')[0]
            line = '%s, violations = %d/%d' %\
                   (key, self.ViolationDict[key], self.GroupDict[group])
            print line
            outputFile.writelines('%s\n' % line)
        outputFile.close()
            


if __name__ == '__main__':
    p = pExceptionParser('Jan/15/2010 00:00:00', 30)
    p.run('violations.txt')
