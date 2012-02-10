from namespaces import xpath

class RdfContainer(object):
    
    def __init__(self, xml):
        self._xml = xml

    def resolve(self, uri):
        results = xpath(self._xml, "//*[@rdf:about='%s']" % uri)
        return results[0] if results else None
