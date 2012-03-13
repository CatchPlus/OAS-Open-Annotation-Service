
from seecr.test import SeecrTestCase, CallTrace
from meresco.components.http.utils import CRLF
from urllib import urlencode

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

    def testLoginWithPOSTsucceeds(self):
        form = BasicHtmlLoginForm(action='/login', page='/home')
        observer = CallTrace()
        form.addObserver(observer)
        observer.returnValues['validateUser'] = True
        Body = urlencode(dict(username='user', password='secret'))
        session = {}

        result = ''.join(form.handleRequest(path='/login', Client=('127.0.0.1', 3451), method='POST', Body=Body, session=session))

        self.assertEquals('user', session['user'].name)
        header, body = result.split(CRLF*2)
        self.assertTrue('302' in header)
        self.assertTrue('Location: /home' in header)

        self.assertEquals(['validateUser'], [m.name for m in observer.calledMethods])
        self.assertEquals({'username': 'user', 'password':'secret'}, observer.calledMethods[0].kwargs)

    def testLoginWithPOSTfails(self):
        form = BasicHtmlLoginForm(action='/login', page='/home')
        observer = CallTrace()
        form.addObserver(observer)
        observer.returnValues['validateUser'] = False
        Body = urlencode(dict(username='user', password='wrong'))
        session = {}

        result = ''.join(form.handleRequest(path='/login', Client=('127.0.0.1', 3451), method='POST', Body=Body, session=session))

        self.assertFalse('user' in session)
        self.assertEquals({'username':'user', 'errorMessage': 'Invalid username or password'}, session['BasicHtmlLoginForm.formValues'])
        header, body = result.split(CRLF*2)
        self.assertTrue('302' in header)
        self.assertTrue('Location: /home' in header)

        self.assertEquals(['validateUser'], [m.name for m in observer.calledMethods])
        self.assertEquals({'username': 'user', 'password':'wrong'}, observer.calledMethods[0].kwargs)


    def testLoginFormWithError(self):
        form = BasicHtmlLoginForm(action='/login', page='/home') 
        session = {}
        session['BasicHtmlLoginForm.formValues']={'username': '<us"er>', 'errorMessage': 'Invalid <username> or "password"'}
        result = ''.join(form.loginForm(session=session))  

        self.assertEquals("""<div id="login">
    <p class="error">Invalid &lt;username&gt; or "password"</p>
    <form method="POST" action="/login">
        <dl>
            <dt>Username</dt>
            <dd><input type="text" name="username" value='&lt;us"er&gt;'/></dd>
            <dt>Password</dt>
            <dd><input type="password" name="password"/></dd>
            <dd class="submit"><input type="submit" value="login"/></dd>
        </dl>
    </form>
</div>""", result)


