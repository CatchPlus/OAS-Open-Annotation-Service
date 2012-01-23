from integrationtestcase import IntegrationTestCase
from utils import getRequest
from socket import socket

class OasTest(IntegrationTestCase):

    def testGetInfo(self):
        headers, body = getRequest(self.portNumber, "/info/version", parse=False)
        self.assertTrue(body.startswith("Open Annotation Service, version: "), body)
