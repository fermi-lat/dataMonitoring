#!/usr/bin/env python

from pLongTermTrendMaker import *


VARIABLE_DICT = { 
    'OutF_Ratio_EvtSize_CompressedEvtSize': (1, 'F'),
    'Rate_CompressedEvtSizeInBytes': (1, 'F'),
    'TimeStampFirstEvt': (1, 'D'),
    'Bin_Start': (1, 'I'),
    'Bin_End': (1, 'I')
    }


class pDigiTrendMerger:

    def __init__(self, fileListPath, outputFilePath, maxStartDate,
                 daysSpanned = 56):
        if not os.path.exists(fileListPath):
            print 'Creating the file list...'
            maxStartTime = utc2met(convert2sec(maxStartDate))
            minStartTime = maxStartTime - daysSpanned*24*3600
            minRunDuration = 1000
            runIntent = ['nomSciOps_diagEna', 'nomSciOps']
            query = pDataCatalogQuery('DIGITREND', minStartTime, maxStartTime,
                                      minRunDuration, runIntent)
            query.dumpList(fileListPath)
            logFilePath = outputFilePath.replace('.root', '.log')
            logFile = file(logFilePath, 'w')
            logFile.writelines('File created by pDigiTrendMerger.py on %s.' %\
                       time.asctime())
            logFile.writelines('\n\n')
            logFile.writelines('Selections for histogram merging:\n')
            logFile.writelines('- Start run between %s (UTC) and -%d d.\n' %\
                               (maxStartDate, daysSpanned))
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

    def createArrays(self):
        print 'Creating arrays...'
        self.InputArrayDict  = {}
        self.OutputArrayDict = {}
        for (name, (length, type)) in self.VariableDict.items():
            self.InputArrayDict[name] = array.array(type.lower(), [0.]*length)
            self.OutputArrayDict[name] = array.array(type.lower(), [0.]*length)
            suffix = '/%s' % type
            if length > 1:
                suffix = '[%d]%s' % (length, type)
            self.OutputTree.Branch(name, self.OutputArrayDict[name],
                                   '%s%s' % (name, suffix))
        print 'Done.'

    def copyArrays(self):
        for (name, (length, type)) in self.VariableDict.items():
            for i in range(length):
                self.OutputArrayDict[name][i] = self.InputArrayDict[name][i]

    def run(self, local = False):
        self.OutputFile = ROOT.TFile(self.OutputFilePath, 'RECREATE')
        self.OutputTree = ROOT.TTree('Time', 'Time')
        self.createArrays()
        for filePath in self.FileList:
            print 'Looping over %s...' % filePath
            if local:
                rootFile = ROOT.TFile(filePath)
            else:
                rootFile = ROOT.TXNetFile(filePath)
            rootTree = rootFile.Get('Time')
            for name in self.VariableDict.keys():
                rootTree.SetBranchAddress(name, self.InputArrayDict[name])
            numEntries = rootTree.GetEntries()
            for i in xrange(numEntries):
                rootTree.GetEntry(i)
                self.copyArrays()
                self.OutputTree.Fill()
            rootFile.Close()
        self.OutputFile.cd()
        self.OutputTree.Write()
        self.OutputFile.Close()
        print 'Done.'

        
if __name__ == '__main__':
    merger = pDigiTrendMerger('digimerge_filelist.txt', 'digimerge.root',
                               'Feb/10/2014 00:00:00', 120)
    merger.run()
