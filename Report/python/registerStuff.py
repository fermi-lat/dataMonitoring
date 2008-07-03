"""@brief Register output data with the data server.
@author W. Focke <focke@slac.stanford.edu>
"""
# This script is automagically pasted into the XML at install time
import os
import sys

from java.util import HashMap
from org.glast.datacat.client.sql import NewDataset

def getVar(handler, name):
    mangledName = '_'.join([nameManglingPrefix, reportType, name])
    value = parentPI.getVariable(mangledName)
    return value

parentPI = pipeline.getProcessInstance(parentProcess)

fileFormat = getVar(reportType, 'format')
fileType = getVar(reportType, 'fileType')
dcPath = getVar(reportType, 'path')
dcGroup = getVar(reportType, 'group')
site = getVar(reportType, 'site')
creator = getVar(reportType, 'creator')
fullName = getVar(reportType, 'fullName')
dsName = getVar(reportType, 'shortName')
tStart = getVar(reportType, 'tStart')
tStop = getVar(reportType, 'tStop')

attributes = HashMap()
attributes.put('sCreator', creator)
attributes.put('nMetStart', tStart)
attributes.put('nMetStop', tStop)

dsNew = NewDataset(dsName, fileFormat, fileType, dcPath, dcGroup, site, fullName)
ds = datacatalog.registerDataset(dsNew, attributes);
