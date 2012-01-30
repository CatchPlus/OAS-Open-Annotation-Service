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
        self.assertQuery('RDF.Description.title = "Annotation of the Hubble Deep Field Image"', 1)
        self.assertQuery('RDF.Description.title = hubble', 1)
        self.assertQuery('Hubble', 1)
        self.assertQuery('dc:title = hubble', 1)
        self.assertQuery('dcterms:created = "2010-02-02"', 1)
        self.assertQuery('dcterms:created = 2010', 1)



    def testOaiIdentify(self):
        headers,body = getRequest(self.portNumber, "/oai", arguments=dict(verb='Identify'), parse='lxml')
        self.assertEquals("CatchPlus OpenAnnotation", xpath(body, "/oai:OAI-PMH/oai:Identify/oai:repositoryName/text()")[0])

    def testOaiListRecords(self):
        headers,body = getRequest(self.portNumber, "/oai", arguments=dict(verb='ListRecords', metadataPrefix="rdf"), parse='lxml')
        self.assertEquals(1, len(xpath(body, "/oai:OAI-PMH/oai:ListRecords/oai:record/oai:metadata")))

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
        <dcterms:created>2000-02-01 12:34:56</dcterms:created>
    </rdf:Description>
</rdf:RDF>""" % locals()
        self.assertQuery('RDF.Description.title = "An Annotions submitted through a form"', 0)

        postRequest(self.portNumber, '/uploadform', urlencode(dict(annotation=annotationBody)))
        self.assertQuery('RDF.Description.title = "An Annotions submitted through a form"', 1)


