## @package pAlarmBaseAlgorithm
## @brief Base package for implementation of algorithms.

import pSafeLogger
logger = pSafeLogger.getLogger('pAlarmBaseAlgorithm')

import pUtils
import types
from pAlarmOutput import pAlarmOutput
from copy         import copy, deepcopy


## @brief Base class for alarm algorithms. Look at the inheritance diagram for
#  the list of implemented algorithms.
#
#  Provides a general structure for the implementation of the algorithms,
#  along with some ROOT-related useful functions (like setting histogram
#  range etc...).

class pAlarmBaseAlgorithm:

    ## @var SUPPORTED_TYPES
    ## @brief The list of ROOT object types which are supported by a given
    #  algorithm.

    ## @var SUPPORTED_PARAMETERS
    ## @brief The list of (optional) parameters supported by a given
    #  algorithm.

    ## @var OUTPUT_DICTIONARY
    ## @brief The initial value of the output dictionary for the alarms.

    SUPPORTED_TYPES      = []
    SUPPORTED_PARAMETERS = []
    OUTPUT_DICTIONARY    = {}
    OUTPUT_LABEL         = 'N/A'

    ## @brief Basic constructor
    ## @param self
    #  The class instance.
    ## @param limits
    #  The alarm limits.
    ## @param object
    #  The ROOT object the alarm is set on.
    ## @param paramsDict
    #  The dictionary of optional algorithm parameters.

    def __init__(self, limits, object, paramsDict):

        ## @var Limits
        ## @brief The alarm limits.

        ## @var RootObject
        ## @brief The ROOT object the alarm is set on.
        
        ## @var ParamsDict
        ## @brief The dictionary of optional algorithm parameters.

        ## @var __RootObjectOK
        ## @brief Flag.

        ## @var __ParametersOK
        ## @brief Flag.
        
        ## @var Output
        ## @brief The alarm output (initialized to an undefined pAlarmOutput
        #  object in the constructor).
     
        self.Limits = limits
        self.RootObject = object
        self.ParamsDict = paramsDict
        self.__RootObjectOK = True
        self.__ParametersOK = True
        self.checkObjectType()
        self.checkParameters()
        self.Output = pAlarmOutput(limits)
        self.Output.Label = copy(self.OUTPUT_LABEL)
        self.Output.DetailedDict = deepcopy(self.OUTPUT_DICTIONARY)

    ## @brief Return True if the algorithm is valid (i.e. both the ROOT
    #  object type and the parameters type are supported).
    ## @param self
    #  The class instance.

    def isValid(self):
        return self.__RootObjectOK and self.__ParametersOK

    ## @brief Return the algorithm name.
    ## @param self
    #  The class instance.

    def getName(self):
        return self.__class__.__name__.strip('alg__')

    ## @brief Return the ROOT object type (the name of the class the
    #  object belongs to).
    ## @param self
    #  The class instance.

    def getObjectType(self):
        return self.RootObject.Class().GetName()

    ## @brief Make sure the algorithm supports the ROOT object it has
    #  to operate on.
    ## @param self
    #  The class instance.

    def checkObjectType(self):
        if self.getObjectType() not in self.SUPPORTED_TYPES:
            self.__RootObjectOK = False
            logger.error('Invalid object type (%s) for %s. '    %\
                          (self.getObjectType(), self.getName()) +\
                          'The alarm will be ignored.')

    ## @brief Make sure all the optional parameters are supported.
    ## @param self
    #  The class instance.

    def checkParameters(self):
        for paramName in self.ParamsDict.keys():
            if paramName not in self.SUPPORTED_PARAMETERS:
                self.__ParametersOK = False
                logger.error('Invalid parameter (%s) for %s.' %\
                              (paramName, self.getName())      +\
                              'The alarm will be ignored.')

    ## @brief Apply the algorithm on the ROOT object.
    ## @param self
    #  The class instance.

    def apply(self):
        if not self.__RootObjectOK:
            logger.warn('Invalid object, %s will not be applied.' %\
                         self.getName())
        elif not self.__ParametersOK:
            logger.warn('Invalid parameter(s), %s will not be applied.' %\
                         self.getName())
        else:
            try:
                exec('self.run%s()' % self.getObjectType())
            except AttributeError:
                self.run()

    ## @brief Actual algorithm implementation ("virtual" function to be
    #  overridden by the derived classes).
    ## @param self
    #  The class instance.

    def run(self):
        logger.warn('Method run() not implemented for %s.' % self.getName())

    ## @brief Adjust the range of the x axis of a ROOT object according
    #  to the dictionary of optional parameters.
    ## @param self
    #  The class instance.

    def adjustXRange(self):
        if self.getObjectType() not in ['TH1F']:
            logger.warn('Cannot use setRangeX() on a %s object.' %\
                         self.getObjectType())
            return None
        try:
            min = self.ParamsDict['min']
        except KeyError:
            min = self.RootObject.GetXaxis().GetXmin()
        try:
            max = self.ParamsDict['max']
        except KeyError:
            max = self.RootObject.GetXaxis().GetXmax()
        self.RootObject.GetXaxis().SetRangeUser(min, max)

    ## @brief Restore the original x axis range for a ROOT object.
    ## @param self
    #  The class instance.

    def resetXRange(self):
        if self.getObjectType() not in ['TH1F']:
            logger.warn('Cannot use setRangeX() on a %s object.' %\
                         self.getObjectType())
            return None
        self.RootObject.GetXaxis().SetRange(1, 0)

    def getFitParameter(self, fitFunction, paramNumber):
        self.adjustXRange()
        self.RootObject.Fit(fitFunction, 'QN')
        self.resetXRange()
        return fitFunction.GetParameter(paramNumber)

    ## @brief Return the average value of a list of number.
    ## @param self
    #  The class instance.
    ## @param list
    #  The list to be averaged.
    ## @param default
    #  The default value to be returned in case something goes wrong during the
    #  average evaluation.

    def getAverage(self, list, default = 0):
        try:
            return sum(list)/float(len(list))
        except:
            logger.error('Could not evaluate the average of %s.' % list)
            logger.info('Returning %s.' % default)
            return default

    ## @brief Return a list of bins close to a given bin.
    ## @param self
    #  The class instance.
    ## @param bin
    #  The bin we're interested into.
    #
    #  If the bin is a simple integer, then is it interpreted as the bin
    #  ID of a 1-dimensional histogram; a list of integers is returned in this
    #  case. If it's a list or a tuple of length 2 it is interpreted as the
    #  (i, j) bin ID of a 2-dimensional histogram and a list of tuples of
    #  length 2 is returned.
    ## @param numNeighbours
    #  The number of bins on the left and right---as well as top and bottom,
    #  for the 2-dimensional histograms---which are considered neighbours.

    def getNeighbourBinsList(self, bin, numNeighbours):
        binsList = []
        if type(bin) == types.IntType:
            numBins = self.RootObject.GetNbinsX()
            minBin = max(1, bin - numNeighbours)
            maxBin = min(numBins, bin + numNeighbours)
            for i in range(minBin, maxBin + 1):
                if i != bin:
                    binsList.append(i)
        elif len(bin) == 2:
            (binX, binY) = bin
            numBinsX = self.RootObject.GetNbinsX()
            numBinsY = self.RootObject.GetNbinsY()
            minBinX  = max(1, binX - numNeighbours)
            maxBinX  = min(numBinsX, binX + numNeighbours)
            minBinY  = max(1, binY - numNeighbours)
            maxBinY  = min(numBinsY, binY + numNeighbours)
            for i in range(minBinX, maxBinX + 1):
                for j in range(minBinY, maxBinY + 1):
                    if (i, j) != (binX, binY):
                        binsList.append((i, j))
        else:
            logger.error('Invalid bin identifier in getNeighbourBinsList().')
            logger.info('Returning an empty list.')
        return binsList

    ## @brief Return the average content of the histogram bins located close
    #  to a given bin.
    ## @param self
    #  The class instance.
    ## @param bin
    #  The bin we're interested into.
    #
    #  If the bin is a simple integer, then is it interpreted as the bin
    #  ID of a 1-dimensional histogram. If it's a list or a tuple of length 2
    #  it is interpreted as the (i, j) bin ID of a 2-dimensional histogram.
    ## @param numNeighbours
    #  The number of bins on the left and right---as well as top and bottom,
    #  for the 2-dimensional histograms---which are considered neighbours.
    ## @param lowCut
    #  The <em>fraction</em> of bins with the lowest content to be excluded in
    #  the average evaluation.
    ## @param highCut
    #  The <em>fraction</em> of bins with the highest content to be excluded in
    #  the average evaluation.

    def getNeighbourAverage(self, bin, numNeighbours, lowCut, highCut):
        binsContent = []
        binsList = self.getNeighbourBinsList(bin, numNeighbours)
        firstBin = binsList[0]
        if type(firstBin) == types.IntType:
            for i in binsList:
                binsContent.append(self.RootObject.GetBinContent(i))
        elif len(firstBin) == 2:
            for (i, j) in binsList:
                binsContent.append(self.RootObject.GetBinContent(i, j))
        binsContent.sort()
        numBins = len(binsContent)
        numCutBinsLow = int(numBins*lowCut)
        numCutBinsHigh = int(numBins*highCut)
        binsContent =  binsContent[numCutBinsLow:-(numCutBinsHigh + 1)]
        return self.getAverage(binsContent)


if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    from pSafeROOT    import ROOT
    limits = pAlarmLimits(-1, 3, -1, 6)

    print
    print 'Testing on a 1-dimensional histogram...'
    histogram1d = ROOT.TH1F('h1d', 'h1d', 10, -5, 5)
    algorithm1d = pAlarmBaseAlgorithm(limits, histogram1d, {})
    print algorithm1d.getNeighbourBinsList(3, 1)
    print algorithm1d.getNeighbourBinsList(3, 2)
    print algorithm1d.getNeighbourBinsList(3, 3)
    print algorithm1d.getNeighbourBinsList(3, 10)
    
    print
    print 'Testing on a 2-dimensional histogram...'
    histogram2d = ROOT.TH2F('h2d', 'h2d', 10, -5, 5, 10, -5, 5)
    algorithm2d = pAlarmBaseAlgorithm(limits, histogram2d, {})
    print algorithm2d.getNeighbourBinsList((3, 3), 1)
    print algorithm2d.getNeighbourBinsList((3, 3), 2)
