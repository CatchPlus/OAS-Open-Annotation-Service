from simplejson import load as jsonRead, dump as jsonWrite
from os.path import isfile
from os import rename, chmod
from hashlib import md5
from stat import S_IRUSR, S_IWUSR
USER_RW = S_IRUSR | S_IWUSR

def md5Hash(data, salt='salt'):
    return md5(data+salt).hexdigest()

class PasswordFile(object):

    def __init__(self, filename, hashPassword=md5Hash):
        self._filename = filename
        self._users = jsonRead(open(filename)) if isfile(filename) else {}
        self._hashPassword = hashPassword

    def addUser(self, username, password):
        self._users[username] = self._hashPassword(password)
        self._makePersistent()

    def validPassword(self, username, password):
        valid = False
        try:
            valid = self._users[username] == self._hashPassword(password)
        except:
            pass
        return valid

    def changePassword(self, username, oldPassword, newPassword):
        self._users[username] = self._hashPassword(newPassword)
        self._makePersistent()

    def _makePersistent(self):
        tmpFilename = self._filename + ".tmp"
        jsonWrite(self._users, open(tmpFilename, 'w'))
        rename(tmpFilename, self._filename)
        chmod(self._filename, USER_RW)
        
