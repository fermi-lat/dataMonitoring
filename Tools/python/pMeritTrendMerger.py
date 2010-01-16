#!/usr/bin/env python

from pLongTermTrendMaker import *


VARIABLE_DICT = {'Rate_EvtsBeforeCuts': (1, 'F'),
                 'Rate_EvtsBeforeCuts_err': (1, 'F'),
                 'Rate_EvtsBeforeCutsWithGAMMAFilter': (1, 'F'),
                 'Rate_EvtsBeforeCutsWithGAMMAFilter_err': (1, 'F'),
                 'Rate_TransientEvts': (1, 'F'),
                 'Rate_TransientEvts_err': (1, 'F'),
                 'Rate_DiffuseEvts': (1, 'F'),
                 'Rate_DiffuseEvts_err': (1, 'F'),
                 'Rate_SourceEvts': (1, 'F'),
                 'Rate_SourceEvts_err': (1, 'F'),
                 'CounterDiffRate_EvtsBeforeFilters': (1, 'F'),
                 'CounterDiffRate_EvtsBeforeFilters_err': (1, 'F'),
                 'Rate_MeritTriggerEngine': (16, 'F'),
                 'Rate_MeritTriggerEngine_err': (16, 'F'),
                 'Rate_GAMMAFilterAndTriggerEngine': (16, 'F'),
                 'Rate_GAMMAFilterAndTriggerEngine_err': (16, 'F'),
                 'Mean_PtLat': (1, 'F'),
                 'Mean_PtLat_err': (1, 'F'),
                 'Mean_PtLon': (1, 'F'),
                 'Mean_PtLon_err': (1, 'F'),
                 'Mean_PtMcIlwainL': (1, 'F'),
                 'Mean_PtMcIlwainL_err': (1, 'F'),
                 'Mean_PtMcIlwainB': (1, 'F'),
                 'Mean_PtMcIlwainB_err': (1, 'F'),
                 'Mean_PtSCzenith': (1, 'F'),
                 'Mean_PtSCzenith_err': (1, 'F'),
                 'TimeStampFirstEvt': (1, 'D'),
                 }


class pMeritTrendMerger:

    def __init__(self, fileListPath, outputFilePath, maxStartDate,
                 daysSpanned = 56):
        if not os.path.exists(fileListPath):
            print 'Creating the file list...'
            maxStartTime = utc2met(convert2sec(maxStartDate))
            minStartTime = maxStartTime - daysSpanned*24*3600
            minRunDuration = 1000
            runIntent = 'nomSciOps_diagEna'
            query = pDataCatalogQuery('MERITTREND', minStartTime, maxStartTime,
                                      minRunDuration, runIntent)
            query.dumpList(fileListPath)
            logFilePath = outputFilePath.replace('.root', '.log')
            logFile = file(logFilePath, 'w')
            logFile.writelines('File created by pMeritTrendMerger.py on %s.' %\
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
        print 'Done. %d file(s) found.' % len(self.FileList)

    def createArrays(self):
        print 'Creating arrays...'
        self.InputArrayDict  = {}
        self.OutputArrayDict = {}
        for (name, (length, type)) in VARIABLE_DICT.items():
            self.InputArrayDict[name] = array.array(type.lower(), [0.]*length)
            self.OutputArrayDict[name] = array.array(type.lower(), [0.]*length)
            suffix = '/%s' % type
            if length > 1:
                suffix = '[%d]%s' % (length, type)
            self.OutputTree.Branch(name, self.OutputArrayDict[name],
                                   '%s%s' % (name, suffix))
        print 'Done.'

    def copyArrays(self):
        for (name, (length, type)) in VARIABLE_DICT.items():
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
            for name in VARIABLE_DICT.keys():
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
    merger = pMeritTrendMerger('merit_norm_filelist.txt', 'merit_norm.root',
                               'Jan/15/2010 00:00:00', 56)
    merger.run()
