from seecr.test import SeecrTestCase, CallTrace

from lxml.etree import parse, tostring
from StringIO import StringIO

from weightless.core import compose

from meresco.core import Observable
from meresco.components import FilterMessages
from weightless.core import be
from oas import MultipleAnnotationSplit
from oas.namespaces import namespaces
from meresco.components.xml_generic.validate import ValidateException

class MultipleAnnotationSplitTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.observer = CallTrace('Observer', emptyGeneratorMethods=['add'])
        self.storageObserver = CallTrace("storage")
        self.storageObserver.returnValues['isAvailable'] = (True, True)
        self.storageObserver.returnValues['getStream'] = StringIO("""<foaf:Agent rdf:about="urn:creator" xmlns:foaf="%(foaf)s" xmlns:rdf="%(rdf)s">
    <foaf:mbox>info@example.org</foaf:mbox>
</foaf:Agent>""" % namespaces)
        self.dna = be(
            (Observable(),
                (MultipleAnnotationSplit(),
                    (FilterMessages(allowed=['getStream', 'isAvailable']),
                        (self.storageObserver,),
                    ),
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
            self.assertEquals('No annotations found.', str(e))

    def testNoRdf(self):
        inputText = """<oai_dc:dc xmlns:oai_dc="http://example.org"/>"""
        try:
            list(compose(self.dna.all.add(identifier="IDENTIFIER", partname="rdf", lxmlNode=parse(StringIO(inputText)))))
            self.fail()
        except ValidateException, e:
            self.assertEquals('No annotations found.', str(e))

    def testInlineURNs(self):
        xml = """<rdf:RDF
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:foaf="http://xmlns.com/foaf/0.1/"
            xmlns:oac="http://www.openannotation.org/ns/"
            xmlns:dcterms="http://purl.org/dc/terms/">
            <oac:Annotation rdf:about="identifier:1">
                <dcterms:creator rdf:resource="urn:creator"/>
            </oac:Annotation>
            <rdf:Description rdf:about="urn:creator">
               <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Agent"/>
               <foaf:mbox>info@otherexample.org</foaf:mbox>
            </rdf:Description>
        </rdf:RDF>"""
        list(compose(self.dna.all.add(identifier="IDENTIFIER", partname="rdf", lxmlNode=parse(StringIO(xml)))))
        resultNode = self.observer.calledMethods[0].kwargs['lxmlNode']
        self.assertEqualsWS("""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <oac:Annotation xmlns:oac="http://www.openannotation.org/ns/" xmlns:dcterms="http://purl.org/dc/terms/" rdf:about="identifier:1">
        <dcterms:creator>
            <rdf:Description xmlns:foaf="http://xmlns.com/foaf/0.1/" rdf:about="urn:creator">
                <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Agent"/>
                <foaf:mbox>info@otherexample.org</foaf:mbox>
            </rdf:Description>
        </dcterms:creator>
    </oac:Annotation>
</rdf:RDF>""", tostring(resultNode))

    def testInlineURNFromStorage(self):
        xml = """<rdf:RDF
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:foaf="http://xmlns.com/foaf/0.1/"
            xmlns:oac="http://www.openannotation.org/ns/"
            xmlns:dcterms="http://purl.org/dc/terms/">
            <oac:Annotation rdf:about="identifier:1">
                <dcterms:creator rdf:resource="urn:creator"/>
            </oac:Annotation>
        </rdf:RDF>"""
        list(compose(self.dna.all.add(identifier="IDENTIFIER", partname="rdf", lxmlNode=parse(StringIO(xml)))))
        resultNode = self.observer.calledMethods[0].kwargs['lxmlNode']
        self.assertEqualsWS("""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <oac:Annotation xmlns:oac="http://www.openannotation.org/ns/" xmlns:dcterms="http://purl.org/dc/terms/" rdf:about="identifier:1">
        <dcterms:creator>
            <foaf:Agent xmlns:foaf="http://xmlns.com/foaf/0.1/" rdf:about="urn:creator">
                <foaf:mbox>info@example.org</foaf:mbox>
            </foaf:Agent>
        </dcterms:creator>
    </oac:Annotation>
</rdf:RDF>""", tostring(resultNode))

    def testUrnNotInSelfAndNotInStorage(self):
        self.storageObserver.returnValues['isAvailable'] = (False, False)
        xml = """<rdf:RDF
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:foaf="http://xmlns.com/foaf/0.1/"
            xmlns:oac="http://www.openannotation.org/ns/"
            xmlns:dcterms="http://purl.org/dc/terms/">
            <oac:Annotation rdf:about="identifier:1">
                <dcterms:creator rdf:resource="urn:othercreator"/>
            </oac:Annotation>
        </rdf:RDF>"""
        list(compose(self.dna.all.add(identifier="IDENTIFIER", partname="rdf", lxmlNode=parse(StringIO(xml)))))
        resultNode = self.observer.calledMethods[0].kwargs['lxmlNode']
        self.assertEqualsWS("""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <oac:Annotation xmlns:oac="http://www.openannotation.org/ns/" xmlns:dcterms="http://purl.org/dc/terms/" rdf:about="identifier:1">
        <dcterms:creator rdf:resource="urn:othercreator"/>
    </oac:Annotation>
</rdf:RDF>""", tostring(resultNode))
