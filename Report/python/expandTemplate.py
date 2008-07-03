#!/afs/slac/g/glast/isoc/flightOps/rhel3_gcc32/ISOC_PROD/bin/shisoc python2.5

def expand(inFile, outFile, dic):
    inData = open(inFile).read()
    outData = inData % dic
    open(outFile, 'w').write(outData)
    return
