from seecr.test import SeecrTestCase, CallTrace

from weightless.core import be, compose
from meresco.core import Observable

from lxml.etree import parse, tostring
from StringIO import StringIO

from oas import Deanonymize

class DeanonymizeTest(SeecrTestCase):

    def setUp(self):
        SeecrTestCase.setUp(self)
        self.observer = CallTrace(emptyGeneratorMethods=['process'])
        self.deanonymize = Deanonymize()
        self.dna = be(
            (Observable(),
                (self.deanonymize,
                    (self.observer,)
                )
            )
        )

    def testPassThroughAbout(self):
        xml = """<rdf:RDF 
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:oac="http://www.openannotation.org/ns/"> 
    <oac:Annotation rdf:about="urn:id:1"/>
</rdf:RDF>"""

        list(compose(self.dna.all.process(lxmlNode=parse(StringIO(xml)))))
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEqualsWS(xml, tostring(self.observer.calledMethods[0].kwargs['lxmlNode']))

    def testPassThroughResource(self):
        xml = """<rdf:RDF 
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:oac="http://www.openannotation.org/ns/"> 
    <oac:Annotation rdf:resource="urn:id:1"/>
</rdf:RDF>"""

        list(compose(self.dna.all.process(lxmlNode=parse(StringIO(xml)))))
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEqualsWS(xml, tostring(self.observer.calledMethods[0].kwargs['lxmlNode']))

    def testAddUrn(self):
        xml = """<rdf:RDF 
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:oac="http://www.openannotation.org/ns/"> 
    <oac:Annotation%s/>
</rdf:RDF>"""

        newIdentifier = 'urn:some:form:of:identifier'
        self.deanonymize._urnGen = lambda: newIdentifier
        list(compose(self.dna.all.process(lxmlNode=parse(StringIO(xml % "")))))
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEqualsWS(xml % ' rdf:about="%s"' % newIdentifier, tostring(self.observer.calledMethods[0].kwargs['lxmlNode']))

    def testAddUrnToOacBody(self):
        xml = """<rdf:RDF 
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:oac="http://www.openannotation.org/ns/"> 
    <oac:Annotation rdf:about="urn:annotation:identifier">
        <oac:hasBody>
            <oac:Body%s/>
        </oac:hasBody>
    </oac:Annotation>
</rdf:RDF>"""

        newIdentifier = 'urn:some:form:of:identifier'
        self.deanonymize._urnGen = lambda: newIdentifier
        list(compose(self.dna.all.process(lxmlNode=parse(StringIO(xml % "")))))
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEqualsWS(xml % ' rdf:about="%s"' % newIdentifier, tostring(self.observer.calledMethods[0].kwargs['lxmlNode']))


