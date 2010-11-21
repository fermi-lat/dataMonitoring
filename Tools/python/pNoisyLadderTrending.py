
from pLongTermTrendMaker import *


TOWER = 3
PLANE = 'Y17'
HITMAP_PATH = 'TkrNoiseOcc/Hitmap/Tower%d/hTkrHitMapT%d%s' % (TOWER, TOWER, PLANE)


class pTKRANALYSISAnalyzer(pBaseFileAnalyzer):

    def __init__(self, fileListPath, outputFilePath, minStartTime,
                 maxStartTime = None):
        self.LabelList = ['NumEvents']
        self.QuantityList = ['']
        pBaseFileAnalyzer.__init__(self, fileListPath, outputFilePath,
                                   'TKRANALYSIS', minStartTime,
                                   maxStartTime)

    def analyze(self):
        runId = self.Arrays['RunId'][0]
        numEvents = self.InputFile.Get('TkrHits/numCalXtal').GetEntries()
        self.Arrays['NumEvents'][0] = numEvents
        hitmap = self.InputFile.Get(HITMAP_PATH)
        hitmap.SetName('%s_%s' % (runId, hitmap.GetName()))
        self.OutputFile.cd()
        hitmap.Write()



if __name__ == '__main__':
    MIN_START_TIME = utc2met(convert2sec('Sep/01/2008 00:00:00'))
    MAX_START_TIME = None
    analyzer = pTKRANALYSISAnalyzer('TKRANALYSISANALYZER.txt',
                                    'TKRANALYSISANALYZER.root',
                                    MIN_START_TIME,
                                    MAX_START_TIME)
    analyzer.run()
    
