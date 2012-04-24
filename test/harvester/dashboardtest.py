from seecr.test import SeecrTestCase

from meresco.components.http.utils import CRLF
from oas.harvester import Dashboard, Environment
from oas.login.basichtmlloginform import User

from testutil import joco

from urllib import urlencode

class DashboardTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.dashboard = Dashboard()
        self.env = Environment(root=self.tempdir)
        self.dashboard.addObserver(self.env)

    def testRedirectOnGet(self):
        result = joco(self.dashboard.handleRequest(path='/whatever', Client=('127.0.0.1', 3451), Method='GET', session={}))
        header, body = result.split(CRLF*2)
        self.assertTrue('302' in header)
        self.assertTrue('Location: /' in header, header)

    def testCreateNotLoggedIn(self):
        result = joco(self.dashboard.handleRequest(path="/create", Client=('127.0.0.1', 1234), Method='POST', session={}))
        header, body = result.split(CRLF*2)
        self.assertTrue('302' in header)
        self.assertTrue('Location: /' in header, header)

    def testCreateLoggedIn(self):
        session = {
            'user': User('admin'),
        }
        Body = urlencode(dict(repository='repoId1', formUrl='/harvester_dashboard'))
        result = joco(self.dashboard.handleRequest(path="/create", Client=('127.0.0.1', 1234), Method='POST', session=session, Body=Body))
        header, body = result.split(CRLF*2)
        self.assertTrue('302' in header)
        self.assertTrue('Location: /harvester_dashboard' in header, header)

        self.assertEquals("repoId1", list(self.env.getRepositories())[0].name)

