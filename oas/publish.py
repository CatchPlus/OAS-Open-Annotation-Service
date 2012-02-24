from meresco.core import Observable

from oas.utils import identifierFromXml, filterAnnotations, validIdentifier
from oas.namespaces import setAttrib, getAttrib, namespaces

from urllib import quote_plus
from lxml.etree import SubElement

from meresco.components.xml_generic.validate import ValidateException

class Publish(Observable):

    def __init__(self, baseUrl):
        Observable.__init__(self)
        self._baseUrl = baseUrl
        if not self._baseUrl[-1] == '/':
            self._baseUrl += '/'

    def process(self, lxmlNode):
        for annotation in filterAnnotations(lxmlNode):
            identifier = getAttrib(annotation, 'rdf:about')
            if identifier.startswith('urn:'):
                newIdentifier = self._baseUrl + quote_plus(identifier)
                setAttrib(annotation, 'rdf:about', newIdentifier)
                SubElement(annotation, '{%(dc)s}identifier' % namespaces).text = identifier
                identifier = newIdentifier
            if not validIdentifier(identifier):
                raise ValidateException("Invalid identifier")
        yield self.all.add(identifier=identifier, partname="rdf", lxmlNode=lxmlNode)
