import random
import numpy
import logging

from ROOT                        import TFile, TTree, TH1F
from pRootTreeProcessor          import pRootTreeProcessor


class pRootTreeMaker:

    def __init__(self, xmlParser, outputFilePath):
        self.__RootFile  = TFile(outputFilePath, 'recreate')
        self.__RootTree  = TTree('IsocDataTree', 'IsocDataTree')
        self.__XmlParser = xmlParser
        self.__Processor = pRootTreeProcessor(self.__RootTree,\
                                              self.__XmlParser)
        self.DefaultVariablesDictionary = None
        self.VariablesDictionary = None        
        self.__createTree()
        logging.info('Created File %s with Tree %s\n' % (outputFilePath, self.__RootTree.GetName()) )

    def __createTree(self):
        self.VariablesDictionary = {}
        self.__createDefaultBranches()
        for variable in self.__XmlParser.EnabledVariablesDict.values():
            self.VariablesDictionary[variable.getName()] = variable.Array
            self.__createTreeBranch(variable)

    def __createTreeBranch(self, variable):
        self.__RootTree.Branch(variable.getName(),\
                               self.VariablesDictionary[variable.getName()],\
                               variable.LeafList)

    def __createDefaultBranches(self):
        self.DefaultVariablesDictionary = {}
        variable_name = 'event_timestamp'
        variable = numpy.zeros(1, 'double')
        self.DefaultVariablesDictionary[variable_name] = variable
        self.__RootTree.Branch(variable_name, variable,\
                               '%s[1]/D' % variable_name)
        
    def fillTree(self):
        self.__RootTree.Fill()

    ## @brief Reset variable Array
    ## @param self
    #  The class instance.

    def resetVariables(self):

        for variable in self.__XmlParser.EnabledVariablesDict.values():
            variable.reset()
	    
	    

    def close(self):
        self.__Processor.process()
        self.__RootFile.Write()
        self.__RootFile.Close()

