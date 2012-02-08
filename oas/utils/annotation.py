from oas.namespaces import xpath
from Ft.Xml.Lib import Uri

def identifierFromXml(lxmlNode):
    identifier = None
    identifierFromRdf = xpath(lxmlNode, '/rdf:RDF/rdf:Description[rdf:type/@rdf:resource="http://www.openannotation.org/ns/Annotation"]/@rdf:about')
    if identifierFromRdf != []:
        identifier = identifierFromRdf[0]
    else:
        identifierFromAnnotation = xpath(lxmlNode, '/rdf:RDF/oas:Annotation/@rdf:about')
        if identifierFromAnnotation != []:
            identifier = identifierFromAnnotation[0]
    return identifier

def validIdentifier(identifier):
    return Uri.MatchesUriSyntax(identifier) if identifier else False
