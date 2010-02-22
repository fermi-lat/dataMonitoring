import os
import sys
import math
import numpy

sys.path.append('../../Common/python')
sys.path.append('../../Report/python')

from pTimeConverter import utc2met, convert2sec
import ROOT

ROOT.gStyle.SetOptStat(111111)
ROOT.gStyle.SetMarkerStyle(26)
ROOT.gStyle.SetMarkerSize(0.3)
ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetCanvasColor(10)
ROOT.gStyle.SetFrameBorderMode(0)
ROOT.gStyle.SetFrameFillColor(0)
ROOT.gStyle.SetPadBorderMode(0)
ROOT.gStyle.SetPadColor(0)
ROOT.gStyle.SetHistFillStyle(0)
ROOT.gStyle.SetStatColor(10)
ROOT.gStyle.SetGridColor(16)
ROOT.gStyle.SetLegendBorderSize(1)
ROOT.gStyle.SetTitleYOffset(1.1)
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(111111)
ROOT.gStyle.SetPaintTextFormat("1.2g")
ROOT.gStyle.SetTitleSize(0.06, 'XY')
ROOT.gStyle.SetTitleOffset(1.00, 'X')
ROOT.gStyle.SetTitleOffset(0.60, 'Y')

LABEL_SIZE = 0.04
TIME_FORMAT = '%m/%d/20%y%F2001-01-01 00:00:00'

MIN_TIME = 2.4e8
MAX_TIME = 2.9e8

SECS_PER_YEAR = 60*60*24*365


class pTkrTrendPlotter:

    def __init__(self, filePath, treeName = 'Time'):
        if not os.path.exists(filePath):
            sys.exit('Could not find %s. Abort.' % filePath)
        self.FilePath = filePath
        print 'Opening %s and retrieving "%s"...' % (self.FilePath, treeName)
        self.RootFile = ROOT.TFile(self.FilePath)
        self.RootTree = self.RootFile.Get(treeName)
        self.NumEntries = self.RootTree.GetEntries()
        print 'Done. %s entries found.' % self.NumEntries
        self.__retrieveTimestamps()
        self.GraphDict  = {}
        self.CanvasDict = {}
        self.FuncDict   = {}
        self.Pool       = []

    def store(self, rootObject):
        self.Pool.append(rootObject) 

    def __retrieveTimestamps(self):
        print 'Retrieving timestamps...'
        self.Timestamps = []
        startTime = numpy.zeros((1,), 'd')
        stopTime = numpy.zeros((1,), 'd')
        self.RootTree.SetBranchStatus('*', 0)
        self.RootTree.SetBranchStatus('TimeStampFirstEvt', 1)
        self.RootTree.SetBranchStatus('TimeStampLastEvt', 1)
        self.RootTree.SetBranchAddress('TimeStampFirstEvt', startTime)
        self.RootTree.SetBranchAddress('TimeStampLastEvt', stopTime)
        for i in xrange(self.NumEntries):
            self.RootTree.GetEntry(i)
            t = 0.5*(startTime[0] + stopTime[0])
            self.Timestamps.append(t)
        print 'Done.'
        
    def getTimestamp(self, i):
        return self.Timestamps[i]

    def plotHitEfficiency(self):
        self.RootTree.SetBranchStatus('*', 0)
        self.RootTree.SetBranchStatus('Mean_towerEff_Tower', 1)
        self.RootTree.SetBranchStatus('Mean_towerEff_Tower_err', 1)
        v  = numpy.zeros((16,), 'f')
        dv = numpy.zeros((16,), 'f')
        self.RootTree.SetBranchAddress('Mean_towerEff_Tower', v)
        self.RootTree.SetBranchAddress('Mean_towerEff_Tower_err', dv)
        for tower in range(16):
            g = ROOT.TGraphErrors()
            g.SetName('hit_efficiency_%d' % tower)
            self.GraphDict[g.GetName()] = g
        for i in xrange(self.NumEntries):
            self.RootTree.GetEntry(i)
            x = self.getTimestamp(i)
            for tower in range(16):
                g = self.GraphDict['hit_efficiency_%d' % tower]
                g.SetPoint(i, x, v[tower])
                g.SetPointError(i, 0, dv[tower])
        self.EffMeanHist = ROOT.TH1F('h_eff_mean', 'h_eff_mean',
                                     50, 0.98, 1.01)
        self.EffMeanHist.SetXTitle('Average hit efficiency')
        self.EffSlopeHist = ROOT.TH1F('h_eff_slope', 'h_eff_slope',
                                     50, -0.2, 0.2)
        self.EffSlopeHist.SetXTitle('Hit efficiency slope (% in 5 years)')
        for tower in range(16):
            c = ROOT.TCanvas('hit_eff_canvas_%d' % tower,
                             'Hit efficiency, tower %d' % tower, 1000, 400)
            self.CanvasDict[c.GetName()] = c
            c.SetGridx(True)
            c.SetGridy(True)
            c.SetLeftMargin(0.08)
            c.SetRightMargin(0.03)
            c.SetTopMargin(0.15)
            c.SetBottomMargin(0.15)
            f = ROOT.TF1('hit_eff_func_%d' % tower, 'pol1', MIN_TIME, MAX_TIME)
            f.SetLineColor(ROOT.kRed)
            self.FuncDict[f.GetName()] = f
            g = self.GraphDict['hit_efficiency_%d' % tower]
            g.GetXaxis().SetRangeUser(MIN_TIME, MAX_TIME)
            g.GetYaxis().SetRangeUser(0.96, 1.005)
            g.GetXaxis().SetTimeDisplay(True)
            g.GetXaxis().SetTimeFormat(TIME_FORMAT)
            g.GetXaxis().SetTitle('Time UTC')
            g.GetYaxis().SetNdivisions(508)
            g.GetYaxis().SetTitle('Average hit efficiency')
            g.Draw('ap')
            g.Fit('hit_eff_func_%d' % tower)
            l = ROOT.TLatex(0.5, 0.9, 'Tower %d' % tower)
            l.SetNDC()
            l.SetTextSize(0.07)
            l.SetTextAlign(22)
            self.store(l)
            l.Draw()
            f.Draw('same')
            effMean = f.GetParameter(0)
            effMeanErr = f.GetParError(0)
            effSlope = f.GetParameter(1)
            effSlopeErr = f.GetParError(1)
            effSlope *= (5*100*SECS_PER_YEAR)
            effSlopeErr *= (5*100*SECS_PER_YEAR)
            line1 = 'Average efficiency = %.2f #pm %.2f' %\
                    (effMean*100, effMeanErr*100)
            line2 = 'Slope = %s%.3f #pm %.3f %% in 5 years' %\
                    ('+'*(effSlope > 0), effSlope, effSlopeErr)
            text = '#splitline{%s}{%s}' % (line1, line2)
            l = ROOT.TLatex(0.23, 0.22, text)
            l.SetNDC()
            l.SetTextSize(0.05)
            l.SetTextAlign(22)
            l.SetTextColor(ROOT.kRed)
            self.store(l)
            l.Draw()
            c.Update()
            self.EffMeanHist.Fill(effMean)
            self.EffSlopeHist.Fill(effSlope)
        c = ROOT.TCanvas('eff_mean_canvas', 'Mean hit efficiency')
        c.SetBottomMargin(0.15)
        self.CanvasDict[c.GetName()] = c
        self.EffMeanHist.Draw()
        c = ROOT.TCanvas('eff_slope_canvas', 'Hit efficiency slope')
        c.SetBottomMargin(0.15)
        self.CanvasDict[c.GetName()] = c
        self.EffSlopeHist.Draw()


if __name__ == '__main__':
    p = pTkrTrendPlotter('/data/work/datamon/runs/tkrtrend/tkrtrend.root')
    g = p.plotHitEfficiency()
