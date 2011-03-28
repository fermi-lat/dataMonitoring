import ROOT
ROOT.gROOT.SetStyle('Plain')
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetPadRightMargin(0.01)
ROOT.gStyle.SetPadLeftMargin(0.08)
ROOT.gStyle.SetPadBottomMargin(0.14)
ROOT.gStyle.SetTitleOffset(0.5, 'Y')
ROOT.gStyle.SetPadGridX(True)
ROOT.gStyle.SetPadGridY(True)
ROOT.gStyle.SetTitleSize(0.07, 'XY')
ROOT.gStyle.SetLabelSize(0.05, 'XY')

import sys
sys.path.append('../../Report/python')

import numpy
import pickle
import os
import copy

from pTimeConverter import *


#TIME_FORMAT = '%b %d 20%y %H:%M%F2000-12-31 23:00:00'
TIME_FORMAT = '%b/%d/%y %H:%M%F2000-12-31 23:00:00'
ALIAS_DICT  = {'Time': '0.5*(Digi_Trend_Bin_Start + Digi_Trend_Bin_End)',
               'Hit63': 'Digi_Trend_OutF_Normalized_AcdHit_AcdTile[63]',
               'NormTransient': 'Merit_Trend_OutF_NormRateTransientEvts',
               'Transient': 'Merit_Trend_Rate_TransientEvts',
               'RockAngle': 'FastMon_Trend_Mean_FastMon_SpaceCraft_RockAngle'}
NORM_ACD_TILE_COUNT_ALIAS = 'Merit.Mean_AcdTileCount/(8.73 - 0.283466*Rate_TriggerEngine[10] + 0.00615361*Rate_TriggerEngine[10]*Rate_TriggerEngine[10])'
HIT_RATE_THR_63 = 0.22
NUM_BINS_THR_63 = 3
PICKLE_FILE_NAME = 'flares.pickle'

# Finder algorithm parameters
TIME_PADDING   = 1200 # [s]   the time pad before/after the flare
PLATEAU_LEN    = 200  # [s]   the legth of the interval to fit the plateau
BAD_TIME_START = 0.1  # [min] the absolute time loss defining the BTI start
BAD_TIME_END   = 0.98 # []    the fraction of the int. loss defining the BTI end
BAD_TIME_PAD   = 0.0  # [s]   additional padding to the BTI
MIN_INT_LOSS   = 1.0  # [min] the minimum integrated loss for defining a BTI
MIN_DIFF_LOSS  = 0.15 # []    the minimum fractional loss for defining a BTI
ACD_TILE_THRES = 1.6  # []    the threshold on Eric's normalized tile count



class pFlareInterval:

    def __init__(self, startTime, startRow, endTime, endRow):
        self.StartRow = startRow
        self.StartTime = startTime
        self.EndRow = endRow
        self.EndTime = endTime
        self.NumRows = self.EndRow - self.StartRow
        # Mind the gaps between runs, here!
        self.Duration = self.EndTime - self.StartTime
        
    def getBounds(self, ymin = 0, ymax = 1):
        startLine = ROOT.TLine(self.StartTime, ymin, self.StartTime, ymax)
        endLine = ROOT.TLine(self.EndTime, ymin, self.EndTime, ymax)
        for l in [startLine, endLine]:
            l.SetLineColor(ROOT.kBlue)
            l.SetLineStyle(7)
            l.SetLineWidth(2)
        return (startLine, endLine)

    def __str__(self):
        return 'T = %d--%d (%d row(s): %d--%d)' %\
            (self.StartTime, self.EndTime, self.NumRows, self.StartRow,
             self.EndRow)


    def __cmp__(self, other):
        if self.NumRows <= other.NumRows:
            return 1
        else:
            return -1


class pBadTimeInterval:

    def __init__(self, startTime, endTime, intLoss):
        self.StartTime = startTime
        self.EndTime   = endTime
        self.Duration  = (self.EndTime - self.StartTime)/60.
        self.IntLoss   = intLoss
        self.DiffLoss  = self.IntLoss/self.Duration
        self.Canvas    = None

    def __cmp__(self, other):
        if self.StartTime > other.StartTime:
            return 1
        elif self.StartTime < other.StartTime:
            return -1
        else:
            return 0

    def __str__(self):
        return '%s--%s (dur=%.2f min, int. loss=%.2f min, diff. loss=%.2f)' %\
            (self.StartTime, self.EndTime, self.Duration, self.IntLoss,
             self.DiffLoss)



class pSolarFlarePlotter:

    def __init__(self, filePath):
        self.RootTree = ROOT.TChain('Time')
        self.RootTree.Add(filePath)
        for (key, value) in ALIAS_DICT.items():
            self.RootTree.SetAlias(key, value)
        if os.path.exists(PICKLE_FILE_NAME):
            print 'Unpickling the flare list...'
            pickleFile = file(PICKLE_FILE_NAME)
            self.FlareList = pickle.load(pickleFile)
            pickleFile.close()
            print 'Done.'
        else:
            self.__findFlares()
        self.Pool = []
        self.BadTimeIntervalList = []
        # New stuff from Eric
        self.DigiTree = ROOT.TChain('Time')
        self.DigiTree.Add('/data/work/datamon/solartrend/digiTrend_reduce.root')
        self.MeritTree = ROOT.TChain('Time')
        self.MeritTree.Add('/data/work/datamon/solartrend/meritTrend_reduce.root')
        self.DigiTree.AddFriend(self.MeritTree, 'Merit')
        self.DigiTree.SetAlias('NormAcdTileCount', NORM_ACD_TILE_COUNT_ALIAS)
        self.DigiTree.SetAlias('Time', '0.5*(Bin_Start + Bin_End)')

    def __findFlares(self):
        print 'Looping over data points to identify flares...'
        self.FlareList = []
        hitRate = numpy.zeros((128,), 'f')
        branchName = 'Digi_Trend_OutF_Normalized_AcdHit_AcdTile'
        self.RootTree.SetBranchAddress(branchName, hitRate)
        binStart = numpy.zeros((1,), 'I')
        branchName = 'Digi_Trend_Bin_Start'
        self.RootTree.SetBranchAddress(branchName, binStart)
        inFlare = False
        self.RootTree.GetEntry(0)
        tprev = binStart[0]
        for i in xrange(self.RootTree.GetEntries()):
            self.RootTree.GetEntry(i)
            r = hitRate[63]
            t = binStart[0]
            if r > HIT_RATE_THR_63:
                if not inFlare:
                    (startTime, startRow) = (tprev, i - 1)
                inFlare = True
            else:
                if inFlare:
                    # Gap between runs?
                    #if t - previousTime > 20:
                    #    endTime = previousTime
                    #    endRow = i - 1
                    #else:
                    endTime = t
                    endRow = i
                    if endRow - startRow > NUM_BINS_THR_63:
                        interval = pFlareInterval(startTime, startRow,
                                                  endTime, endRow)
                        self.FlareList.append(interval)
                inFlare = False
            tprev = t
        print 'Done!'
        print 'Pickling the flare list...'
        self.FlareList.sort()
        pickleFile = file(PICKLE_FILE_NAME, 'w')
        pickle.dump(self.FlareList, pickleFile)
        pickleFile.close()
        print 'Done.'

    def drawStripChart(self, expr,
                       tmin = 'Jan/01/2011 00:00:00',
                       tmax = 'Mar/20/2011 00:00:00',
                       ytitle = None, ymin = None, ymax = None, tree = None):
        ytitle = ytitle or expr
        if isinstance(tmin, str):
            tmin = utc2met(convert2sec(tmin))
        if isinstance(tmax, str):
            tmax = utc2met(convert2sec(tmax))
        tcut = '(Time > %f && Time < %f)' % (tmin, tmax)
        tree = tree or self.RootTree
        tree.Draw('%s:Time' % expr, tcut)
        g = ROOT.gPad.GetPrimitive('Graph').Clone()
        g.SetMarkerStyle(26)
        g.SetMarkerSize(0.5)
        g.GetXaxis().SetTitle('Time UTC')
        g.GetXaxis().SetNdivisions(506)
        g.GetXaxis().SetTimeDisplay(True)
        g.GetXaxis().SetTimeFormat(TIME_FORMAT)
        g.GetYaxis().SetTitle(ytitle)
        if ymin is not None and ymax is not None:
            g.GetYaxis().SetRangeUser(ymin, ymax)
        g.Draw('ap')
        ROOT.gPad.Update()
        self.Pool.append(g)
        return g

    def drawFlare(self, i = 0, interactive = False):
        c = ROOT.TCanvas('cFlare%d' % i, 'Flare #%d' % i, 1200, 800)
        self.Pool.append(c)
        c.Divide(2, 3)
        interval = self.FlareList[i]
        tmin = interval.StartTime - TIME_PADDING
        tmax = interval.EndTime + TIME_PADDING
        # Draw the ACD hit rate.
        c.cd(1)
        self.drawStripChart('Hit63', tmin, tmax, 'Hit rate in tile 63', 0, 1)
        for item in interval.getBounds(0, 1):
            self.Pool.append(item)
            item.Draw()
        # Draw the transient rate event.
        c.cd(3)
        g33 = self.drawStripChart('Transient', tmin, tmax, 'Transient Rate')
        # Draw the rocking angle.
        c.cd(5)
        g55 = self.drawStripChart('RockAngle', tmin, tmax, 'Rocking Angle',
                                  0., 90.)
        # Draw Eric's metric.
        c.cd(2)
        g22 = self.drawStripChart('NormAcdTileCount', tmin, tmax,
                                  'Normalized ACD tile count', 0, 8,
                                  tree = self.DigiTree)
        l = ROOT.TLine(tmin,  ACD_TILE_THRES, tmax,  ACD_TILE_THRES)
        l.SetLineColor(ROOT.kBlue)
        l.SetLineWidth(2)
        l.SetLineStyle(7)
        self.Pool.append(l)
        l.Draw()
        x = ROOT.Double()
        y = ROOT.Double()
        inFlare = False
        minEric = None
        maxEric = None
        for i in range(g22.GetN()):
            g22.GetPoint(i, x, y)
            if not inFlare and y > ACD_TILE_THRES:
                minEric = float(x)
                inFlare = True
            if inFlare and y < ACD_TILE_THRES:
                maxEric = float(x)
                break
        if minEric is not None and maxEric is not None:
            print minEric, maxEric
            l1 = ROOT.TLine(minEric, 0, minEric, 2)
            l1.SetLineColor(ROOT.kRed)
            l1.SetLineWidth(2)
            l1.SetLineStyle(7)
            self.Pool.append(l1)
            l1.Draw()
            l2 = ROOT.TLine(maxEric, 0, maxEric, 2)
            l2.SetLineColor(ROOT.kRed)
            l2.SetLineWidth(2)
            l2.SetLineStyle(7)
            self.Pool.append(l2)
            l2.Draw()
            strFormat = getStringFormat('GCN notice')
            minEricStr = sec2string(met2utc(minEric), strFormat)
            maxEricStr = sec2string(met2utc(maxEric), strFormat)
            l1 = ROOT.TLatex(minEric, 2, '%d--%s' % (minEric, minEricStr))
            l1.SetTextAngle(30)
            l1.SetTextColor(ROOT.kRed)
            self.Pool.append(l1)
            l1.Draw()
            l2 = ROOT.TLatex(maxEric, 2, '%d--%s' % (maxEric, maxEricStr))
            l2.SetTextAngle(30)
            l2.SetTextColor(ROOT.kRed)
            self.Pool.append(l2)
            l2.Draw()
            ROOT.gPad.Update()
        # Draw the normalized transient rate and fit excluding the flare
        # interval.
        c.cd(4)
        g2 = self.drawStripChart('NormTransient', tmin, tmax,
                                 'Normalized transient rate', 0, 2.5)
        if interactive:
            c.Update()
            c.SaveAs('Step1.pdf')
            raw_input('Press enter to continue')
        self.StartTime = interval.StartTime
        self.EndTime = interval.EndTime
        fName = 'fFitRate%d' % i
        f = ROOT.TF1(fName, self.fitFuncRate, self.StartTime, self.EndTime, 3)
        g2.Fit(fName, 'N')
        f2 = ROOT.TF1(fName, '[0] + [1]*(x-[3]) + [2]*(x-[3])**2', tmin, tmax)
        f2.SetParameter(0, f.GetParameter(0))
        f2.SetParameter(1, f.GetParameter(1))
        f2.SetParameter(2, f.GetParameter(2))
        f2.SetParameter(3, 0.5*(self.StartTime + self.EndTime))
        f2.SetLineColor(ROOT.kBlue)
        f2.SetLineStyle(7)
        self.Pool.append(f2)
        f2.Draw('same')
        ROOT.gPad.Update()
        if interactive:
            c.Update()
            c.SaveAs('Step2.pdf')
            raw_input('Press enter to continue')
        # Construct the integral deficit.
        c.cd(6)
        g3 = g2.Clone()
        x = ROOT.Double()
        y = ROOT.Double()
        integral = 0
        for i in range(g2.GetN()):
            g2.GetPoint(i, x, y)
            if x > self.StartTime:
                delta = -15./60.*(y - f2.Eval(x))
                if integral <= 0 and delta < 0:
                    pass
                else:
                    integral += delta
            g3.SetPoint(i, x, integral)
        g3.GetXaxis().SetTitle('Time UTC')
        g3.GetXaxis().SetNdivisions(506)
        g3.GetXaxis().SetTimeDisplay(True)
        g3.GetXaxis().SetTimeFormat(TIME_FORMAT)
        g3.GetYaxis().SetTitle('Integrated loss (minutes)')
        self.Pool.append(g3)
        g3.Draw('ap')
        if interactive:
            c.Update()
            c.SaveAs('Step3.pdf')
            raw_input('Press enter to continue')
        # Define the bad interval
        fName = 'fFitLoss%d' % i
        f4 = ROOT.TF1(fName, 'pol0', self.EndTime, self.EndTime + PLATEAU_LEN)
        g3.Fit(f4, 'RN')
        loss = f4.GetParameter(0)
        f4 = ROOT.TF1(fName, 'pol0', tmin, tmax)
        f4.SetParameter(0, loss)
        f4.SetLineColor(ROOT.kBlue)
        f4.SetLineStyle(7)
        self.Pool.append(f4)
        f4.Draw('same')
        label = ROOT.TLatex(0.7, 0.6, 'Total loss: %.2f minutes' % loss)
        label.SetTextColor(ROOT.kBlue)
        label.SetNDC()
        self.Pool.append(label)
        label.Draw()
        if loss < MIN_INT_LOSS:
            ROOT.gPad.Update()
            return c
        minBad = None
        maxBad = None
        for i in range(g3.GetN()):
            g3.GetPoint(i, x, y)
            if x > self.StartTime:
                if minBad is None and y > BAD_TIME_START:
                    minBad = float(x)
                if maxBad is None and y > BAD_TIME_END*loss:
                    maxBad = float(x)
        if minBad is None or maxBad is None or maxBad < minBad:
            return c
        minBad -= BAD_TIME_PAD
        maxBad += BAD_TIME_PAD
        badMinutes = (maxBad - minBad)/60.
        badTimeInterval = pBadTimeInterval(minBad, maxBad, loss) 
        if loss/badMinutes < MIN_DIFF_LOSS:
            ROOT.gPad.Update()
            return c
        label = ROOT.TLatex(0.7, 0.55, 'Bad time interval: %.2f minutes' %\
                                badMinutes)
        label.SetTextColor(ROOT.kBlue)
        label.SetNDC()
        self.Pool.append(label)
        label.Draw()
        l1 = ROOT.TLine(minBad, 0, minBad, loss)
        l1.SetLineColor(ROOT.kRed)
        l1.SetLineWidth(2)
        l1.SetLineStyle(7)
        self.Pool.append(l1)
        l1.Draw()
        l2 = ROOT.TLine(maxBad, 0, maxBad, loss)
        l2.SetLineColor(ROOT.kRed)
        l2.SetLineWidth(2)
        l2.SetLineStyle(7)
        self.Pool.append(l2)
        l2.Draw()
        ROOT.gPad.Update()
        c.cd(4)
        l1 = ROOT.TLine(minBad, 0, minBad, 1)
        l1.SetLineColor(ROOT.kRed)
        l1.SetLineWidth(2)
        l1.SetLineStyle(7)
        self.Pool.append(l1)
        l1.Draw()
        l2 = ROOT.TLine(maxBad, 0, maxBad, 1)
        l2.SetLineColor(ROOT.kRed)
        l2.SetLineWidth(2)
        l2.SetLineStyle(7)
        self.Pool.append(l2)
        l2.Draw()
        strFormat = getStringFormat('GCN notice')
        minBadStr = sec2string(met2utc(minBad), strFormat)
        maxBadStr = sec2string(met2utc(maxBad), strFormat)
        l1 = ROOT.TLatex(minBad, 1, '%d--%s' % (minBad, minBadStr))
        l1.SetTextAngle(30)
        l1.SetTextColor(ROOT.kRed)
        self.Pool.append(l1)
        l1.Draw()
        l2 = ROOT.TLatex(maxBad, 1, '%d--%s' % (maxBad, maxBadStr))
        l2.SetTextAngle(30)
        l2.SetTextColor(ROOT.kRed)
        self.Pool.append(l2)
        l2.Draw()
        ROOT.gPad.Update()
        badTimeInterval.Canvas = c
        self.BadTimeIntervalList.append(badTimeInterval)
        if interactive:
            c.Update()
            c.SaveAs('Step4.pdf')
        return c

    def fitFuncRate(self, x, par):
        x = x[0]
        if x > self.StartTime and x < self.EndTime:
            ROOT.TF1.RejectPoint()
            return 0
        x = x - 0.5*(self.StartTime + self.EndTime)
        return par[0] + par[1]*x + par[2]*(x**2)

    def createReport(self, numFlares = None):
        numFlares = numFlares or len(self.FlareList)
        filePath = 'flare_intervals.ps'
        for i in range(numFlares):
            c = self.drawFlare(i)
            c.Update()
            if i == 0:
                c.SaveAs('%s(' % filePath)
            elif i == numFlares - 1:
                c.SaveAs('%s)' % filePath)
            else:
                c.SaveAs('%s' % filePath)
        os.system('ps2pdf %s' % filePath)
        filePath = 'bad_time_intervals.ps'
        self.BadTimeIntervalList.sort()
        for (i, interval) in enumerate(self.BadTimeIntervalList):
            print i, interval
            c = interval.Canvas
            c.SaveAs('bad_time_interval_%d.pdf' % i)
            if i == 0:
                c.SaveAs('%s(' % filePath)
            elif i == numFlares - 1:
                c.SaveAs('%s)' % filePath)
            else:
                c.SaveAs('%s' % filePath)
        os.system('ps2pdf %s' % filePath)

if __name__ == '__main__':
    filePath = '/data/work/datamon/solartrend/solarflare_trend*.root'
    plotter = pSolarFlarePlotter(filePath)
    plotter.createReport()
    #plotter.drawFlare(0)
    #plotter.drawFlare(0, True)
    #plotter.drawFlare(12)
    #plotter.drawFlare(37)
    #plotter.drawFlare(47)
    #plotter.drawFlare(52)
    #plotter.drawFlare(7)
    #plotter.drawFlare(56)
    #plotter.drawFlare(15)
