"""@brief Register output data with the data server.
@author W. Focke <focke@slac.stanford.edu>
"""
# This script is automagically pasted into the XML at install time
parentPI = pipeline.getProcessInstance(parentProcess)
logicalPath = parentPI.getVariable("REGISTER_LOGIPATH")
fileType = parentPI.getVariable("REGISTER_FILETYPE")
filePath = parentPI.getVariable("REGISTER_FILEPATH")
attributes = parentPI.getVariable("REGISTER_ATTRIBUTES")
datacatalog.registerDataset(fileType, logicalPath, filePath, attributes)
