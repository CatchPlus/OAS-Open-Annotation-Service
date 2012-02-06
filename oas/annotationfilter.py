from meresco.core import Observable

from namespaces import xpath


def validAnnotation(lxmlNode):
    return xpath(lxmlNode, '/rdf:RDF/rdf:Description/rdf:type[@rdf:resource="http://www.openannotation.org/ns/Annotation"]') or xpath(lxmlNode, '/rdf:RDF/oas:Annotation')

class AnnotationFilter(Observable):

    def add(self, identifier, partname, lxmlNode):
        if validAnnotation(lxmlNode):
            yield self.all.add(identifier=identifier, partname=partname, lxmlNode=lxmlNode)
