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

from lxml.etree import parse, tostring

from meresco.oai import OaiDownloadProcessor
from oas.namespaces import xpath

from socket import socket
from xml.sax.saxutils import escape as xmlEscape

class SruUpload(object):
    def __init__(self, hostname='localhost', portnumber=8000, path='/update', apiKey=''):
        self.hostname = hostname
        self.portnumber = portnumber
        self.path = path
        self.apiKey = apiKey

    def add(self, identifier, lxmlNode):
        for record in xpath(lxmlNode, "/oai:record/oai:metadata/*"):
            # construct the body, insert the identifier and supplied XML.
            body = """<ucp:updateRequest xmlns:ucp="info:lc/xmlns/update-v1">
            <srw:version xmlns:srw="http://www.loc.gov/zing/srw/">1.0</srw:version>
            <ucp:action>info:srw/action/1/replace</ucp:action>
            <ucp:recordIdentifier>IGNORED</ucp:recordIdentifier>
            <srw:record xmlns:srw="http://www.loc.gov/zing/srw/">
                <srw:recordPacking>xml</srw:recordPacking>
                <srw:recordSchema>rdf</srw:recordSchema>
                <srw:recordData>%s</srw:recordData>
            </srw:record>
        </ucp:updateRequest>""" % tostring(record)
            self._send(body)
        yield

    def delete(self, identifier):
        body = """<ucp:updateRequest xmlns:ucp="info:lc/xmlns/update-v1">
            <srw:version xmlns:srw="http://www.loc.gov/zing/srw/">1.0</srw:version>
            <ucp:action>info:srw/action/1/delete</ucp:action>
            <ucp:recordIdentifier>%s</ucp:recordIdentifier>
        </ucp:updateRequest>""" % xmlEscape(identifier)
        self._send(body)
        yield

    def _socket(self):
        return socket()

    def _send(self, body):
         # Connect to the server and send the update request.
        s = self._socket()
        s.connect((self.hostname, self.portnumber))
        s.send("POST %s HTTP/1.0\r\n" % self.path)
        s.send("Content-Type: text/xml\r\n")
        s.send("Content-Length: %s\r\n" % len(body))
        s.send("Authorization: %s\r\n" % self.apiKey)
        s.send("\r\n")
        s.sendall(body)

        # Receive the answer from the server and print it to stdout.
        response = s.recv(1024)
        while True:
            part = s.recv(1024)
            if part == "":
                break
            response += part
        s.close()
        return response


