import ROOT
ROOT.gROOT.SetStyle('Plain')
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetPadRightMargin(0.01)
ROOT.gStyle.SetPadLeftMargin(0.07)
ROOT.gStyle.SetTitleOffset(0.7, 'Y')
ROOT.gStyle.SetPadGridX(True)
ROOT.gStyle.SetPadGridY(True)

import sys
sys.path.append('../../Report/python')

import numpy
import pickle
import os
import copy

from pTimeConverter import *


TIME_FORMAT = '%b %d 20%y %H:%M%F2000-12-31 23:00:00'
ALIAS_DICT  = {'Time': '0.5*(Digi_Trend_Bin_Start + Digi_Trend_Bin_End)',
               'Hit63': 'Digi_Trend_OutF_Normalized_AcdHit_AcdTile[63]',
               'NormTransient': 'Merit_Trend_OutF_NormRateTransientEvts',
               'RockAngle': 'FastMon_Trend_Mean_FastMon_SpaceCraft_RockAngle'}
HIT_RATE_THR_63 = 0.22
NUM_BINS_THR_63 = 3
PICKLE_FILE_NAME = 'flares.pickle'



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
            l.SetLineColor(ROOT.kRed)
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



class pSolarFlarePlotter:

    def __init__(self, filePath):
        self.RootFile = ROOT.TFile(filePath)
        self.RootTree = self.RootFile.Get('Time')
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
                       ytitle = None, ymin = None, ymax = None):
        ytitle = ytitle or expr
        if isinstance(tmin, str):
            tmin = utc2met(convert2sec(tmin))
        if isinstance(tmax, str):
            tmax = utc2met(convert2sec(tmax))
        tcut = '(Time > %f && Time < %f)' % (tmin, tmax)
        self.RootTree.Draw('%s:Time' % expr, tcut)
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

    def drawFlare(self, i = 0, padding = 1200, minLoss = 0.1, badPadding = 0,
                  thresholdIntLoss = 1., thresholdDiffLoss = 0.15):
        c = ROOT.TCanvas('cFlare%d' % i, 'Flare #%d' % i, 600, 800)
        self.Pool.append(c)
        c.Divide(1, 3)
        interval = self.FlareList[i]
        tmin = interval.StartTime - padding
        tmax = interval.EndTime + padding
        # Draw the ACD hit rate.
        c.cd(1)
        self.drawStripChart('Hit63', tmin, tmax, 'Hit rate in tile 63', 0, 1)
        for item in interval.getBounds(0, 1):
            self.Pool.append(item)
            item.Draw()
        # Draw the normalized transient rate and fit excluding the flare
        # interval.
        c.cd(2)
        g2 = self.drawStripChart('NormTransient', tmin, tmax,
                            'Normalized transient rate', 0, 2)
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
        # Construct the integral deficit.
        c.cd(3)
        g3 = g2.Clone()
        x = ROOT.Double()
        y = ROOT.Double()
        integral = 0
        for i in range(g2.GetN()):
            g2.GetPoint(i, x, y)
            if x > self.StartTime:
                integral -= 15./60.*(y - f2.Eval(x))
            g3.SetPoint(i, x, integral)
        g3.GetXaxis().SetTitle('Time UTC')
        g3.GetXaxis().SetNdivisions(506)
        g3.GetXaxis().SetTimeDisplay(True)
        g3.GetXaxis().SetTimeFormat(TIME_FORMAT)
        g3.GetYaxis().SetTitle('Transient loss (minutes equivalent)')
        self.Pool.append(g3)
        g3.Draw('ap')
        # Define the bad interval
        fName = 'fFitLoss%d' % i
        f4 = ROOT.TF1(fName, 'pol0', self.EndTime, tmax)
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
        if loss < thresholdIntLoss:
            ROOT.gPad.Update()
            return c
        minBad = None
        maxBad = None
        for i in range(g3.GetN()):
            g3.GetPoint(i, x, y)
            if x > self.StartTime:
                if minBad is None and y > minLoss:
                    minBad = float(x)
                if maxBad is None and y > 0.98*loss:
                    maxBad = float(x)
        if minBad is None or maxBad is None or maxBad < minBad:
            return c
        minBad -= badPadding
        maxBad += badPadding
        badMinutes = (maxBad - minBad)/60.
        if loss/badMinutes < thresholdDiffLoss:
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
        c.cd(2)
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
        return c

    def fitFuncRate(self, x, par):
        x = x[0]
        if x > self.StartTime and x < self.EndTime:
            ROOT.TF1.RejectPoint()
            return 0
        x = x - 0.5*(self.StartTime + self.EndTime)
        return par[0] + par[1]*x + par[2]*(x**2)

    def createReport(self, filePath, numFlares = None):
        numFlares = numFlares or len(self.FlareList)
        for i in range(numFlares):
            c = self.drawFlare(i)
            c.Update()
            if i == 0:
                c.SaveAs('%s(' % filePath)
            elif i == numFlares - 1:
                c.SaveAs('%s)' % filePath)
            else:
                c.SaveAs('%s' % filePath)
        


if __name__ == '__main__':
    filePath = '/data/work/datamon/solartrend/solarflare_trend.root'
    plotter = pSolarFlarePlotter(filePath)
    plotter.createReport('bad_time_intervals.ps')
