
import urllib
import sys
import logging
logging.basicConfig(level = logging.DEBUG)

from pDataPoint import pDataPoint

DB_BASE_URL = 'http://glast-ground.slac.stanford.edu/DataQualityMonitoring/'



class pUrlReader:
    
    def open(self, url):
        return urllib.urlopen(url)
        
    def getAllData(self, url):
        logging.debug('Opening url %s' % url)
        urlObject = self.open(url)
        logging.debug('Getting data...')
        data = urlObject.readlines(url)
        urlObject.close()
        logging.debug('Done.')
        return data



class pTrendingDataBaseBugger(pUrlReader):

    def __init__(self, runId):
        self.RunId = runId

    def getVariableString(self, variable):
        return 'selectedData=%s' % variable

    def getSelectionString(self, selection):
        return selection

    def getRunIdString(self):
        return 'runId=%d' % self.RunId

    def getAllPointsOptionString(self):
        return 'forceSmallest=true&maxBins=-1'

    def getDataUrl(self, variable, selection, allPoints = True):
        dataUrl = '%sgetData?%s&%s&%s' %\
            (DB_BASE_URL,\
                 self.getVariableString(variable),\
                 self.getSelectionString(selection),\
                 self.getRunIdString())
        if allPoints:
            dataUrl += '&%s' % self.getAllPointsOptionString()
        return dataUrl
        
    def getData(self, variable, selection, allPoints = True):
        dataUrl = self.getDataUrl(variable, selection, allPoints)
        return self.getAllData(dataUrl)

    def getDataPoints(self, variable, selection, allPoints = True):
        data = self.getData(variable, selection, allPoints)
        dataPoints = []
        for (lineNumber, line) in enumerate(data):
            if '<trendingdata>' in line:
                time = data[lineNumber + 3].split()[3]
                time = time.replace('value="', '').replace('"', '')
                time = float(time)
                value = data[lineNumber + 1].split()[3]
                value = value.replace('value="', '').replace('"/>', '')
                value = float(value)
                error = data[lineNumber + 2].split()[3]
                error = error.replace('value="', '').replace('"/>', '')
                error = float(error)
                dataPoints.append(pDataPoint(time, value, error))
        if dataPoints == []:
            logging.error('No data points from the trending database.')
            sys.exit('Abort.')
        dataPoints.sort()
        return dataPoints



if __name__ == '__main__':
    bugger = pTrendingDataBaseBugger(258292096)
    print bugger.getDataPoints('Digi_Trend_Mean_AcdPha_PmtB_AcdTile',\
                                   'acdtile=23')
