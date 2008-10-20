#!/usr/bin/env python

import ROOT
import os
import sys

sys.path.append('../../Common/python')

ROOT.gStyle.SetOptStat(111111)

from pOptionParser import pOptionParser
optparser = pOptionParser('', 1, 1, False)
filePath = optparser.Argument

if not os.path.exists(filePath):
    sys.exit('Could not find %s. Abort.' % filePath)

rootFile = ROOT.TFile(filePath)
rootTree = rootFile.Get('Output')

rootTree.Draw('PMTA_average_mean:RunId')
