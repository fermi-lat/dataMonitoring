#!/usr/bin/env python

import ROOT
import os
import sys


from pOptionParser import pOptionParser
optparser = pOptionParser('', 1, 1, False)
filePath = optparser.Argument

if not os.path.exists(filePath):
    sys.exit('Could not find %s. Abort.' % filePath)
    
rootFile = ROOT.TFile(filePath)
for key in rootFile.GetListOfKeys():
    objectName = key.GetName()
    rootObject = rootFile.Get(objectName)
    try:
        print 'Trying to draw %s...' % objectName
        rootObject.Draw()
        ROOT.gPad.Update()
    except:
        print 'Failed.'
    answer = raw_input('Press q to quit, anything else to continue...')
    if answer == 'q':
        sys.exit('Done.')

