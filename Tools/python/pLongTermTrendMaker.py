#!/usr/bin/env python

import os
import sys

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


if __name__ == '__main__':
    MIN_START_TIME = utc2met(convert2sec('Sep/04/2008 00:00:00'))
    MAX_START_TIME = None
    GROUP = 'RECONHISTALARMDIST'
    query = pDataCatalogQuery(GROUP, MIN_START_TIME, MAX_START_TIME)
    query.dumpList('%s.txt' % GROUP)

    import ROOT
    import array
    
    filesList = file('test.txt', 'r').readlines()
    plotDict = {'PMTA':\
        'ReconAcdPhaMipsCorrectedAngle_PMTA_Zoom_TH1_AcdTile_gauss_mean_TH1',
                'PMTB':\
        'ReconAcdPhaMipsCorrectedAngle_PMTB_Zoom_TH1_AcdTile_gauss_mean_TH1',
                'LACP':\
        'Lac_Thresholds_FacePos_TH1_TowerCalLayerCalColumn_leftmost_edge_TH1',
                'LACN':\
        'Lac_Thresholds_FaceNeg_TH1_TowerCalLayerCalColumn_leftmost_edge_TH1',
                }
    labels = plotDict.keys()
    labels.sort()
    outputFilePath = 'test.root'
    outputFile = ROOT.TFile(outputFilePath, 'RECREATE')
    outputTree = ROOT.TTree('Output', 'Output')
    Arrays = {}
    Arrays['RunId'] = array.array('i', [0])
    outputTree.Branch('RunId', Arrays['RunId'], 'RunId/I')
    for label in labels:
        for quantity in ['mean', 'rms', 'entries', 'gauss_mean',
                         'gauss_mean_error']:
            key = '%s_%s' % (label, quantity)
            Arrays[key] = array.array('d', [0.0])
            outputTree.Branch(key, Arrays[key], '%s/D' % key)
    fitFunction = ROOT.TF1('fit_function', 'gaus')
    ## Loop over the files
    for filePath in filesList:
        filePath = filePath.strip('\n')
        print 'Analyzing %s...' % filePath
        fileName = os.path.basename(filePath)
        Arrays['RunId'][0] = int(fileName.split('_')[0].strip('r'))
        inputFile = ROOT.TXNetFile(filePath)
        if inputFile.Get(plotDict[labels[0]]) is not None:
            for label in labels:
                plot = inputFile.Get(plotDict[label])
                average = plot.GetMean()
                rms = plot.GetRMS()
                entries = plot.GetEntries()
                plot.Fit(fitFunction, 'QN')
                gauss_mean = fitFunction.GetParameter(1)
                gauss_mean_error = fitFunction.GetParError(1)
                Arrays['%s_mean' % label][0] = average
                Arrays['%s_rms' % label][0] = rms
                Arrays['%s_entries' % label][0] = entries
                Arrays['%s_gauss_mean' % label][0] = gauss_mean
                Arrays['%s_gauss_mean_error' % label][0] = gauss_mean_error
            outputTree.Fill()
        else:
            print 'Skipping...'
        inputFile.Close()

    outputFile.cd()
    outputTree.Write()
    outputFile.Close()
