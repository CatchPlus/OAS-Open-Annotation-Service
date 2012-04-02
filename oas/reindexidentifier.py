from meresco.core import Observable

from meresco.components.http.utils import serverErrorHtml, okPlainText

from lxml.etree import parse

class ReindexIdentifier(Observable):
    def handleRequest(self, arguments, **kwargs):
        identifier = arguments.get('identifier', [None])[0]
        if identifier and all(self.call.isAvailable(identifier, "rdf")):
            lxmlNode = parse(self.call.getStream(identifier=identifier, partname="rdf"))
            yield self.all.add(identifier=identifier, partname='rdf', lxmlNode=lxmlNode)
            yield okPlainText
            yield 'SUCCESS %s' % identifier
            return
        yield serverErrorHtml
