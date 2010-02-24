import os
import sys
import math
import numpy
import time

sys.path.append('../../Common/python')
sys.path.append('../../Report/python')

from pTimeConverter import *
from pRootStyle     import *

TIME_FORMAT = '%b %d, 20%y%F2001-01-01 00:00:00'

MIN_TIME = 2.4e8
MAX_TIME = 2.9e8

SECS_PER_YEAR = 60*60*24*365

# Apr 07--08 2009: jump in the TOT peak.
# Oct 27--28 2008: jump in the TOT peak.
# Mar 11--15 2009: no data.
TOT_SCALE_DICT = {244419664: 'New TOT charge scale (SSC-140)',
                  260810033: 'New TOT charge scale (SSC-181)'
                  }

# Masked strips.
PRE_FLIGHT_NUM_MASKED_STRIPS = 203
STRIP_MASK_DICT = {'2008/204'   : (3 , 206, 'OBCONF-49' ),
                   '18/Aug/2008': (14, 220, 'OBCONF-66' ),
                   '28/Oct/2008': (61, 281, 'OBCONF-86' ),
                   '2009/33'    : (35, 316, 'OBCONF-97' ),
                   '28/Apr/2009': (9 , 325, 'OBCONF-105'),
                   '16/Oct/2009': (4 , 329, 'OBCONF-118'),
                   '23/Jan/2010': (2 , 331, 'OBCONF-120'),
                   '23/Feb/2010': (2 , 333, 'OBCONF-121')
                   }

# There was a bug in the tkr monitoring code that screwed up the
# calculation of the occupancy.
# Documented in SSC-132.
MIN_TKRMON_BUG_RUN = 242053458
MAX_TKRMON_BUG_RUN = 242206725

# SIU reboot.
SIU_REBOOT  = utc2met(string2sec('11/Mar/2009', '%d/%b/%Y'))
SIU_RECOVER = utc2met(string2sec('2009/74', '%Y/%j'))


def setupStripChart(g):
    g.GetXaxis().SetRangeUser(MIN_TIME, MAX_TIME)
    g.GetXaxis().SetTimeDisplay(True)
    g.GetXaxis().SetTimeFormat(TIME_FORMAT)
    g.GetXaxis().SetNdivisions(509)
    g.GetXaxis().SetTitle('Time (UTC)')

def drawMarker(timestamp, ymin, ymax, text, color = ROOT.kBlue, ylabel = None):
    l = ROOT.TLine(timestamp, ymin, timestamp, ymax)
    l.SetLineColor(color)
    l.SetLineWidth(2)
    l.SetLineStyle(7)    
    l.Draw()
    store(l)
    ylabel = ylabel or ymax
    l = ROOT.TLatex(timestamp, ylabel, text)
    l.SetTextColor(color)
    l.SetTextAlign(21)
    l.SetTextSize(TEXT_SIZE - 5)
    store(l)
    l.Draw()
    ROOT.gPad.Update()

def drawSIUReboot(ymin, ymax):
    drawMarker(SIU_REBOOT, ymin, ymax, 'SIU reboot', ROOT.kRed, 1.1*ymax)
    drawMarker(SIU_RECOVER, ymin, ymax, '', ROOT.kRed, 1.1*ymax)
        
def fitTrend(g, minTime = MIN_TIME, maxTime = MAX_TIME,
             label = 'Average value'):
    gName = g.GetName()
    print 'Fitting graph %s...' % gName
    fName = '%s_fitfunc' % gName
    f = ROOT.TF1(fName, 'pol1', minTime, maxTime)
    f.SetLineColor(ROOT.kBlue)
    store(f)
    g.Fit(fName, 'RQ')
    f.Draw('same')
    intercept = f.GetParameter(0)
    interceptErr = f.GetParError(0)
    slope = f.GetParameter(1)
    slopeErr = f.GetParError(1)
    mean = f.Eval(0.5*(MIN_TIME + MAX_TIME))
    meanErr = interceptErr
    if 'hit_eff' in gName:
        try:
            proj = (0.98 - intercept)/slope
            proj = sec2string(met2utc(proj))
            print 'Tower will intercept 0.98 at %s' % proj
        except:
            pass
        mean     *= 100
        meanErr  *= 100
        slope    *= (100*SECS_PER_YEAR)
        slopeErr *= (100*SECS_PER_YEAR)
        line1 = 'Average hit efficiency = (%.2f #pm %.2f) %%' % (mean, meanErr)
        line2 = 'Slope = (%s%.3f #pm %.3f) %% year^{-1}' %\
                ('+'*(slope > 0), slope, slopeErr)
    elif 'trg_eff' in gName:
        mean     *= 100
        meanErr  *= 100
        slope    *= (100*SECS_PER_YEAR)
        slopeErr *= (100*SECS_PER_YEAR)
        line1 = 'Average trigger efficiency = (%.2f #pm %.2f) %%' %\
                (mean, meanErr)
        line2 = 'Slope = (%s%.3f #pm %.3f) %% year^{-1}' %\
                ('+'*(slope > 0), slope, slopeErr)
    elif 'tot_peak' in gName:
        slope    *= SECS_PER_YEAR
        slopeErr *= SECS_PER_YEAR
        line1 = 'Average TOT peak = (%.3f #pm %.3f) fC' %\
                (mean, meanErr)
        line2 = 'Slope = (%s%.2e #pm %.2e) fC year^{-1}' %\
                ('+'*(slope > 0), slope, slopeErr)
    elif 'noise_occ' in gName:
        slope    *= SECS_PER_YEAR
        slopeErr *= SECS_PER_YEAR
        line1 = 'Average layer occupancy = (%.2e #pm %.2e)' %\
                (mean, meanErr)
        line2 = 'Slope = (%s%.2e #pm %.2e) year^{-1}' %\
                ('+'*(slope > 0), slope, slopeErr)
    else:
        line1 = '%s = (%.2e #pm %.1e)' % (label, mean, meanErr)
        line2 = 'Slope = (%s%.2e #pm %.1e)' %\
                ('+'*(slope > 0), slope, slopeErr)
    text = '#splitline{%s}{%s}' % (line1, line2)
    l = ROOT.TLatex(0.15, 0.225, text)
    l.SetNDC()
    l.SetTextAlign(12)
    l.SetTextColor(ROOT.kBlue)
    store(l)
    l.Draw()
    return f

def drawTitle(title):
    l = ROOT.TPaveText(0.70, 0.90, 0.99, 0.99, 'NDC')
    l.SetTextSize(TEXT_SIZE)
    l.AddText(title)
    store(l)
    l.Draw()


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
                                     61, 0.97, 1.01)
        self.EffMeanHist.SetXTitle('Average hit efficiency')
        self.EffMeanHist.SetYTitle('Entries/bin')
        self.EffMeanHist.SetLineWidth(LINE_WIDTH)
        self.EffSlopeHist = ROOT.TH1F('h_eff_slope', 'h_eff_slope',
                                      50, -0.2, 0.2)
        self.EffSlopeHist.SetXTitle('Hit efficiency slope (% year^{-1})')
        self.EffSlopeHist.SetYTitle('Entries/bin')
        self.EffSlopeHist.SetLineWidth(LINE_WIDTH)
        l98h = ROOT.TLine(MIN_TIME, 0.98, MAX_TIME, 0.98)
        l98h.SetLineWidth(2)
        l98h.SetLineStyle(7)
        l98h.SetLineColor(ROOT.kRed)
        store(l98h)
        for tower in range(16):
            c = getSkinnyCanvas('hit_eff_canvas_%d' % tower,
                                'Hit efficiency, tower %d' % tower,
                                grid = True)
            g = self.GraphDict['hit_efficiency_%d' % tower]
            setupStripChart(g)
            g.GetYaxis().SetRangeUser(0.96, 1.005)
            g.GetYaxis().SetNdivisions(508)
            g.GetYaxis().SetTitle('Average hit efficiency')
            g.Draw('ap')
            f = fitTrend(g)
            drawTitle('Tower %d' % tower) 
            self.EffMeanHist.Fill(f.Eval(0.5*(MIN_TIME + MAX_TIME)))
            self.EffSlopeHist.Fill(f.GetParameter(1)*(100*SECS_PER_YEAR))
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

    def plotTrigEfficiency(self):
        self.RootTree.SetBranchStatus('*', 0)
        self.RootTree.SetBranchStatus('Mean_trigEff_Tower', 1)
        self.RootTree.SetBranchStatus('Mean_trigEff_Tower_err', 1)
        v  = numpy.zeros((16,), 'f')
        dv = numpy.zeros((16,), 'f')
        self.RootTree.SetBranchAddress('Mean_trigEff_Tower', v)
        self.RootTree.SetBranchAddress('Mean_trigEff_Tower_err', dv)
        for tower in range(16):
            g = ROOT.TGraphErrors()
            g.SetName('trg_efficiency_%d' % tower)
            self.GraphDict[g.GetName()] = g
        for i in xrange(self.NumEntries):
            self.RootTree.GetEntry(i)
            x = self.getTimestamp(i)
            for tower in range(16):
                g = self.GraphDict['trg_efficiency_%d' % tower]
                g.SetPoint(i, x, v[tower])
                g.SetPointError(i, 0, dv[tower])
        for tower in range(16):
            c = getSkinnyCanvas('trg_eff_canvas_%d' % tower,
                                'Trigger efficiency, tower %d' % tower,
                                grid = True)
            g = self.GraphDict['trg_efficiency_%d' % tower]
            setupStripChart(g)
            g.GetYaxis().SetRangeUser(0.8, 1.1)
            g.GetYaxis().SetNdivisions(508)
            g.GetYaxis().SetTitle('Average trigger efficiency')
            g.Draw('ap')
            f = fitTrend(g, 1.01*MIN_TIME)
            drawTitle('Tower %d' % tower) 
            c.Update()

    def plotTOTPeak(self, probThreshold = 0, sampleLayer = (15, 10)):
        self.RootTree.SetBranchStatus('*', 0)
        self.RootTree.SetBranchStatus('Mean_TOT_Peak_TowerPlane', 1)
        self.RootTree.SetBranchStatus('Mean_TOT_Peak_TowerPlane_err', 1)
        self.RootTree.SetBranchStatus('Number_TOT_FitProb_TowerPlane', 1)
        v  = numpy.zeros((16, 36), 'f')
        dv = numpy.zeros((16, 36), 'f')
        p  = numpy.zeros((16, 36), 'f')
        self.RootTree.SetBranchAddress('Mean_TOT_Peak_TowerPlane', v)
        self.RootTree.SetBranchAddress('Mean_TOT_Peak_TowerPlane_err', dv)
        self.RootTree.SetBranchAddress('Number_TOT_FitProb_TowerPlane', p)
        g = ROOT.TGraphErrors()
        g.SetName('tot_peak')
        self.GraphDict[g.GetName()] = g
        gSample = ROOT.TGraphErrors()
        gSample.SetName('tot_peak_%d%d' % sampleLayer)
        self.GraphDict[gSample.GetName()] = gSample
        one = numpy.ones((16, 36), 'f')
        for i in xrange(self.NumEntries):
            self.RootTree.GetEntry(i)
            x = self.getTimestamp(i)
            peak = (v*(p > probThreshold)).sum()
            peakErr = (dv*(p > probThreshold)).sum()
            entries = (one*(p > probThreshold)).sum()
            peak /= entries
            peakErr /= entries**1.5
            g.SetPoint(i, x, peak)
            g.SetPointError(i, 0, peakErr)
            peakSample = v[sampleLayer[0]][sampleLayer[1]]
            peakErrSample = dv[sampleLayer[0]][sampleLayer[1]]
            gSample.SetPoint(i, x, peakSample)
            gSample.SetPointError(i, 0, peakErrSample)
        g.GetYaxis().SetRangeUser(4, 6)
        g.GetYaxis().SetTitle('Average TOT peak position (fC)')
        c = getSkinnyCanvas('tot_peak_c', 'TOT average peak position', True)
        setupStripChart(g)
        g.Draw('ap')
        f = fitTrend(g, 260810033)
        gSample.GetYaxis().SetRangeUser(4, 6)
        gSample.GetYaxis().SetTitle('Average TOT peak position (fC)')
        cSample = getSkinnyCanvas('tot_peak_c_%d_%d' % sampleLayer,
                  'TOT average peak position (Tower %d, plane %d)' %\
                                  sampleLayer, True)
        setupStripChart(gSample)
        gSample.Draw('ap')
        f = fitTrend(gSample, 260810033)
        for (timestamp, text) in TOT_SCALE_DICT.items():
            c.cd()
            drawMarker(timestamp, 4, 5.5, text)
            cSample.cd()
            drawMarker(timestamp, 4, 5.5, text)
        c.Update()
        cSample.Update()

    def plotNoiseOcc(self, sampleLayer = (15, 10)):
        self.RootTree.SetBranchStatus('*', 0)
        self.RootTree.SetBranchStatus('Number_layerOcc_TowerPlane', 1)
        v  = numpy.zeros((16, 36), 'f')
        self.RootTree.SetBranchAddress('Number_layerOcc_TowerPlane', v)
        g = ROOT.TGraph()
        g.SetName('noise_occ_worst')
        self.GraphDict[g.GetName()] = g
        gSample = ROOT.TGraph()
        gSample.SetName('noise_occ_sample')
        self.GraphDict[gSample.GetName()] = gSample
        for i in xrange(self.NumEntries):
            self.RootTree.GetEntry(i)
            x = self.getTimestamp(i)
            occWorst = v.max()
            g.SetPoint(i, x, occWorst)
            occSample = v[sampleLayer[0]][sampleLayer[1]]
            gSample.SetPoint(i, x, occSample)
        g.GetYaxis().SetRangeUser(1e-2, 10)
        g.GetYaxis().SetTitle('Occupancy')
        gSample.GetYaxis().SetRangeUser(1e-3, 1e-1)
        gSample.GetYaxis().SetTitle('Occupancy')
        cSample = getSkinnyCanvas('noise_occ_sample_c',
                            'Occupancy for Tower %d, layer %d' % sampleLayer,
                            True)
        cSample.SetLogy(True)
        setupStripChart(gSample)
        gSample.Draw('ap')
        f = fitTrend(gSample, 1.015*MIN_TIME)
        drawSIUReboot(1e-3, 1e-1)
        gInsert = gSample.Clone()
        store(gInsert)
        gInsert.GetYaxis().SetTitleOffset(0.9)
        gInsert.GetYaxis().SetRangeUser(1e-3, 1e-1)
        gInsert.GetXaxis().SetTitleOffset(1.75)
        setupStripChart(gInsert)
        insert = ROOT.TPad('insert', 'insert', 0.45, 0.45, 0.95, 0.9)
        store(insert)
        insert.SetTopMargin(0.1)
        insert.SetBottomMargin(0.28)
        insert.SetRightMargin(0.03)
        insert.SetLeftMargin(0.13)
        insert.SetLogy(True)
        insert.Draw()
        insert.cd()
        gInsert.Draw('ap')
        gInsert.GetXaxis().SetRangeUser(1.006*MIN_TIME, 1.0115*MIN_TIME)
        drawMarker(MIN_TKRMON_BUG_RUN, 1e-3, 1.1e-1, '')
        drawMarker(MAX_TKRMON_BUG_RUN, 1e-3, 1.1e-1,
                   'TKR monitoring feature :-)')
        insert.Update()
        c = getSkinnyCanvas('noise_occ_worst_c',
                            'Occupancy for the worst layer', True)
        c.SetLogy(True)
        setupStripChart(g)
        g.Draw('ap')
        drawSIUReboot(1e-2, 10)
        yDict = {'OBCONF-49' : 5,
                 'OBCONF-66' : 1.5,
                 'OBCONF-86' : 3.5,
                 'OBCONF-97' : 2,
                 'OBCONF-105': 1,
                 'OBCONF-118': 0.3,
                 'OBCONF-120': 2,
                 'OBCONF-121': 0.4
                 }
        for timestamp, (numStr, totNumStr, jira) in STRIP_MASK_DICT.items():
            try:
                timestamp = utc2met(string2sec(timestamp, '%Y/%j'))
            except ValueError:
                timestamp = utc2met(string2sec(timestamp, '%d/%b/%Y'))
            if timestamp > MIN_TIME and timestamp < MAX_TIME:
                text = '#splitline{+%d strips (%d)}{%s}' %\
                       (numStr, totNumStr, jira)
                drawMarker(timestamp, 1e-2, yDict[jira], text,
                           ylabel = 1.3*yDict[jira])
        
        

if __name__ == '__main__':
    p = pTkrTrendPlotter('/data/work/datamon/runs/tkrtrend/tkrtrend.root')
    #p.plotHitEfficiency()
    #p.plotTrigEfficiency()
    #p.plotTOTPeak()
    p.plotNoiseOcc()
