import os
import sys
import math

sys.path.append('../../Common/python')
sys.path.append('../../Report/python')

from pTimeUtils import *
from pSafeROOT  import ROOT
from pGOESDownloader import *
from pLongTermTrendPlotter import *

ROOT.gStyle.SetOptStat(111111)
ROOT.gStyle.SetMarkerStyle(1)
	
rootFile = ROOT.TFile(os.path.join(TARGET_DIR, 'goes.root'))
rootTree = rootFile.Get('Time')

canvas = ROOT.TCanvas()
canvas.SetLogy(True)
canvas.SetGridy(True)
gGOES = ROOT.TGraph()
for i in xrange(rootTree.GetEntries()):
    rootTree.GetEntry(i)
    f = rootTree.FluxLong
    if f > 0:
        t = rootTree.Timestamp
        gGOES.SetPoint(gGOES.GetN(), t, f)
gGOES.GetXaxis().SetTitle('Time UTC')
gGOES.GetXaxis().SetNdivisions(506)
gGOES.GetXaxis().SetLabelSize(LABEL_SIZE)
gGOES.GetXaxis().SetTimeDisplay(True)
gGOES.GetXaxis().SetTimeFormat(TIME_FORMAT)
gGOES.GetYaxis().SetTitle('GOES-14 x-ray Flux 1.0-8.0 A (Wm^{-2})')
gGOES.GetYaxis().SetLabelSize(LABEL_SIZE)
gGOES.GetYaxis().SetRangeUser(1e-9, 1e-4)
gGOES.Draw('ALP')
canvas.Update()
