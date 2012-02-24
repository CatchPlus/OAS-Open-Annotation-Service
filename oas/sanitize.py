from weightless.core import be
from meresco.core import Transparent, Observable

from oas import MultipleAnnotationSplit, Normalize, Deanonymize, Publish

class Sanitize(object):
    
    def __init__(self, urnGen=None, resolveBaseUrl=''):
        outside = Transparent()
        self.addObserver = outside.addObserver
        self.addStrand = outside.addStrand
        self._dna = be(
            (Observable(),
                (MultipleAnnotationSplit(),
                    (outside, ),
                    (Normalize(),
                        (Deanonymize(urnGen=urnGen),
                            (Publish(baseUrl=resolveBaseUrl),
                                (outside,)
                            )
                        )
                    )
                )
            )
        )   

    def add(self, identifier, partname, lxmlNode):
        yield self._dna.all.add(identifier=identifier, partname=partname, lxmlNode=lxmlNode)
