
import sys
import ROOT


CAL_ROOT_FILE_PATH = '/data/work/leo/saa/f1001_2360728414034220.root'
CAL_ROOT_TREE_NAME = 'CalLrsTree'
TKR_ROOT_FILE_PATH = '/data/work/leo/saa/f1002_2361209078065470.root'
TKR_ROOT_TREE_NAME = 'TkrLrsTree'

rootFile = ROOT.TFile(TKR_ROOT_FILE_PATH)
rootTree = rootFile.Get(TKR_ROOT_TREE_NAME)
rootCanvas = ROOT.TCanvas()
rootCanvas.Divide(4, 4)


#import time
#t1 = time.time()
#t2 = t1 + 100000
#print time.strftime('%d-%b-%Y %H:%M:%S', time.gmtime(t1))
#print time.strftime('%d-%b-%Y %H:%M:%S', time.gmtime(t2))
#h = ROOT.TH2F('h', 'h', 100, t1, t2, 100, 0, 1)
#h.GetXaxis().SetTimeDisplay(1)
#h.GetXaxis().SetTimeFormat('%y %b %d %H:%M:%S%F1970-01-01 00:00:00')
#h.GetXaxis().SetNdivisions(5)
#h.GetXaxis().SetLabelSize(0.02)
#h.Draw()

for tower in range(16):
    plotName = 'tower%d' % tower
    rootCanvas.cd(tower + 1)
    rootTree.Draw('LrsRate[%d][0]:Time>>%s' % (tower, plotName))
    plot = ROOT.gDirectory.Get(plotName)
    plot.GetXaxis().SetTimeDisplay(1)
    plot.GetXaxis().SetTimeFormat('%y %b %d %H:%M:%S%F1970-01-01 00:00:00')
    plot.GetXaxis().SetNdivisions(5)
    plot.GetXaxis().SetLabelSize(0.02)
    plot.Draw()
    rootCanvas.Update()
