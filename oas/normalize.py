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
from namespaces import xpath, prefixes, namespaces

from lxml.etree import SubElement

def splitType(typeString):
    def splitOn(delimeter):
        namespace, name = typeString.rsplit(delimeter, 1)
        namespace += delimeter
        return namespace, name

    return splitOn("#" if "#" in typeString else "/")

class Normalize(Transparent):
  
    def process(self, lxmlNode):
        descriptions = xpath(lxmlNode, "//rdf:Description[rdf:type]")
        for description in descriptions:
            rdfType = xpath(description, "rdf:type/@rdf:resource")[0]

            namespace, name = splitType(rdfType)
            parent = description.getparent()
            newNode = SubElement(
                parent, 
                "{%(ns)s}%(tag)s" % {'ns': namespace, 'tag': name}, 
                attrib=description.attrib,
                nsmap={prefixes[namespace]: namespace})
            firstChildDeleted = False
            for child in description.getchildren():
                if child.tag == "{%(rdf)s}type" % namespaces and not firstChildDeleted:
                    firstChildDeleted = True
                    continue
                newNode.append(child)
            parent.remove(description)

        yield self.all.process(lxmlNode=lxmlNode)
