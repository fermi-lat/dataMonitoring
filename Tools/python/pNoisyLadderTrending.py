from pLongTermTrendMaker import *
from __coupling_shorts__ import *

LAYER_LIST = BAD_DEFECT_DICT.keys()
LAYER_LIST.sort()

def getHitmapPath(layer):
    (id, sn, plane) = layer
    return 'TkrNoiseOcc/Hitmap/Tower%d/hTkrHitMapT%d%s' % (id, id, plane)

HITMAP_PATH_LIST = [getHitmapPath(layer) for layer in LAYER_LIST]


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
        hitmaps = []
        for hitmapPath in HITMAP_PATH_LIST:
            hitmap = self.InputFile.Get(hitmapPath)
            hitmap.SetName('%s_%s' % (runId, hitmap.GetName()))
            hitmaps.append(hitmap)
        self.OutputFile.cd()
        for hitmap in hitmaps:
            hitmap.Write()



if __name__ == '__main__':
    MIN_START_TIME = utc2met(convert2sec('Sep/01/2008 00:00:00'))
    MAX_START_TIME = None
    analyzer = pTKRANALYSISAnalyzer('TKRANALYSISANALYZER.txt',
                                    'TKRANALYSISANALYZER.root',
                                    MIN_START_TIME,
                                    MAX_START_TIME)
    analyzer.run()
    
