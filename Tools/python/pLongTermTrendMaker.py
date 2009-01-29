#!/usr/bin/env python

import os
import sys
import ROOT
import array

sys.path.append('../../Report/python')

from pTimeConverter import *

BASE_PATH = '/afs/slac.stanford.edu/u/gl/glast/datacatalog/prod/datacat'
BASE_COMMAND = 'find'
DEFAULT_SITE = 'SLAC_XROOT /Data/Flight/Level1/LPA'
DEFAULT_SORT = 'nRun'


class pDataCatalogQuery:

    def __init__(self, group, minStartTime, maxStartTime = None,
                 minDuration = 1000, intent = 'nomSciOps'):
        self.Command = BASE_PATH
        self.Command += ' %s' % BASE_COMMAND
        self.Command += ' --group %s' % group
        self.Command += ' --site %s' % DEFAULT_SITE
        self.Command += ' --sort %s' % DEFAULT_SORT
        self.Command += ' --filter '
        self.Command += "'"
        self.Command += 'sIntent=="%s"' % intent
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


class pBaseFileAnalyzer:

    def __init__(self, fileListPath, outputFilePath, group, minStartTime,
                 maxStartTime = None):
        if not os.path.exists(fileListPath):
            print 'Creating the file list...'
            query = pDataCatalogQuery(group, minStartTime, maxStartTime)
            query.dumpList(fileListPath)
        else:
            print 'File list %s found.' % fileListPath
            print 'Delete the file if you want to recreate it.'
        self.FileList = file(fileListPath, 'r').readlines()
        for (i, filePath) in enumerate(self.FileList):
            self.FileList[i] = filePath.strip('\n')
        self.OutputFile = ROOT.TFile(outputFilePath, 'RECREATE')
        self.OutputTree = ROOT.TTree('Output', 'Output')
        self.createArrays()

    def createArrays(self):
        print 'Creating the arrays...'
        self.Arrays = {}
        self.Arrays['RunId'] = array.array('i', [0])
        self.OutputTree.Branch('RunId', self.Arrays['RunId'], 'RunId/I')
        for label in self.LabelList:
            for quantity in self.QuantityList:
                key = '%s_%s' % (label, quantity)
                self.Arrays[key] = array.array('d', [0.0])
                self.OutputTree.Branch(key, self.Arrays[key], '%s/D' % key)

    def run(self):
        for filePath in self.FileList:
            print 'Analyzing %s...' % filePath
            fileName = os.path.basename(filePath)
            self.Arrays['RunId'][0] = int(fileName.split('_')[0].strip('r'))
            self.InputFile = ROOT.TXNetFile(filePath)
            self.analyze()
            self.OutputTree.Fill()
            self.InputFile.Close()
        self.OutputFile.cd()
        self.OutputTree.Write()
        self.OutputFile.Close()



class pRECONHISTALARMDISTAnalyzer(pBaseFileAnalyzer):

    def __init__(self, fileListPath, outputFilePath, minStartTime,
                 maxStartTime = None):
        self.PlotDict = {'PMTA':\
        'ReconAcdPhaMipsCorrectedAngle_PMTA_Zoom_TH1_AcdTile_gauss_mean_TH1',
                         'PMTB':\
        'ReconAcdPhaMipsCorrectedAngle_PMTB_Zoom_TH1_AcdTile_gauss_mean_TH1',
                         'LACP':\
        'Lac_Thresholds_FacePos_TH1_TowerCalLayerCalColumn_leftmost_edge_TH1',
                         'LACN':\
        'Lac_Thresholds_FaceNeg_TH1_TowerCalLayerCalColumn_leftmost_edge_TH1',
                         }
        self.LabelList = self.PlotDict.keys()
        self.LabelList.sort()
        self.QuantityList = ['mean', 'rms', 'entries']
        pBaseFileAnalyzer.__init__(self, fileListPath, outputFilePath,
                                   'RECONHISTALARMDIST', minStartTime,
                                   maxStartTime)

    def analyze(self):
        for label in self.LabelList:
            plot = self.InputFile.Get(self.PlotDict[label])
            average = plot.GetMean()
            rms = plot.GetRMS()
            entries = plot.GetEntries()
            self.Arrays['%s_mean' % label][0] = average
            self.Arrays['%s_rms' % label][0] = rms
            self.Arrays['%s_entries' % label][0] = entries


class pACDPEDSANALYZERAnalyzer(pBaseFileAnalyzer):

    def __init__(self, fileListPath, outputFilePath, minStartTime,
                 maxStartTime = None):
        self.PlotDict = {'PMTA': 'AcdPedPedMeanDeviation_PMTA_TH1',
                         'PMTB': 'AcdPedPedMeanDeviation_PMTB_TH1'
                         }
        self.LabelList = self.PlotDict.keys()
        self.LabelList.sort()
        self.QuantityList = ['tile%d' % tile for tile in range(128)]
        pBaseFileAnalyzer.__init__(self, fileListPath, outputFilePath,
                                   'ACDPEDSANALYZER', minStartTime,
                                   maxStartTime)

    def analyze(self):
        for label in self.LabelList:
            plot = self.InputFile.Get(self.PlotDict[label])
            for (tile, quantity) in enumerate(self.QuantityList):
                self.Arrays['%s_%s' % (label, quantity)][0] =\
                                    plot.GetBinContent(tile + 1)


if __name__ == '__main__':
    MIN_START_TIME = utc2met(convert2sec('Sep/05/2008 00:00:00'))
    MAX_START_TIME = None
    analyzer1 = pACDPEDSANALYZERAnalyzer('ACDPEDSANALYZER.txt',
                                        'ACDPEDSANALYZER.root',
                                        MIN_START_TIME,
                                        MAX_START_TIME)
    analyzer1.run()
    analyzer2 = pRECONHISTALARMDISTAnalyzer('RECONHISTALARMDIST.txt',
                                           'RECONHISTALARMDIST.root',
                                           MIN_START_TIME,
                                           MAX_START_TIME)
    analyzer2.run()
