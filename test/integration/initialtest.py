
from integrationtestcase import IntegrationTestCase
from utils import getRequest, postRequest
from urllib import urlencode

from lxml.etree import tostring

class InitialTest(IntegrationTestCase):
    def testNoAdmin(self):
        headers, body = getRequest(self.portNumber, "/login", parse='lxml')
        parsedHeaders = dict([l.split(':',1) for l in headers.split('\r\n') if ':' in l])
        cookie = parsedHeaders['Set-Cookie'].strip()
        print cookie

        self.assertEquals(1, len(body.xpath("/html/body/div/div[@id='login']/form/input[@name='username' and @value='admin']")))
        self.assertEquals(1, len(body.xpath("/html/body/div/div[@id='login']/form/dl/dd/input[@name='oldPassword']")))

        postBody = urlencode(dict(username='admin', newPassword="password", retypedPassword="password"))

        headers, body = postRequest(self.portNumber, "/login/changepassword", postBody, additionalHeaders={'Cookie': cookie}, parse='lxml')
        print 50*"="
        print headers
        print 50*"="


        headers, body = postRequest(self.portNumber, '/login', urlencode(dict(username="admin", password="password")), additionalHeaders={'Cookie': cookie}, parse='lxml')
        print headers, body

