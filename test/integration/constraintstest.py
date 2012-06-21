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
from urllib import urlencode
from uuid import uuid4
from oas.namespaces import xpath, getAttrib
from os.path import join

from seecr.test.integrationtestcase import IntegrationTestCase
from seecr.test.utils import getRequest, postRequest

class ConstraintsTest(IntegrationTestCase):
    def testOne(self):
        query='oac:hasTarget="http://catchplus.nl/annotation/Canvas1"'
        headers, body = getRequest(self.portNumber, "/sru", arguments=dict(
            version="1.2", operation="searchRetrieve", query=query), parse='lxml')
        print tostring(body)
        self.assertEquals(["4"], xpath(body, '//srw:numberOfRecords/text()'))
        print tostring(body)
        self.assertEquals([
                'http://localhost:%s/resolve/urn%%3Aid%%3Aia%%3A1' % self.portNumber, 
                'http://localhost:%s/resolve/urn%%3Aid%%3Ata%%3A0' % self.portNumber, 
                'http://localhost:%s/resolve/urn%%3Aid%%3Ata%%3A1' % self.portNumber, 
                'http://localhost:%s/resolve/urn%%3Aid%%3Ata%%3A2' % self.portNumber
            ], xpath(body, '//srw:records/srw:record/srw:recordIdentifier/text()'))
