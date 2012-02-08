from oas.namespaces import xpath, namespaces
from Ft.Xml.Lib import Uri

def aboutNode(lxmlNode):
    for path in ['/rdf:RDF/rdf:Description[rdf:type/@rdf:resource="http://www.openannotation.org/ns/Annotation"]', '/rdf:RDF/oas:Annotation']:
        xpathResult = xpath(lxmlNode, path)
        if xpathResult:
            return xpathResult[0]

def identifierFromXml(lxmlNode):
    nodeWithAbout = aboutNode(lxmlNode)
    if nodeWithAbout is not None:
        return nodeWithAbout.attrib['{%(rdf)s}about' % namespaces]

def validIdentifier(identifier):
    return Uri.MatchesUriSyntax(identifier) if identifier else False
