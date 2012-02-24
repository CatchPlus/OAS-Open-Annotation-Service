from seecr.test import SeecrTestCase, CallTrace
from weightless.core import be, compose
from meresco.core import Observable

from lxml.etree import parse
from StringIO import StringIO

from oas.sanitize import Sanitize
from oas.utils import identifierFromXml

class SanitizeTest(SeecrTestCase):

    def testOne(self):
        urnGenerator=('urn:number:'+str(n) for n in range(10))

        observer = CallTrace(emptyGeneratorMethods=['add', 'isAvailable', 'getStream', 'process'])
        dna = be(
            (Observable(),
                (Sanitize(urnGen=urnGenerator.next, resolveBaseUrl="http://some.where/here"),
                    (observer, )
                )
            )
        )

        xml = """<rdf:RDF 
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:oac="http://www.openannotation.org/ns/">
            <rdf:Description rdf:about="urn:identifier:1">
                <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
            </rdf:Description>
            <oac:Annotation rdf:about="http://here.and.there"/>
            <oac:Annotation/>
            <rdf:Description>
                <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
            </rdf:Description>
        </rdf:RDF>"""

        list(compose(dna.all.add(identifier='IDENTIFIER', partname="rdf", lxmlNode=parse(StringIO(xml)))))

        addMethods = [m for m in observer.calledMethods if m.name == "add"]
        self.assertEquals(4, len(addMethods))
        identifiers = [method.kwargs['identifier'] for method in addMethods]
        identifiersFromLxmlNodes = [identifierFromXml(method.kwargs['lxmlNode']) for method in addMethods]
        self.assertEquals(['http://some.where/here/urn%3Aidentifier%3A1', 'http://some.where/here/urn%3Anumber%3A0', 'http://here.and.there', 'http://some.where/here/urn%3Anumber%3A1'], identifiers)
        self.assertEquals(identifiers, identifiersFromLxmlNodes)

