
# Abstract:
# pyroot macro producing the plots for the memo on rate normalization.
# Author:
# Luca Baldini (luca.baldini@pi.infn.it)

import os
import sys

#
# This is hard-coded for my laptop :-) 
#
BASE_FOLDER = '/data/work/datamon/dataMonitoring/Tools/python'
COMMON_FOLDER = '/data/work/datamon/dataMonitoring/Common/python'
NORM_FOLDER = os.path.join(BASE_FOLDER, 'normrates_v2')
RUN_FOLDER  = '/data/work/datamon/runs/normrates'

sys.path.append(BASE_FOLDER)
sys.path.append(COMMON_FOLDER)
from pMeritTrendTester import *

originalFilePath = os.path.join(NORM_FOLDER, 'merit_norm.root')
procFilePath     = os.path.join(NORM_FOLDER, 'merit_norm_proc.root')
postprocFilePath = os.path.join(NORM_FOLDER, 'merit_norm_postproc.root')
runFilePath      = os.path.join(RUN_FOLDER , 'r0303054436_merittrend.root')

tester = pMeritTrendTester(runFilePath, postprocFilePath)
tester.draw('EvtsBeforeCuts')
tester.OrigGraph.GetYaxis().SetRangeUser(0.7, 1.3)
tester.OrigCanvas.Update()
tester.OrigCanvas.SaveAs('figures/EvtsBeforeCuts_old.pdf')
tester.NewGraph.GetYaxis().SetRangeUser(0.7, 1.3)
tester.NewGraph.Draw('ap')
tester.NewCanvas.Update()
tester.NewCanvas.SaveAs('figures/EvtsBeforeCuts_new.pdf')

tester.draw('DiffuseEvts')
tester.OrigGraph.GetYaxis().SetRangeUser(0, 6)
tester.OrigCanvas.Update()
tester.OrigCanvas.SaveAs('figures/DiffuseEvts_old.pdf')
tester.NewGraph.GetYaxis().SetRangeUser(0, 6)
tester.NewGraph.Draw('ap')
tester.NewCanvas.Update()
tester.NewCanvas.SaveAs('figures/DiffuseEvts_new.pdf')

h = tester.NormRootFile.Get('hRate_EvtsBeforeCuts')
h.SetXTitle('McIlwain L')
h.SetYTitle('Rate for EvtsBeforeCuts (Hz)')
h.Draw()
ROOT.gPad.Update()
ROOT.gPad.SaveAs('figures/EvtsBeforeCuts_mcIlwainL.pdf')

h = tester.NormRootFile.Get('hRate_DiffuseEvts')
h.SetXTitle('McIlwain L')
h.SetYTitle('Rate for DiffuseEvts (Hz)')
h.Draw()
ROOT.gPad.Update()
ROOT.gPad.SaveAs('figures/DiffuseEvts_mcIlwainL.pdf')

pproc = pMeritTrendPostProcessor(procFilePath)
pproc.GraphCanvas = ROOT.TCanvas('Graph canvas')
pproc.GraphCanvas.SetGridx(True)
pproc.drawGraph('Rate_DiffuseEvts')
pproc.drawGraph('Rate_EvtsBeforeCuts')
