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

class InlineTest(IntegrationTestCase):
    def testEntityAnnotation(self):
        query = "urn:id:ea:1"
        headers, body = getRequest(self.portNumber, "/sru", arguments=dict(
            version="1.2", operation="searchRetrieve", query=query), parse='lxml')

        ea_1 = xpath(body, "/srw:searchRetrieveResponse/srw:records/srw:record/srw:recordData/rdf:RDF")[0]

        self.assertEquals(["urn:id:ea:1"], xpath(ea_1, 'oac:Annotation/dc:identifier/text()'))
        self.assertEquals(["location"], xpath(ea_1, 'oac:Annotation/oac:hasBody/cnt:ContentAsText[@rdf:about="urn:id:ib:1"]/cnt:chars/text()'))

        self.assertEquals(['Dit is een beschrijving van Den Haag. En dit is een tweede zin.'], xpath(ea_1, 'oac:Annotation/oac:hasTarget/oac:ConstrainedTarget[dc:identifier/text()="urn:id:ct:3"]/oac:constrains/cnt:ContentAsText[@rdf:about="urn:id:ib:0"]/cnt:chars/text()'))
        self.assertEquals(['Dit is een beschrijving van Den Haag. En dit is een tweede zin.'], xpath(ea_1, 'oac:Annotation/oac:hasTarget/oac:ConstrainedTarget[dc:identifier/text()="urn:id:ct:4"]/oac:constrains/cnt:ContentAsText[@rdf:about="urn:id:ib:0"]/cnt:chars/text()'))

        self.assertEquals(["UTF-8"], xpath(ea_1, 'oac:Annotation/oac:hasTarget/oac:ConstrainedTarget[dc:identifier/text()="urn:id:ct:3"]/oac:constrainedBy/oac:Constraint[@rdf:about="urn:id:c:5"]/cnt:characterEncoding/text()'))

    def testTextAnnotations_ta0(self):
        query = "urn:id:ta:0"
        headers, body = getRequest(self.portNumber, "/sru", arguments=dict(
            version="1.2", operation="searchRetrieve", query=query), parse='lxml')

        ta_0 = xpath(body, "/srw:searchRetrieveResponse/srw:records/srw:record/srw:recordData/rdf:RDF")[0]

        self.assertEquals(['Dit is een beschrijving van Den Haag. En dit is een tweede zin.'], xpath(ta_0, 'oac:Annotation/oac:hasBody/cnt:ContentAsText[@rdf:about="urn:id:ib:0"]/cnt:chars/text()'))
        self.assertEquals(['Canvas for imageScan1.jpg'], xpath(ta_0, 'oac:Annotation/oac:hasTarget/dms:Canvas[@rdf:about="http://catchplus.nl/annotation/Canvas1"]/dc:title/text()'))
        
    def testTextAnnotations_ta1(self):
        query = "urn:id:ta:1"
        headers, body = getRequest(self.portNumber, "/sru", arguments=dict(
            version="1.2", operation="searchRetrieve", query=query), parse='lxml')

        ta_1 = xpath(body, "/srw:searchRetrieveResponse/srw:records/srw:record/srw:recordData/rdf:RDF")[0]

        self.assertEquals(['Dit is een beschrijving van Den Haag. En dit is een tweede zin.'], xpath(ta_1, 'oac:Annotation/oac:hasBody/oac:ConstrainedBody[@rdf:about="urn:id:cb:1"]/oac:constrains/cnt:ContentAsText[@rdf:about="urn:id:ib:0"]/cnt:chars/text()'))
        self.assertEquals(['Canvas for imageScan1.jpg'], xpath(ta_1, 'oac:Annotation/oac:hasTarget/oac:ConstrainedTarget[dc:identifier/text()="urn:id:ct:1"]/oac:constrains/dms:Canvas[@rdf:about="http://catchplus.nl/annotation/Canvas1"]/dc:title/text()'))
        
    def testTextAnnotations_ta2(self):
        query = "urn:id:ta:2"
        headers, body = getRequest(self.portNumber, "/sru", arguments=dict(
            version="1.2", operation="searchRetrieve", query=query), parse='lxml')

        ta_2 = xpath(body, "/srw:searchRetrieveResponse/srw:records/srw:record/srw:recordData/rdf:RDF")[0]

        self.assertEquals(['Dit is een beschrijving van Den Haag. En dit is een tweede zin.'], xpath(ta_2, 'oac:Annotation/oac:hasBody/oac:ConstrainedBody[@rdf:about="urn:id:cb:2"]/oac:constrains/cnt:ContentAsText[@rdf:about="urn:id:ib:0"]/cnt:chars/text()'))
        self.assertEquals(['Canvas for imageScan1.jpg'], xpath(ta_2, 'oac:Annotation/oac:hasTarget/oac:ConstrainedTarget[dc:identifier/text()="urn:id:ct:2"]/oac:constrains/dms:Canvas[@rdf:about="http://catchplus.nl/annotation/Canvas1"]/dc:title/text()'))
        
    def testImageAnnotations_ia1(self):
        query = "urn:id:ia:1"
        headers, body = getRequest(self.portNumber, "/sru", arguments=dict(
            version="1.2", operation="searchRetrieve", query=query), parse='lxml')

        ia_1 = xpath(body, "/srw:searchRetrieveResponse/srw:records/srw:record/srw:recordData/rdf:RDF")[0]

        self.assertEquals(['http://catchplus.nl/annotation/imageScan1.jpg'], xpath(ia_1, 'oac:Annotation/oac:hasBody/@rdf:resource'))
        self.assertEquals(['Canvas for imageScan1.jpg'], xpath(ia_1, 'oac:Annotation/oac:hasTarget/dms:Canvas[@rdf:about="http://catchplus.nl/annotation/Canvas1"]/dc:title/text()'))
        
