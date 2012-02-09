from weightless.core import Observable

from oas.namespaces import xpath, namespaces, attrib

class MboxAsIdentifier(Observable):
    def add(self, identifier, partname, lxmlNode):
        creators = xpath(lxmlNode, "//dcterms:creator")
        for creator in creators:
            mbox = xpath(creator, "foaf:mbox/text()")
            if mbox:
                creator.attrib[attrib('rdf:resource')] = 'mailto:%s' % mbox[0]
        yield self.all.add(identifier=identifier, partname=partname, lxmlNode=lxmlNode)

    def delete(self, identifier, partname):
        yield self.all.delete(identifier=identifier, partname=partname)

