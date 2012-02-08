from seecr.test import SeecrTestCase, CallTrace

from lxml.etree import parse
from StringIO import StringIO

from weightless.core import compose

from meresco.core import Observable
from weightless.core import be
from oas import AboutUriRewrite
from oas.utils import identifierFromXml

def addMock(identifier, partname, lxmlNode):
    return
    yield

class AboutUriRewriteTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.observer = CallTrace('Observer', methods={'add': addMock})
        self.dna = be(
            (Observable(),
                (AboutUriRewrite(baseUrl="http://oas.dev.seecr.nl:8000/resolve/"),
                    (self.observer,)
                )
            ))

    def testOne(self):
        XML = """
        <rdf:RDF 
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:oac="http://www.openannotation.org/ns/">
            <rdf:Description rdf:about="urn:identifier&amp;1">
                <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
            </rdf:Description>
        </rdf:RDF>
        """

        list(compose(self.dna.all.add(identifier="urn:identifier&1", partname="rdf", lxmlNode=parse(StringIO(XML)))))
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEquals('urn:identifier&1', self.observer.calledMethods[0].kwargs['identifier'])
        self.assertEquals('http://oas.dev.seecr.nl:8000/resolve/urn%3Aidentifier%261', identifierFromXml(self.observer.calledMethods[0].kwargs['lxmlNode']))

    def testResolveURNsOnly(self):
        XML = """
        <rdf:RDF 
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:oac="http://www.openannotation.org/ns/">
            <rdf:Description rdf:about="http://example.org/identifier:1">
                <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
            </rdf:Description>
        </rdf:RDF>
        """

        list(compose(self.dna.all.add(identifier="http://example.org/identifier:1", partname="rdf", lxmlNode=parse(StringIO(XML)))))
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEquals('http://example.org/identifier:1', self.observer.calledMethods[0].kwargs['identifier'])
        self.assertEquals('http://example.org/identifier:1', identifierFromXml(self.observer.calledMethods[0].kwargs['lxmlNode']))

