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

from seecr.test import SeecrTestCase, CallTrace

from oas.namespaces import namespaces
from oas.harvester import SruUpload, SruUploadException
from lxml.etree import parse
from StringIO import StringIO
from testutil import lico

class SruUploadTest(SeecrTestCase):
    def testAdd(self):
        sruUpload = SruUpload(apiKey="apiKey")
        socket = CallTrace()

        answers = ["""HTTP/1.0 200 OK\r\n\r\n""", SUCCESS_SRU_UPLOAD_RESPONSE, ""]
        def recv(size):
            return answers.pop(0)
            
        socket.methods['recv'] = recv
        sruUpload._socket = lambda: socket

        lico(sruUpload.add(identifier="IDENTIFIER", lxmlNode=parse(StringIO("""<oai:record xmlns:oai="%(oai)s"><oai:metadata><xml/></oai:metadata></oai:record>""" % namespaces))))
        self.assertEquals([
            "connect(('localhost', 8000))", 
            "send('POST /update HTTP/1.0\r\n')", 
            "send('Content-Type: text/xml\r\n')", 
            "send('Content-Length: 609\r\n')", 
            "send('Authorization: apiKey\r\n')", 
            "send('\r\n')", 
            'sendall(\'<ucp:updateRequest xmlns:ucp="info:lc/xmlns/update-v1">\n            <srw:version xmlns:srw="http://www.loc.gov/zing/srw/">1.0</srw:version>\n            <ucp:action>info:srw/action/1/replace</ucp:action>\n            <ucp:recordIdentifier>IGNORED</ucp:recordIdentifier>\n            <srw:record xmlns:srw="http://www.loc.gov/zing/srw/">\n                <srw:recordPacking>xml</srw:recordPacking>\n                <srw:recordSchema>rdf</srw:recordSchema>\n                <srw:recordData><xml xmlns:oai="http://www.openarchives.org/OAI/2.0/"/></srw:recordData>\n            </srw:record>\n        </ucp:updateRequest>\')', 
            'recv(1024)', 
            'recv(1024)', 
            'recv(1024)', 
            'close()'], [str(m) for m in socket.calledMethods])
        
    def testDelete(self):
        sruUpload = SruUpload(apiKey="apiKey")
        socket = CallTrace()

        answers = ["""HTTP/1.0 200 OK\r\n\r\n""", SUCCESS_SRU_UPLOAD_RESPONSE, ""]
        def recv(size):
            return answers.pop(0)
            
        socket.methods['recv'] = recv
        sruUpload._socket = lambda: socket

        lico(sruUpload.delete(identifier="IDENTIFIER"))
        self.assertEquals([
            "connect(('localhost', 8000))", 
            "send('POST /update HTTP/1.0\r\n')", 
            "send('Content-Type: text/xml\r\n')", 
            "send('Content-Length: 298\r\n')", 
            "send('Authorization: apiKey\r\n')", 
            "send('\r\n')", 
            'sendall(\'<ucp:updateRequest xmlns:ucp="info:lc/xmlns/update-v1">\n            <srw:version xmlns:srw="http://www.loc.gov/zing/srw/">1.0</srw:version>\n            <ucp:action>info:srw/action/1/delete</ucp:action>\n            <ucp:recordIdentifier>IDENTIFIER</ucp:recordIdentifier>\n        </ucp:updateRequest>\')', 
            'recv(1024)', 
            'recv(1024)', 
            'recv(1024)', 
            'close()'], [str(m) for m in socket.calledMethods])

    def testFailedUpload(self):
        sruUpload = SruUpload(apiKey="apiKey")
        sruUpload._send = lambda data: "HTTP/1.0 200 Ok\r\n\r\n" + FAILED_SRU_UPLOAD_RESPONSE
        self.assertRaises(SruUploadException, lambda: lico(sruUpload.add(identifier="IDENTIFIER", lxmlNode=parse(StringIO("""<oai:record xmlns:oai="%(oai)s"><oai:metadata><xml/></oai:metadata></oai:record>""" % namespaces)))))


SUCCESS_SRU_UPLOAD_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<srw:updateResponse xmlns:srw="http://www.loc.gov/zing/srw/" xmlns:ucp="info:lc/xmlns/update-v1">
    <srw:version>1.0</srw:version>
    <ucp:operationStatus>success</ucp:operationStatus>
</srw:updateResponse>"""

FAILED_SRU_UPLOAD_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<srw:updateResponse xmlns:srw="http://www.loc.gov/zing/srw/" xmlns:ucp="info:lc/xmlns/update-v1">
    <srw:version>1.0</srw:version>
    <ucp:operationStatus>fail</ucp:operationStatus>
<srw:diagnostics>
    <diag:diagnostic xmlns:diag="http://www.loc.gov/zing/srw/diagnostic/">
        <diag:uri>diag:uri</diag:uri>
        <diag:details>diag:details</diag:details>
        <diag:message>diag:message</diag:message>
    </diag:diagnostic>
</srw:diagnostics>
</srw:updateResponse>"""



