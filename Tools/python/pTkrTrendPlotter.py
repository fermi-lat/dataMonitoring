import os
import sys
import math
import numpy
import time

sys.path.append('../../Common/python')
sys.path.append('../../Report/python')

from pTimeConverter import utc2met, met2utc, convert2sec, sec2string
from pRootStyle     import *

TIME_FORMAT = '%b %d, 20%y%F2001-01-01 00:00:00'

MIN_TIME = 2.4e8
MAX_TIME = 2.9e8

SECS_PER_YEAR = 60*60*24*365


def setupStripChart(g):
    g.GetXaxis().SetRangeUser(MIN_TIME, MAX_TIME)
    g.GetXaxis().SetTimeDisplay(True)
    g.GetXaxis().SetTimeFormat(TIME_FORMAT)
    g.GetXaxis().SetNdivisions(509)
    g.GetXaxis().SetTitle('Time (UTC)')


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
        self.FuncDict   = {}

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
                                     50, 0.97, 1.01)
        self.EffMeanHist.SetXTitle('Average hit efficiency')
        self.EffMeanHist.SetYTitle('Entries/bin')
        self.EffMeanHist.SetLineWidth(LINE_WIDTH)
        self.EffSlopeHist = ROOT.TH1F('h_eff_slope', 'h_eff_slope',
                                     50, -0.2, 0.2)
        self.EffSlopeHist.SetXTitle('Hit efficiency slope (% in 5 years)')
        self.EffSlopeHist.SetYTitle('Entries/bin')
        self.EffSlopeHist.SetLineWidth(LINE_WIDTH)
        l98h = ROOT.TLine(MIN_TIME, 0.98, MAX_TIME, 0.98)
        l98h.SetLineWidth(2)
        l98h.SetLineStyle(7)
        l98h.SetLineColor(ROOT.kRed)
        store(l98h)
        for tower in range(16):
            c = getSkinnyCanvas('hit_eff_canvas_%d' % tower,
                                'Hit efficiency, tower %d' % tower)
            c.SetGridx(True)
            c.SetGridy(True)
            f = ROOT.TF1('hit_eff_func_%d' % tower, 'pol1', MIN_TIME, MAX_TIME)
            f.SetLineColor(ROOT.kBlue)
            self.FuncDict[f.GetName()] = f
            g = self.GraphDict['hit_efficiency_%d' % tower]
            setupStripChart(g)
            g.GetYaxis().SetRangeUser(0.96, 1.005)
            g.GetYaxis().SetNdivisions(508)
            g.GetYaxis().SetTitle('Average hit efficiency')
            g.Draw('ap')
            g.Fit('hit_eff_func_%d' % tower)
            l = ROOT.TLatex(0.5, 0.9, 'Tower %d' % tower)
            l.SetNDC()
            l.SetTextAlign(22)
            store(l)
            l.Draw()
            f.Draw('same')
            effMean = f.GetParameter(0)
            effMeanErr = f.GetParError(0)
            effSlope = f.GetParameter(1)
            effSlopeErr = f.GetParError(1)
            if effSlope > 0:
                intercept = (1 - effMean)/effSlope
                intercept = sec2string(met2utc(intercept))
                print 'Tower %d intercepts 1 at %s' % (tower, intercept)
            else:
                intercept = (0.98 - effMean)/effSlope
                intercept = sec2string(met2utc(intercept))
                print 'Tower %d intercepts 0.98 at %s' % (tower, intercept)
            effSlope *= (5*100*SECS_PER_YEAR)
            effSlopeErr *= (5*100*SECS_PER_YEAR)
            line1 = 'Average efficiency = %.2f #pm %.2f' %\
                    (effMean*100, effMeanErr*100)
            line2 = 'Slope = %s%.3f #pm %.3f %% in 5 years' %\
                    ('+'*(effSlope > 0), effSlope, effSlopeErr)
            text = '#splitline{%s}{%s}' % (line1, line2)
            l = ROOT.TLatex(0.27, 0.22, text)
            l.SetNDC()
            l.SetTextAlign(22)
            l.SetTextColor(ROOT.kBlue)
            store(l)
            l.Draw()
            self.EffMeanHist.Fill(effMean)
            self.EffSlopeHist.Fill(effSlope)
            l98h.Draw()
            c.Update()
        c = getCanvas('eff_mean_canvas', 'Mean hit efficiency')
        self.EffMeanHist.Draw()
        l98v = ROOT.TLine(0.98, 0, 0.98, 1.05*self.EffMeanHist.GetMaximum())
        l98v.SetLineWidth(2)
        l98v.SetLineStyle(7)
        l98v.SetLineColor(ROOT.kRed)
        store(l98v)
        l98v.Draw()
        c = getCanvas('eff_slope_canvas', 'Hit efficiency slope')
        self.EffSlopeHist.Draw()


if __name__ == '__main__':
    p = pTkrTrendPlotter('/data/work/datamon/runs/tkrtrend/tkrtrend.root')
    g = p.plotHitEfficiency()
