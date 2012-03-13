from seecr.test import SeecrTestCase
from simplejson import dump as jsonSave

from os.path import join
from hashlib import md5
from uuid import uuid4
from oas import PasswordFile

poorHash = lambda pwd: ''.join(reversed(pwd))

class PasswordFileTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.filename=join(self.tempdir, 'passwd')
        self.pwd = PasswordFile(filename=self.filename, hashPassword=poorHash)

    def testReadPasswordFile(self):
        passwdHash = poorHash('password')
        userlist = {'John':passwdHash}
        jsonSave(userlist, open(self.filename, 'w'))
        pf = PasswordFile(filename=self.filename, hashPassword=poorHash)
        self.assertTrue(pf.validPassword('John', 'password'))

    def testAddUser(self):
        self.pwd.addUser(username='John', password='password')
        # reopen file.
        pf = PasswordFile(filename=self.filename, hashPassword=poorHash)
        self.assertTrue(pf.validPassword('John', 'password'))

    def testValidPassword(self):
        self.pwd.addUser(username='John', password='password')
        self.assertFalse(self.pwd.validPassword(username='John', password=''))
        self.assertFalse(self.pwd.validPassword(username='John', password=' '))
        self.assertFalse(self.pwd.validPassword(username='John', password='abc'))
        self.assertTrue(self.pwd.validPassword(username='John', password='password'))
        self.assertFalse(self.pwd.validPassword(username='John', password='password '))

        self.assertFalse(self.pwd.validPassword(username='', password=''))
        self.assertFalse(self.pwd.validPassword(username='Piet', password=''))

    def testChangePassword(self):
        self.pwd.addUser(username='John', password='password')
        self.pwd.changePassword(username='John', oldPassword='password', newPassword='newpasswd')
        self.assertTrue(self.pwd.validPassword(username='John', password='newpasswd'))
