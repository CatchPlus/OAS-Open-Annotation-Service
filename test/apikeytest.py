## begin license ##
# 
# "Open Annotation Service" enables exchange, storage and search of 
# heterogeneous annotations using a uniform format (Open Annotation format) and
# a uniform web service interface. 
# 
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
        self.apiKey = ApiKey(databaseFile=join(self.tempdir, 'db'))
        self.pwd = createPasswordFile(join(self.tempdir, 'pwd'), salt="13241")
        self.apiKey.addObserver(self.pwd)

    def testCreateKey(self):
        session = {
            'user': User('admin'),
        }
        Body = urlencode(dict(username='user', description="A User", formUrl='/apikeyform'))
        self.assertEquals(['admin'], self.pwd.listUsernames())

        result = ''.join(compose(self.apiKey.handleRequest(session=session, Body=Body, path='/action/create', Method='POST')))
        headers, body = result.split(CRLF*2)

        self.assertTrue(' 302 ' in headers, headers)
        self.assertEquals('/apikeyform', parseHeaders(headers)['Location'])
        self.assertEquals(['admin', 'user'], sorted(self.pwd.listUsernames()))

        aList = self.apiKey.listApiKeysAndData()
        self.assertEquals(1, len(aList))
        apiKey, userdata = aList[0]
        self.assertEquals('user', userdata['username'])
        self.assertTrue(16, len(apiKey))

        result = ''.join(compose(self.apiKey.handleRequest(session=session, Body=Body, path='/action/create', Method='POST')))
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

        result = ''.join(compose(self.apiKey.handleRequest(session=session, Body=Body, path='/action/create', Method='POST')))
        headers, body = result.split(CRLF*2)

        self.assertTrue(' 302 ' in headers, headers)
        self.assertEquals('/apikeyform', parseHeaders(headers)['Location'])
        self.assertEquals([], list(self.apiKey.listApiKeysAndData()))
        self.assertEquals({'errorMessage': 'No admin privileges.'}, session['ApiKey.formValues'])

    def testChangeDescription(self):
        session = {
            'user': User('admin'),
        }
        Body = urlencode(dict(username='user', formUrl='/apikeyform'))

        result = ''.join(compose(self.apiKey.handleRequest(session=session, Body=Body, path='/action/create', Method='POST')))
        headers, body = result.split(CRLF*2)
        self.assertEquals(['admin', 'user'], sorted(self.pwd.listUsernames()))

        aList = self.apiKey.listApiKeysAndData()
        apiKey = aList[0][0]

        result = ''.join(compose(self.apiKey.handleRequest(session=session, Body=urlencode(dict(apiKey=apiKey, formUrl="/apikeyform", description="This is the description")), path="/action/update", Method="POST")))
        aList = self.apiKey.listApiKeysAndData()
        self.assertEquals(1, len(aList))
        apiKey, data = aList[0]
        self.assertEquals('This is the description', data['description'])
       
    def testGetForApiKey(self):
        self.assertEquals(None, self.apiKey.getForApiKey('nonexistent'))

        result = ''.join(compose(self.apiKey.handleRequest(
            session={ 'user': User('admin')},
            Body=urlencode(dict(username='user', formUrl='/apikeyform')), 
            path='/action/create', 
            Method='POST')))
        [(apiKey, userdata)] = self.apiKey.listApiKeysAndData()

        dataByApiKey = self.apiKey.getForApiKey(apiKey)
        self.assertEquals(userdata, dataByApiKey)

