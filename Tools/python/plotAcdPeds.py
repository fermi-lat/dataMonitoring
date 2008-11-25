import ROOT

from __tile_map__ import *

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options] rootFilePath')
    (opts, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('Exactly one argument required.')
    filePath = args[0]

    averageDict = {}
    countsDict = {}
    for garc in range(12):
        averageDict[garc] = 0
        countsDict[garc] = 0
        
    rootFile = ROOT.TFile(filePath)
    hA = rootFile.Get('AcdPedPedMeanDeviation_PMTA_TH1')
    hB = rootFile.Get('AcdPedPedMeanDeviation_PMTB_TH1')
    averageA = 0
    averageB = 0
    counts = 0
    for tile in range(128):
        if tile in TILE_DICT_A.keys():
            garcA = TILE_DICT_A[tile]
            garcB = TILE_DICT_B[tile]
            print tile, garcA, garcB
            averageDict[garcA] += hA.GetBinContent(tile + 1)
            countsDict[garcA] += 1.0
            averageDict[garcB] += hB.GetBinContent(tile + 1)
            countsDict[garcB] += 1.0
            averageA += hA.GetBinContent(tile + 1)
            averageB += hB.GetBinContent(tile + 1)
            counts += 1.0
    averageA /= counts
    averageB /= counts
    print averageA, averageB
    for garc in range(12):
        try:
            averageDict[garc] /= countsDict[garc]
        except:
            pass
        print 'Average deviation for GARC %d: %f' % (garc, averageDict[garc])
    print sum(averageDict.values())/12.
