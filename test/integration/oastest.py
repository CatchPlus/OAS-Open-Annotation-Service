from integrationtestcase import IntegrationTestCase
from utils import getRequest, postRequest
from lxml.etree import tostring
from uuid import uuid4
from urllib import urlencode

from oas.namespaces import xpath

class OasTest(IntegrationTestCase):

    def assertQuery(self, query, count):
        headers, body = getRequest(self.portNumber, "/sru", arguments=dict(
            version="1.1", operation="searchRetrieve", query=query), parse='lxml')
        self.assertEquals([str(count)], xpath(body, '/srw:searchRetrieveResponse/srw:numberOfRecords/text()'))

    def testGetInfo(self):
        headers, body = getRequest(self.portNumber, "/info/version", parse=False)
        self.assertTrue(body.startswith("Open Annotation Service, version: "), body)

    def testSru(self):
        self.assertQuery('RDF.Description.name = "J. Bloggs"', 1)
        self.assertQuery('Bloggs', 1)

    def testPostAnnotation(self):
        identifier = "urn:uuid:%s" % uuid4()
        annotationBody = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
    xmlns:oac="http://www.openannotation.org/ns/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:foaf="http://xmlns.com/foaf/0.1/">

    <rdf:Description about="%(identifier)s">
        <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
        <oac:hasBody rdf:resource="ex:HDFI-1"/>
        <oac:hasTarget rdf:resource="ex:HDFV"/>
        <dc:title>An Annotions submitted through a form</dc:title>
        <dcterms:creator rdf:resource="ex:User"/>
        <dcterms:created>2010-02-01 12:34:56</dcterms:created>
    </rdf:Description>
</rdf:RDF>""" % locals()
        self.assertQuery('RDF.Description.title = "An Annotions submitted through a form"', 0)

        postRequest(self.portNumber, '/uploadform', urlencode(dict(annotation=annotationBody)))
        self.assertQuery('RDF.Description.title = "An Annotions submitted through a form"', 1)
