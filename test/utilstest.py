from oas.utils import identifierFromXml

from seecr.test import SeecrTestCase
from lxml.etree import parse
from StringIO import StringIO

class UtilsTest(SeecrTestCase):
    def testIdentifierFromLxmlNode(self):
        self.assertEquals(None, identifierFromXml(parse(StringIO("<xml/>"))))
        self.assertEquals("ex:Anno", identifierFromXml(parse(StringIO("""
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
            <rdf:Description rdf:about="ex:Anno">
                <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
            </rdf:Description>
        </rdf:RDF>"""))))
        self.assertEquals("ex:Anno", identifierFromXml(parse(StringIO("""
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:oas="http://www.openannotation.org/ns/">
            <oas:Annotation rdf:about="ex:Anno"/>
        </rdf:RDF>"""))))



