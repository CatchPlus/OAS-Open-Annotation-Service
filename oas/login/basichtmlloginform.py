
from meresco.core import Observable
from meresco.components.http.utils import CRLF
from cgi import parse_qs
from xml.sax.saxutils import quoteattr, escape as xmlEscape

class BasicHtmlLoginForm(Observable):
    def __init__(self, action, page, name=None):
        Observable.__init__(self, name=name)
        self._action = action
        self._page = page

    def handleRequest(self, method=None, session=None, Body=None, **kwargs):
        if method == 'POST':
            bodyArgs = parse_qs(Body, keep_blank_values=True)
            username = bodyArgs.get('username', [None])[0]
            password = bodyArgs.get('password', [None])[0]
            if self.call.validateUser(username=username, password=password):
                session['user'] = User(username)
            else:
                session['BasicHtmlLoginForm.formValues']={'username': username, 'errorMessage': 'Invalid username or password'}


        yield "HTTP/1.0 302 Found"+CRLF+"Location: %s" % self._page
        yield 2*CRLF

    def loginForm(self, session=None, **kwargs):
        formValues = session.get('BasicHtmlLoginForm.formValues', {}) if session else {}
        yield """<div id="login">\n"""
        if 'errorMessage' in formValues:
            yield '    <p class="error">%s</p>\n' % xmlEscape(formValues['errorMessage'])
        action = self._action
        usernameValue = '' if 'username' not in formValues else " value=%s" % quoteattr(formValues['username'])
        yield """    <form method="POST" action="%(action)s">
        <dl>
            <dt>Username</dt>
            <dd><input type="text" name="username"%(usernameValue)s/></dd>
            <dt>Password</dt>
            <dd><input type="password" name="password"/></dd>
            <dd class="submit"><input type="submit" value="login"/></dd>
        </dl>
    </form>
</div>""" % locals()

class User(object):
    def __init__(self, name):
        self.name = name
