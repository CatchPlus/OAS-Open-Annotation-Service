
from meresco.core import Observable
from meresco.components.http.utils import CRLF

class BasicHtmlLoginForm(Observable):
    def __init__(self, action, page, name=None):
        Observable.__init__(self, name=name)
        self._action = action
        self._page = page

    def handleRequest(self, method=None, **kwargs):
        yield "HTTP/1.0 302 Found"+CRLF+"Location: %s" % self._page
        yield 2*CRLF

    def loginForm(self):
        yield """<div id="login">
    <form method="POST" action="%s">
        <dl>
            <dt>Username</dt>
            <dd><input type="text" name="username"/></dd>
            <dt>Password</dt>
            <dd><input type="password" name="password"/></dd>
            <dd class="submit"><input type="submit" value="login"/></dd>
        </dl>
    </form>
</div>""" % self._action
