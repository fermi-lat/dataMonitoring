
import logging
logging.basicConfig(level = logging.DEBUG)

import ROOT
import numpy
import types


BASKET_SIZE = 100000


class lrsTreeWriter:
    
    def __init__(self, outputFilePath, outputTreeName, branchesList):
        logging.info('Opening output file %s...' % outputFilePath)
        self.OutputFile = ROOT.TFile(outputFilePath, 'RECREATE')
        if self.OutputFile.IsZombie():
            sys.exit('Could not open output file.')
        logging.info('Creating output tree %s...' % outputTreeName)
        self.OutputTree = ROOT.TTree(outputTreeName, outputTreeName)
        self.ArraysDict = {}
        for branch in branchesList:
            (branchName, branchType, branchShape) = branch.split(':')
            branchShape = eval(branchShape)
            if type(branchShape) == types.IntType:
                branchShape = (branchShape, )
            branchTitle = branchName
            for dim in branchShape:
                branchTitle += '[%d]' % dim
            branchTitle += '/%s' % branchType.upper()
            array = numpy.zeros(branchShape, branchType)
            self.ArraysDict[branchName] = array
            self.OutputTree.Branch(branchName, array, branchTitle, BASKET_SIZE)

    def getArray(self, branchName):
        return self.ArraysDict[branchName]

    def setArrayValue(self, branchName, value, position = (0,)):
        statement = 'self.getArray("%s")' % branchName
        for index in position:
            statement += '[%d]' % index
        statement += ' = %s' % value
        exec(statement)

    def fillTree(self):
        self.OutputTree.Fill()

    def closeTree(self):
        logging.info('Writing tree and closing root file...')
        self.OutputTree.Write()
        self.OutputFile.Close()        


if __name__ == '__main__':
    branchesList = ['test1:f:(1)', 'test2:f:(16,4)']
    writer = lrsTreeWriter('test.root', 'testTree', branchesList)
    for i in range(10):
        writer.getArray('test1')[0] = i
        writer.setArrayValue('test2', 34., (2, 2))
        writer.fillTree()


    
