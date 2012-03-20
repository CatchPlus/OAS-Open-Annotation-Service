from oas.utils import identifierFromXml, generateApiKey

from seecr.test import SeecrTestCase
from lxml.etree import parse
from StringIO import StringIO
from re import compile as reCompile

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

    def testGenerateApiKey(self):
        keyRe = reCompile(r'^[a-zA-Z0-9]{16}$')
        for i in xrange(100):
            aKey = generateApiKey()
            self.assertEquals(16, len(aKey))
            self.assertTrue(keyRe.match(aKey))




