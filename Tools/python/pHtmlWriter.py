
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

    def openPage(self, filePath):
        self.openFile(filePath)
        self.writeComment('Generated by pHtmlWriter on %s.' % time.asctime())
        self.newline()
        self.openTag('html')
        self.newline()

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
