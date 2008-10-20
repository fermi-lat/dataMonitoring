#!/usr/bin/env python

import os
import sys
import math

sys.path.append('../../Common/python')
sys.path.append('../../Report/python')

import pSafeLogger
logger = pSafeLogger.getLogger('pLongTerm')

from pTimeConverter import utc2met, convert2sec
from pSafeROOT import ROOT

ROOT.gStyle.SetOptStat(111111)
ROOT.gStyle.SetMarkerStyle(26)
ROOT.gStyle.SetMarkerSize(0.3)


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

    def draw(self, varName, ylabel = None, ymin = None, ymax = None):
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
        if ymin is not None and ymax is not None:
            self.Graph.GetYaxis().SetRangeUser(ymin, ymax)
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
        self.LastVarName = varName
        return self.Graph

    def save(self, filePath = None):
        if filePath is None:
            filePath = '%s.png' % self.LastVarName
        self.Canvas.SaveAs(filePath)
    



if __name__ == '__main__':
    from pOptionParser import pOptionParser
    optparser = pOptionParser('', 1, 1, False)
    filePath = optparser.Argument
    plotter = pLongTermTrendPlotter(filePath)

    plotter.draw('PMTA', 'PMTA MIP peak (MIPs)', 0.8, 1.4)
    plotter.save()
    raw_input('Press enter to continue...')
    plotter.draw('PMTB', 'PMTB MIP peak (MIPs)', 0.8, 1.4)
    plotter.save()
    raw_input('Press enter to continue...')
    plotter.draw('LACP', 'Positive end LAC threshold (MeV)', 1.8, 2.2)
    plotter.save()
    raw_input('Press enter to continue...')
    plotter.draw('LACN', 'Negative end LAC threshold (MeV)', 1.8, 2.2)
    plotter.save()
    raw_input('Press enter to continue...')

    MIN_ZOOM = utc2met(convert2sec('Oct/01/2008 00:00:00'))
    MAX_ZOOM = utc2met(convert2sec('Oct/05/2008 00:00:00'))
    plot = plotter.draw('PMTA', 'PMTA MIP peak (MIPs)', 1.08, 1.14)
    plot.GetXaxis().SetRangeUser(MIN_ZOOM, MAX_ZOOM)
    plotter.Canvas.Update()
    plotter.save('PMTA_zoom.png')
    raw_input('Press enter to continue...')
    plot = plotter.draw('LACP', 'Positive end LAC threshold (MeV)', 1.98, 2.02)
    plot.GetXaxis().SetRangeUser(MIN_ZOOM, MAX_ZOOM)
    plotter.Canvas.Update()
    plotter.save('LACP_zoom.png')
    raw_input('Press enter to continue...')    
    plotter.RootTree.Draw('PMTA_mean:LACP_mean')
