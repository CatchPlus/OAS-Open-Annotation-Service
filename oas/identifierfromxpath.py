
from namespaces import xpath
from meresco.core import Transparent

class IdentifierFromXPath(Transparent):

    def __init__(self, xpath):
        Transparent.__init__(self)
        self._xpath = xpath

    def add(self, identifier, partname, lxmlNode):
        try:
            newIdentifier = xpath(lxmlNode, self._xpath)[0]
        except:
            raise ValueError("Identifier not found")
        yield self.all.add(identifier=newIdentifier, partname=partname, lxmlNode=lxmlNode)
