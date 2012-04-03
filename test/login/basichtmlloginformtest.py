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

from weightless.core import be, compose
from meresco.core import Observable

from seecr.test import SeecrTestCase, CallTrace
from meresco.components.http.utils import CRLF
from urllib import urlencode

from oas.login import BasicHtmlLoginForm
from oas.login.basichtmlloginform import User

def joco(gen):
    return ''.join(compose(gen))

class BasicHtmlLoginFormTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.form = BasicHtmlLoginForm(action='/action', loginPath='/login', home='/home')

    def testLoginForm(self):
        result = joco(self.form.loginForm(session={}, path='/page/login2'))

        self.assertEqualsWS("""<div id="login">
    <form method="POST" action="/action">
    <input type="hidden" name="formUrl" value="/page/login2"/>
        <dl>
            <dt>Username</dt>
            <dd><input type="text" name="username" value=""/></dd>
            <dt>Password</dt>
            <dd><input type="password" name="password"/></dd>
            <dd class="submit"><input type="submit" value="login"/></dd>
        </dl>
    </form>
</div>""", result)

    def testRedirectOnGet(self):

        result = joco(self.form.handleRequest(path='/whatever', Client=('127.0.0.1', 3451), Method='GET'))

        header, body = result.split(CRLF*2)
        self.assertTrue('302' in header)
        self.assertTrue('Location: /home' in header, header)

    def testLoginWithPOSTsucceeds(self):
        observer = CallTrace()
        self.form.addObserver(observer)
        observer.returnValues['validateUser'] = True
        Body = urlencode(dict(username='user', password='secret'))
        session = {}

        result = joco(self.form.handleRequest(path='/login', Client=('127.0.0.1', 3451), Method='POST', Body=Body, session=session))

        self.assertEquals('user', session['user'].name)
        header, body = result.split(CRLF*2)
        self.assertTrue('302' in header)
        self.assertTrue('Location: /home' in header)

        self.assertEquals(['validateUser'], [m.name for m in observer.calledMethods])
        self.assertEquals({'username': 'user', 'password':'secret'}, observer.calledMethods[0].kwargs)

    def testLoginWithPOSTfails(self):
        observer = CallTrace()
        self.form.addObserver(observer)
        observer.returnValues['validateUser'] = False
        Body = urlencode(dict(username='user', password='wrong'))
        session = {}

        result = joco(self.form.handleRequest(path='/login', Client=('127.0.0.1', 3451), Method='POST', Body=Body, session=session))

        self.assertFalse('user' in session)
        self.assertEquals({'username':'user', 'errorMessage': 'Invalid username or password'}, session['BasicHtmlLoginForm.formValues'])
        header, body = result.split(CRLF*2)
        self.assertTrue('302' in header)
        self.assertTrue('Location: /login' in header, header)

        self.assertEquals(['validateUser'], [m.name for m in observer.calledMethods])
        self.assertEquals({'username': 'user', 'password':'wrong'}, observer.calledMethods[0].kwargs)


    def testLoginFormWithError(self):
        session = {}
        session['BasicHtmlLoginForm.formValues']={'username': '<us"er>', 'errorMessage': 'Invalid <username> or "password"'}
        result = joco(self.form.loginForm(session=session, path='/show/login'))

        self.assertEqualsWS("""<div id="login">
    <p class="error">Invalid &lt;username&gt; or "password"</p>
    <form method="POST" action="/action">
    <input type="hidden" name="formUrl" value="/show/login"/>
        <dl>
            <dt>Username</dt>
            <dd><input type="text" name="username" value='&lt;us"er&gt;'/></dd>
            <dt>Password</dt>
            <dd><input type="password" name="password"/></dd>
            <dd class="submit"><input type="submit" value="login"/></dd>
        </dl>
    </form>
</div>""", result)

    def testShowChangePasswordForm(self):
        session = {
            'user': User('username'),
            'BasicHtmlLoginForm.formValues': {'errorMessage': 'BAD BOY'},
        }
        result = joco(self.form.changePasswordForm(session=session, path='/show/changepasswordform'))

        self.assertEqualsWS("""<div id="login">
    <p class="error">BAD BOY</p>
    <form method="POST" action="/action/changepassword">
    <input type="hidden" name="formUrl" value="/show/changepasswordform"/>
    <input type="hidden" name="username" value="username"/>
        <dl>
            <dt>Old password</dt>
            <dd><input type="password" name="oldPassword"/></dd>
            <dt>New password</dt>
            <dd><input type="password" name="newPassword"/></dd>
            <dt>Retype new password</dt>
            <dd><input type="password" name="retypedPassword"/></dd>
            <dd class="submit"><input type="submit" value="change"/></dd>
        </dl>
    </form>
</div>""", result)

    def testShowChangePasswordFormErrorWithoutUser(self):
        session = {}
        result = joco(self.form.changePasswordForm(session=session, path='/show/changepasswordform'))

        self.assertEqualsWS("""<div id="login">
    <p class="error">Please login to change password.</p>
</div>""", result)

    def testChangePasswordMismatch(self):
        
        Body = urlencode(dict(username='user', oldPassword='correct', newPassword="good", retypedPassword="mismatch", formUrl='/show/changepasswordform'))
        session = {}

        result = joco(self.form.handleRequest(path='/login/changepassword', Client=('127.0.0.1', 3451), Method='POST', Body=Body, session=session))
        self.assertEquals({'username':'user', 'errorMessage': 'New passwords do not match'}, session['BasicHtmlLoginForm.formValues'])
        self.assertEqualsWS("""HTTP/1.0 302 Redirect\r\nLocation: /show/changepasswordform\r\n\r\n""", result)

    def testChangePasswordWrongOld(self):
        observer = CallTrace()
        self.form.addObserver(observer)
        observer.returnValues['validateUser'] = False
        
        Body = urlencode(dict(username='user', oldPassword='wrong', newPassword="good", retypedPassword="good", formUrl='/show/changepasswordform'))
        session = {}

        result = joco(self.form.handleRequest(path='/login/changepassword', Client=('127.0.0.1', 3451), Method='POST', Body=Body, session=session))
        self.assertEquals({'username':'user', 'errorMessage': 'Username and password do not match.'}, session['BasicHtmlLoginForm.formValues'])
        self.assertEquals("HTTP/1.0 302 Redirect\r\nLocation: /show/changepasswordform\r\n\r\n", result)

    def testChangePassword(self):
        observer = CallTrace()
        self.form.addObserver(observer)
        observer.returnValues['validateUser'] = True
        
        Body = urlencode(dict( username='user', oldPassword='correct', newPassword="good", retypedPassword="good", formUrl='/show/changepasswordform'))
        session = {}

        result = joco(self.form.handleRequest(path='/login/changepassword', Client=('127.0.0.1', 3451), Method='POST', Body=Body, session=session))
        self.assertEquals(['validateUser', 'changePassword'], [m.name for m in observer.calledMethods])
        self.assertEquals("HTTP/1.0 302 Redirect\r\nLocation: /home\r\n\r\n", result)


    def testDeleteUserNoAdmin(self):
        observer = CallTrace()
        self.form.addObserver(observer)
        result = joco(self.form.handleRequest(
            path='/login/remove', 
            Client=('127.0.0.1', 3451), 
            Method='POST', 
            Body=urlencode(dict(username='user', formUrl='/show/userlist')), 
            session={}))
        self.assertEquals([], [m.name for m in observer.calledMethods])
        self.assertEquals("HTTP/1.0 302 Redirect\r\nLocation: /show/userlist\r\n\r\n", result)

    def testDeleteUserAsAdmin(self):
        observer = CallTrace(returnValues={'hasUser': True})
        self.form.addObserver(observer)
        result = joco(self.form.handleRequest(
            path='/login/remove', 
            Client=('127.0.0.1', 3451), 
            Method='POST', 
            Body=urlencode(dict(username='user', formUrl='/show/userlist')), 
            session={'user': User('admin')}))

        self.assertEquals(['hasUser', 'removeUser'], [m.name for m in observer.calledMethods])
        self.assertEquals("HTTP/1.0 302 Redirect\r\nLocation: /show/userlist\r\n\r\n", result)
    
    def testDeleteNonExistingUser(self):
        observer = CallTrace(returnValues={'hasUser': False})
        self.form.addObserver(observer)
        session = {'user': User('admin')}
        result = joco(self.form.handleRequest(
            path='/login/remove', 
            Client=('127.0.0.1', 3451), 
            Method='POST', 
            Body=urlencode(dict(username='user', formUrl='/show/userlist')), 
            session=session))

        self.assertEquals(['hasUser'], [m.name for m in observer.calledMethods])
        self.assertEquals("HTTP/1.0 302 Redirect\r\nLocation: /show/userlist\r\n\r\n", result)
        self.assertEquals({'errorMessage': 'User "user" does not exist.'}, session['BasicHtmlLoginForm.formValues'])
