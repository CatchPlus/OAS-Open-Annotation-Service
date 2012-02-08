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
        self.assertQuery('dcterms:creator = "ex:User"', 1)
        self.assertQuery('ex:HDFV', 1)
        self.assertQuery('ex:HDFI-1', 1)

    def testOaiIdentify(self):
        headers,body = getRequest(self.portNumber, "/oai", arguments=dict(verb='Identify'), parse='lxml')
        self.assertEquals("CatchPlus OpenAnnotation", xpath(body, "/oai:OAI-PMH/oai:Identify/oai:repositoryName/text()")[0])

    def testOaiListRecords(self):
        headers,body = getRequest(self.portNumber, "/oai", arguments=dict(verb='ListRecords', metadataPrefix="rdf"), parse='lxml')
        self.assertEquals(4, len(xpath(body, "/oai:OAI-PMH/oai:ListRecords/oai:record/oai:metadata")))

    def testPostAnnotation(self):
        identifier = "urn:uuid:%s" % uuid4()
        annotationBody = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
    xmlns:oac="http://www.openannotation.org/ns/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:foaf="http://xmlns.com/foaf/0.1/">

    <rdf:Description rdf:about="%(identifier)s">
        <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
        <oac:hasBody rdf:resource="ex:HDFI-2"/>
        <oac:hasTarget rdf:resource="ex:HDFV2"/>
        <dc:title>An Annotions submitted through a form</dc:title>
        <dcterms:creator rdf:resource="ex:AnotherUser"/>
        <dcterms:created>2000-02-01 12:34:56</dcterms:created>
    </rdf:Description>
</rdf:RDF>""" % locals()
        self.assertQuery('RDF.Description.title = "An Annotions submitted through a form"', 0)

        postRequest(self.portNumber, '/uploadform', urlencode(dict(annotation=annotationBody)))
        self.assertQuery('RDF.Description.title = "An Annotions submitted through a form"', 1)

    def assertNotAValidAnnotiation(self, annotationBody):
        annotationBody = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
    xmlns:oac="http://www.openannotation.org/ns/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:foaf="http://xmlns.com/foaf/0.1/">
    %s
</rdf:RDF>""" % annotationBody

        header,body = postRequest(self.portNumber, '/uploadform', urlencode(dict(annotation=annotationBody)), parse='lxml')
        self.assertEquals(['Child node 0 has no or invalid identifier'], xpath(body, '//p[@class="error"]/text()'))


    def testErrorWhenNotAnnotation(self):
        self.assertNotAValidAnnotiation("""<rdf:Description rdf:about="urn:uuid:%s">
        <dc:title>This is a wannabe annotation</dc:title>
    </rdf:Description>""" % uuid4())
        self.assertNotAValidAnnotiation("""<rdf:Description rdf:about=" ">
        <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
        <dc:title>This is a wrongfully identified annotation</dc:title>
    </rdf:Description>""")


    def testErrorWhenNotAnnotationSruUpdate(self):
        identifier = "urn:uuid:%s" % uuid4()
        sruUpdateBody = """<ucp:updateRequest xmlns:ucp="info:lc/xmlns/update-v1">
    <srw:version xmlns:srw="http://www.loc.gov/zing/srw/">1.0</srw:version>
    <ucp:action>info:srw/action/1/replace</ucp:action>
    <ucp:recordIdentifier>ex:Anno</ucp:recordIdentifier>
    <srw:record xmlns:srw="http://www.loc.gov/zing/srw/">
        <srw:recordPacking>xml</srw:recordPacking>
        <srw:recordSchema>rdf</srw:recordSchema>
        <srw:recordData><rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
    xmlns:oac="http://www.openannotation.org/ns/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:foaf="http://xmlns.com/foaf/0.1/">

    <rdf:Description rdf:about="%(identifier)s">
        <dc:title>This is a wannabe annotation</dc:title>
    </rdf:Description>
</rdf:RDF></srw:recordData></srw:record>
</ucp:updateRequest>""" % locals()

        header, body = postRequest(self.portNumber, '/update', sruUpdateBody, parse='lxml')
        self.assertEquals(['info:srw/diagnostic/12/12'], xpath(body, '/srw:updateResponse/srw:diagnostics/diag:diagnostic/diag:uri/text()'))
        
    def testReindex(self):
        header, body = getRequest(self.portNumber, '/reindex', {'session': 'newReindex'}, parse=False)
        self.assertEquals("#\n=batches: 1", body)
        header, body = getRequest(self.portNumber, '/reindex', {'session': 'newReindex'}, parse=False)
        lines = body.split('\n')
        self.assertEquals('=batches left: 0', lines[-1])
        self.assertTrue('+ex:Anno' in lines, lines)

    def testMultipleAnnotationsInOneUpdate(self):
        self.assertQuery('dc:title="Multiple Annotations In One Update"', 3)

