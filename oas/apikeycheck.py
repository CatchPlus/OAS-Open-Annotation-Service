from meresco.core import Observable

from meresco.components.http.utils import unauthorizedHtml

class ApiKeyCheck(Observable):

    def handleRequest(self, **kwargs):
        apikey = None
        try:
            apikey = self.ctx.authorization['apikey']
        except AttributeError:
            pass 

        if apikey == None:
            yield unauthorizedHtml
            return

        data = self.call.getForApikey(apikey)
        if data == None:
            yield unauthorizedHtml
            return
        print ">>>", data
       
        yield self.all.handleRequest(**kwargs)
