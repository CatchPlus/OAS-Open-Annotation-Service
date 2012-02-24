from meresco.core import Observable

from namespaces import xpath, getAttrib, setAttrib
from uuid import uuid4

def urn():
    return 'urn:uuid:'+str(uuid4())

class Deanonymize(Observable):

    def __init__(self, urnGen=None):
        Observable.__init__(self)
        self._urnGen = urnGen if urnGen else urn

    def process(self, lxmlNode):
        for node in xpath(lxmlNode, '//oac:Annotation'):
            if getAttrib(node, 'rdf:about') == None and getAttrib(node, 'rdf:resource') == None:
                setAttrib(node, 'rdf:about', self._urnGen())

        yield self.all.process(lxmlNode=lxmlNode)
