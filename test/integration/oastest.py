## begin license ##
# 
# "Open Annotation Service" enables exchange, storage and search of
# heterogeneous annotations using a uniform format (Open Annotation format) and
# a uniform web service interface. 
# 
# Copyright (C) 2012 Meertens Instituut (KNAW) http://meertens.knaw.nl
# Copyright (C) 2012 Seecr (Seek You Too B.V.) http://seecr.nl
# 
# This file is part of "Open Annotation Service"
# 
# "Open Annotation Service" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# "Open Annotation Service" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with "Open Annotation Service"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 
## end license ##

from os import listdir
from oas.utils import parseHeaders
from lxml.etree import tostring
from uuid import uuid4
from urllib import urlencode
from urlparse import urlsplit

from oas.namespaces import xpath, getAttrib

from seecr.test.integrationtestcase import IntegrationTestCase
from seecr.test.utils import getRequest, postRequest

class OasTest(IntegrationTestCase):

    def assertQuery(self, query, count):
        headers, body = getRequest(self.portNumber, "/sru", arguments=dict(
            version="1.1", operation="searchRetrieve", query=query), parse='lxml')
        recordCount = int(xpath(body, '/srw:searchRetrieveResponse/srw:numberOfRecords/text()')[0])
        if recordCount != count:
            print tostring(body)
        self.assertEquals(count, recordCount)

    def assertNotAValidAnnotiation(self, errorText, annotationBody):
        annotationBody = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
    xmlns:oac="http://www.openannotation.org/ns/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:foaf="http://xmlns.com/foaf/0.1/">
    %s
</rdf:RDF>""" % annotationBody

        header,body = postRequest(self.portNumber, '/uploadform', urlencode(dict(annotation=annotationBody, apiKey=self.apiKeyForPostUser)), parse='lxml')
        self.assertEquals([errorText], xpath(body, '//p[@class="upload-error"]/text()'))
        self.assertEquals([], xpath(body, '//p[@class="upload-success"]/text()'))
    
    def testGetInfo(self):
        headers, body = getRequest(self.portNumber, "/info/version", parse=False)
        self.assertTrue(body.startswith("Open Annotation Service, version: "), body)

    def testSru(self):
        self.assertQuery('RDF.Annotation.title = "Annotation of the Hubble Deep Field Image"', 1)
        self.assertQuery('RDF.Annotation.title = hubble', 1)
        self.assertQuery('Hubble', 1)
        self.assertQuery('dc:title = hubble', 1)
        self.assertQuery('dcterms:created = "2010-02-02"', 1)
        self.assertQuery('dcterms:created = 2010', 3)
        self.assertQuery('dcterms:creator = "ex:User"', 1)
        self.assertQuery('ex:HDFV', 1)
        self.assertQuery('ex:HDFI-1', 1)
        self.assertQuery('mailto:unique@info.org', 1)
        self.assertQuery('oac:hasTarget = "http://example.org/target/for/test"', 1)
        self.assertQuery('RDF.Annotation.creator.Agent.name = "billy butcher"', 2)
        self.assertQuery('api.user = testuser', 7)
        self.assertQuery('api.user = anothertestuser', 8)

    def testQueryOnRdfType(self):
        self.assertQuery('rdf:type = "http://www.openannotation.org/ns/Annotation"', 16)

    def testOaiIdentify(self):
        headers,body = getRequest(self.portNumber, "/oai", arguments=dict(verb='Identify'), parse='lxml')
        self.assertEquals("CatchPlus OpenAnnotation", xpath(body, "/oai:OAI-PMH/oai:Identify/oai:repositoryName/text()")[0])

    def testOaiListRecords(self):
        headers,body = getRequest(self.portNumber, "/oai", arguments=dict(verb='ListRecords', metadataPrefix="rdf"), parse='lxml')
        self.assertEquals(15, len(xpath(body, "/oai:OAI-PMH/oai:ListRecords/oai:record/oai:metadata")))

    def testOaiListRecordsWithUserAsSet(self):
        headers,body = getRequest(self.portNumber, "/oai", arguments=dict(verb='ListRecords', metadataPrefix="rdf", set='testUser'), parse='lxml')
        self.assertEquals(7, len(xpath(body, "/oai:OAI-PMH/oai:ListRecords/oai:record/oai:metadata")))

        headers,body = getRequest(self.portNumber, "/oai", arguments=dict(verb='ListRecords', metadataPrefix="rdf", set='anotherTestUser'), parse='lxml')
        self.assertEquals(8, len(xpath(body, "/oai:OAI-PMH/oai:ListRecords/oai:record/oai:metadata")))

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
        self.assertQuery('RDF.Annotation.title = "An Annotions submitted through a form"', 0)

        header, body = postRequest(self.portNumber, '/uploadform', urlencode(dict(annotation=annotationBody, apiKey=self.apiKeyForPostUser)), parse='lxml')
        self.assertQuery('RDF.Annotation.title = "An Annotions submitted through a form"', 1)
        textarea = xpath(body, '//textarea[@name="annotation"]/text()')
        apiKey = xpath(body, '//input[@name="apiKey"]/@value')[0]
        message = xpath(body, '//p[@class="upload-success"]/text()')[0]
        self.assertEquals(self.apiKeyForPostUser, apiKey)
        self.assertEquals([], textarea)
        self.assertTrue('success' in message, message)


    def testErrorWhenBadApiKey(self):
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

        header, body = postRequest(self.portNumber, '/uploadform', urlencode(dict(annotation=annotationBody, apiKey="WRONGKEY")), parse='lxml')
        error =  xpath(body, '//p[@class="upload-error"]/text()')[0]
        self.assertEquals('No valid API Key given', error)

    def testErrorWhenNotAnnotation(self):
        self.assertNotAValidAnnotiation('No annotations found.', """<rdf:Description rdf:about="urn:uuid:%s">
        <dc:title>This is a wannabe annotation</dc:title>
    </rdf:Description>""" % uuid4())
        self.assertNotAValidAnnotiation('Invalid identifier', """<rdf:Description rdf:about=" ">
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

        header, body = postRequest(self.portNumber, '/update', sruUpdateBody, parse='lxml', additionalHeaders={'Authorization':self.apiKeyForTestUser})
        self.assertEquals(['info:srw/diagnostic/12/12'], xpath(body, '/srw:updateResponse/srw:diagnostics/diag:diagnostic/diag:uri/text()'))
        
    def testReindex(self):
        header, body = getRequest(self.portNumber, '/reindex', {'session': 'newReindex'}, parse=False)
        self.assertEquals("#\n=batches: 1", body)
        header, body = getRequest(self.portNumber, '/reindex', {'session': 'newReindex'}, parse=False)
        lines = body.split('\n')
        self.assertEquals('=batches left: 0', lines[-1])
        self.assertTrue('+http:%2F%2Flocalhost:'+str(self.portNumber)+'%2Fresolve%2Furn%253Aex%253AAnno' in lines, lines)

    def testMultipleAnnotationsInOneUpdate(self):
        self.assertQuery('dc:title="Multiple Annotations In One Update"', 3)

    def testUrnResolvable(self):
        header, body = getRequest(self.portNumber, '/resolve/urn%3Aex%3AAnno', {}, parse='lxml')
        self.assertEquals(["http://localhost:%s/resolve/urn%%3Aex%%3AAnno" % self.portNumber], xpath(body, '/rdf:RDF/oac:Annotation/@rdf:about'))

        header, body = getRequest(self.portNumber, '/resolve/urn%3Anr%3A0%3Fb', {}, parse='lxml')
        self.assertEquals(["http://localhost:%s/resolve/urn%%3Anr%%3A0%%3Fb" % self.portNumber], xpath(body, '/rdf:RDF/oac:Annotation/@rdf:about'))

    def testResolveConstrainedTargets(self):
        header, body = getRequest(self.portNumber, '/resolve/urn%3Aid%3Act%3A1', {}, parse='lxml')
        self.assertEquals(["http://localhost:%s/resolve/urn%%3Aid%%3Act%%3A1" % self.portNumber], xpath(body, '/rdf:RDF/oac:ConstrainedTarget/@rdf:about'))

    def testDocumentationPage(self):
        header, body = getRequest(self.portNumber, '/documentation', {}, parse='lxml')
        nodes = xpath(body, '/html/body/div/div[@id="filelist"]/ul/li/a')
        expected = sorted(listdir(self.publicDocumentationPath))
        self.assertTrue(len(expected) > 1)
        self.assertEquals(expected, [node.text for node in nodes])
        self.assertTrue(all(['target' in node.attrib for node in nodes]))
        self.assertEquals(['/public/%s' % f for f in expected], [node.attrib['href'] for node in nodes])

    def testDocumentationLink(self):
        filename = listdir(self.publicDocumentationPath)[0]
        header, body = getRequest(self.portNumber, '/public/%s' % filename, {}, parse=False)
        self.assertTrue(header.startswith('HTTP/1.0 200 OK'), header)

    def testOacBodiesStored(self):
        headers, body = getRequest(self.portNumber, "/sru", arguments=dict(
            version="1.1", operation="searchRetrieve", query="IamUnique42"), parse='lxml')

        oacBody = xpath(body, "/srw:searchRetrieveResponse/srw:records/srw:record/srw:recordData/rdf:RDF/oac:Annotation/oac:hasBody/oac:Body")[0]

        about = getAttrib(oacBody, "rdf:about")
        _,_,path,_,_ = urlsplit(about)
        headers, body = getRequest(self.portNumber, path, parse=False)
        self.assertTrue('200' in headers, headers)
        lines = body.split('\n')
        self.assertEquals('<?xml version="1.0" encoding="utf-8"?>', lines[0])
        self.assertEquals('<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">', lines[1])
        self.assertEquals('</rdf:RDF>', lines[-1])

