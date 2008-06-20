
import logging
logging.basicConfig(level = logging.DEBUG)

import sys
import os
import time

from pAsciiWriter import pAsciiWriter


COMMONS_PATH = 'http://glast-ground.slac.stanford.edu/Commons'

class pHtmlWriter(pAsciiWriter):

    def openFile(self, filePath):
        pAsciiWriter.openFile(self, filePath)
        self.OpenTags = []

    def openTag(self, tagName, attributesDict = {}, element = None,\
                close = False):
        self.OpenTags.append(tagName)
        self.writeIndented('<%s' % tagName)
        if attributesDict != {}:
            for item in attributesDict.items():
                self.write(' %s="%s"' % item)
        self.indent()
        if element is not None:
            self.write('>')
            self.write(element)
            if close:
                self.closeTag(False)
        else:
            if close:
                self.write('/>')
                self.OpenTags.pop()
                self.backup()
            else:
                self.write('>')
            self.newline()

    def closeTag(self, indented = True):
        self.backup()
        if indented:
            self.writeIndented('</%s>' % self.OpenTags.pop())
        else:
            self.write('</%s>' % self.OpenTags.pop())
        self.newline()

    def closeTags(self):
        for i in range(len(self.OpenTags) - 1):
            self.closeTag()
        self.newline()
        self.closeTag()

    def openDiv(self, attributesDict = {}, element = None, close = False):
        self.openTag('div', attributesDict, element, close)

    def writePageTitle(self, title):
        self.openTag('title', {}, title, True)

    def linkStyleSheet(self, cssFilePath, media = 'all'):
        self.openTag('link', {'rel': 'StyleSheet', 'href': cssFilePath,
                              'type': 'text/css', 'media': media}, None, True)

    def openPage(self, filePath, title):
        self.openFile(filePath)
        self.writeComment('Generated by pHtmlWriter on %s.' % time.asctime())
        self.newline()
        self.openTag('html')
        self.newline()
        self.writePageHead(title, '%s/css/glastCommons.jsp' % COMMONS_PATH)
        self.openBody(False)
        self.newline()
        self.openDiv({'class': 'pageBody'})

    def closePage(self):
        self.closeTags()
        self.closeFile()

    def writeComment(self, text):
        self.writeIndented('<!-- %s -->' % text)
        self.newline()

    def writePageHead(self, title, cssFilePath):
        self.openTag('head')
        self.writePageTitle(title)
        self.linkStyleSheet(cssFilePath)
        self.closeTag()
        self.newline()

    def openBody(self, center = True):
        self.openTag('body')
        if center:
            self.openTag('center')

    def switchLineType(self):
        if self.CurrentLineType == 'even':
            self.CurrentLineType = 'odd'
        else:
            self.CurrentLineType = 'even'

    def openTable(self, headerEntries = None):
        self.openTag('table', {'class': 'datatable'})
        self.CurrentLineType = 'odd'
        if headerEntries is not None:
            self.writeTableHeader(headerEntries)

    def writeTableHeader(self, entries):
        self.openTag('thead')
        self.openTag('tr')
        for entry in entries:
            self.openTag('th', {}, str(entry), True)
        self.closeTag()
        self.closeTag()
        self.openTag('tbody')

    def writeTableLine(self, entries):
        self.openTag('tr', {'class': self.CurrentLineType})
        for entry in entries:
            self.openTag('td', {'class': 'leftAligned'}, str(entry), True)
        self.closeTag()
        self.switchLineType()

    def addParagraph(self, text):
        pass
