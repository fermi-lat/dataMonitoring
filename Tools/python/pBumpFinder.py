from pLongTermTrendMaker import *


ROOT.gStyle.SetCanvasColor(10)
ROOT.gStyle.SetPalette(1)


class pBumpFinder:
    
    def __init__(self, fileListPath, outputFilePath):
        self.HistogramDict = {}
        self.FitFunction = ROOT.TF1('fitFunction', 'pol3')
        self.HighThreshold = 1.125
        self.LowThreshold = 1.10

    def addHistogram(self, histogram):
        self.HistogramDict[histogram.GetName()] = histogram

    def analyzeRun(self, filePath, debug = False, timeBinWidth = 25):
        print 'Analyzing %s...' % filePath

        # Retrieve run information.
        fileName = os.path.basename(filePath)       
        runId = int(fileName.split('_')[0].strip('r'))
        rootFile = ROOT.TFile(filePath)
        meritTuple = rootFile.Get('MeritTuple')
        numEntries = meritTuple.GetEntries()
        meritTuple.GetEntry(0)
        startTime = meritTuple.EvtElapsedTime
        meritTuple.GetEntry(numEntries - 1)
        stopTime = meritTuple.EvtElapsedTime
        runDuration = stopTime - startTime
        numTimeBins = int(runDuration/timeBinWidth)

        if debug:
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
        if debug:
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
        if debug:
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
        if debug:
            fitOptions = ''
        else:
            fitOptions = 'QN'
        fitGraph.Fit('fitFunction', fitOptions)
        if debug:
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
        if debug:
            rateCanvas.cd(4)
            hNormRate.Draw()
            rateCanvas.Update()

        # Search for highest peak.
        maximumBin =  hNormRate.GetMaximumBin()
        peakTime = hNormRate.GetBinCenter(maximumBin)
        peakValue = hNormRate.GetBinContent(maximumBin)
        if peakValue > self.HighThreshold:
            print 'Found significant peak (%f) at %f s since the run start.' %\
                (peakValue, peakTime)
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
            print 'Peak edges: %f--%f' % (bumpStartTime, bumpStopTime)
            print 'Creating sky map...'
            if debug:
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
            if debug:
                mapCanvas.cd(1)
                hMapBump.Draw('colz')
                mapCanvas.Update()
            hName = '%d_map_%s' % (runId, 'before')
            hMapBefore = ROOT.TH2F(hName, hName, 100, 0, 360, 100, -90, 90)
            meritTuple.Project(hName, 'FT1Dec:FT1Ra', beforeCut)
            hMapBefore.SetMaximum(zmax)
            if debug:
                mapCanvas.cd(2)
                hMapBefore.Draw('colz')
                mapCanvas.Update()
            hName = '%d_map_%s' % (runId, 'after')
            hMapAfter = ROOT.TH2F(hName, hName, 100, 0, 360, 100, -90, 90)
            hMapAfter.SetMaximum(zmax)
            meritTuple.Project(hName, 'FT1Dec:FT1Ra', afterCut)                
            if debug:
                mapCanvas.cd(3)
                hMapAfter.Draw('colz')
                mapCanvas.Update()
            hName = '%d_map_%s' % (runId, 'around')
            hMapAround = ROOT.TH2F(hName, hName, 100, 0, 360, 100, -90, 90)
            meritTuple.Project(hName, 'FT1Dec:FT1Ra', aroundCut)
            hMapAround.SetMaximum(2*zmax)
            if debug:
                mapCanvas.cd(4)
                hMapAround.Draw('colz')
                mapCanvas.Update()

        if debug:
            raw_input()
        


if __name__ == '__main__':
    finder = pBumpFinder([], '')
    finder.analyzeRun('/data/work/darkmatter/r0249358020_v001_merit.root', True)
