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

    def testChangePasswordWithBadOldpassword(self):
        self.pwd.addUser(username='John', password='password')
        self.assertRaises(ValueError, self.pwd.changePassword, username='John', oldPassword='wrong', newPassword='newpasswd')
        self.assertTrue(self.pwd.validPassword(username='John', password='password'))
        self.assertFalse(self.pwd.validPassword(username='John', password='newpasswd'))

    def testChangePasswordWithBadUsername(self):
        self.pwd.addUser(username='John', password='password')
        self.assertRaises(ValueError, self.pwd.changePassword, username='Harry', oldPassword='wrong', newPassword='newpasswd')

    def testPasswordTest(self):
        self.assertTrue(self.pwd._passwordTest('something'))
        self.assertTrue(self.pwd._passwordTest('s om et hing'))
        self.assertTrue(self.pwd._passwordTest('ng'))
        self.assertTrue(self.pwd._passwordTest('SOMETHING'))
        self.assertTrue(self.pwd._passwordTest('123513'))
        self.assertFalse(self.pwd._passwordTest(''))
        self.assertFalse(self.pwd._passwordTest(' '))
        self.assertFalse(self.pwd._passwordTest('\t'))
        self.assertFalse(self.pwd._passwordTest('\t\n'))

    def testAddUserWithBadPassword(self):
        self.assertRaises(ValueError, self.pwd.addUser, username='Harry', password='')

    def testAddUserWithBadname(self):
        self.assertRaises(ValueError, self.pwd.addUser, username='', password='good')

    def testChangePasswordWithBadPassword(self):
        self.pwd.addUser(username='Harry', password='good')
        self.assertRaises(ValueError, self.pwd.changePassword, username='Harry', oldPassword='good', newPassword='')

    def testUsernameTest(self):
        self.assertTrue(self.pwd._usernameTest('name'))
        self.assertTrue(self.pwd._usernameTest('name@domain.com'))
        self.assertTrue(self.pwd._usernameTest('name-1235'))
        self.assertFalse(self.pwd._usernameTest('name\t-1235'))
        self.assertFalse(self.pwd._usernameTest(''))
        self.assertFalse(self.pwd._usernameTest(' '))
        self.assertFalse(self.pwd._usernameTest(' name'))

    def testAddExistingUser(self):
        self.pwd.addUser(username='John', password='password')
        self.assertRaises(ValueError, self.pwd.addUser, username='John', password='good')

    def testAddMultipleUsers(self):
        self.pwd.addUser(username='John', password='password')
        self.pwd.addUser(username='Johnny', password='password2')
        self.pwd.addUser(username='Johann', password='password3')
        self.assertTrue(self.pwd.validPassword('John', 'password'))
        self.assertTrue(self.pwd.validPassword('Johnny', 'password2'))
        self.assertTrue(self.pwd.validPassword('Johann', 'password3'))

    def testRemoveUser(self):
        self.pwd.addUser(username='John', password='password')
        self.assertTrue(self.pwd.validPassword('John', 'password'))
        self.pwd.removeUser(username='John')
        self.assertFalse(self.pwd.validPassword('John', 'password'))



