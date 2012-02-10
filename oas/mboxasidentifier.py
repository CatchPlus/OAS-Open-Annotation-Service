from weightless.core import Observable

from oas.namespaces import xpath, namespaces, getAttrib, setAttrib
from oas.utils.annotation import filterFoafAgents


class MboxAsIdentifier(Observable):
    def add(self, identifier, partname, lxmlNode):
        creatorAgents = filterFoafAgents(xpath(lxmlNode, "//dcterms:creator"))
        for creatorAgent in creatorAgents:
            aboutUri = getAttrib(creatorAgent, 'rdf:about', None)
            if not aboutUri or not aboutUri.startswith('urn:'):
                continue
            mbox = xpath(creatorAgent, "foaf:mbox/text()")
            if mbox:
                setAttrib(creatorAgent, 'rdf:about', 'mailto:%s' % mbox[0])
        yield self.all.add(identifier=identifier, partname=partname, lxmlNode=lxmlNode)

    def delete(self, identifier, partname):
        yield self.all.delete(identifier=identifier, partname=partname)

