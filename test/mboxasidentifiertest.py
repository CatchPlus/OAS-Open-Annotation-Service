from seecr.test import SeecrTestCase, CallTrace

from weightless.core import Observable, compose, be

from lxml.etree import parse
from StringIO import StringIO

from oas import MboxAsIdentifier
from oas.namespaces import xpath

class MboxAsIdentifierTest(SeecrTestCase):
    
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.observer = CallTrace(emptyGeneratorMethods=['add', 'delete'])
        self.dna = be(
            (Observable(), 
                (MboxAsIdentifier(),
                    (self.observer, )
                )
            ))

    def testOne(self):
        list(compose(self.dna.all.add(
            identifier="identifier", 
            partname="rdf", 
            lxmlNode=parse(StringIO(XML % {'urn': 'urn:this:should:be:gone'})))))
        self.assertEquals(1, len(self.observer.calledMethods))
        lxmlNode = self.observer.calledMethods[0].kwargs['lxmlNode']
        self.assertEquals(["mailto:joe@example.org"], xpath(lxmlNode, "/rdf:RDF/oac:Annotation/dcterms:creator/@rdf:resource"))

    def testDeletePassesThrough(self):
        list(compose(self.dna.all.delete(identifier="identifier", partname="rdf")))
        self.assertEquals(['delete'], [m.name for m in self.observer.calledMethods])


XML = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
    xmlns:oac="http://www.openannotation.org/ns/"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:foaf="http://xmlns.com/foaf/0.1/">

    <oac:Annotation rdf:about="urn:identifier">
        <dcterms:creator rdf:resource="%(urn)s">
            <foaf:mbox>joe@example.org</foaf:mbox>
        </dcterms:creator>
    </oac:Annotation>
</rdf:RDF>"""

