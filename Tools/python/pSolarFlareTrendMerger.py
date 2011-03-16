#! /bin/env python

import os
import ROOT
import numpy

import sys
sys.path.append('../../Report/python')
from pTimeConverter import *

BASE_PATH = '/afs/slac.stanford.edu/g/glast/ground/bin/datacat'
BASE_COMMAND = 'find'
DEFAULT_SITE = 'SLAC_XROOT /Data/Flight/Level1/LPA'
DEFAULT_SORT = 'nRun'

VARIABLE_DICT = {
    'Digi_Trend_Bin_Start'                              : ('l', ''     ),
    'Digi_Trend_TimeStampFirstEvt'                      : ('D', ''     ),
    'Digi_Trend_TimeStampLastEvt'                       : ('D', ''     ),
    'Digi_Trend_Rate_AcdDigis'                          : ('F', ''     ),
    'Digi_Trend_Rate_FswFilters_GAMMA'                  : ('F', ''     ),
    'Digi_Trend_OutF_Normalized_AcdHit_AcdTile'         : ('F', '[128]'),
    'Digi_Trend_Rate_AnyAcdVeto_AcdTile'                : ('F', '[128]'),
    'FastMon_Trend_Mean_FastMon_SpaceCraft_RockAngle'   : ('F', ''     ),
    'Merit_Trend_OutF_NormRateTransientEvts'            : ('F', ''     ),
    'Merit_Trend_Rate_TransientEvts'                    : ('F', ''     ),
    'Merit_Trend_Rate_TransientEvtsBelowZenithTheta100' : ('F', ''     )
    }

GROUP_LIST  = ['DIGITREND', 'FASTMONTREND', 'MERITTREND']


def dumpVarDict(filePath):
    rootFile = ROOT.TFile(filePath)
    rootTree = rootFile.Get('Time')
    for branch in rootTree.GetListOfBranches():
        branchName  = branch.GetName()
        branchType  = branch.GetTitle().split('/')[-1]
        branchShape = branch.GetTitle().split('/')[0].strip(branchName)
        print "'%s': ('%s', '%s')," % (branchName, branchType, branchShape)


class pDataCatalogQuery:

    def __init__(self, minStartTime = None, maxStartTime = None,
                 minDuration = 10):
        self.Command = BASE_PATH
        self.Command += ' %s' % BASE_COMMAND
        groupFilter  = '(DataType=="DIGITREND" || DataType=="FASTMONTREND" || DataType=="MERITTREND")'
        intentFilter = '(sIntent=="nomSciOps" || sIntent=="nomSciOps_diagEna")'
        self.Command += ' --filter \'%s && %s' % (groupFilter, intentFilter)
        if minStartTime is not None:
            self.Command += ' && nMetStart>%s' % minStartTime
        if maxStartTime is not None:
            self.Command += ' && nMetStart<%s' % maxStartTime
        self.Command += ' && (nMetStop - nMetStart)>%s' % minDuration
        self.Command += '\''
        self.Command += ' --search-groups'
        self.Command += ' --sort nMetStart --sort DataType'
        self.Command += ' /Data/Flight/Level1/LPA'

    def dumpList(self, filePath):
        cmd = self.Command
        if filePath is not None:
            cmd += ' >> %s' % filePath
        print 'Executing "%s"...' % cmd
        os.system(cmd)
        print 'Done.'




class pSolarFlareTrendMerger:

    def __init__(self, outputFilePath, recreateFileLists = True,
                 minStartDate = None, maxStartDate = None):
        if recreateFileLists:
            print 'Creating the file lists...'
            if minStartDate is not None:
                minStartTime = utc2met(convert2sec(minStartDate))
            else:
                minStartTime = None
            if maxStartDate is not None:
                maxStartTime = utc2met(convert2sec(maxStartDate))
            else:
                maxStartTime = None
            minRunDuration = 10
            runIntents = ['nomSciOps', 'nomSciOps_diagEna']
            for group in self.GROUPS:
                query = pDataCatalogQuery(group, minStartTime, maxStartTime,
                                          minRunDuration, runIntents)
                query.dumpList(self.getFileListPath(group))
                logFilePath = outputFilePath.replace('.root', '_group.log')
                logFile = file(logFilePath, 'w')
                logFile.writelines('Created by pSolarFlareTrendMerger on %s.' %\
                                       time.asctime())
                logFile.writelines('\n\n')
                logFile.writelines('Selections for histogram merging:\n')
                logFile.writelines('- Start run between %s and %s (UTC).\n' %\
                                       (minStartDate, maxStartDate))
                logFile.writelines('- Minimum run duration: %s s.\n' %\
                                       minRunDuration)
                logFile.writelines('- Run intent: "%s".\n' % runIntents)
                logFile.writelines('\n')
                logFile.writelines('See the file lists for details. Bye.')
                logFile.close()

        self.FileListDict = {}
        for group in self.GROUPS:
            filePath = self.getFileListPath(group)
            self.FileList[group] =\
                [line.strip('\n') for line in file(filePath, 'r')]
            self.FileList[group].sort()
        self.OutputFilePath = outputFilePath
        self.VariableDict = VARIABLE_DICT
        print 'Done. %d file(s) found.' % len(self.FileList)

    def getFileListPath(self, group):
        return 'SOLARFLARE_%s_FILELIST.txt' % group

    def createArrays(self):
        print 'Creating arrays...'
        self.InputArrayDict  = {}
        self.OutputArrayDict = {}
        for (name, (type, shape)) in self.VariableDict.items():
            if shape == '':
                arrayShape = (1,)
            else:
                arrayShape = shape.strip('[').strip(']').split('][')
                arrayShape = [int(item) for item in arrayShape]
                arrayShape = tuple(arrayShape)
            self.InputArrayDict[name] = numpy.zeros(arrayShape, type.lower())
            self.OutputArrayDict[name] = numpy.zeros(arrayShape, type.lower())
            suffix = '%s/%s' % (shape, type)
            self.OutputTree.Branch(name, self.OutputArrayDict[name],
                                   '%s%s' % (name, suffix))
        print 'Done.'

    def copyArrays(self):
        for (name, (type, shape)) in self.VariableDict.items():
            if shape == '':
                self.OutputArrayDict[name][0] = self.InputArrayDict[name][0]
            elif shape == '[16]':
                for i in range(16):
                    self.OutputArrayDict[name][i] =\
                         self.InputArrayDict[name][i]
            elif shape == '[16][36]':
                for i in range(16):
                    for j in range(36):
                        self.OutputArrayDict[name][i][j] =\
                             self.InputArrayDict[name][i][j]

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
    q = pDataCatalogQuery()
    q.dumpList('testlist.txt')
    #dumpVarDict('r0288475156_tkrtrend.root')
    #merger = pTkrTrendMerger('tkrtrend_filelist.txt', 'tkrtrend.root',
    #None, None)
    #                         'Jan/15/2010 00:00:00', 'Jan/20/2010 00:00:00')
    #merger.run(False)
