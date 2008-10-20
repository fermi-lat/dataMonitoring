#!/usr/bin/env python

import os
import sys
import math

sys.path.append('../../Common/python')

from pSafeROOT import ROOT
ROOT.gStyle.SetOptStat(111111)


LABEL_SIZE = 0.04
TIME_FORMAT = '%m/%d/20%y%F2001-01-01 00:00:00'
TIME_FORMAT = '%b %d 20%y%F2001-01-01 00:00:00'
OUTLIERS_NUM_SIGMAS = 5

class pLongTermTrendPlotter:

    def __init__(self, filePath, treeName = 'Output'):
        if not os.path.exists(filePath):
            sys.exit('Could not find %s. Abort.' % filePath)
        self.FilePath = filePath
        print 'Opening %s and retrieving "%s"...' % (self.FilePath, treeName)
        self.RootFile = ROOT.TFile(self.FilePath)
        self.RootTree = self.RootFile.Get('Output')
        self.NumEntries = self.RootTree.GetEntries()
        print 'Done. %s entries found.' % self.NumEntries
        self.Graph = None
        self.Canvas = None

    def createCanvas(self):
        self.Canvas = ROOT.TCanvas('long_term_trend', 'Long-term trend',
                                   1000, 400)

    def draw(self, varName, ylabel = None):
        varMean = 0.0
        varRms = 0.0
        if self.Canvas is None:
            self.createCanvas()
        if ylabel is None:
            ylabel = varName
        print 'Drawing "%s"...' % varName
        self.Graph = ROOT.TGraphErrors(self.NumEntries)
        for i in xrange(self.NumEntries):
            self.RootTree.GetEntry(i)
            timestamp = float(self.RootTree.RunId)
            mean = eval('self.RootTree.%s_%s' % (varName, 'mean'))
            rms = eval('self.RootTree.%s_%s' % (varName, 'rms'))
            numEntries = eval('self.RootTree.%s_%s' % (varName, 'entries'))
            self.Graph.SetPoint(i, timestamp, mean)
            self.Graph.SetPointError(i, 0.0, rms/math.sqrt(numEntries))
            varMean += mean
            varRms += mean*mean
        self.Graph.Draw('AP')
        self.Graph.GetXaxis().SetTitle('Time UTC')
        self.Graph.GetXaxis().SetNdivisions(506)
        self.Graph.GetXaxis().SetLabelSize(LABEL_SIZE)
        self.Graph.GetXaxis().SetTimeDisplay(True)
        self.Graph.GetXaxis().SetTimeFormat(TIME_FORMAT)
        self.Graph.GetYaxis().SetTitle(ylabel)
        self.Graph.GetYaxis().SetLabelSize(LABEL_SIZE)
        self.Canvas.Update()
        varMean /= float(self.NumEntries)
        varRms /= float(self.NumEntries)
        varRms = math.sqrt(varRms - varMean*varMean)
        print
        print '%s average value: %.3f' % (varName, varMean)
        print '%s RMS value: %.3f' % (varName, varRms)
        print
        print 'Detecting outliers (at %d sigma)...' % OUTLIERS_NUM_SIGMAS
        for i in xrange(self.NumEntries):
            self.RootTree.GetEntry(i)
            runId = self.RootTree.RunId
            mean = eval('self.RootTree.%s_%s' % (varName, 'mean'))
            if abs(mean - varMean) > OUTLIERS_NUM_SIGMAS*varRms:
                print 'RunId %d, mean = %.3f' % (runId, mean)

    def save(self, filePath):
        pass
    



if __name__ == '__main__':
    from pOptionParser import pOptionParser
    optparser = pOptionParser('', 1, 1, False)
    filePath = optparser.Argument
    plotter = pLongTermTrendPlotter(filePath)
    plotter.draw('PMTA_average', 'PMTA MIP peak (MIPs)')


