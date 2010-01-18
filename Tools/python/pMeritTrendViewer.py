#! /bin/env python

from pMeritTrendProcessor import *


VIEW_VAR_LIST = ['OutF_NormRateEvtsBeforeFilters',
                 'OutF_NormRateEvtsBeforeCuts',
                 'OutF_NormRateEvtsBeforeCutsWithGAMMAFilter',
                 'OutF_NormRateEvtsBeforeCutsWithFswGAMMAFilter',
                 'OutF_NormRateTransientEvts',
                 'OutF_NormRateSourceEvts',
                 'OutF_NormRateDiffuseEvts'
                 ]

from optparse import OptionParser
parser = OptionParser(usage = 'usage: %prog [options] rootFilePath')
(opts, args) = parser.parse_args()
if len(args) != 1:
    parser.print_help()
    parser.error('Exactly one argument required.')
rootFilePath = args[0]

rootFile = ROOT.TFile(rootFilePath)
rootTree = rootFile.Get('Time')


def drawVariable(varName):
    rootTree.Draw('%s' % varName)
    ROOT.gPad.Update()
    raw_input('Press enter to continue...')


for varName in VIEW_VAR_LIST:
    drawVariable(varName)
    
