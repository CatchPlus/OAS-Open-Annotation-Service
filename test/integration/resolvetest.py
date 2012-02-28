from integrationtestcase import IntegrationTestCase
from utils import getRequest, postRequest
from lxml.etree import tostring
from uuid import uuid4
from urllib import urlencode
from os.path import join, isdir
from os import makedirs

from oas.namespaces import xpath
from oas.resolve.server import startServer

class ResolveTest(IntegrationTestCase):
    
    def assertQuery(self, query, count):
        headers, body = getRequest(self.portNumber, "/sru", arguments=dict(
            version="1.1", operation="searchRetrieve", query=query), parse='lxml')
        self.assertEquals([str(count)], xpath(body, '/srw:searchRetrieveResponse/srw:numberOfRecords/text()'))

    def countUnresolved(self):
        headers, body = getRequest(self.portNumber, "/sru", arguments=dict(
            version="1.1", operation="searchRetrieve", query='__resolved__ = "no"'), parse='lxml')
        return int(xpath(body, '/srw:searchRetrieveResponse/srw:numberOfRecords/text()')[0])

    def testResolveAgent(self):
        identifier = "urn:uuid:%s" % uuid4()
        resourceUrl = "http://localhost:%s/rdf/testResolve" % self.httpPortNumber
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

    <oac:Annotation rdf:about="http://oas.dev.seecr.nl/resolve/%s">
        <dc:title>This is an annotation</dc:title>
        <dcterms:creator rdf:resource="%s"/>
    </oac:Annotation>

</rdf:RDF></srw:recordData></srw:record>
</ucp:updateRequest>""" % (identifier, resourceUrl)
        header, body = postRequest(self.portNumber, '/update', sruUpdateBody, parse='lxml')
        self.assertEquals("success", xpath(body, "/srw:updateResponse/ucp:operationStatus/text()")[0])

        before = self.countUnresolved()

        destDir = join(self.httpDataDir, "rdf")
        if not isdir(destDir):
            makedirs(destDir)
        open(join(destDir, "testResolve"), "w").write("""<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:dc="http://purl.org/dc/elements/1.1/">
    <rdf:Description rdf:about="%s">
        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Agent"/>
        <foaf:name>Pietje Puk</foaf:name>
        <dc:title>Gewillig slachtoffer</dc:title>    
    </rdf:Description>
</rdf:RDF>""" % resourceUrl)

        startServer(self.configFile)
        self.assertEquals(before-1, self.countUnresolved())
    
    def testResolveBody(self):
        identifier = "urn:uuid:%s" % uuid4()
        resourceUrl = "http://localhost:%s/rdf/testResolve" % self.httpPortNumber
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
    xmlns:dcterms="http://purl.org/dc/terms/">

    <oac:Annotation rdf:about="http://oas.dev.seecr.nl/resolve/%s">
        <dc:title>This is an annotation</dc:title>
        <oac:hasBody rdf:resource="%s"/>
    </oac:Annotation>

</rdf:RDF></srw:recordData></srw:record>
</ucp:updateRequest>""" % (identifier, resourceUrl)
        header, body = postRequest(self.portNumber, '/update', sruUpdateBody, parse='lxml')
        self.assertEquals("success", xpath(body, "/srw:updateResponse/ucp:operationStatus/text()")[0])

        before = self.countUnresolved()

        destDir = join(self.httpDataDir, "rdf")
        if not isdir(destDir):
            makedirs(destDir)
        open(join(destDir, "testResolve"), "w").write("""<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dc="http://purl.org/dc/elements/1.1/">
    xmlns:oac="http://www.openannotation.org/ns/"
    <rdf:Description rdf:about="%s">
        <rdf:type rdf:resource="http://www.openannotation.org/ns/Body"/>
        <dc:description>This is the body</dc:description>
    </rdf:Description>
</rdf:RDF>""" % resourceUrl)
        
        startServer(self.configFile)
        self.assertEquals(before-1, self.countUnresolved())
