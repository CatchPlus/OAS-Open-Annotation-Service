from weightless.core import be, compose
from meresco.core import Observable

from seecr.test import SeecrTestCase, CallTrace
from meresco.components.http.utils import CRLF
from urllib import urlencode

from oas.login import BasicHtmlLoginForm

class BasicHtmlLoginFormTest(SeecrTestCase):
    def testLoginForm(self):
        form = BasicHtmlLoginForm(page='/home') 
        result = ''.join(form.loginForm(path='/page/login2'))  

        self.assertEqualsWS("""<div id="login">
    <form method="POST" action="/page/login2">
        <dl>
            <dt>Username</dt>
            <dd><input type="text" name="username"/></dd>
            <dt>Password</dt>
            <dd><input type="password" name="password"/></dd>
            <dd class="submit"><input type="submit" value="login"/></dd>
        </dl>
    </form>
</div>""", result)

    def testShowFormOnGet(self):
        form = BasicHtmlLoginForm(page='/home')

        result = ''.join(compose(form.handleRequest(path='/login', Client=('127.0.0.1', 3451), Method='GET')))

        header, body = result.split(CRLF*2)
        self.assertTrue('200' in header)
        self.assertTrue('Content-Type: text/html; charset=utf-8' in header)

    def testLoginWithPOSTsucceeds(self):
        form = BasicHtmlLoginForm(page='/home')
        observer = CallTrace()
        form.addObserver(observer)
        observer.returnValues['validateUser'] = True
        Body = urlencode(dict(username='user', password='secret'))
        session = {}

        result = ''.join(form.handleRequest(path='/login', Client=('127.0.0.1', 3451), Method='POST', Body=Body, session=session))

        self.assertEquals('user', session['user'].name)
        header, body = result.split(CRLF*2)
        self.assertTrue('302' in header)
        self.assertTrue('Location: /home' in header)

        self.assertEquals(['validateUser'], [m.name for m in observer.calledMethods])
        self.assertEquals({'username': 'user', 'password':'secret'}, observer.calledMethods[0].kwargs)

    def testLoginWithPOSTfails(self):
        form = BasicHtmlLoginForm(page='/home')
        observer = CallTrace()
        form.addObserver(observer)
        observer.returnValues['validateUser'] = False
        Body = urlencode(dict(username='user', password='wrong'))
        session = {}

        result = ''.join(form.handleRequest(path='/login', Client=('127.0.0.1', 3451), Method='POST', Body=Body, session=session))

        self.assertFalse('user' in session)
        self.assertEquals({'username':'user', 'errorMessage': 'Invalid username or password'}, session['BasicHtmlLoginForm.formValues'])
        header, body = result.split(CRLF*2)
        self.assertTrue('302' in header)
        self.assertTrue('Location: /login' in header, header)

        self.assertEquals(['validateUser'], [m.name for m in observer.calledMethods])
        self.assertEquals({'username': 'user', 'password':'wrong'}, observer.calledMethods[0].kwargs)


    def testLoginFormWithError(self):
        form = BasicHtmlLoginForm(page='/home') 
        session = {}
        session['BasicHtmlLoginForm.formValues']={'username': '<us"er>', 'errorMessage': 'Invalid <username> or "password"'}
        result = ''.join(form.loginForm(session=session, path='/login'))  

        self.assertEqualsWS("""<div id="login">
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

    def testShowChangePasswordForm(self):
        form = BasicHtmlLoginForm(page='/home') 
        observer = CallTrace(
            emptyGeneratorMethods=['handleRequest', 'addUser'], 
            methods={'hasUser': False})
        dna = be(
            (Observable(),
                (form, 
                    (observer, )
                )
            )
        )
        result = ''.join(compose(dna.all.handleRequest(
            Method='GET', 
            path="/blah/changepassword", 
            session={})))

        self.assertEqualsWS("""<div id="login">
    <form method="POST" action="/blah/changepassword">
    <input type="hidden" name="username" value=""/>
        <dl>
            <dt>Old password</dt>
            <dd><input type="password" name="oldPassword" value=""/></dd>
            <dt>New password</dt>
            <dd><input type="password" name="newPassword"/></dd>
            <dt>Retype new password</dt>
            <dd><input type="password" name="retypedPassword"/></dd>
            <dd class="submit"><input type="submit" value="change"/></dd>
        </dl>
    </form>
</div>""", result)

        result = ''.join(compose(dna.all.handleRequest(
            Method='GET', 
            path="/blah/changepassword", 
            session={'BasicHtmlLoginForm.formValues': {'errorMessage': 'The error Message'}})))
        
        self.assertEqualsWS("""<div id="login">
    <p class="error">The error Message</p>
    <form method="POST" action="/blah/changepassword">
    <input type="hidden" name="username" value=""/>
        <dl>
            <dt>Old password</dt>
            <dd><input type="password" name="oldPassword" value=""/></dd>
            <dt>New password</dt>
            <dd><input type="password" name="newPassword"/></dd>
            <dt>Retype new password</dt>
            <dd><input type="password" name="retypedPassword"/></dd>
            <dd class="submit"><input type="submit" value="change"/></dd>
        </dl>
    </form>
</div>""", result)


    def testChangePasswordMismatch(self):
        form = BasicHtmlLoginForm(page='/home') 
        
        Body = urlencode(dict(username='user', oldPassword='correct', newPassword="good", retypedPassword="mismatch"))
        session = {}

        result = ''.join(form.handleRequest(path='/login/changepassword', Client=('127.0.0.1', 3451), Method='POST', Body=Body, session=session))
        self.assertEquals({'username':'user', 'errorMessage': 'New passwords do not match'}, session['BasicHtmlLoginForm.formValues'])
        self.assertEqualsWS("""HTTP/1.0 302 Redirect\r\nLocation: changepassword\r\n\r\n""", result)

    def testChangePasswordWrongOld(self):
        form = BasicHtmlLoginForm(page='/home') 
        observer = CallTrace()
        form.addObserver(observer)
        observer.returnValues['validateUser'] = False
        
        Body = urlencode(dict(username='user', oldPassword='wrong', newPassword="good", retypedPassword="good"))
        session = {}

        result = ''.join(form.handleRequest(path='/login/changepassword', Client=('127.0.0.1', 3451), Method='POST', Body=Body, session=session))
        self.assertEquals({'username':'user', 'errorMessage': 'Username and password do not match.'}, session['BasicHtmlLoginForm.formValues'])
        self.assertEquals("HTTP/1.0 302 Redirect\r\nLocation: changepassword\r\n\r\n", result)

    def testChangePassword(self):
        form = BasicHtmlLoginForm(page='/home') 
        observer = CallTrace()
        form.addObserver(observer)
        observer.returnValues['validateUser'] = True
        
        Body = urlencode(dict( username='user', oldPassword='correct', newPassword="good", retypedPassword="good"))
        session = {}

        result = ''.join(form.handleRequest(path='/login/changepassword', Client=('127.0.0.1', 3451), Method='POST', Body=Body, session=session))
        self.assertEquals(['validateUser', 'changePassword'], [m.name for m in observer.calledMethods])
        self.assertEquals("HTTP/1.0 302 Redirect\r\nLocation: /login\r\n\r\n", result)


