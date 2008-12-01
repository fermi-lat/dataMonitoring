#!/usr/bin/env python

import os
import sys

from pLongTermTrendMaker import *

sys.path.append('../../Report/python')
from pTimeConverter import *          

ROOT.gStyle.SetCanvasColor(10)
ROOT.gStyle.SetPalette(1)


class pBumpFinder:
    
    def __init__(self, fileListPath, outputFilePath, minStartTime,
                 maxStartTime = None):
        self.HistogramDict = {}
        self.FitFunction = ROOT.TF1('fitFunction', 'pol3')
        self.HighThreshold = 1.13
        self.LowThreshold = 1.10
        if not os.path.exists(fileListPath):
            print 'Creating the file list...'
            query = pDataCatalogQuery('MERIT', minStartTime, maxStartTime)
            query.dumpList(fileListPath)
        else:
            print 'File list %s found.' % fileListPath
            print 'Delete the file if you want to recreate it.'
        self.FileList = file(fileListPath, 'r').readlines()
        for (i, filePath) in enumerate(self.FileList):
            self.FileList[i] = filePath.strip('\n')
        print 'File list contains %s entries.' % len(self.FileList)
        self.OutputRootFile = ROOT.TFile(outputFilePath, 'RECREATE')
        self.OutputLogFile = file(outputFilePath.replace('.root', '.log'), 'w')

    def addHistogram(self, histogram):
        self.HistogramDict[histogram.GetName()] = histogram

    def run(self, interactive = False):
        for filePath in self.FileList:
            self.analyzeRun(filePath, interactive)
        self.OutputRootFile.Write()
        self.OutputRootFile.Close()
        self.OutputLogFile.close()
            

    def analyzeRun(self, filePath, interactive = False, timeBinWidth = 25,
                   runPadding = 150):
        print '\nAnalyzing %s...' % filePath

        # Retrieve run information.
        fileName = os.path.basename(filePath)       
        runId = int(fileName.split('_')[0].strip('r'))
        self.OutputLogFile.writelines('\nAnalyzing run %d...\n' % runId)
        rootFile = ROOT.TXNetFile(filePath)
        if rootFile.IsZombie():
            print 'Switching to local mode.'
            rootFile = ROOT.TFile(filePath)
        meritTuple = rootFile.Get('MeritTuple')
        numEntries = meritTuple.GetEntries()
        meritTuple.GetEntry(0)
        startTime = meritTuple.EvtElapsedTime
        meritTuple.GetEntry(numEntries - 1)
        stopTime = meritTuple.EvtElapsedTime
        runDuration = stopTime - startTime
        numTimeBins = int(runDuration/timeBinWidth)

        if interactive:
            rateCanvas = ROOT.TCanvas('Rate')
            rateCanvas.Divide(2, 2)

        # Create rate histogram.
        hExpression = 'EvtElapsedTime - %f' % startTime
        hName = '%d_rate' % runId
        hRate = ROOT.TH1F(hName, hName, numTimeBins, 0, runDuration)
        hRate.GetXaxis().SetTitle('Elapsed time - run start time (s)')
        hRate.GetYaxis().SetTitle('Average rate (Hz)')
        meritTuple.Project(hName, hExpression)
        for i in range(1, numTimeBins + 1):
            counts = float(hRate.GetBinContent(i))
            timeInterval = hRate.GetBinWidth(i)
            hRate.SetBinContent(i, counts/timeInterval)
        if interactive:
            rateCanvas.cd(1)
            hRate.Draw()
            rateCanvas.Update()

        # Create the McIlwainL histogram and fit the rate vs. McIlwain.
        hExpression = 'PtMcIlwainL:(EvtElapsedTime - %f)' % startTime
        hName = '%d_mcIlwainL2D' % runId
        hMag2D = ROOT.TH2F(hName, hName, numTimeBins, 0, runDuration,
                           1000, 0, 10)
        meritTuple.Project(hName, hExpression)
        profileMag = hMag2D.ProfileX()
        hName = '%d_mcIlwainL' % runId
        hMag = ROOT.TH1F(hName, hName, numTimeBins, 0, runDuration)
        for i in range(1, numTimeBins + 1):
            mcIlwainL = profileMag.GetBinContent(i)
            hMag.SetBinContent(i, mcIlwainL)
        hMag.GetXaxis().SetTitle('Elapsed time - run start time (s)')
        hMag.GetYaxis().SetTitle('McIlwain L')
        if interactive:
            rateCanvas.cd(2)
            hMag.Draw()
            rateCanvas.Update()
        fitGraph = ROOT.TGraph()
        for i in range(1, numTimeBins + 1):
            rate = hRate.GetBinContent(i)
            mcIlwainL = hMag.GetBinContent(i)
            fitGraph.SetPoint(i - 1, mcIlwainL, rate)
        fitGraph.GetXaxis().SetTitle('McIlwain L')
        fitGraph.GetYaxis().SetTitle('Average rate (Hz)')
        if interactive:
            fitOptions = ''
        else:
            fitOptions = 'QN'
        fitGraph.Fit('fitFunction', fitOptions)
        if interactive:
            rateCanvas.cd(3)
            fitGraph.Draw('AP*')
            rateCanvas.Update()
            
        # Create the normalized rate histogram.
        hName = '%d_normalized_rate' % runId
        hNormRate = ROOT.TH1F(hName, hName, numTimeBins, 0, runDuration)
        hNormRate.GetXaxis().SetTitle('Elapsed time - run start time (s)')
        hNormRate.GetYaxis().SetTitle('Normalize rate')
        for i in range(1, numTimeBins + 1):
            rate = hRate.GetBinContent(i)
            mcIlwainL = hMag.GetBinContent(i)
            expRate = self.FitFunction.Eval(mcIlwainL)
            hNormRate.SetBinContent(i, rate/expRate)
        if interactive:
            rateCanvas.cd(4)
            hNormRate.Draw()
            rateCanvas.Update()

        # Search for highest peak.
        maximumBin =  hNormRate.GetMaximumBin()
        peakTime = hNormRate.GetBinCenter(maximumBin)
        peakValue = hNormRate.GetBinContent(maximumBin)
        if peakValue > self.HighThreshold:
            msg = 'Found significant peak (%f) at %f s since the run start.' %\
                  (peakValue, peakTime)
            print msg
            self.OutputLogFile.writelines('%s\n' % msg)
            value = peakValue
            bin = maximumBin
            while value > self.LowThreshold:
                bin -= 1
                value = hNormRate.GetBinContent(bin)
            bumpStartTime = hNormRate.GetBinCenter(bin)
            value = peakValue
            bin = maximumBin
            while value > self.LowThreshold:
                bin += 1
                value = hNormRate.GetBinContent(bin)
            bumpStopTime = hNormRate.GetBinCenter(bin)
            bumpDuration = bumpStopTime - bumpStartTime
            msg = 'Peak edges: %f--%f' % (bumpStartTime, bumpStopTime)
            print msg
            self.OutputLogFile.writelines('%s\n' % msg)
            if bumpStartTime < runPadding:
                msg = 'Bump is close to the beginning of the run.'
                print msg
                self.OutputLogFile.writelines('%s\n' % msg)
            elif (stopTime - startTime - bumpStopTime) < runPadding:
                msg = 'Bump is close to the end of the run.'
                print msg
                self.OutputLogFile.writelines('%s\n' % msg)
            else:
                if interactive:
                    mapCanvas = ROOT.TCanvas('Sky map')
                    mapCanvas.Divide(2, 2)
                bumpCut = 'EvtElapsedTime-%f>%f && EvtElapsedTime-%f<%f' %\
                    (startTime, bumpStartTime, startTime, bumpStopTime)
                beforeCut = 'EvtElapsedTime-%f>%f && EvtElapsedTime-%f<%f' %\
                    (startTime, bumpStartTime - 2*bumpDuration,
                     startTime, bumpStartTime - bumpDuration)
                afterCut = 'EvtElapsedTime-%f>%f && EvtElapsedTime-%f<%f' %\
                    (startTime, bumpStopTime + bumpDuration,
                     startTime, bumpStopTime + 2*bumpDuration)
                aroundCut = '(%s) || (%s)' % (beforeCut, afterCut)
                hName = '%d_map_%s' % (runId, 'bump')
                hMapBump = ROOT.TH2F(hName, hName, 100, 0, 360, 100, -90, 90)
                meritTuple.Project(hName, 'FT1Dec:FT1Ra', bumpCut)
                zmax = hMapBump.GetMaximum()
                if interactive:
                    mapCanvas.cd(1)
                    hMapBump.Draw('colz')
                    mapCanvas.Update()
                hName = '%d_map_%s' % (runId, 'before')
                hMapBefore = ROOT.TH2F(hName, hName, 100, 0, 360, 100, -90, 90)
                meritTuple.Project(hName, 'FT1Dec:FT1Ra', beforeCut)
                hMapBefore.SetMaximum(zmax)
                if interactive:
                    mapCanvas.cd(2)
                    hMapBefore.Draw('colz')
                    mapCanvas.Update()
                hName = '%d_map_%s' % (runId, 'after')
                hMapAfter = ROOT.TH2F(hName, hName, 100, 0, 360, 100, -90, 90)
                hMapAfter.SetMaximum(zmax)
                meritTuple.Project(hName, 'FT1Dec:FT1Ra', afterCut)
                if interactive:
                    mapCanvas.cd(3)
                    hMapAfter.Draw('colz')
                    mapCanvas.Update()
                hName = '%d_map_%s' % (runId, 'around')
                hMapAround = ROOT.TH2F(hName, hName, 100, 0, 360, 100, -90, 90)
                meritTuple.Project(hName, 'FT1Dec:FT1Ra', aroundCut)
                hMapAround.SetMaximum(2*zmax)
                if interactive:
                    mapCanvas.cd(4)
                    hMapAround.Draw('colz')
                    mapCanvas.Update()

                # Spacecraft position.
                hName = '%d_ptpos' % (runId)
                hPtPos = ROOT.TH2F(hName, hName, 100, -180, 180, 100, -35, 35)
                meritTuple.Project(hName, 'PtLat:PtLon', bumpCut)
                if interactive:
                    ptposCanvas = ROOT.TCanvas('PtPos')
                    ptposCanvas.cd()
                    hSpacePos.Draw('colz')
                    ptposCanvas.Update()

                # Write objects to the output ROOT file.
                self.OutputRootFile.cd()
                for object in [hRate, hMag, hNormRate, hMapBump, hMapBefore,
                               hMapAfter, hMapAround, hPtPos]:
                    object.Write()

        if interactive:
            raw_input('Press enter to continue.')
        


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options] rootFilePath')
    parser.add_option('-o', '--output-file', dest = 'o',
                      default = 'out.root', type = str,
                      help = 'path to the output file.')
    parser.add_option('-i', '--interactive', dest = 'i',
                      default = False, action = 'store_true',
                      help = 'run in interactive mode.')
    (opts, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('Exactly one argument required.')
    inputPath = args[0]

    MIN_START_TIME = utc2met(convert2sec('Nov/01/2008 00:00:00'))
    MAX_START_TIME = utc2met(convert2sec('Dec/01/2008 00:00:00'))
    finder = pBumpFinder(inputPath, opts.o, MIN_START_TIME, MAX_START_TIME)
    finder.run(opts.i)
