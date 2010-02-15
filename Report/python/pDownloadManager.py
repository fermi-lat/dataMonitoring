import os
import sys
import logging
import commands

logging.basicConfig(level = logging.DEBUG)


BASE_REPORT_URL  = 'http://glast-ground.slac.stanford.edu/Reports/'
INVALIDATE_URL   = '%s%s' % (BASE_REPORT_URL, 'invalidateSession')
COOKIE_FILE_NAME = 'cookies.txt'


class pDownloadManager:

    def __init__(self, downloadFolder, cookieFolder):
        self.DownloadFolder = downloadFolder
        self.CookieFolderPath = cookieFolder
        self.CookieFilePath = os.path.join(cookieFolder, COOKIE_FILE_NAME)
        if not os.path.exists(self.CookieFolderPath):
            os.makedirs(self.CookieFolderPath)

    def downloadUrl(self, url, options = ''):
        command  = 'wget -p -nv --convert-links -nH -nd '
        if not os.path.exists(self.CookieFilePath):
            logging.debug('Storing cookies in %s...' % self.CookieFilePath)
            command += '--save-cookies %s ' % self.CookieFilePath
        else:
            logging.debug('Loading cookies from %s...' % self.CookieFilePath)
            command += '--load-cookies %s ' % self.CookieFilePath
        command += '--keep-session-cookies -P%s "%s%s"' %\
                   (self.DownloadFolder, url, options)
        logging.info('Executing "%s"' % command)
        logging.info(commands.getoutput(command))

    def downloadPanel(self, name, startTime, endTime, imageFormat = 'png'):
        url = '%sreport.jsp?reportId=%s' % (BASE_REPORT_URL, name)
        options = '&timeInterval=%d-%d&maxBins=-1&imageFormat=%s' %\
                  (startTime, endTime, imageFormat)
        self.downloadUrl(url, options)

    def downloadBaseReportUrl(self):
        self.downloadUrl(BASE_REPORT_URL, '')

    def invalidateSession(self):
        logging.debug('Invalidating session...')
        self.downloadUrl(INVALIDATE_URL)
        self.cleanup()
        self.cleanupCookies()

    def cleanup(self):
        logging.info('Cleaning up download folder...')
        os.system('rm -rf %s' % self.DownloadFolder)

    def cleanupCookies(self):
        logging.info('Removing stored cookies...')
        os.system('rm -rf %s' % self.CookieFolderPath)


if __name__ == '__main__':
    startTime = 1208649599000 - 3600*1000*24
    endTime  = 1208649599000
    downloadManager = pDownloadManager('download')
    downloadManager.downloadBaseReportUrl()
    downloadManager.downloadPanel('EnvPanel1', startTime, endTime)
