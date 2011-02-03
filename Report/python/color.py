#!/bin/env python
from optparse import OptionParser

import re

def getLaTeXColor(color):
        color = color.strip('#')
        cList = list(color) 
        r = (16*int(cList[0],16)+int(cList[1],16))/255.
        g = (16*int(cList[2],16)+int(cList[3],16))/255.
        b = (16*int(cList[4],16)+int(cList[5],16))/255.
        laTeX = '{%s,%s,%s}' % (r,g,b)
        return laTeX

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-c', '--color', dest = 'c',
                      default = '#000000', type = str)
    (opts, args) = parser.parse_args()
    laTeX = getLaTeXColor(opts.c)
    print "color=%s" % (laTeX)
