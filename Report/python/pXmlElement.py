## @package pXmlElement
## @brief Description of a minimal xml element.

import sys
import logging

## @brief Class describing a minimal xml element.
#
#  At the lowest level, the class describe a piece of xml looking like:
#  @code
#  <node_name attribute1="..." ... attributeN="...">
#  ...
#  </node_name>
#  @endcode
#  and provides convenience functions for accessing sub-elements, attributes
#  and convert them to non-string objects.

class pXmlElement:

    ## @brief Base constructor.
    ## @param self
    #  The class instance.
    ## @param domElement
    #  A xml element, as returned by the getElementsByTagName()
    #  function of the xml.dom.minidom module.

    def __init__(self, domElement):

        ## @var DomElement
        #  @brief The underlying xml.dom.minidom element.

        ## @var NodeName
        #  The node name of the element.

        self.DomElement = domElement
        self.NodeName   = self.DomElement.nodeName

    ## @brief Return the attribute corresponing to a given attribute name.
    #
    #  The attribute is converted from unicode to standard string,
    #  as needed by numpy.
    #  An optional default value can be provided, in case the attribute does
    #  not exist.
    ## @param self
    #  The class instance.
    ## @param attributeName
    #  The attribute name.
    ## @param default
    #  The default value (returned if the attribute does not exist).

    def getAttribute(self, attributeName, default = None):
        attribute = str(self.DomElement.getAttribute(attributeName))
        if attribute == '':
            attribute = default
        return attribute

    ## @brief Eval the attribute corresponing to a given attribute name.
    #
    #  An optional default value can be provided, in case the attribute does
    #  not exist, or the eval statement fails.
    ## @param self
    #  The class instance.
    ## @param attributeName
    #  The attribute name.
    ## @param default
    #  The default value (returned if the attribute does not exist or the
    #  eval statement fails).

    def evalAttribute(self, attributeName, default = None):
        attribute = self.getAttribute(attributeName, default)
        if attribute == default:
            return default
        try:
            return eval(attribute)
        except:
            logging.error('Could not eval attribute %s for node %s. ' %\
                              (attributeName, self.NodeName)          +\
                              'Returning %s...' % default)
            return default

    ## @brief Return a list of dom elements corrisponding to a given tag
    #  name.
    #
    #  If there are no such elements, an empty list is returned instead.
    ## @param self
    #  The class instance.
    ## @param tagName
    #  The tag name
    
    def getElementsByTagName(self, tagName):
        elementsList = []
        for element in  self.DomElement.getElementsByTagName(tagName):
            elementsList.append(pXmlElement(element))
        return elementsList

    ## @brief Return a single dom element corresponding to a given tag name.
    #
    #  This function should be used for those tag that apperar exactly once
    #  into the underlying DomElement.
    #  An optional default value can be provided, to be returned in case there
    #  are no tags corresponding to the given tag name. If the tags are
    #  multiply defined, an error message is printed and the first is
    #  returned.
    ## @param self
    #  The class instance.
    ## @param tagName
    #  The tag name
    ## @param default
    #  The value to be returned in case there are no tags corresponding to a
    #  given tag name.
    ## @param required
    #  If true the xml elemnt is required and an error is raised if it's
    #  missing in the xml file.

    def getElementByTagName(self, tagName, default = None, required = True):
        elementsList = self.getElementsByTagName(tagName)
        if elementsList == []:
            if required:
                logging.error('Tag %s missing.' % tagName)
            return default
        elif len(elementsList) > 1:
            logging.error('Tag %s multiply defined. ' % tagName)
            logging.info('Returning the first one...')
        return elementsList[0]

    ## @brief Get the content of a particular tag (supposingly defined
    #  exactly once).
    ## @param self
    #  The class instance.
    ## @param tagName
    #  The tag name
    ## @param default
    #  The value to be returned in case there are no tags corresponding to a
    #  given tag name or the tag has no value.
    ## @param required
    #  If true the xml elemnt is required and an error is raised if it's
    #  missing in the xml file.
    
    def getTagValue(self, tagName, default = None, required = False):
        element = self.getElementByTagName(tagName, default, required)
        if element == default:
            return default
        try:
            return str(element.childNodes[0].data).strip()
        except:
            return default

    ## @brief Eval the content of a particular tag (supposingly defined
    #  exactly once).
    ## @param self
    #  The class instance.
    ## @param tagName
    #  The tag name
    ## @param default
    #  The value to be returned in case there are no tags corresponding to a
    #  given tag name or the tag has no value or the eval statement fails
    #  for some reason.
    ## @param required
    #  If true the xml elemnt is required and an error is raised if it's
    #  missing in the xml file.

    def evalTagValue(self, tagName, default = None, required = False):
        value = self.getTagValue(tagName, default, required)
        if value == default:
            return default
        try:
            return eval(self.getTagValue(tagName))
        except:
            return default


