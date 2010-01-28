import ROOT
import time
import calendar
import array

from pGOESDownloader import *
from pTimeUtils      import *


# UTC Date  Time   Julian  of the
# YR MO DA  HHMM    Day     Day       Short       Long
#-------------------------------------------------------


outputFilePath = os.path.join(TARGET_DIR, 'goes.root')
outputFile = ROOT.TFile(outputFilePath, 'RECREATE')
outputTree = ROOT.TTree('Time', 'Time')
ts = array.array('d', [0.0])
fs = array.array('d', [0.0])
fl = array.array('d', [0.0])
outputTree.Branch('Timestamp', ts, 'Timestamp/D')
outputTree.Branch('FluxShort', fs, 'FluxShort/D')
outputTree.Branch('FluxLong' , fl, 'FluxLong/D' )

fileList = os.listdir(TARGET_DIR)
fileList.sort()
for filePath in fileList:
    if filePath.endswith('m.txt'):
        filePath = os.path.join(TARGET_DIR, filePath)
        print 'Reading file %s...' % filePath
        for line in file(filePath):
            if not line.startswith(':') and not line.startswith('#'):
                line = line.strip('\n')
                year, month, day, hm, jd, sec, fluxs, fluxl = line.split()
                hour  = hm[:2]
                min   = hm[2:]
                fmtst = '%d %m %Y %H:%M'
                date  = '%s %s %s %s:%s' % (day, month, year, hour, min)
                ts[0] = utc2met(calendar.timegm(time.strptime(date, fmtst)))
                fs[0] = float(fluxs)
                fl[0] = float(fluxl)
                outputTree.Fill()
print 'Writing output file...'
outputFile.Write()
outputFile.Close()
print 'Done.'

