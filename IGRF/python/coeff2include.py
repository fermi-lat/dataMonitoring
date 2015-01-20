#!/usr/bin/env python

import argparse
import sys

skipLines = 4
format = '     n                %(nn)s , %(mm)s , %(gCof)s , %(hCof)s , \n'

arghParser = argparse.ArgumentParser(description='Format a column from the IGRF coeffiecients file for inclusion in dgrfdata.inc')
arghParser.add_argument('inFileName')
arghParser.add_argument('colNum')
arghs = arghParser.parse_args()

ifp = open(arghs.inFileName)
colNum = int(arghs.colNum)

for ii in range(skipLines):
    ifp.readline()
    continue

for line in ifp:
    fields = line.split()
    sign = fields[0]
    nn = float(fields[1])
    mm = float(fields[2])

    if 'g' == sign:
        gCof = fields[colNum]
        if 0.0 == mm:
            hCof = 0.0
            sys.stdout.write(format % locals())
            pass
        pass
    elif 'h' == sign:
        hCof = fields[colNum]
        sys.stdout.write(format % locals())
        pass
    else:
        raise ValueError
    
    continue
