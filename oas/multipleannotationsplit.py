from meresco.core import Observable
from lxml.etree import tostring, Element

from oas.utils import identifierFromXml, validIdentifier
from oas.namespaces import namespaces, xpath
from meresco.components.xml_generic.validate import ValidateException

class MultipleAnnotationSplit(Observable):

    def add(self, identifier, partname, lxmlNode):
        children = xpath(lxmlNode, '/rdf:RDF/child::*')
        if len(children) == 0:
            raise ValidateException('Expected child Annotations.')
        for nr, child in enumerate(children):
            newRoot = Element("{%(rdf)s}RDF" % namespaces)
            newRoot.append(child)
            identifier=identifierFromXml(newRoot)
            if not validIdentifier(identifier):
                raise ValidateException("Child node %s has no or invalid identifier" % nr)
            yield self.all.add(identifier=identifier, partname=partname, lxmlNode=newRoot)

    def delete(self, idenfifier):
        return self.all.delete(identifier)
