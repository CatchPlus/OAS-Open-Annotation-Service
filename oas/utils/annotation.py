## begin license ##
# 
# "Open Annotation Service" enables exchange, storage and search of
# heterogeneous annotations using a uniform format (Open Annotation format) and
# a uniform web service interface. 
# 
# Copyright (C) 2012 Meertens Instituut (KNAW) http://meertens.knaw.nl
# Copyright (C) 2012 Seecr (Seek You Too B.V.) http://seecr.nl
# 
# This file is part of "Open Annotation Service"
# 
# "Open Annotation Service" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# "Open Annotation Service" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with "Open Annotation Service"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 
## end license ##

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
