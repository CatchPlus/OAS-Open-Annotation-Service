
from integrationtestcase import IntegrationTestCase
from utils import getRequest, postRequest, parseHeaders
from urllib import urlencode

from lxml.etree import tostring
from oas.namespaces import xpath

class InitialTest(IntegrationTestCase):
    def testAdmin(self):
        headers, body = getRequest(self.portNumber, "/login", parse='lxml')
        cookie = parseHeaders(headers)['Set-Cookie']

        headers, body = postRequest(self.portNumber, '/login.action', urlencode(dict(username="admin", password="admin", formUrl='/login')), parse='lxml', additionalHeaders={'Cookie': cookie})
        self.assertTrue('302' in headers, headers)
        self.assertEquals('/', parseHeaders(headers)['Location'])
        
        headers, body = getRequest(self.portNumber, "/index", parse='lxml', additionalHeaders={'Cookie': cookie})
        self.assertEquals(['Logged in as: admin'], xpath(body, '//div[@id="loginbar"]/p/text()'))

        headers, body = getRequest(self.portNumber, "/changepassword", parse='lxml', additionalHeaders={'Cookie': cookie})
        self.assertEquals(['admin'], xpath(body, '/html/body/div[@id="content"]/div[@id="login"]/form/input[@type="hidden" and @name="username"]/@value'), tostring(body))
        self.assertEquals(['oldPassword', 'newPassword', 'retypedPassword'], xpath(body, '/html/body/div[@id="content"]/div[@id="login"]/form/dl/dd/input[@type="password"]/@name'), tostring(body))
        self.assertEquals(['/login.action/changepassword'], xpath(body, '/html/body/div[@id="content"]/div[@id="login"]/form/@action'))

        headers, body = postRequest(self.portNumber, '/login.action/changepassword', urlencode(dict(username="admin", oldPassword="admin", newPassword="password", retypedPassword="password", formUrl="/changepassword")), parse='lxml', additionalHeaders={'Cookie': cookie})
        self.assertTrue('302' in headers, headers)
        self.assertEquals('/', parseHeaders(headers)['Location'])

        # Test new password
        headers, body = getRequest(self.portNumber, "/login", parse='lxml')
        newcookie = parseHeaders(headers)['Set-Cookie']

        headers, body = postRequest(self.portNumber, '/login.action', urlencode(dict(username="admin", password="admin", formUrl='/login')), parse='lxml', additionalHeaders={'Cookie': newcookie})
        self.assertTrue('302' in headers, headers)
        self.assertEquals('/login', parseHeaders(headers)['Location'])

        headers, body = postRequest(self.portNumber, '/login.action', urlencode(dict(username="admin", password="password", formUrl='/login')), parse='lxml', additionalHeaders={'Cookie': newcookie})
        self.assertTrue('302' in headers, headers)
        self.assertEquals('/', parseHeaders(headers)['Location'])

