from weightless.core import Observable

from oas.namespaces import xpath, namespaces, getAttrib, setAttrib

class MboxAsIdentifier(Observable):
    def add(self, identifier, partname, lxmlNode):
        creators = xpath(lxmlNode, "//dcterms:creator")
        for creator in creators:
            if not getAttrib(creator, 'rdf:resource').startswith('urn:'):
                continue
            mbox = xpath(creator, "foaf:mbox/text()")
            if mbox:
                setAttrib(creator, 'rdf:resource', 'mailto:%s' % mbox[0])
        yield self.all.add(identifier=identifier, partname=partname, lxmlNode=lxmlNode)

    def delete(self, identifier, partname):
        yield self.all.delete(identifier=identifier, partname=partname)

