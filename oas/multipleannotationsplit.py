from meresco.core import Observable
from lxml.etree import tostring, Element, parse
from StringIO import StringIO

from rdfcontainer import RdfContainer
from oas.utils.annotation import filterAnnotations, validIdentifier
from oas.namespaces import namespaces, xpath, getAttrib, expandNs
from meresco.components.xml_generic.validate import ValidateException

class MultipleAnnotationSplit(Observable):
    def add(self, identifier, partname, lxmlNode):
        rdfContainer = RdfContainer(lxmlNode)
        annotationFound = False
        for annotation in filterAnnotations(lxmlNode):
            annotationFound = True
            newRoot = Element("{%(rdf)s}RDF" % namespaces)
            newRoot.append(annotation)
            self._inlineURNs(newRoot, rdfContainer)
            yield self.all.process(lxmlNode=newRoot)
        if not annotationFound:
            raise ValidateException("No annotations found.")

    def delete(self, idenfifier):
        return self.all.delete(identifier)

    def _inlineURNs(self, root, rdfContainer):
        for relation in [{'tag': 'dcterms:creator', 'partname': 'foafAgent'}, {'tag': 'oac:hasBody', 'partname': 'oacBody'}]:
            nodes = xpath(root, '//%s[@rdf:resource]' % relation['tag'])
            for node in nodes:
                urn = getAttrib(node, 'rdf:resource')
                if urn:
                    resolvedNode = rdfContainer.resolve(urn)
                    if not resolvedNode is None:
                        node.append(resolvedNode)
                        del node.attrib[expandNs('rdf:resource')]
                    elif self.call.isAvailable(identifier=urn, partname=relation['partname']) == (True, True):
                        data = self.call.getStream(identifier=urn, partname=relation['partname'])
                        node.append(parse(StringIO(data.read())).getroot())
                        del node.attrib[expandNs('rdf:resource')]

