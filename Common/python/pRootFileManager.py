## @package pRootFileManager
## @brief Module providing utilities for managing ROOT files.

import pSafeLogger
logger = pSafeLogger.getLogger('pRootFileManager')

import sys
import os
import time

from pSafeROOT import ROOT



TREE_BRANCH_SEPARATOR = '::'

## @brief Class for ROOT file handling.

class pRootFileManager:

    ## @brief Basic constructor.
    ## @param self
    #  The class instance.
    ## @param rootFilePath
    #  The path to the input ROOT file.

    def __init__(self, rootFilePath = None):

        ## @var RootFile
        ## @brief The underlying ROOT file.
        
        self.RootFile = None
        if rootFilePath is not None:
            self.openFile(rootFilePath)

    ## @brief Open a ROOT file.
    ## @param self
    #  The class instance.
    ## @param rootFilePath
    #  The path to the input ROOT file.

    def openFile(self, rootFilePath):
        logger.info('Opening file %s...' % rootFilePath)
        if not os.path.exists(rootFilePath):
            sys.exit('File %s does not exist.' % rootFilePath)
        self.RootFile = ROOT.TFile(rootFilePath)
        if self.RootFile.GetFd() == -1:
            sys.exit('Could not open file %s.' % rootFilePath)
        logger.info('Done. %s objects found.\n' %\
                    (self.RootFile.GetListOfKeys().LastIndex() + 1))

    ## @brief Close the ROOT file.
    ## @param self
    #  The class instance.

    def closeFile(self):
        logger.info('Closing ROOT file...')
        if self.RootFile is not None:
            self.RootFile.Close()
            self.RootFile = None
        logger.info('Done.')

    ## @brief Get a ROOT object from the ROOT File (by object name).
    ## @param self
    #  The class instance.
    ## @param name
    #  The object name.

    def get(self, name):
        try:
            return self.RootFile.Get(name)
        except:
            logger.error('Could not find %s in ROOT file %s.' %\
                         (name, self.RootFile.GetName()))
            return None

    def getPlotsDict(self):
        plotsDict = {}
        keys = self.RootFile.GetListOfKeys()
        for key in keys:
            plotName = key.GetName()
            plotsDict[plotName] = self.get(plotName)
        return plotsDict

    ## @brief Function implementing the pattern match.
    #
    #  Return True if the name (after the * has been stripped off) differs
    #  from the pattern by numbers only (i.e. wildcards stand for numbers
    #  only).

    def __match(self, name, pattern, selection):
        patternPieces = pattern.split('*')
        for piece in patternPieces:
            name = name.replace(piece, '')
        if not name.isdigit():
            return False
        else:
            if selection is None:
                return True
            name = int(name)
            (mode, list) = selection
            if mode == 'exclude':
                return name not in list
            elif mode == 'only':
                return name in list
            else:
                logger.error('Wrong selection mode (%s) to match objects.' %\
                             mode)
                return False

    ## @brief Find ROOT objects whose name matches a certain pattern in a
    #  ROOT file.
    #
    #  If the pattern contains a slash branch separator it is assumed that the
    #  method is intended to return a TBranch of a TTree in the form
    #  "branch/separator/tree". Otherwise the objects are searched directly.
    ## @param self
    #  The class instance
    ## @param pattern
    #  The name pattern.

    def find(self, pattern, selection = None):
        if TREE_BRANCH_SEPARATOR in pattern:
            return self.findTreeBranches(pattern)
        else:
            if '*' not in pattern:
                obj = self.RootFile.FindObjectAny(pattern)
                if obj is not None:
                    return [obj]
                else:
                    return []
            else:
                return self.findObjects(pattern, selection)

    ## @brief Find ROOT objects whose name matches a certain pattern in a
    #  ROOT file.
    ## @param self
    #  The class instance
    ## @param pattern
    #  The name pattern.

    def findObjects(self, pattern, selection):
        objects = []
        for i in range(self.RootFile.GetListOfKeys().LastIndex() + 1):
	    key = self.RootFile.GetListOfKeys().At(i).GetName()
            if key == pattern or self.__match(key, pattern, selection):
                objects.append(self.RootFile.FindObjectAny(key))
        return objects

    ## @brief Find ROOT branches whose name matches a certain pattern in a
    #  ROOT file.
    ## @param self
    #  The class instance
    ## @param pattern
    #  The name pattern.

    def findTreeBranches(self, pattern):
        try:
            (treeName, branchName) = pattern.split(TREE_BRANCH_SEPARATOR)
        except ValueError:
            logger.error('"%s" does not seem like a tree-branch pattern.' %\
                         pattern)
            return []
        tree = self.RootFile.FindObjectAny(treeName)
        if tree is None:
            logger.error('Could not find "%s" TTree in the ROOT file' %\
                             treeName)
            return []
        branch = tree.GetBranch(branchName)
        try:
            zombie = branch.IsZombie()
        except ReferenceError:
            logger.error('"%s" TTree does not have a TBranch named "%s".' %
                         (treeName, branchName))
            return []
        if branch is None or zombie:
            logger.error('"%s" TTree does not have a TBranch named "%s".' %
                         (treeName, branchName))
            return []
        return [branch]


if __name__ == '__main__':
    manager = pRootFileManager()
