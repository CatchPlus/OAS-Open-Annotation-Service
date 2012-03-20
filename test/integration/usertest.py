from integrationtestcase import IntegrationTestCase
from os import listdir
from utils import getRequest, postRequest
from oas.utils import parseHeaders
from lxml.etree import tostring
from urllib import urlencode
from oas.namespaces import xpath, getAttrib

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
        self.assertEquals(['/apikey.action/create'], xpath(body, '//form/@action'))
        self.assertEquals(['/admin'], xpath(body, '//form/input[@type="hidden" and @name="formUrl"]/@value'))

        headers, body = postRequest(self.portNumber, '/apikey.action/create', urlencode(dict(formUrl='/admin', username='newuser')), parse='lxml', additionalHeaders=dict(cookie=cookie))
        self.assertTrue('302' in headers, headers)
        self.assertEquals('/admin', parseHeaders(headers)['Location'], headers)

        headers, body = getRequest(self.portNumber, '/admin', parse='lxml', additionalHeaders={'Cookie': cookie})

    def testAddSameUserTwice(self):
        headers, body = postRequest(self.portNumber, '/login.action', urlencode(dict(username="admin", password="admin")), parse='lxml')
        cookie = parseHeaders(headers)['Set-Cookie']

        headers, body = postRequest(self.portNumber, '/apikey.action/create', urlencode(dict(formUrl='/admin', username='newuser')), parse='lxml', additionalHeaders=dict(cookie=cookie))
        self.assertTrue('302' in headers, headers)
        self.assertEquals('/admin', parseHeaders(headers)['Location'], headers)
        
        headers, body = postRequest(self.portNumber, '/apikey.action/create', urlencode(dict(formUrl='/admin', username='newuser')), parse='lxml', additionalHeaders=dict(cookie=cookie))
        self.assertTrue('302' in headers, headers)
        self.assertEquals('/admin', parseHeaders(headers)['Location'], headers)
