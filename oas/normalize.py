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

from meresco.core import Transparent
from namespaces import xpath, prefixes, namespaces, getAttrib

from lxml.etree import SubElement

def splitType(typeString):
    def splitOn(delimeter):
        namespace, name = typeString.rsplit(delimeter, 1)
        namespace += delimeter
        return namespace, name

    return splitOn("#" if "#" in typeString else "/")

class NamespaceEnum(object):
    def __init__(self):
        self._map = {}
        self._enum = 0

    def get(self, ns):
        if ns not in self._map:
            prefix = 'ns%s' % self._enum
            self._enum += 1
            self._map[ns] = prefix
        return self._map[ns]

class Normalize(Transparent):

    def __init__(self):
        Transparent.__init__(self)
        self._namespaceEnum = NamespaceEnum()
 
    def delete(self, identifier):
        return self.all.delete(identifier)

    def process(self, lxmlNode):
        def prefixForNamespace(ns):
            if ns in prefixes:
                return prefixes[ns]
            return self._namespaceEnum.get(ns)

        def filterOac(nodes):
            result = []
            for node in nodes:
                namespace, name = splitType(getAttrib(node, 'rdf:resource'))
                if namespace == namespaces['oa']:
                    result.append(node)
            return result

        descriptions = xpath(lxmlNode, "//rdf:Description[rdf:type]")
        for description in descriptions:
            nodes = xpath(description, "rdf:type")
            oacNodes = filterOac(nodes)
            typeNode = nodes[0]
            if len(oacNodes) > 0:
                typeNode = oacNodes[0]

            parent = description.getparent()
            namespace, name = splitType(getAttrib(typeNode, 'rdf:resource'))
            prefix = prefixForNamespace(namespace)
            newNode = SubElement(
                parent, 
                "{%(ns)s}%(tag)s" % {'ns': namespace, 'tag': name}, 
                attrib=description.attrib,
                nsmap={prefix: namespace})
            for child in (child for child in description.getchildren() if child != typeNode):
                newNode.append(child)
            parent.remove(description)

        yield self.all.process(lxmlNode=lxmlNode)
