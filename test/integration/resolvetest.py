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

from lxml.etree import tostring
from uuid import uuid4
from urllib import urlencode
from os.path import join, isdir
from os import makedirs

from oas.namespaces import xpath
from subprocess import Popen

from seecr.test.utils import getRequest, postRequest
from seecr.test.integrationtestcase import IntegrationTestCase

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
    xmlns:oa="http://www.w3.org/ns/openannotation/core/"
    xmlns:dc="http://purl.org/dc/elements/1.1/">

    <oa:Annotation rdf:about="http://oas.dev.seecr.nl/resolve/%s">
        <dc:title>This is an annotation</dc:title>
        <oa:annotatedBy rdf:resource="%s"/>
    </oa:Annotation>

</rdf:RDF></srw:recordData></srw:record>
</ucp:updateRequest>""" % (identifier, resourceUrl)
        header, body = postRequest(self.portNumber, '/update', sruUpdateBody, parse='lxml', additionalHeaders={'Authorization':self.apiKeyForTestUser})
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

        self.runResolveService()
        self.assertEquals(before-1, self.countUnresolved())
    
