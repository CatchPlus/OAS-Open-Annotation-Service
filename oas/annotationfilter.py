from meresco.core import Observable

from namespaces import xpath

class AnnotationFilter(Observable):

    def add(self, identifier, partname, lxmlNode):
        if xpath(lxmlNode, '/rdf:RDF/rdf:Description/rdf:type[@rdf:resource="http://www.openannotation.org/ns/Annotation"]') or xpath(lxmlNode, '/rdf:RDF/oas:Annotation'):
            yield self.all.add(identifier=identifier, partname=partname, lxmlNode=lxmlNode)
