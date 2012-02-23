from meresco.core import Transparent
from namespaces import xpath, prefixes, namespaces

from lxml.etree import SubElement

def splitType(typeString):
    def splitOn(delimeter):
        namespace, name = typeString.rsplit(delimeter, 1)
        namespace += delimeter
        return namespace, name

    return splitOn("#" if "#" in typeString else "/")

class NormalizeRecord(Transparent):
  
    def add(self, identifier, partname, lxmlNode):
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
            for child in description.getchildren():
                if child.tag == "{%(rdf)s}type" % namespaces:
                    continue
                newNode.append(child)
            parent.remove(description)

        yield self.all.add(identifier=identifier, partname=partname, lxmlNode=lxmlNode)