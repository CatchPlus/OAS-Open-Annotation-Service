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

from os.path import isdir, join, splitext, isfile
from os import makedirs, listdir, remove
from oas.namespaces import xpath
from meresco.components import readConfig
from urllib import urlencode
from urllib2 import urlopen
from lxml.etree import parse
from xml.sax.saxutils import escape as escapeXml
from socket import socket

class UserDelete(object):
    def __init__(self, dataPath):
        self._dataPath = dataPath
        isdir(dataPath) or makedirs(dataPath)

    def removeUser(self, username):
        open(join(self._dataPath, '%s.delete' % username), 'w').close()

class UserDeleteProcess(object):
    def __init__(self, config):
        self._sruUrl = "http://%(hostName)s:%(portNumber)s/sru" % config
        self._sruUpdateHostAndPort = ("localhost", int(config['portNumber']))
        self._userDeleteDataPath = join(config['databasePath'], 'userdelete')

    def process(self):
        usersToBeDeleted = (splitext(f)[0] for f in listdir(self._userDeleteDataPath) if f.endswith('.delete') and isfile(join(self._userDeleteDataPath,f)))
        for username in usersToBeDeleted:
            ready = self._deleteUser(username)
            if ready:
                remove(join(self._userDeleteDataPath, '%s.delete' % username))

    def _deleteUser(self, username):
        recordIds = self._listRecordIds(username)
        for recordId in recordIds:
            self._deleteRecord(recordId)
        return len(recordIds) == 0

    def _listRecordIds(self, username):
        query = urlencode(dict(
            operation='searchRetrieve',
            version='1.2',
            query='api.user="%s"' % username
        ))
        result = parse(urlopen('%s?%s' % (self._sruUrl, query)))
        return xpath(result, '//srw:records/srw:record/srw:recordIdentifier/text()')

    def _deleteRecord(self, recordId):
        print 'DELETING', recordId
        body = """<ucp:updateRequest xmlns:ucp="info:lc/xmlns/update-v1">
    <srw:version xmlns:srw="http://www.loc.gov/zing/srw/">1.0</srw:version>
    <ucp:action>info:srw/action/1/delete</ucp:action>
    <ucp:recordIdentifier>%s</ucp:recordIdentifier>
</ucp:updateRequest>""" % escapeXml(recordId)
        s = socket()
        s.connect(self._sruUpdateHostAndPort)
        s.send("POST /internal/update HTTP/1.0\r\n")
        s.send("Content-Type: text/xml\r\n")
        s.send("Content-Length: %s\r\n" % len(body))
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
        if 'success' in response:
            return
        raise ValueError(response)
            

def startServer(configFile):
    config = readConfig(configFile)
    processor = UserDeleteProcess(config)
    processor.process()
