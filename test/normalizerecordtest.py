from seecr.test import SeecrTestCase, CallTrace

from weightless.core import be, compose
from meresco.core import Observable

from lxml.etree import parse, tostring
from StringIO import StringIO

from oas import NormalizeRecord
from oas.normalizerecord import splitType

class NormalizeRecordTest(SeecrTestCase):

    def setUp(self):
        SeecrTestCase.setUp(self)
        self.observer = CallTrace(emptyGeneratorMethods=['add', "delete"])
        self.dna = be(
            (Observable(),
                (NormalizeRecord(),
                    (self.observer,)
                )
            )
        )
   
    def assertConvert(self, expected, source):
        list(compose(self.dna.all.add(
            identifier='identifier', 
            partname='rdf', 
            lxmlNode=parse(StringIO(source)))))

        resultNode = self.observer.calledMethods[0].kwargs['lxmlNode']
        self.assertEqualsWS(
            expected, 
            tostring(resultNode, pretty_print=True))


    def testOne(self):
        XML = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about="urn:identifier">
        <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
    </rdf:Description>
</rdf:RDF>"""
        EXPECTED_XML = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <oac:Annotation xmlns:oac="http://www.openannotation.org/ns/" rdf:about="urn:identifier"/>
</rdf:RDF>"""
        self.assertConvert(EXPECTED_XML, XML)

    def testSubElements(self):
        XML = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dc="http://purl.org/dc/elements/1.1/">
    <rdf:Description rdf:about="urn:identifier">
        <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
        <dc:title>A title</dc:title>
    </rdf:Description>
</rdf:RDF>"""
        EXPECTED_XML = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dc="http://purl.org/dc/elements/1.1/">
    <oac:Annotation xmlns:oac="http://www.openannotation.org/ns/" rdf:about="urn:identifier">
        <dc:title>A title</dc:title>
    </oac:Annotation>
</rdf:RDF>"""
        self.assertConvert(EXPECTED_XML, XML)

    def testMultiple(self):
        XML = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dcterms="http://purl.org/dc/terms/">
    <rdf:Description rdf:about="urn:identifier">
        <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
        <dcterms:creator>
            <rdf:Description rdf:about="urn:agent">
                <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Agent"/>
            </rdf:Description>
        </dcterms:creator>
    </rdf:Description>
</rdf:RDF>"""
        EXPECTED_XML = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dcterms="http://purl.org/dc/terms/">
    <oac:Annotation xmlns:oac="http://www.openannotation.org/ns/" rdf:about="urn:identifier">
        <dcterms:creator>
            <foaf:Agent xmlns:foaf="http://xmlns.com/foaf/0.1/" rdf:about="urn:agent"/>
        </dcterms:creator>
    </oac:Annotation>
</rdf:RDF>"""
        self.assertConvert(EXPECTED_XML, XML)
    
    def testLeaveDescriptionsWithoutTypeAlone(self):
        XML = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dcterms="http://purl.org/dc/terms/">
    <rdf:Description rdf:about="urn:identifier">
        <dcterms:creator>
            <rdf:Description rdf:about="urn:agent"/>
        </dcterms:creator>
    </rdf:Description>
</rdf:RDF>"""
        self.assertConvert(XML, XML)

    def testSplitRdfType(self):
        self.assertEquals(("http://ns/", "Type"), splitType("http://ns/Type")) 
        self.assertEquals(("http://ns#", "Type"), splitType("http://ns#Type")) 

    def testDeletePassedOn(self):
        list(compose(self.dna.all.delete(
            identifier='identifier', 
            partname='rdf', 
            lxmlNode=parse(StringIO("<xml/>")))))

        self.assertEquals(['delete'], [m.name for m in self.observer.calledMethods])
