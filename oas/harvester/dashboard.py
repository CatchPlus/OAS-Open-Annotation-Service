from meresco.core import Observable
from meresco.components.http.utils import redirectHttp
from cgi import parse_qs

class Dashboard(Observable):
    def __init__(self, home="/", name=None):
        Observable.__init__(self, name=name)
        self._home = home
        self._actions = {
            'create': self.handleCreate,
        }

    def handleRequest(self, Method, path, session, **kwargs):
        if Method == 'GET':
            yield redirectHttp % self._home
            return

        prefix, action = path.rsplit('/', 1)
        if 'user' in session and session['user'].isAdmin():
            yield self._actions[action](**kwargs)
            return

        yield redirectHttp % self._home
        return

    def handleCreate(self, Body, **kwargs):
        bodyArgs = parse_qs(Body, keep_blank_values=True)
        repository = bodyArgs['repository'][0]
        formUrl = bodyArgs['formUrl'][0]
        self.call.addRepository(name=repository)
        yield redirectHttp % formUrl

