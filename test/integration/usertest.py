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

from integrationtestcase import IntegrationTestCase
from os import listdir
from utils import getRequest, postRequest
from oas.utils import parseHeaders
from lxml.etree import tostring
from urllib import urlencode
from uuid import uuid4
from oas.namespaces import xpath, getAttrib
from os.path import join

class UserTest(IntegrationTestCase):
    def testLoginPage(self):
        headers, body = getRequest(self.portNumber, "/login", parse='lxml')
        cookie = parseHeaders(headers)['Set-Cookie']
        self.assertTrue('200' in headers, headers)
        self.assertEquals(1, len(xpath(body, '/html/body/div[@id="content"]/div[@id="login"]/form/dl/dd/input[@name="username"]')))
        self.assertEquals(1, len(xpath(body, '/html/body/div[@id="content"]/div[@id="login"]/form/dl/dd/input[@type="password" and @name="password"]')))
        self.assertEquals(1, len(xpath(body, '/html/body/div[@id="content"]/div[@id="login"]/form/dl/dd/input[@type="submit"]')))
        self.assertEquals(['/login.action'], xpath(body, '/html/body/div[@id="content"]/div[@id="login"]/form/@action'))

        headers, body = postRequest(self.portNumber, '/login.action', urlencode(dict(username="doesnotexist", password="secret")), parse='lxml', additionalHeaders={'Cookie': cookie})
        self.assertTrue('302' in headers, headers)
        self.assertEquals('/login', parseHeaders(headers)['Location'], headers)

        headers, body = getRequest(self.portNumber, '/login', parse='lxml', additionalHeaders={'Cookie': cookie})
        self.assertEquals(['doesnotexist'], xpath(body, '/html/body/div[@id="content"]/div[@id="login"]/form/dl/dd/input[@name="username"]/@value'))
        self.assertEquals(['Invalid username or password'], xpath(body, '/html/body/div[@id="content"]/div[@id="login"]/p[@class="error"]/text()'))

    def testChangePasswordFormNotAllowed(self):
        headers, body = getRequest(self.portNumber, "/changepassword", parse='lxml')
        self.assertTrue('302' in headers, headers)
        self.assertEquals('/', parseHeaders(headers)['Location'], headers)

    def testApiKeyAddition(self):
        headers, body = postRequest(self.portNumber, '/login.action', urlencode(dict(username="admin", password="admin")), parse='lxml')
        cookie = parseHeaders(headers)['Set-Cookie']

        headers, body = getRequest(self.portNumber, '/admin', parse='lxml', additionalHeaders={'Cookie': cookie})
        self.assertEquals(['/apikey.action/create'], xpath(body, '//form[@name="create"]/@action'))
        self.assertEquals(['/admin'], xpath(body, '//form[@name="create"]/input[@type="hidden" and @name="formUrl"]/@value'))

        headers, body = postRequest(self.portNumber, '/apikey.action/create', urlencode(dict(formUrl='/admin', username='testuser')), parse='lxml', additionalHeaders=dict(cookie=cookie))
        self.assertTrue('302' in headers, headers)
        self.assertEquals('/admin', parseHeaders(headers)['Location'], headers)

        headers, body = getRequest(self.portNumber, '/admin', parse='lxml', additionalHeaders={'Cookie': cookie})

        self.assertEquals("",  xpath(body, '//div[@id="apiKeys"]/table/tr/form/td/input[@name="description"]/@value')[0])
        apiKey = xpath(body, '//div[@id="apiKeys"]/table/tr/form/td[@class="apiKey"]/text()')[0]
        self.assertNotEqual("", apiKey)

        headers, body = postRequest(self.portNumber, '/apikey.action/update', urlencode(dict(formUrl='/admin', apiKey=apiKey, description="Some description")), parse='lxml', additionalHeaders=dict(cookie=cookie))
        self.assertTrue('302' in headers, headers)
        self.assertEquals('/admin', parseHeaders(headers)['Location'], headers)
        headers, body = getRequest(self.portNumber, '/admin', parse='lxml', additionalHeaders={'Cookie': cookie})
        self.assertEquals("Some description",  xpath(body, '//div[@id="apiKeys"]/table/tr/form/td/input[@name="description"]/@value')[0])
        

    def testAddSameUserTwice(self):
        headers, body = postRequest(self.portNumber, '/login.action', urlencode(dict(username="admin", password="admin")), parse='lxml')
        cookie = parseHeaders(headers)['Set-Cookie']

        headers, body = postRequest(self.portNumber, '/apikey.action/create', urlencode(dict(formUrl='/admin', username='newuser')), parse='lxml', additionalHeaders=dict(cookie=cookie))
        self.assertTrue('302' in headers, headers)
        self.assertEquals('/admin', parseHeaders(headers)['Location'], headers)
        
        headers, body = postRequest(self.portNumber, '/apikey.action/create', urlencode(dict(formUrl='/admin', username='newuser')), parse='lxml', additionalHeaders=dict(cookie=cookie))
        self.assertTrue('302' in headers, headers)
        self.assertEquals('/admin', parseHeaders(headers)['Location'], headers)


    def testAddByNewUser(self):
        headers, body = postRequest(self.portNumber, '/login.action', urlencode(dict(username="admin", password="admin")), parse='lxml')
        cookie = parseHeaders(headers)['Set-Cookie']

        headers, body = postRequest(self.portNumber, '/apikey.action/create', urlencode(dict(formUrl='/admin', username='another')), parse='lxml', additionalHeaders=dict(cookie=cookie))

        headers, body = getRequest(self.portNumber, '/admin', parse='lxml', additionalHeaders={'Cookie': cookie})
        apiKey = self.apiKeyForUser(body, "another")
        self.assertTrue(len(apiKey) > 0, apiKey)

    def testAddInsertDelete(self):
        headers, body = postRequest(self.portNumber, '/login.action', urlencode(dict(username="admin", password="admin")), parse='lxml')
        cookie = parseHeaders(headers)['Set-Cookie']

        headers, body = postRequest(self.portNumber, '/apikey.action/create', urlencode(dict(formUrl='/admin', username='addDelete')), parse='lxml', additionalHeaders=dict(cookie=cookie))

        headers, body = getRequest(self.portNumber, '/admin', parse='lxml', additionalHeaders={'Cookie': cookie})
        apiKey = self.apiKeyForUser(body, "addDelete")

        annotationBody = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
    xmlns:oac="http://www.openannotation.org/ns/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:foaf="http://xmlns.com/foaf/0.1/">

    <rdf:Description rdf:about="urn:uuid:%s">
        <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
        <dc:title>To be deleted</dc:title>
    </rdf:Description>
</rdf:RDF>""" % uuid4()
        self.assertQuery('RDF.Annotation.title = "To be deleted"', 0)

        header, body = postRequest(self.portNumber, '/uploadform', urlencode(dict(annotation=annotationBody, apiKey=apiKey)), parse='lxml')
        self.assertQuery('RDF.Annotation.title = "To be deleted"', 1)

        headers, body = postRequest(self.portNumber, '/login.action/remove', urlencode(dict(formUrl='/admin', username='addDelete')), parse='lxml', additionalHeaders=dict(cookie=cookie))
        
        headers, body = getRequest(self.portNumber, '/admin', parse='lxml', additionalHeaders={'Cookie': cookie})
        apiKey = xpath(body, '//div[@id="apiKeys"]/table/form/tr[td[text()="addDelete"]]/td[@class="apiKey"]/text()')
        self.assertEquals([], apiKey)
        #### Delete user, then query again; number of results should be 0
        self.assertEquals(['addDelete.delete'], listdir(join(self.integrationTempdir, 'database', 'userdelete')))
        self.runUserDeleteService()
        self.assertQuery('RDF.Annotation.title = "To be deleted"', 0)
        self.assertEquals(['addDelete.delete'], listdir(join(self.integrationTempdir, 'database', 'userdelete')))
        self.runUserDeleteService()
        self.assertEquals([], listdir(join(self.integrationTempdir, 'database', 'userdelete')))



    def assertQuery(self, query, count):
        headers, body = getRequest(self.portNumber, "/sru", arguments=dict(
            version="1.1", operation="searchRetrieve", query=query), parse='lxml')
        recordCount = int(xpath(body, '/srw:searchRetrieveResponse/srw:numberOfRecords/text()')[0])
        if recordCount != count:
            print tostring(body)
        self.assertEquals(count, recordCount)


    def apiKeyForUser(self, body, username):
        return xpath(body, '//div[@id="apiKeys"]/table/tr[form/td[text()="%s"]]/form/td[@class="apiKey"]/text()' % username)[0]
