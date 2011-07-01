import os
import sys
import math
import numpy
import time

sys.path.append('../../Common/python')
sys.path.append('../../Report/python')

from pTimeConverter import *
from pRootStyle     import *

ROOT.gStyle.SetTitleOffset(0.5, 'Y')

TIME_FORMAT = '%b %d, 20%y%F2001-01-01 00:00:00'

LAUNCH_DATE = '11/Jun/2008'
LAUNCH_TIME = utc2met(string2sec(LAUNCH_DATE, '%d/%b/%Y'))
MIN_TIME    = 2.40e8
MAX_TIME    = 3.35e8

SECS_PER_YEAR = 60*60*24*365

# Apr 07--08 2009: jump in the TOT peak.
# Oct 27--28 2008: jump in the TOT peak.
# Mar 11--15 2009: no data.
TOT_CHANGE_DICT = {#244419664: 'New TOT charge scale (SSC-140)',
                   260810033: 'New TOT charge scale (SSC-181)',
                   246823875: '#splitline{Timing change}{trigger window set to 14 ticks}'
                   }

# Masked strips.
STRIP_MASK_DICT   = {LAUNCH_DATE  : (0, 203, 'Pre-flight'),
                     '2008/204'   : (3 , 206, 'OBCONF-49' ),
                     '18/Aug/2008': (14, 220, 'OBCONF-66' ),
                     '28/Oct/2008': (61, 281, 'OBCONF-86' ),
                     '2009/33'    : (35, 316, 'OBCONF-97' ),
                     '28/Apr/2009': (9 , 325, 'OBCONF-105'),
                     '16/Oct/2009': (4 , 329, 'OBCONF-118'),
                     '23/Jan/2010': (2 , 331, 'OBCONF-120'),
                     '23/Feb/2010': (2 , 333, 'OBCONF-121'),
                     '08/Mar/2010': (3 , 336, 'OBCONF-122'),
                     '19/Aug/2010': (4 , 340, 'OBCONF-136'),
                     '10/Sep/2010': (2 , 342, 'OBCONF-137'),
                     '20/Sep/2010': (4 , 346, 'OBCONF-140'),
                     '30/Nov/2010': (16, 362, 'OBCONF-144'),
                     '10/Jan/2011': (19, 381, 'OBCONF-145'),
                     '21/Mar/2011': (13, 394, 'OBCONF-148'),
                     '27/May/2011': (22, 416, 'OBCONF-151')
                     }

STRIP_MASK_DICT_0 = {LAUNCH_DATE  : (0 , 18 , 'Pre-flight'),
                     '18/Aug/2008': (9 , 27 , 'OBCONF-66' ),
                     '28/Oct/2008': (52, 79 , 'OBCONF-86' ),
                     '2009/33'    : (29, 108, 'OBCONF-97' ),
                     '28/Apr/2009': (3 , 111, 'OBCONF-105')
                     }

STRIP_MASK_DICT_3 = {LAUNCH_DATE  : (0 , 1, 'Pre-flight'),
                     '2008/204'   : (2 , 3, 'OBCONF-49' ),
                     '2009/33'    : (2 , 5, 'OBCONF-97' ),
                     '28/Apr/2009': (1 , 6 , 'OBCONF-105'),
                     '16/Oct/2009': (2 , 8 , 'OBCONF-118'),
                     '23/Jan/2010': (2 , 10, 'OBCONF-120'),
                     '08/Mar/2010': (2 , 12, 'OBCONF-122'),
                     '19/Aug/2010': (2 , 14, 'OBCONF-136'),
                     '10/Sep/2010': (2 , 16, 'OBCONF-137'),
                     '20/Sep/2010': (4 , 20, 'OBCONF-140'),
                     '30/Nov/2010': (14, 34, 'OBCONF-144'),
                     '10/Jan/2011': (19, 53, 'OBCONF-145'),
                     '21/Mar/2011': (12, 65, 'OBCONF-148'),
                     '27/May/2011': (21, 86, 'OBCONF-151')
                     }

# There was a bug in the tkr monitoring code that screwed up the
# calculation of the occupancy.
# Documented in SSC-132.
MIN_TKRMON_BUG_RUN = 242053458
MAX_TKRMON_BUG_RUN = 242206725

# SIU reboot.
SIU_REBOOT  = utc2met(string2sec('11/Mar/2009', '%d/%b/%Y'))
SIU_RECOVER = utc2met(string2sec('2009/74', '%Y/%j'))
DRAW_SIU_REBOOT = False


def getMaskedStripChart(ymin, ymax, color, tower = None, logscale = False,
                        minTime = LAUNCH_TIME, maxTime = MAX_TIME):
    maskDict = {}
    if tower is None:
        baseDict = STRIP_MASK_DICT
    else:
        baseDict = eval('STRIP_MASK_DICT_%d' % tower)
    for timestamp, (numStr, totNumStr, jira) in baseDict.items():
        try:
            timestamp = utc2met(string2sec(timestamp, '%Y/%j'))
        except ValueError:
            timestamp = utc2met(string2sec(timestamp, '%d/%b/%Y'))
        if timestamp >= minTime and timestamp <= maxTime:
            maskDict[timestamp] = totNumStr
    timestamps = maskDict.keys()
    timestamps.sort()
    pl = ROOT.TPolyLine()
    pl.SetLineWidth(2)
    pl.SetLineColor(color)
    pl.SetLineStyle(0)
    ylast = None
    for (i, x) in enumerate(timestamps):
        n = maskDict[x]
        y = n
        if ylast is not None:
            pl.SetNextPoint(x, ylast)
            pl.SetNextPoint(x, y)
        else:
            pl.SetNextPoint(x, y)
        ylast = y
    pl.SetNextPoint(maxTime, ylast)
    store(pl)
    return pl

def setupStripChart(g, minTime = MIN_TIME, maxTime = MAX_TIME):
    g.GetXaxis().SetRangeUser(minTime, maxTime)
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

def drawSIUReboot(ymin, ymax, ylabel = None):
    if not DRAW_SIU_REBOOT:
        return
    ylabel = ylabel or 1.1*ymax
    drawMarker(SIU_REBOOT, ymin, ymax, 'SIU reboot', ROOT.kRed, ylabel)
    drawMarker(SIU_RECOVER, ymin, ymax, '', ROOT.kRed, ylabel)
        
def fitTrend(g, minTime = MIN_TIME, maxTime = MAX_TIME,
             label = 'Average value', draw = True):
    gName = g.GetName()
    print 'Fitting graph %s...' % gName
    fName = '%s_fitfunc' % gName
    f = ROOT.TF1(fName, 'pol1', minTime, maxTime)
    f.SetLineColor(ROOT.kBlue)
    store(f)
    g.Fit(fName, 'RQN')
    if draw:
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
            proj = sec2string(met2utc(proj), '%d-%b-%Y %H:%M:%S')
            print 'Tower will intercept 0.98 at %s' % proj
        except:
            pass
        mean     *= 100
        meanErr  *= 100
        slope    *= (100*SECS_PER_YEAR)
        slopeErr *= (100*SECS_PER_YEAR)
        line1 = 'Average hit efficiency = (%.2f #pm %.2f) %%' % (mean, meanErr)
        line2 = 'Slope = (%s%.4f #pm %.4f) %% year^{-1}' %\
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
    if draw:
        l.Draw()
        ROOT.gPad.Update()
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

    def plotHitEfficiency(self, sampleTowers = [0, 15]):
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
        hMean = ROOT.TH1F('h_hit_eff_mean', 'h_hit_eff_mean', 61, 0.97, 1.01)
        store(hMean)
        hMean.SetXTitle('Average hit efficiency')
        hMean.SetYTitle('Entries/bin')
        hMean.SetLineWidth(LINE_WIDTH)
        hSlope = ROOT.TH1F('h_hit_eff_slope', 'h_hit_eff_slope', 50, -0.2, 0.2)
        store(hSlope)
        hSlope.SetXTitle('Hit efficiency slope (% year^{-1})')
        hSlope.SetYTitle('Entries/bin')
        hSlope.SetLineWidth(LINE_WIDTH)
        l98h = ROOT.TLine(MIN_TIME, 0.98, MAX_TIME, 0.98)
        l98h.SetLineWidth(2)
        l98h.SetLineStyle(7)
        l98h.SetLineColor(ROOT.kRed)
        store(l98h)
        for tower in range(16):
            g = self.GraphDict['hit_efficiency_%d' % tower]
            setupStripChart(g)
            g.GetYaxis().SetRangeUser(0.96, 1.005)
            g.GetYaxis().SetNdivisions(508)
            g.GetYaxis().SetTitle('Average hit efficiency')
            if tower in sampleTowers:
                c = getSkinnyCanvas('hit_eff_canvas_%d' % tower,
                                    'Hit efficiency, tower %d' % tower,
                                    grid = True)
                g.Draw('ap')
                drawTitle('Tower %d' % tower) 
                l98h.Draw()
                drawSIUReboot(0.96, 1.005, 1.006)
                c.Update()
            f = fitTrend(g, draw = (tower in sampleTowers))
            if tower in sampleTowers:
                saveCanvas(c)
            hMean.Fill(f.Eval(0.5*(MIN_TIME + MAX_TIME)))
            hSlope.Fill(f.GetParameter(1)*(100*SECS_PER_YEAR))
        c = getCanvas('hit_eff_mean_canvas', 'Mean hit efficiency')
        hMean.Draw()
        l98v = ROOT.TLine(0.98, 0, 0.98, 1.05*hMean.GetMaximum())
        l98v.SetLineWidth(2)
        l98v.SetLineStyle(7)
        l98v.SetLineColor(ROOT.kRed)
        store(l98v)
        l98v.Draw()
        c.Update()
        saveCanvas(c)
        c = getCanvas('hit_eff_slope_canvas', 'Hit efficiency slope')
        hSlope.Draw()
        c.Update()
        saveCanvas(c)

    def plotTrigEfficiency(self, sampleTowers = [0, 15]):
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
        hMean = ROOT.TH1F('h_trg_eff_mean', 'h_trg_eff_mean', 50, 0.995, 1.005)
        store(hMean)
        hMean.SetXTitle('Average trigger efficiency')
        hMean.SetYTitle('Entries/bin')
        hMean.SetLineWidth(LINE_WIDTH)
        hSlope = ROOT.TH1F('h_trg_eff_slope', 'h_trg_eff_slope', 50, -0.2, 0.2)
        store(hSlope)
        hSlope.SetXTitle('Trigger efficiency slope (% year^{-1})')
        hSlope.SetYTitle('Entries/bin')
        hSlope.SetLineWidth(LINE_WIDTH)
        for tower in range(16):
            g = self.GraphDict['trg_efficiency_%d' % tower]
            setupStripChart(g)
            g.GetYaxis().SetRangeUser(0.8, 1.1)
            g.GetYaxis().SetNdivisions(508)
            g.GetYaxis().SetTitle('Average trigger efficiency')
            if tower in sampleTowers:
                c = getSkinnyCanvas('trg_eff_canvas_%d' % tower,
                                    'Trigger efficiency, tower %d' % tower,
                                    grid = True)
                g.Draw('ap')
                drawSIUReboot(0.8, 1.1, 1.108)
                drawTitle('Tower %d' % tower) 
            f = fitTrend(g, 1.06*MIN_TIME, draw = (tower in sampleTowers))
            if tower in sampleTowers:
                saveCanvas(c)
            hMean.Fill(f.Eval(0.5*(MIN_TIME + MAX_TIME)))
            hSlope.Fill(f.GetParameter(1)*(100*SECS_PER_YEAR))
            c.Update()
        c = getCanvas('trg_eff_mean_canvas', 'Mean trigger efficiency')
        hMean.Draw()
        c.Update()
        saveCanvas(c)
        c = getCanvas('trg_eff_slope_canvas', 'Trigger efficiency slope')
        hSlope.Draw()
        c.Update()
        saveCanvas(c)

    def plotTOTPeak(self, probThreshold = 0,
                    sampleLayers = [(15, 10), (0, 14), (6, 26), (6, 31)]):
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
        gLAT = ROOT.TGraphErrors()
        gLAT.SetName('tot_peak')
        self.GraphDict[gLAT.GetName()] = gLAT
        for tower in range(16):
            for plane in range(36):
                g = ROOT.TGraphErrors()
                g.SetName('tot_peak_%d_%d' % (tower, plane))
                self.GraphDict[g.GetName()] = g
        one = numpy.ones((16, 36), 'f')
        for i in xrange(self.NumEntries):
            self.RootTree.GetEntry(i)
            x = self.getTimestamp(i)
            peak = (v*(p > probThreshold)).sum()
            peakErr = (dv*(p > probThreshold)).sum()
            entries = (one*(p > probThreshold)).sum()
            peak /= entries
            peakErr /= entries**1.5
            gLAT.SetPoint(i, x, peak)
            gLAT.SetPointError(i, 0, peakErr)
            for tower in range(16):
                for plane in range(36):
                    g = self.GraphDict['tot_peak_%d_%d' % (tower, plane)]
                    g.SetPoint(i, x, v[tower][plane])
                    g.SetPointError(i, 0, dv[tower][plane])
        gLAT.GetYaxis().SetRangeUser(4, 6)
        gLAT.GetYaxis().SetTitle('Average TOT peak position (fC)')
        c = getSkinnyCanvas('tot_peak_c', 'TOT average peak position', True)
        setupStripChart(gLAT)
        gLAT.Draw('ap')
        drawSIUReboot(4, 6, 6.05)
        drawTitle('LAT average')
        f = fitTrend(gLAT, 260810033)
        totDict = {260810033: 5.8,
                   246823875: 5.6}
        for (timestamp, text) in TOT_CHANGE_DICT.items():
            drawMarker(timestamp, 4, totDict[timestamp], text)
        c.Update()
        saveCanvas(c)
        hMean = ROOT.TH1F('h_tot_peak_mean', 'h_tot_peak_mean', 50, 4.7, 5.0)
        store(hMean)
        hMean.SetXTitle('Average TOT peak (fC)')
        hMean.SetYTitle('Entries/bin')
        hMean.SetLineWidth(LINE_WIDTH)
        hSlope = ROOT.TH1F('h_tot_peak_slope', 'h_tot_peak_slope',
                           50, -0.075, 0.075)
        store(hSlope)
        hSlope.SetXTitle('TOT peak slope (fC year^{-1})')
        hSlope.SetYTitle('Entries/bin')
        hSlope.SetLineWidth(LINE_WIDTH)
        notes = []
        for tower in range(16):
            for plane in range(36):
                g = self.GraphDict['tot_peak_%d_%d' % (tower, plane)]
                g.GetYaxis().SetRangeUser(4, 6)
                g.GetYaxis().SetTitle('Average TOT peak position (fC)')
                if (tower, plane) in sampleLayers:
                    c = getSkinnyCanvas('tot_peak_c_%d_%d' % (tower, plane),
                        'TOT average peak position (Tower %d, plane %d)' %\
                        (tower, plane), True)
                    setupStripChart(g)
                    g.Draw('ap')
                    drawSIUReboot(4, 6, 6.05)
                    drawTitle('Tower %d, plane %d' % (tower, plane))
                f = fitTrend(g, 260810033,
                             draw = ((tower, plane) in sampleLayers))
                if (tower, plane) in sampleLayers:
                    for (timestamp, text) in TOT_CHANGE_DICT.items():
                        drawMarker(timestamp, 4, totDict[timestamp], text)
                    c.Update()
                    saveCanvas(c)
                mean  = f.Eval(0.5*(MIN_TIME + MAX_TIME))
                slope = f.GetParameter(1)*SECS_PER_YEAR
                if abs(mean - 4.85) > 0.15 or abs(slope) > 0.075:
                    notes.append('Tower %d, plane %d: mean = %f, slope = %f' %\
                                     (tower, plane, mean, slope))
                hMean.Fill(mean)
                hSlope.Fill(slope)
        for note in notes:
            print note
        c = getCanvas('tot_peak_mean_canvas', 'Mean TOT peak')
        hMean.Draw()
        c.Update()
        saveCanvas(c)
        c = getCanvas('tot_peak_slope_canvas', 'TOT peak slope')
        hSlope.Draw()
        c.Update()
        saveCanvas(c)

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
        g.GetYaxis().SetTitle('Noise occupancy')
        gSample.GetYaxis().SetRangeUser(1e-3, 1.5e-1)
        gSample.GetYaxis().SetTitle('Noise occupancy')
        cSample = getSkinnyCanvas('noise_occ_sample_c',
                            'Occupancy for Tower %d, layer %d' % sampleLayer,
                            True)
        cSample.SetLogy(True)
        setupStripChart(gSample)
        gSample.Draw('ap')
        llim = ROOT.TLine(MIN_TIME, 0.08, MAX_TIME, 0.08)
        store(llim)
        llim.SetLineColor(ROOT.kRed)
        llim.SetLineStyle(7)
        llim.SetLineWidth(2)
        llim.Draw()
        drawTitle('Tower %d, plane %d' % sampleLayer)
        f = fitTrend(gSample, 1.015*MIN_TIME)
        drawSIUReboot(1e-3, 1.5e-1)
        cSample.Update()
        saveCanvas(cSample)
        gInsert = gSample.Clone()
        store(gInsert)
        gInsert.GetYaxis().SetTitleOffset(0.9)
        gInsert.GetYaxis().SetRangeUser(1e-3, 1e-1)
        gInsert.GetXaxis().SetTitleOffset(1.75)
        setupStripChart(gInsert)
        insert = ROOT.TPad('insert', 'insert', 0.15, 0.45, 0.65, 0.9)
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
                   'TKR monitoring feature (SSC-132) :-)')
        insert.Update()
        cSample.Update()
        saveCanvas(cSample, 'noise_occ_sample_c_insert.eps')
        c = getSkinnyCanvas('noise_occ_worst_c',
                            'Occupancy for the worst layer', True)
        c.SetLogy(True)
        setupStripChart(g)
        g.Draw('ap')
        drawTitle('Worst TKR plane')
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
            if timestamp >= MIN_TIME and timestamp <= MAX_TIME:
                text = '#splitline{+%d strips (%d)}{%s}' %\
                       (numStr, totNumStr, jira)
                #drawMarker(timestamp, 1e-2, yDict[jira], text,
                #           ylabel = 1.3*yDict[jira])
        c.Update()
        saveCanvas(c)

    def plotMaskStripChart(self, minTime = LAUNCH_TIME, maxTime = MAX_TIME):
        ROOT.gStyle.SetOptStat(0)
        ymin = 0
        ymax = 475
        sc = getMaskedStripChart(ymin, ymax, ROOT.kBlack)
        sc0 = getMaskedStripChart(ymin, ymax, ROOT.kRed, 0)
        sc3 = getMaskedStripChart(ymin, ymax, ROOT.kBlue, 3)
        h = ROOT.TH1F('h_mask_strip', 'h_mask_strip', 10000, minTime, maxTime)
        store(h)
        setupStripChart(h, minTime)
        h.SetMinimum(ymin)
        h.SetMaximum(ymax)
        c = getSkinnyCanvas('c_masked_strip', 'Masked strips', True)
        h.SetYTitle('Number of masked strips')
        h.GetYaxis().SetTitleOffset(0.5)
        h.Draw()
        sc.Draw('same')
        sc0.Draw('same')
        sc3.Draw('same')
        for timestamp, (numStr, totNumStr, jira) in STRIP_MASK_DICT.items():
            try:
                totNumStr0 = STRIP_MASK_DICT_0[timestamp][1]
            except:
                totNumStr0 = None
            try:
                totNumStr3 = STRIP_MASK_DICT_3[timestamp][1]
            except:
                totNumStr3 = None
            try:
                timestamp = utc2met(string2sec(timestamp, '%Y/%j'))
            except ValueError:
                timestamp = utc2met(string2sec(timestamp, '%d/%b/%Y'))
            if timestamp >= minTime and timestamp <= maxTime and \
                    totNumStr not in [333, 342]:
                l = ROOT.TLatex(timestamp, totNumStr+5, '%d' % totNumStr)
                store(l)
                l.SetTextAlign(12)
                l.SetTextAngle(60)
                l.SetTextColor(ROOT.kBlack)
                l.SetTextSize(TEXT_SIZE - 5)
                l.Draw()
                if totNumStr0 is not None:
                    l = ROOT.TLatex(timestamp, totNumStr0+5, '%d' % totNumStr0)
                    store(l)
                    l.SetTextAlign(12)
                    l.SetTextAngle(60)
                    l.SetTextColor(ROOT.kRed)
                    l.SetTextSize(TEXT_SIZE - 5)
                    l.Draw()
                if totNumStr3 is not None and totNumStr3 not in [1, 3, 20]:
                    l = ROOT.TLatex(timestamp, totNumStr3+5, '%d' % totNumStr3)
                    store(l)
                    l.SetTextAlign(12)
                    l.SetTextAngle(60)
                    l.SetTextColor(ROOT.kBlue)
                    l.SetTextSize(TEXT_SIZE - 5)
                    l.Draw()
        l = ROOT.TLatex(1.18*MIN_TIME, 290, 'Full LAT')
        l.SetTextColor(ROOT.kBlack)
        l.Draw()
        store(l)
        l = ROOT.TLatex(1.18*MIN_TIME, 75, 'Tower 0')
        l.SetTextColor(ROOT.kRed)
        l.Draw()
        store(l)
        l = ROOT.TLatex(1.25*MIN_TIME, 50, 'Tower 3')
        l.SetTextColor(ROOT.kBlue)
        l.Draw()
        store(l)
        c.Update()
        saveCanvas(c)


if __name__ == '__main__':
    print LAUNCH_TIME
    p = pTkrTrendPlotter('/data/work/datamon/runs/tkrtrend/tkrtrend.root')
    #p.plotHitEfficiency()
    #p.plotTrigEfficiency()
    #p.plotTOTPeak()
    #p.plotNoiseOcc()
    #p.plotMaskStripChart()
