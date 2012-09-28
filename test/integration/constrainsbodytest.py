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
from oas.namespaces import xpath, getAttrib

from seecr.test.integrationtestcase import IntegrationTestCase
from seecr.test.utils import getRequest, postRequest

class ConstrainsBodyTest(IntegrationTestCase):
    def assertQuery(self, query, count):
        headers, body = getRequest(self.portNumber, "/sru", arguments=dict(
            version="1.1", operation="searchRetrieve", query=query), parse='lxml')
        recordCount = int(xpath(body, '/srw:searchRetrieveResponse/srw:numberOfRecords/text()')[0])
        if recordCount != count:
            print tostring(body)
        self.assertEquals(count, recordCount)

    def testOne(self):

        uuid = "urn:uuid:8ab4ee28-651a-45bd-9206-59763f9e5487"
        query = uuid 
        headers, body = getRequest(self.portNumber, "/sru", arguments=dict(
            version="1.1", 
            operation="searchRetrieve", 
            query=query), parse='lxml')

        self.assertEquals(2, len(xpath(body, '//oac:constrains/oac:Body/cnt:chars')))

