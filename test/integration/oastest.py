from integrationtestcase import IntegrationTestCase
from utils import getRequest
from lxml.etree import tostring

from oas.namespaces import xpath

class OasTest(IntegrationTestCase):

    def testGetInfo(self):
        headers, body = getRequest(self.portNumber, "/info/version", parse=False)
        self.assertTrue(body.startswith("Open Annotation Service, version: "), body)

    def testSru(self):
        headers, body = getRequest(self.portNumber, "/sru", arguments=dict(version="1.1", operation="searchRetrieve", query='RDF.Description.name = "J. Bloggs"'), parse='lxml')
        self.assertEquals(["1"], xpath(body, '/srw:searchRetrieveResponse/srw:numberOfRecords/text()'))

