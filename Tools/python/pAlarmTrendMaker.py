#! /bin/env python

from pLongTermTrendMaker import *

sys.path.append('../../Report/python')
sys.path.append('../../Common/python')

from pTimeConverter import *



class pAlarmTrendMaker(pBaseFileAnalyzer):

    def __init__(self, fileListPath, outputFilePath, group, minStartTime,
                 maxStartTime = None):
        self.LabelList = []
        self.QuantityList = []
        pBaseFileAnalyzer.__init__(self, fileListPath, outputFilePath, group,
                                   minStartTime, maxStartTime)


    def run(self):
        for filePath in self.FileList:
            print 'Analyzing %s...' % filePath
            fileName = os.path.basename(filePath)
            self.Arrays['RunId'][0] = int(fileName.split('_')[0].strip('r'))
            #self.InputFile = None
            #self.OutputTree.Fill()
            #self.InputFile.Close()
        self.OutputFile.cd()
        self.OutputTree.Write()
        self.OutputFile.Close()



if __name__ == '__main__':
    MIN_START_TIME = utc2met(convert2sec('Nov/23/2008 00:00:00'))
    MAX_START_TIME = None
    trendMaker = pAlarmTrendMaker('ACDPEDSANALYZER.txt',
                                  'ACDPEDSANALYZER.root',
                                  MIN_START_TIME,
                                  MAX_START_TIME)
