from meresco.core import Observable

from oas.utils import identifierFromXml, filterAnnotations, validIdentifier
from oas.namespaces import setAttrib, getAttrib, namespaces, xpath

from urllib import quote_plus
from lxml.etree import SubElement

from meresco.components.xml_generic.validate import ValidateException

class Publish(Observable):

    def __init__(self, baseUrl):
        Observable.__init__(self)
        self._baseUrl = baseUrl
        if not self._baseUrl[-1] == '/':
            self._baseUrl += '/'

    def urnToUrl(self, lxmlNode, identifier):
        newIdentifier = self._baseUrl + quote_plus(identifier)
        setAttrib(lxmlNode, 'rdf:about', newIdentifier)
        SubElement(lxmlNode, '{%(dc)s}identifier' % namespaces).text = identifier
        return newIdentifier

    def process(self, lxmlNode):
        for annotation in filterAnnotations(lxmlNode):
            identifier = getAttrib(annotation, 'rdf:about')
            if identifier.lower().startswith('urn:'):
                identifier = self.urnToUrl(annotation, identifier)
            if not validIdentifier(identifier):
                raise ValidateException("Invalid identifier")

            for body in xpath(annotation, '//oac:Body'):
                bodyIdentifier = getAttrib(body, 'rdf:about')
                if bodyIdentifier.startswith('urn:'):
                    self.urnToUrl(body, bodyIdentifier)
        yield self.all.add(identifier=identifier, partname="rdf", lxmlNode=lxmlNode)
