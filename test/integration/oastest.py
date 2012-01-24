from integrationtestcase import IntegrationTestCase
from utils import getRequest
from socket import socket
from lxml.etree import tostring

class OasTest(IntegrationTestCase):

    def testGetInfo(self):
        headers, body = getRequest(self.portNumber, "/info/version", parse=False)
        self.assertTrue(body.startswith("Open Annotation Service, version: "), body)

    def testSru(self):
        headers, body = getRequest(self.portNumber, "/sru", arguments=dict(version="1.1", operation="searchRetrieve", query='RDF.Description exact "ex:Anno"'), parse='lxml')
        print tostring(body, pretty_print=True)
