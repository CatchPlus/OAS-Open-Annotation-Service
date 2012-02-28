from oas.namespaces import xpath, namespaces, getAttrib
from Ft.Xml.Lib import Uri

def filterAnnotations(lxmlNode):
    for path in ['/rdf:RDF/rdf:Description[rdf:type/@rdf:resource="http://www.openannotation.org/ns/Annotation"]', '/rdf:RDF/oac:Annotation']:
        for node in xpath(lxmlNode, path):
            yield node

def filterFoafAgents(lxmlNode):
    for path in ['rdf:Description[rdf:type/@rdf:resource="%sAgent"]' % namespaces['foaf'], 'foaf:Agent']:
        for node in xpath(lxmlNode, path):
            yield node

def filterOacBodies(lxmlNode):
    for path in ['rdf:Description[rdf:type/@rdf:resource="%sBody"]' % namespaces['oac'], 'oac:Body']:
        for node in xpath(lxmlNode, path):
            yield node

def aboutNode(lxmlNode):
    for path in ['/rdf:RDF/rdf:Description[rdf:type/@rdf:resource="http://www.openannotation.org/ns/Annotation"]', '/rdf:RDF/oac:Annotation']:
        xpathResult = xpath(lxmlNode, path)
        if xpathResult:
            return xpathResult[0]

def identifierFromXml(lxmlNode):
    nodeWithAbout = aboutNode(lxmlNode)
    if nodeWithAbout is not None:
        return getAttrib(nodeWithAbout, 'rdf:about')

def validIdentifier(identifier):
    return Uri.MatchesUriSyntax(identifier) if identifier else False
