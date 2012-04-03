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

from meresco.core import Observable
from meresco.components.http.utils import CRLF, redirectHttp, okHtml
from cgi import parse_qs
from xml.sax.saxutils import quoteattr, escape as xmlEscape
from os.path import join, dirname

class BasicHtmlLoginForm(Observable):
    def __init__(self, action, loginPath, home="/", name=None):
        Observable.__init__(self, name=name)
        self._action = action
        self._loginPath = loginPath
        self._home = home
        self._actions = {
            'changepassword': self.handleChangePassword,
            'remove': self.handleRemove,
        }


    def handleRequest(self, Method, path, **kwargs):
        if Method == 'GET':
            yield redirectHttp % self._home
            return
        
        ignored, action = path.rsplit('/', 1)
        if action in self._actions:
            yield self._actions[action](path=path, **kwargs)
            return

        yield self.handleLogin(path=path, **kwargs)

    def handleLogin(self, session=None, Body=None, **kwargs):
        bodyArgs = parse_qs(Body, keep_blank_values=True)
        username = bodyArgs.get('username', [None])[0]
        password = bodyArgs.get('password', [None])[0]
        if self.call.validateUser(username=username, password=password):
            session['user'] = User(username)
            yield redirectHttp % self._home
        else:
            session['BasicHtmlLoginForm.formValues'] = {'username': username, 'errorMessage': 'Invalid username or password'}
            yield redirectHttp % self._loginPath

    def loginForm(self, session, path, **kwargs):
        formValues = session.get('BasicHtmlLoginForm.formValues', {}) if session else {}
        yield """<div id="login">\n"""
        if 'errorMessage' in formValues:
            yield '    <p class="error">%s</p>\n' % xmlEscape(formValues['errorMessage'])
        username = quoteattr(formValues.get('username', ''))
        action = quoteattr(self._action)
        formUrl = quoteattr(path)
        yield """    <form method="POST" action=%(action)s>
        <input type="hidden" name="formUrl" value=%(formUrl)s/>
        <dl>
            <dt>Username</dt>
            <dd><input type="text" name="username" value=%(username)s/></dd>
            <dt>Password</dt>
            <dd><input type="password" name="password"/></dd>
            <dd class="submit"><input type="submit" value="login"/></dd>
        </dl>
    </form>
</div>""" % locals()

    def handleChangePassword(self, session, Body, **kwargs):
        bodyArgs = parse_qs(Body, keep_blank_values=True) if Body else {}
        username = bodyArgs.get('username', [None])[0]
        oldPassword = bodyArgs.get('oldPassword', [None])[0]
        newPassword = bodyArgs.get('newPassword', [None])[0]
        retypedPassword = bodyArgs.get('retypedPassword', [None])[0]
        formUrl = bodyArgs.get('formUrl', [self._home])[0]

        targetUrl = formUrl
        if newPassword != retypedPassword:
            session['BasicHtmlLoginForm.formValues']={'username': username, 'errorMessage': 'New passwords do not match'}
        else:
            if not self.call.validateUser(username=username, password=oldPassword):
                session['BasicHtmlLoginForm.formValues']={'username': username, 'errorMessage': 'Username and password do not match.'}
            else:
                self.call.changePassword(username, oldPassword, newPassword)
                targetUrl = self._home
        
        yield redirectHttp % targetUrl

    def changePasswordForm(self, session, path, **kwargs):
        formValues = session.get('BasicHtmlLoginForm.formValues', {}) if session else {}
        yield """<div id="login">\n"""
        if not 'user' in session:
            yield '<p class="error">Please login to change password.</p>\n</div>'
            return
        if 'errorMessage' in formValues:
            yield '    <p class="error">%s</p>\n' % xmlEscape(formValues['errorMessage'])
        yield """<form method="POST" action=%s>
        <input type="hidden" name="formUrl" value=%s/>
        <input type="hidden" name="username" value=%s/>
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
</div>""" % (quoteattr(join(self._action, 'changepassword')), quoteattr(path), quoteattr(session['user'].name))

    def handleRemove(self, session, Body, **kwargs):
        bodyArgs = parse_qs(Body, keep_blank_values=True) if Body else {}
        formUrl = bodyArgs.get('formUrl', [self._home])[0]
        if 'user' in session and session['user'].isAdmin():
            username = bodyArgs.get('username', [None])[0]
            if self.call.hasUser(username):
                self.do.removeUser(username)
            else:
                session['BasicHtmlLoginForm.formValues'] = {
                    'errorMessage': 'User "%s" does not exist.' % username
                }

        yield redirectHttp % formUrl

class User(object):
    def __init__(self, name):
        self.name = name

    def isAdmin(self):
        return self.name == "admin"


