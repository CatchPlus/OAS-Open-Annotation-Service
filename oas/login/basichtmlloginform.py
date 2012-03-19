from meresco.core import Observable
from meresco.components.http.utils import CRLF, redirectHttp, okHtml
from cgi import parse_qs
from xml.sax.saxutils import quoteattr, escape as xmlEscape
from os.path import join, dirname

class BasicHtmlLoginForm(Observable):
    def __init__(self, page, name=None):
        Observable.__init__(self, name=name)
        self._page = page

    def handleRequest(self, path, **kwargs):
        if path.endswith('/changepassword'):
            return self.handleChangePassword(path=path, **kwargs)
        return self.handleLogin(path=path, **kwargs)

    def handleLogin(self, path=None, Method=None, session=None, Body=None, **kwargs):
        if Method == 'POST':
            bodyArgs = parse_qs(Body, keep_blank_values=True)
            username = bodyArgs.get('username', [None])[0]
            password = bodyArgs.get('password', [None])[0]
            if self.call.validateUser(username=username, password=password):
                session['user'] = User(username)
                yield redirectHttp % self._page
            else:
                session['BasicHtmlLoginForm.formValues']={'username': username, 'errorMessage': 'Invalid username or password'}
                yield redirectHttp % path

        elif Method == 'GET':
            yield okHtml
            yield self.loginForm(session=session, path=path, **kwargs)

    def loginForm(self, session=None, path=None, **kwargs):
        formValues = session.get('BasicHtmlLoginForm.formValues', {}) if session else {}
        yield """<div id="login">\n"""
        if 'errorMessage' in formValues:
            yield '    <p class="error">%s</p>\n' % xmlEscape(formValues['errorMessage'])
        usernameValue = '' if 'username' not in formValues else " value=%s" % quoteattr(formValues['username'])
        yield """    <form method="POST" action="%(path)s">
        <dl>
            <dt>Username</dt>
            <dd><input type="text" name="username"%(usernameValue)s/></dd>
            <dt>Password</dt>
            <dd><input type="password" name="password"/></dd>
            <dd class="submit"><input type="submit" value="login"/></dd>
        </dl>
    </form>
</div>""" % locals()

    def handleChangePassword(self, Method=None, session=None, Body=None,
            path=None, **kwargs):
        if Method == 'GET':
            yield self.changePasswordForm("", "", session=session, path=path)
            return
        bodyArgs = parse_qs(Body, keep_blank_values=True) if Body else {}
        username = bodyArgs.get('username', [None])[0]
        oldPassword = bodyArgs.get('oldPassword', [None])[0]
        newPassword = bodyArgs.get('newPassword', [None])[0]
        retypedPassword = bodyArgs.get('retypedPassword', [None])[0]

        targetUrl = 'changepassword'
        if newPassword != retypedPassword:
            session['BasicHtmlLoginForm.formValues']={'username': username, 'errorMessage': 'New passwords do not match'}
        else:
            if not self.call.validateUser(username=username, password=oldPassword):
                session['BasicHtmlLoginForm.formValues']={'username': username, 'errorMessage': 'Username and password do not match.'}
            else:
                self.call.changePassword(username, oldPassword, newPassword)
                targetUrl = dirname(path)
        
        yield redirectHttp % targetUrl

    def changePasswordForm(self, username, oldPassword, session=None, path=None):
        formValues = session.get('BasicHtmlLoginForm.formValues', {}) if session else {}
        yield """<div id="login">\n"""
        if 'errorMessage' in formValues:
            yield '    <p class="error">%s</p>\n' % xmlEscape(formValues['errorMessage'])
        yield """<form method="POST" action="%s">
        <input type="hidden" name="username" value=%s/>
        <dl>
            <dt>Old password</dt>
            <dd><input type="password" name="oldPassword" value=%s/></dd>
            <dt>New password</dt>
            <dd><input type="password" name="newPassword"/></dd>
            <dt>Retype new password</dt>
            <dd><input type="password" name="retypedPassword"/></dd>
            <dd class="submit"><input type="submit" value="change"/></dd>
        </dl>
    </form>
</div>""" % (path, quoteattr(username), quoteattr(oldPassword))




class User(object):
    def __init__(self, name):
        self.name = name
