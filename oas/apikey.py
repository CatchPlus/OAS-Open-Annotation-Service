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
        self._apikeys = {}
        self._filename = databaseFile
        if not isfile(self._filename):
            self._makePersistent()
        else:
            self._apikey2user = jsonRead(open(self._filename))

    def handleRequest(self, session, Body, **kwargs):
        bodyArgs = parse_qs(Body, keep_blank_values=True)
        username = bodyArgs['username'][0]
        formUrl = bodyArgs['formUrl'][0]
        self.call.addUser(username=username, password=self.generateKey(8))
        newApikey = self.generateKey(16)
        self._apikeys[newApikey] = {'username': username}
        self._makePersistent()

        yield redirectHttp % formUrl

    def listUsernameAndApiKeys(self):
        for apikey, data in self._apikeys.items():
            yield data['username'], apikey

    def _makePersistent(self):
        tmpFilename = self._filename + ".tmp"
        jsonWrite(self._apikeys, open(tmpFilename, 'w'))
        rename(tmpFilename, self._filename)


    @staticmethod
    def generateKey(length=16):
        return ''.join(choice(ascii_letters + digits) for i in xrange(length))

