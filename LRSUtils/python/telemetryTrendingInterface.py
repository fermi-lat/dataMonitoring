import urllib
import sys
import logging
logging.basicConfig(level = logging.DEBUG)

DB_BASE_URL = 'http://glast-ground.slac.stanford.edu/TelemetryTrending/'


class urlReader:
    
    def open(self, url):
        return urllib.urlopen(url)
        
    def get(self, url):
        logging.debug('Opening url %s' % url)
        urlObject = self.open(url)
        logging.debug('Getting data...')
        data = urlObject.readlines(url)
        urlObject.close()
        logging.debug('Done.')
        return data


class telemetryTrendingInterface(urlReader):

    def __init__(self, startTime, endTime):
        self.StartTime = startTime
        self.EndTime = endTime

    def getData(self, mnemonic):
        dataUrl = '%sgetData?%s&timeInterval=%d-%d' %\
            (DB_BASE_URL, mnemonic, self.StartTime, self.EndTime)
        return self.get(dataUrl)


if __name__ == '__main__':
    interface = telemetryTrendingInterface(1214425919600, 1214510945000)
    print interface.getData('LSPGEOLON')
