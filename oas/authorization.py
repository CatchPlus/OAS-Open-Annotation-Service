from meresco.core import Observable

class Authorization(Observable):
    def handleRequest(self, Headers, **kwargs):
        if 'Authorization' in Headers:
            __callstack_var_authorization__ = {'apikey': Headers['Authorization']}
        yield self.all.handleRequest(Headers=Headers, **kwargs)
