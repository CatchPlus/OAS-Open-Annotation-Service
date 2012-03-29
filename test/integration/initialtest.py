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

from integrationtestcase import IntegrationTestCase
from utils import getRequest, postRequest
from oas.utils import parseHeaders
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
        self.assertEquals(['Logged in as: admin | ', ' | ', ' | '], xpath(body, '//div[@id="loginbar"]/p/text()'))

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

