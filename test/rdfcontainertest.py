from seecr.test import SeecrTestCase
from lxml.etree import parse
from StringIO import StringIO

from oas import RdfContainer
from oas.namespaces import getAttrib

class RdfContainerTest(SeecrTestCase):

    def testOne(self):
        XML = """<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:oac="http://www.openannotation.org/ns/">
    <rdf:Description rdf:about="urn:nr:1"/>
    <rdf:Description rdf:about="urn:nr:2"/>
    <rdf:Description rdf:about="urn:nr:3"/>
    <rdf:Description rdf:about="urn:nr:4"/>
</rdf:RDF>"""

        container = RdfContainer(parse(StringIO(XML)))
        result = container.resolve('urn:nr:3')
        self.assertEquals('urn:nr:3', getAttrib(result, "rdf:about"))
