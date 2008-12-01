#!/usr/bin/env python

import os
import sys
import ROOT

ROOT.gStyle.SetCanvasColor(10)
ROOT.gStyle.SetPalette(1)


class pBumpPlotter:

    def __init__(self, inputFilePath):
        self.RootFile = ROOT.TFile(inputFilePath)
        print 'Populating run list...'
        self.RunList = []
        for object in self.RootFile.GetListOfKeys():
            runId = object.GetName().split('_')[0]
            if runId not in self.RunList:
                self.RunList.append(runId)
        print 'Done. %s run(s) found.' % len(self.RunList)
        self.Canvas = ROOT.TCanvas('bumpHunting', 'bumpHunting', 1000, 600)
        self.Canvas.Divide(3, 2)

    def plot(self, outputFilePath, interactive = False):
        for run in self.RunList:
            self.Canvas.cd(1)
            self.RootFile.Get('%s_rate' % run).Draw()
            self.Canvas.cd(2)
            self.RootFile.Get('%s_mcIlwainL' % run).Draw()
            self.Canvas.cd(3)
            self.RootFile.Get('%s_normalized_rate' % run).Draw()
            self.Canvas.Update()
            self.Canvas.cd(4)
            self.RootFile.Get('%s_map_before' % run).Draw('colz')
            self.Canvas.cd(5)
            self.RootFile.Get('%s_map_bump' % run).Draw('colz')
            self.Canvas.cd(6)
            self.RootFile.Get('%s_map_after' % run).Draw('colz')
            self.Canvas.Update()
            self.Canvas.SaveAs(outputFilePath.replace('.png', '_%s.png' % run))
            if interactive:
                raw_input()

    


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options] rootFilePath')
    parser.add_option('-o', '--output-file', dest = 'o',
                      default = None, type = str,
                      help = 'path to the output file.')
    (opts, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('Exactly one argument required.')
    inputPath = args[0]
    plotter = pBumpPlotter(inputPath)
    plotter.plot('test.png', True)
