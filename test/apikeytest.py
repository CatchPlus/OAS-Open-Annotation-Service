from seecr.test import SeecrTestCase, CallTrace

from weightless.core import be, compose
from meresco.core import Observable, Transparent
from meresco.components.http.utils import CRLF

from urllib import urlencode
from os.path import join
from oas.login.basichtmlloginform import User
from oas.utils import parseHeaders
from oas.apikey import ApiKey
from oas.login import createPasswordFile

class ApiKeyTest(SeecrTestCase):

    def setUp(self):
        SeecrTestCase.setUp(self)
        self.apikey = ApiKey(databaseFile=join(self.tempdir, 'db'))
        self.pwd = createPasswordFile(join(self.tempdir, 'pwd'), salt="13241")
        self.apikey.addObserver(self.pwd)

    def testCreateKey(self):
        session = {
            'user': User('admin'),
        }
        Body = urlencode(dict(username='user', description="A User", formUrl='/apikeyform'))
        self.assertEquals(['admin'], self.pwd.listUsernames())

        result = ''.join(compose(self.apikey.handleRequest(session=session, Body=Body, path='/action/create', Method='POST')))
        headers, body = result.split(CRLF*2)

        self.assertTrue(' 302 ' in headers, headers)
        self.assertEquals('/apikeyform', parseHeaders(headers)['Location'])
        self.assertEquals(['admin', 'user'], sorted(self.pwd.listUsernames()))

        aList = self.apikey.listApiKeysAndData()
        self.assertEquals(1, len(aList))
        apikey, userdata = aList[0]
        self.assertEquals('user', userdata['username'])
        self.assertTrue(16, len(apikey))

        result = ''.join(compose(self.apikey.handleRequest(session=session, Body=Body, path='/action/create', Method='POST')))
        headers, body = result.split(CRLF*2)

        self.assertTrue(' 302 ' in headers, headers)
        self.assertEquals('/apikeyform', parseHeaders(headers)['Location'])
        self.assertEquals(['admin', 'user'], sorted(self.pwd.listUsernames()))
        self.assertEquals({'errorMessage': 'User already exists.'}, session['ApiKey.formValues'])

        b = ApiKey(databaseFile=join(self.tempdir, 'db'))
        self.assertEquals(aList, list(b.listApiKeysAndData()))

    def testWithoutAdminUserLoggedIn(self):
        session = {
            'user': User('nobody'),
        }
        Body = urlencode(dict(username='user', formUrl='/apikeyform'))

        result = ''.join(compose(self.apikey.handleRequest(session=session, Body=Body, path='/action/create', Method='POST')))
        headers, body = result.split(CRLF*2)

        self.assertTrue(' 302 ' in headers, headers)
        self.assertEquals('/apikeyform', parseHeaders(headers)['Location'])
        self.assertEquals([], list(self.apikey.listApiKeysAndData()))
        self.assertEquals({'errorMessage': 'No admin privileges.'}, session['ApiKey.formValues'])

    def testChangeDescription(self):
        session = {
            'user': User('admin'),
        }
        Body = urlencode(dict(username='user', formUrl='/apikeyform'))

        result = ''.join(compose(self.apikey.handleRequest(session=session, Body=Body, path='/action/create', Method='POST')))
        headers, body = result.split(CRLF*2)
        self.assertEquals(['admin', 'user'], sorted(self.pwd.listUsernames()))

        aList = self.apikey.listApiKeysAndData()
        apikey = aList[0][0]

        result = ''.join(compose(self.apikey.handleRequest(session=session, Body=urlencode(dict(apikey=apikey, formUrl="/apikeyform", description="This is the description")), path="/action/update", Method="POST")))
        aList = self.apikey.listApiKeysAndData()
        self.assertEquals(1, len(aList))
        apikey, data = aList[0]
        self.assertEquals('This is the description', data['description'])
        
