from seecr.test import SeecrTestCase, CallTrace

from lxml.etree import parse
from StringIO import StringIO

from weightless.core import compose

from meresco.core import Observable
from weightless.core import be
from oas import MultipleAnnotationSplit
from meresco.components.xml_generic.validate import ValidateException

class MultipleAnnotationSplitTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.observer = CallTrace('Observer', emptyGeneratorMethods=['add'])
        self.dna = be(
            (Observable(),
                (MultipleAnnotationSplit(),
                    (self.observer,)
                )
            ))
    def testOne(self):
        XML = """
        <rdf:RDF 
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:oac="http://www.openannotation.org/ns/">
            <rdf:Description rdf:about="identifier:1">
                <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
            </rdf:Description>
            <oac:Annotation rdf:about="identifier:2"/>
            <rdf:Description rdf:about="identifier:3">
                <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
            </rdf:Description>
        </rdf:RDF>
        """

        list(compose(self.dna.all.add(identifier="IDENTIFIER", partname="rdf", lxmlNode=parse(StringIO(XML)))))
        self.assertEquals(3, len(self.observer.calledMethods))

    def testNoIdentifier(self):
        inputText = """
        <rdf:RDF 
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:some="http://www.example.org/ns/">
            <rdf:Description rdf:about="identifier:1">
                <some:tag/>
            </rdf:Description>
        </rdf:RDF>"""
        try:
            list(compose(self.dna.all.add(identifier="IDENTIFIER", partname="rdf", lxmlNode=parse(StringIO(inputText)))))
            self.fail()
        except ValidateException, e:
            self.assertEquals('Child node 0 has no or invalid identifier', str(e))

    def testNoRdf(self):
        inputText = """<oai_dc:dc xmlns:oai_dc="http://example.org"/>"""
        try:
            list(compose(self.dna.all.add(identifier="IDENTIFIER", partname="rdf", lxmlNode=parse(StringIO(inputText)))))
            self.fail()
        except ValidateException, e:
            self.assertEquals('Expected child Annotations.', str(e))
