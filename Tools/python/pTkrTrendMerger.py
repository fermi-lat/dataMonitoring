#! /bin/env python

import os
import ROOT
import numpy

import sys
sys.path.append('../../Report/python')
from pTimeConverter import *

BASE_PATH = '/afs/slac.stanford.edu/u/gl/glast/datacatalog/prod/datacat'
BASE_COMMAND = 'find'
DEFAULT_SITE = 'SLAC_XROOT /Data/Flight/Level1/LPA'
DEFAULT_SORT = 'nRun'

# These guys have been put in only recently.
# Error in <TTree::SetBranchAddress>: unknown branch -> Number_LATAverage_stripOcc_err
# Error in <TTree::SetBranchAddress>: unknown branch -> Number_fracSat_TowerPlane_err
# Error in <TTree::SetBranchAddress>: unknown branch -> Number_layerOcc_TowerPlane_err


VARIABLE_DICT = {'Bin_Index': ('i', ''),
                 'Bin_Flags': ('i', ''),
                 'nEvents': ('i', ''),
                 'nPassed': ('i', ''),
                 'Bin_End': ('l', ''),
                 #'Number_LATAverage_stripOcc_err': ('F', ''),
                 'Number_LATAverage_stripOcc': ('F', ''),
                 'Bin_Start': ('l', ''),
                 'TimeStampFirstEvt': ('D', ''),
                 'TimeStampLastEvt': ('D', ''),
                 'Mean_towerEff_Tower_err': ('F', '[16]'),
                 'Mean_trigEff_Tower_err': ('F', '[16]'),
                 'Mean_towerEff_Tower_n': ('i', '[16]'),
                 'Mean_trigEff_Tower_n': ('i', '[16]'),
                 'Mean_towerEff_Tower': ('F', '[16]'),
                 'Mean_trigEff_Tower': ('F', '[16]'),
                 'Number_TOT_FitProb_TowerPlane': ('F', '[16][36]'),
                 'Mean_TOT_GSigma_TowerPlane': ('F', '[16][36]'),
                 'Mean_TOT_LWidth_TowerPlane': ('F', '[16][36]'),
                 'Mean_TOT_GSigma_TowerPlane_err': ('F', '[16][36]'),
                 'Mean_TOT_LWidth_TowerPlane_err': ('F', '[16][36]'),
                 'Mean_layerEff_TowerPlane_err': ('F', '[16][36]'),
                 'Mean_TOT_Peak_TowerPlane_err': ('F', '[16][36]'),
                 'Mean_layerdXY_TowerPlane_err': ('F', '[16][36]'),
                 #'Number_fracSat_TowerPlane_err': ('F', '[16][36]'),
                 #'Number_layerOcc_TowerPlane_err': ('F', '[16][36]'),
                 'Number_TOT_FracLowTOT_TowerPlane': ('F', '[16][36]'),
                 'Number_fracSat_TowerPlane': ('F', '[16][36]'),
                 'Number_layerOcc_TowerPlane': ('F', '[16][36]'),
                 'Mean_layerEff_TowerPlane': ('F', '[16][36]'),
                 'Number_stripOcc_TowerPlane': ('F', '[16][36]'),
                 'Mean_TOT_Peak_TowerPlane': ('F', '[16][36]'),
                 'Mean_layerdXY_TowerPlane': ('F', '[16][36]'),
                 'Mean_TOT_GSigma_TowerPlane_n': ('i', '[16][36]'),
                 'Mean_TOT_LWidth_TowerPlane_n': ('i', '[16][36]'),
                 'Mean_TOT_Peak_TowerPlane_n': ('i', '[16][36]'),
                 'Mean_layerEff_TowerPlane_n': ('i', '[16][36]'),
                 'Mean_layerdXY_TowerPlane_n': ('i', '[16][36]'),
                 'Number_TrackerMon_firstRunId': ('i', ''),
                 'Number_TrackerMon_lastRunId': ('i', ''),
                 'TrueTimeInterval': ('D', '')
                 }


def dumpVarDict(filePath):
    rootFile = ROOT.TFile(filePath)
    rootTree = rootFile.Get('Time')
    for branch in rootTree.GetListOfBranches():
        branchName  = branch.GetName()
        branchType  = branch.GetTitle().split('/')[-1]
        branchShape = branch.GetTitle().split('/')[0].strip(branchName)
        print "'%s': ('%s', '%s')," % (branchName, branchType, branchShape)


class pDataCatalogQuery:

    def __init__(self, group = 'TKRTREND',
                 minStartTime = None, maxStartTime = None, minDuration = 1500,
                 intents = ['nomSciOps', 'nomSciOps_diagEna'],
                 site = DEFAULT_SITE):
        self.Command = BASE_PATH
        self.Command += ' %s' % BASE_COMMAND
        self.Command += ' --group %s' % group
        self.Command += ' --site %s' % site
        self.Command += ' --sort %s' % DEFAULT_SORT
        self.Command += ' --filter '
        self.Command += "'"
        for (i, intent) in enumerate(intents):
            if i == 0:
                self.Command += '(sIntent=="%s" || ' % intent
            elif i == (len(intents) - 1):
                self.Command += 'sIntent=="%s")' % intent
            else:
                self.Command += 'sIntent=="%s" || ' % intent
        if minStartTime is not None:
            self.Command += ' && nMetStart>%s' % minStartTime
        if maxStartTime is not None:
            self.Command += ' && nMetStart<%s' % maxStartTime
        self.Command += ' && (nMetStop - nMetStart)>%s' % minDuration
        self.Command += "'"

    def dumpList(self, filePath = None):
        cmd = self.Command
        if filePath is not None:
            cmd += ' >> %s' % filePath
        print 'Executing "%s"...' % cmd
        os.system(cmd)
        print 'Done.'




class pTkrTrendMerger:

    def __init__(self, fileListPath, outputFilePath,
                 minStartDate = None, maxStartDate = None):
        if not os.path.exists(fileListPath):
            print 'Creating the file list...'
            if minStartDate is not None:
                minStartTime = utc2met(convert2sec(minStartDate))
            else:
                minStartTime = None
            if maxStartDate is not None:
                maxStartTime = utc2met(convert2sec(maxStartDate))
            else:
                maxStartTime = None
            minRunDuration = 1500
            runIntents = ['nomSciOps', 'nomSciOps_diagEna']
            query = pDataCatalogQuery('TKRTREND', minStartTime, maxStartTime,
                                      minRunDuration, runIntents)
            query.dumpList(fileListPath)
            logFilePath = outputFilePath.replace('.root', '.log')
            logFile = file(logFilePath, 'w')
            logFile.writelines('File created by pTkrTrendMerger.py on %s.' %\
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
    #dumpVarDict('r0288475156_tkrtrend.root')
    merger = pTkrTrendMerger('tkrtrend_filelist.txt', 'tkrtrend.root',
                             None, None)
    #                         'Jan/15/2010 00:00:00', 'Jan/20/2010 00:00:00')
    merger.run(False)
