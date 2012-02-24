from seecr.test import SeecrTestCase, CallTrace

from weightless.core import be, compose
from meresco.core import Observable

from lxml.etree import parse, tostring
from StringIO import StringIO

from oas import Publish

class PublishTest(SeecrTestCase):

    def testOne(self):
        observer = CallTrace(emptyGeneratorMethods=['add'])
        dna = be(
            (Observable(),
                (Publish(baseUrl="http://some.where/here"),
                    (observer, )
                )
            )
        )
        xml="""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:oac="http://www.openannotation.org/ns/">
    <oac:Annotation rdf:about="urn:id:1"/>
</rdf:RDF>"""
        list(compose(dna.all.process(parse(StringIO(xml)))))
        self.assertEqualsWS("""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:oac="http://www.openannotation.org/ns/">
    <oac:Annotation rdf:about="http://some.where/here/urn%3Aid%3A1"><dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/">urn:id:1</dc:identifier></oac:Annotation>
</rdf:RDF>""", tostring(observer.calledMethods[0].kwargs['lxmlNode']))
        self.assertEquals("http://some.where/here/urn%3Aid%3A1", observer.calledMethods[0].kwargs['identifier'])
