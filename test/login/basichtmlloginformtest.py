
from seecr.test import SeecrTestCase
from meresco.components.http.utils import CRLF

from oas.login import BasicHtmlLoginForm

class BasicHtmlLoginFormTest(SeecrTestCase):
    def testLoginForm(self):
        form = BasicHtmlLoginForm(action='/login', page='/home') 
        result = ''.join(form.loginForm())  

        self.assertEquals("""<div id="login">
    <form method="POST" action="/login">
        <dl>
            <dt>Username</dt>
            <dd><input type="text" name="username"/></dd>
            <dt>Password</dt>
            <dd><input type="password" name="password"/></dd>
            <dd class="submit"><input type="submit" value="login"/></dd>
        </dl>
    </form>
</div>""", result)

    def testRedirectOnGET(self):
        form = BasicHtmlLoginForm(action='/login', page='/home')

        result = ''.join(form.handleRequest(path='/login', Client=('127.0.0.1', 3451), method='GET'))

        header, body = result.split(CRLF*2)
        self.assertTrue('302' in header)
        self.assertTrue('Location: /home' in header)

