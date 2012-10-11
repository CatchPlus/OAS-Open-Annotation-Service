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

from meresco.core import Observable
from lxml.etree import tostring, Element, parse
from StringIO import StringIO
from copy import copy
from urllib import unquote

from rdfcontainer import RdfContainer
from oas.utils.annotation import filterAnnotations, validIdentifier
from oas.namespaces import namespaces, xpath, getAttrib, expandNs
from meresco.components.xml_generic.validate import ValidateException


def isAnnotation(node):
    return ("{%(oa)s}Annotation" % namespaces)  == node.tag or ("%(oa)sAnnotation" % namespaces) in xpath(node, 'rdf:type/@rdf:resource')

class MultipleAnnotationSplit(Observable):

    def __init__(self, baseUrl, **kwargs):
        Observable.__init__(self, **kwargs)
        self._baseUrl = baseUrl

    def add(self, identifier, partname, lxmlNode):
        rdfContainer = RdfContainer(lxmlNode)
        annotationFound = False
        for annotation in filterAnnotations(lxmlNode):
            annotationFound = True
            newRoot = Element("{%(rdf)s}RDF" % namespaces)
            newRoot.append(annotation)
            self._inlineURNs(annotation, rdfContainer)
            yield self.all.process(lxmlNode=newRoot)
        if not annotationFound:
            raise ValidateException("No annotations found.")

    def delete(self, identifier):
        return self.all.delete(identifier)

    def _inlineURNs(self, root, rdfContainer):
        for relation in [
            {'tag': 'oa:annotatedBy', 'partname': 'foafAgent'}, 
            {'tag': 'oa:hasBody', 'partname': 'oacBody'},
            {'tag': 'oa:hasSource'},
            {'tag': 'oa:hasSelector'},
            {'tag': 'oa:hasTarget', 'partname': 'oacConstrainedTarget'},]:

            nodes = xpath(root, '%s[@rdf:resource]' % relation['tag'])
            for node in nodes:
                urn = getAttrib(node, 'rdf:resource')
                if urn:
                    resolvedNode = rdfContainer.resolve(urn)
                    if resolvedNode is not None and not isAnnotation(resolvedNode):
                        node.append(resolvedNode)
                        self._inlineURNs(resolvedNode, rdfContainer)
                        del node.attrib[expandNs('rdf:resource')]
                    elif urn.startswith(self._baseUrl):
                        if self.call.isAvailable(identifier=urn, partname="oacBody") == (True, True):
                            data = self.call.getStream(identifier=urn, partname='oacBody')
                            node.append(parse(StringIO(data.read())).getroot())
                            del node.attrib[expandNs('rdf:resource')]
                    elif 'partname' in relation and self.call.isAvailable(identifier=urn, partname=relation['partname']) == (True, True):
                        data = self.call.getStream(identifier=urn, partname=relation['partname'])
                        node.append(parse(StringIO(data.read())).getroot())
                        del node.attrib[expandNs('rdf:resource')]

