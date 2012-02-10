from meresco.core import Observable
from lxml.etree import tostring, Element

from rdfcontainer import RdfContainer
from oas.utils.annotation import filterAnnotations, validIdentifier
from oas.namespaces import namespaces, xpath, getAttrib, expandNs
from meresco.components.xml_generic.validate import ValidateException

class MultipleAnnotationSplit(Observable):
    def add(self, identifier, partname, lxmlNode):
        rdfContainer = RdfContainer(lxmlNode)
        annotationFound = False
        for annotation in filterAnnotations(lxmlNode):
            identifier = getAttrib(annotation, 'rdf:about')
            if not validIdentifier(identifier):
                continue
            annotationFound = True
            newRoot = Element("{%(rdf)s}RDF" % namespaces)
            newRoot.append(annotation)
            self._inlineURNs(newRoot, rdfContainer)
            yield self.all.add(identifier=identifier, partname=partname, lxmlNode=newRoot)
        if not annotationFound:
            raise ValidateException("No annotations found.")
        

    def delete(self, idenfifier):
        return self.all.delete(identifier)


    def _inlineURNs(self, root, rdfContainer):
        for relation in ['dcterms:creator']:
            nodes = xpath(root, '//%s[@rdf:resource]' % relation)
            for node in nodes:
                urn = getAttrib(node, 'rdf:resource')
                if urn:
                    resolvedNode = rdfContainer.resolve(urn)
                    if not resolvedNode is None:
                        node.append(resolvedNode)
                        del node.attrib[expandNs('rdf:resource')]


