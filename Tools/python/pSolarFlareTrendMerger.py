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
    'Digi_Trend_Bin_Start'                                 : ('I', ''     ),
    'Digi_Trend_Bin_End'                                   : ('I', ''     ),
    'Digi_Trend_TrueTimeInterval'                          : ('D', ''     ),
    'Digi_Trend_Rate_AcdDigis'                             : ('F', ''     ),
    'Digi_Trend_Rate_FswFilters_GAMMA'                     : ('F', ''     ),
    'Digi_Trend_OutF_Normalized_AcdHit_AcdTile'            : ('F', '[128]'),
    'Digi_Trend_Rate_AnyAcdVeto_AcdTile'                   : ('F', '[128]'),
    'FastMon_Trend_Mean_FastMon_SpaceCraft_RockAngle'      : ('F', ''     ),
    'Merit_Trend_OutF_NormRateTransientEvts'               : ('F', ''     ),
    'Merit_Trend_Rate_TransientEvts'                       : ('F', ''     ),
    'Merit_Trend_Rate_TransientEvts_err'                   : ('F', ''     ),
    'Merit_Trend_Rate_TransientEvtsBelowZenithTheta100'    : ('F', ''     ),
    'Merit_Trend_Rate_TransientEvtsBelowZenithTheta100_err': ('F', ''     ),
    'Merit_Trend_Mean_PtLat'                               : ('F', ''     ),
    'Merit_Trend_Mean_PtLon'                               : ('F', ''     ),
    'Merit_Trend_Mean_PtMcIlwainL'                         : ('F', ''     )
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

    def __init__(self, fileListPath, outputFilePath,
                 minStartDate = None, maxStartDate = None):
        if not os.path.exists(fileListPath):
            print 'Creating the file lists...'
            if minStartDate is not None:
                minStartTime = utc2met(convert2sec(minStartDate))
            else:
                minStartTime = None
            if maxStartDate is not None:
                maxStartTime = utc2met(convert2sec(maxStartDate))
            else:
                maxStartTime = None
            query = pDataCatalogQuery(minStartTime, maxStartTime)
            query.dumpList(fileListPath)
        else:
            print 'File list %s found.' % fileListPath
            print 'Delete the file if you want to recreate it.'
        self.FileList = [line.strip('\n') for line in file(fileListPath, 'r')]
        self.OutputFilePath = outputFilePath
        self.VariableDict = VARIABLE_DICT
        self.DigiTree = None
        self.FastmonTree = None
        self.MeritTree = None
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
            if name.startswith('Digi_Trend_'):
                nn = name.replace('Digi_Trend_', '')
                self.DigiTree.SetBranchAddress(nn, self.InputArrayDict[name])
            elif name.startswith('FastMon_Trend_'):
                nn = name.replace('FastMon_Trend_', '')
                self.FastmonTree.SetBranchAddress(nn, self.InputArrayDict[name])
            elif name.startswith('Merit_Trend_'):
                nn = name.replace('Merit_Trend_', '')
                self.MeritTree.SetBranchAddress(nn, self.InputArrayDict[name])
            if shape == '':
                self.OutputArrayDict[name][0] = self.InputArrayDict[name][0]
            elif shape == '[128]':
                for i in range(128):
                    self.OutputArrayDict[name][i] =\
                         self.InputArrayDict[name][i]

    def run(self, local = False):
        self.OutputFile = ROOT.TFile(self.OutputFilePath, 'RECREATE')
        self.OutputTree = ROOT.TTree('Time', 'Time')
        self.createArrays()
        numRuns = len(self.FileList)/3
        for i in xrange(numRuns):
            (digiPath, fastmonPath, meritPath) = self.FileList[i*3:i*3+3]
            print 'Looping over run %d/%d' % (i + 1, numRuns)
            print '\tDigi   : %s' % digiPath
            print '\tFastmon: %s' % fastmonPath
            print '\tMerit  : %s' % meritPath
            if local:
                digiFile    = ROOT.TFile(digiPath)
                fastmonFile = ROOT.TFile(fastmonPath)
                meritFile   = ROOT.TFile(meritPath)
            else:
                digiFile    = ROOT.TXNetFile(digiPath)
                fastmonFile = ROOT.TXNetFile(fastmonPath)
                meritFile   = ROOT.TXNetFile(meritPath)
            self.DigiTree = digiFile.Get('Time')
            self.FastmonTree = fastmonFile.Get('Time')
            self.MeritTree = meritFile.Get('Time')
            # Wanna check that the three trees have the same number of entries?
            try:
                numEntries = self.DigiTree.GetEntries()
                for i in xrange(numEntries):
                    self.DigiTree.GetEntry(i)
                    self.FastmonTree.GetEntry(i)
                    self.MeritTree.GetEntry(i)
                    self.copyArrays()
                    self.OutputTree.Fill()
            except:
                print 'File read failed.'
        self.OutputFile.cd()
        self.OutputTree.Write()
        self.OutputFile.Close()
        print 'Done.'

        
if __name__ == '__main__':
    #q = pDataCatalogQuery()
    #q.dumpList('testlist.txt')
    merger = pSolarFlareTrendMerger('solarflare_filelist_2010_01_2010_04.txt',
                                    'solarflare_trend_2010_01_2010_04.root',
                                    'Jan/01/2010 00:00:00', 'May/01/2010 00:00:00')
    merger.run(False)
