## begin license ##
# 
# "Open Annotation Service" enables exchange, storage and search of
# heterogeneous annotations using a uniform format (Open Annotation format) and
# a uniform web service interface. 
# 
# Copyright (C) 2011-2012 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2012 Meertens Instituut (KNAW) http://meertens.knaw.nl
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

class _namespaces(dict):
    def __getattr__(self, key):
        try: 
            return self[key]
        except KeyError, e:
            raise AttributeError(key)

    def xpath(self, node, path):
        return node.xpath(path, namespaces=self)

def getAttrib(node, name, default=None):
    return node.attrib.get(expandNs(name), default)

def setAttrib(node, name, value):
    node.attrib[expandNs(name)] = value

def expandNs(name):
    ns,value = name.split(':', 1)
    return '{%s}%s' % (namespaces[ns], value)

namespaces = _namespaces(
    cnt="http://www.w3.org/2008/content#",
    dbpedia_owl="http://dbpedia.org/ontology/",
    dc="http://purl.org/dc/elements/1.1/",
    dcterms="http://purl.org/dc/terms/",
    dd="http://meresco.org/namespace/drilldown",
    diag='http://www.loc.gov/zing/srw/diagnostic/',
    document="http://meresco.org/namespace/harvester/document",
    drilldown="http://meresco.org/namespace/drilldown",
    edm='http://www.europeana.eu/schemas/edm/',
    foaf="http://xmlns.com/foaf/0.1/",
    hreview="http://xsd.kennisnet.nl/smd/hreview/1.0/",
    html="http://www.w3.org/1999/xhtml",
    meresco_ext="http://meresco.org/namespace/xslt/extensions",
    meta="http://meresco.org/namespace/harvester/meta",
    oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/",
    oai="http://www.openarchives.org/OAI/2.0/",
    oac="http://www.openannotation.org/ns/",
    ore="http://www.openarchives.org/ore/terms/",
    rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    rdfs="http://www.w3.org/2000/01/rdf-schema#",
    rnax="http://www.rnaproject.org/data/rnax/",
    skos="http://www.w3.org/2004/02/skos/core#",
    sparql="http://www.w3.org/2005/sparql-results#",
    srw='http://www.loc.gov/zing/srw/',
    srw_dc='info:srw/schema/1/dc-v1.1',
    tags="http://www.holygoat.co.uk/owl/redwood/0.1/tags",
    ucp='info:lc/xmlns/update-v1',
    wsdl='http://schemas.xmlsoap.org/wsdl/',
    xml='http://www.w3.org/XML/1998/namespace',
    xsd='http://www.w3.org/2001/XMLSchema',
    xsi='http://www.w3.org/2001/XMLSchema-instance',
    xsl='http://www.w3.org/1999/XSL/Transform',
)

prefixes = dict((item, key) for key, item in namespaces.items())
xpath = namespaces.xpath
rdfAbout = '{%(rdf)s}about' % namespaces
rdfResource = '{%(rdf)s}resource' % namespaces
xmlLang = '{%(xml)s}lang' % namespaces
