from seecr.test import SeecrTestCase, CallTrace

from lxml.etree import parse
from StringIO import StringIO

from meresco.core import be, Observable
from oas import AnnotationFilter

class AnnotationFilterTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.observer = CallTrace('Observer')
        self.dna = be(
            (Observable(),
                (AnnotationFilter(),
                    (self.observer,)
                )
            ))

    def testFilterRdfDescription(self):
        list(self.dna.all.add(identifier="IDENTIFIER", partname="rdf", lxmlNode=parse(StringIO("""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about="some:identifier"><rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/></rdf:Description></rdf:RDF>"""))))
        self.assertEquals(1, len(self.observer.calledMethods))
    
    def testFilterAnnotation(self):
        list(self.dna.all.add(identifier="IDENTIFIER", partname="rdf", lxmlNode=parse(StringIO("""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:oas="http://www.openannotation.org/ns/"><oas:Annotation rdf:about="some:identifier"></oas:Annotation></rdf:RDF>"""))))
        self.assertEquals(1, len(self.observer.calledMethods))
    
    def testFilterOthers(self):
        list(self.dna.all.add(identifier="IDENTIFIER", partname="rdf", lxmlNode=parse(StringIO("""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about="some:identifier"></rdf:Description></rdf:RDF>"""))))
        self.assertEquals(0, len(self.observer.calledMethods))
