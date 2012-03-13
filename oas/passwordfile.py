from simplejson import load as jsonRead, dump as jsonWrite
from os.path import isfile
from os import rename, chmod
from hashlib import md5
from stat import S_IRUSR, S_IWUSR
from re import compile as reCompile
USER_RW = S_IRUSR | S_IWUSR

def md5Hash(data):
    return md5(data+salt).hexdigest()

def saltedPasswordHasher(salt):
    return lambda data: md5Hash(data + salt)

def simplePasswordTest(passwd):
    return bool(passwd.strip())

VALIDNAME=reCompile(r'^[\w@\-\.]+$')
def usernameTest(username):
    return bool(VALIDNAME.match(username))

class PasswordFile(object):

    def __init__(self,
            filename,
            hashPassword,
            passwordTest=simplePasswordTest,
            usernameTest=usernameTest):
        self._filename = filename
        self._users = jsonRead(open(filename)) if isfile(filename) else {}
        self._hashPassword = hashPassword
        self._passwordTest = passwordTest
        self._usernameTest = usernameTest

    def addUser(self, username, password):
        if not self._usernameTest(username):
            raise ValueError('Invalid username.')
        if username in self._users:
            raise ValueError('User already exists.')
        self._setUser(username=username, password=password)

    def removeUser(self, username):
        del self._users[username]
        self._makePersistent()

    def validPassword(self, username, password):
        valid = False
        try:
            valid = self._users[username] == self._hashPassword(password)
        except:
            pass
        return valid

    def changePassword(self, username, oldPassword, newPassword):
        if not self.validPassword(username=username, password=oldPassword):
            raise ValueError('Username and password do not match, password NOT changed.')
        self._setUser(username=username, password=newPassword)

    def listUsernames(self):
        return self._users.keys()

    def hasUser(self, username):
        return username in self._users

    def _makePersistent(self):
        tmpFilename = self._filename + ".tmp"
        jsonWrite(self._users, open(tmpFilename, 'w'))
        rename(tmpFilename, self._filename)
        chmod(self._filename, USER_RW)
        
    def _setUser(self, username, password):
        if not self._passwordTest(password):
            raise ValueError('Invalid password.')
        self._users[username] = self._hashPassword(password)
        self._makePersistent()

