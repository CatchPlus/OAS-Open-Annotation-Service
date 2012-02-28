from seecr.test import SeecrTestCase, CallTrace

from weightless.core import be, compose
from meresco.core import Observable

from lxml.etree import parse, tostring
from StringIO import StringIO

from oas import Publish

class PublishTest(SeecrTestCase):

    def setUp(self):
        SeecrTestCase.setUp(self)
        self.observer = CallTrace(emptyGeneratorMethods=['add'])
        self.dna = be(
            (Observable(),
                (Publish(baseUrl="http://some.where/here"),
                    (self.observer, )
                )
            )
        )

    def testOne(self):
        xml="""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:oac="http://www.openannotation.org/ns/">
    <oac:Annotation rdf:about="urn:id:1"/>
</rdf:RDF>"""
        list(compose(self.dna.all.process(parse(StringIO(xml)))))
        self.assertEqualsWS("""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:oac="http://www.openannotation.org/ns/">
    <oac:Annotation rdf:about="http://some.where/here/urn%3Aid%3A1"><dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/">urn:id:1</dc:identifier></oac:Annotation>
</rdf:RDF>""", tostring(self.observer.calledMethods[0].kwargs['lxmlNode']))
        self.assertEquals("http://some.where/here/urn%3Aid%3A1", self.observer.calledMethods[0].kwargs['identifier'])

    def testDontPublishIfAlreadyAnURL(self):
        xml="""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:oac="http://www.openannotation.org/ns/">
    <oac:Annotation rdf:about="http://some.where.else/1"/>
</rdf:RDF>"""
        list(compose(self.dna.all.process(parse(StringIO(xml)))))
        self.assertEqualsWS(xml, tostring(self.observer.calledMethods[0].kwargs['lxmlNode']))
        self.assertEquals("http://some.where.else/1", self.observer.calledMethods[0].kwargs['identifier'])

    def testPublishBodyToo(self):
        xml="""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:oac="http://www.openannotation.org/ns/">
    <oac:Annotation rdf:about="urn:id:1">
        <oac:hasBody>
            <oac:Body rdf:about="urn:id:2"/>
        </oac:hasBody>
    </oac:Annotation>
</rdf:RDF>"""
        list(compose(self.dna.all.process(parse(StringIO(xml)))))
        self.assertEqualsWS("""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:oac="http://www.openannotation.org/ns/">
    <oac:Annotation rdf:about="http://some.where/here/urn%3Aid%3A1">
        <oac:hasBody>
            <oac:Body rdf:about="http://some.where/here/urn%3Aid%3A2">
                <dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/">urn:id:2</dc:identifier>
            </oac:Body>
        </oac:hasBody>
        <dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/">urn:id:1</dc:identifier>
    </oac:Annotation>
</rdf:RDF>""", tostring(self.observer.calledMethods[0].kwargs['lxmlNode']))
        self.assertEquals("http://some.where/here/urn%3Aid%3A1", self.observer.calledMethods[0].kwargs['identifier'])
