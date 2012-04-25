from meresco.core import Observable
from meresco.components.http.utils import redirectHttp
from cgi import parse_qs

class Dashboard(Observable):
    def __init__(self, home="/", name=None):
        Observable.__init__(self, name=name)
        self._home = home
        self._actions = {
            'create': self.handleCreate,
            'update': self.handleUpdate,
            'delete': self.handleDelete,
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
        repositoryName = bodyArgs['repository'][0]
        repository = self.call.addRepository(name=repositoryName)
        formUrl = bodyArgs['formUrl'][0] % {'repository': repository.name}

        yield redirectHttp % formUrl

    def handleUpdate(self, Body, **kwargs):
        bodyArgs = parse_qs(Body, keep_blank_values=True)
        repository = bodyArgs['repository'][0]
        baseUrl = bodyArgs['baseUrl'][0]
        metadataPrefix = bodyArgs['metadataPrefix'][0]
        setSpec = bodyArgs['setSpec'][0]
        apiKey = bodyArgs['apiKey'][0]
        formUrl = bodyArgs['formUrl'][0]
        active = 'active' in bodyArgs
        self.call.addRepository(name=repository, baseUrl=baseUrl, metadataPrefix=metadataPrefix, setSpec=setSpec, apiKey=apiKey, active=active)
        yield redirectHttp % formUrl

    def handleDelete(self, Body, **kwargs):
        bodyArgs = parse_qs(Body, keep_blank_values=True)
        repository = bodyArgs['repository'][0]
        formUrl = bodyArgs['formUrl'][0]
        self.call.deleteRepository(name=repository)
        yield redirectHttp % formUrl
        
