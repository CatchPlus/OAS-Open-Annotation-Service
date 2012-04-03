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

from string import ascii_letters, digits
from random import choice

from meresco.components.http.utils import CRLF, redirectHttp, okHtml
from meresco.core import Observable
from cgi import parse_qs
from os.path import isfile
from simplejson import load as jsonRead, dump as jsonWrite
from os import rename

class ApiKey(Observable):
    def __init__(self, databaseFile, name=None):
        Observable.__init__(self, name=name)
        self._apiKeys = {}
        self._filename = databaseFile
        if not isfile(self._filename):
            self._makePersistent()
        else:
            self._apiKeys = jsonRead(open(self._filename))
        self._actions = {
            'create': self.handleCreate, 
            'update': self.handleUpdate
        }

    def handleRequest(self, path, Method, **kwargs):
        prefix, action = path.rsplit('/', 1)
        if Method == 'POST' and action in self._actions: 
            yield self._actions[action](**kwargs)
            return
        yield redirectHttp % '/'

    def handleUpdate(self, session, Body, **kwargs):
        bodyArgs = parse_qs(Body, keep_blank_values=True)
        apiKey = bodyArgs['apiKey'][0]
        description = bodyArgs['description'][0]
        formUrl = bodyArgs['formUrl'][0]
        session['ApiKey.formValues'] = {}
        try:
            if 'user' in session and session['user'].isAdmin():
                self._apiKeys[apiKey]['description'] = description 
                self._makePersistent()
            else:
                raise ValueError('No admin privileges.')
        except ValueError, e:
            session['ApiKey.formValues']['errorMessage'] = str(e)

        yield redirectHttp % formUrl
    
    def handleCreate(self, session, Body, **kwargs):
        bodyArgs = parse_qs(Body, keep_blank_values=True)
        username = bodyArgs['username'][0]
        formUrl = bodyArgs['formUrl'][0]
        session['ApiKey.formValues'] = {}
        try:
            if 'user' in session and session['user'].isAdmin():
                self.call.addUser(username=username, password=self.generateKey(8))
            else:       
                raise ValueError('No admin privileges.')
        except ValueError, e:
            session['ApiKey.formValues']['errorMessage'] = str(e)
        else:
            newApiKey = self.generateKey(16)
            self._apiKeys[newApiKey] = {'username': username}
            self._makePersistent()

        yield redirectHttp % formUrl

    def listApiKeysAndData(self):
        return self._apiKeys.items()

    def getForApiKey(self, apiKey):
        return self._apiKeys.get(apiKey, None)

    def removeUser(self, username):
        for k,v in self._apiKeys.items():
            if v.get('username', None) == username:
                del self._apiKeys[k]
                self._makePersistent()
                break

    def _makePersistent(self):
        tmpFilename = self._filename + ".tmp"
        jsonWrite(self._apiKeys, open(tmpFilename, 'w'))
        rename(tmpFilename, self._filename)
    
    @staticmethod
    def generateKey(length=16):
        return ''.join(choice(ascii_letters + digits) for i in xrange(length))

