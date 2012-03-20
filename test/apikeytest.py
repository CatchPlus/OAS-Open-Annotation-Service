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

    def testCreateKey(self):
        a = ApiKey(databaseFile=join(self.tempdir, 'db'))
        pwd = createPasswordFile(join(self.tempdir, 'pwd'), salt="13241")
        a.addObserver(pwd)
        session = {
            'user': User('admin'),
        }
        Body = urlencode(dict(username='user', formUrl='/apikeyform'))
        self.assertEquals(['admin'], pwd.listUsernames())

        result = ''.join(compose(a.handleRequest(session=session, Body=Body)))
        headers, body = result.split(CRLF*2)

        self.assertTrue(' 302 ' in headers, headers)
        self.assertEquals('/apikeyform', parseHeaders(headers)['Location'])
        self.assertEquals(['admin', 'user'], sorted(pwd.listUsernames()))

        aList = list(a.listUsernameAndApiKeys())
        self.assertEquals(1, len(aList))
        self.assertEquals('user', aList[0][0])
        self.assertTrue(16, len(aList[0][1]))

