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

from oas.utils import identifierFromXml, filterAnnotations, validIdentifier
from oas.namespaces import setAttrib, getAttrib, namespaces, xpath, expandNs

from urllib import quote_plus
from lxml.etree import SubElement, parse

from meresco.components.xml_generic.validate import ValidateException

class Publish(Observable):

    def __init__(self, baseUrl):
        Observable.__init__(self)
        self._baseUrl = baseUrl
        if not self._baseUrl[-1] == '/':
            self._baseUrl += '/'

    def urlFor(self, identifier):
        return self._baseUrl + quote_plus(identifier)
    
    def urnToUrl(self, lxmlNode, identifier):
        newIdentifier = self.urlFor(identifier)
        setAttrib(lxmlNode, 'rdf:about', newIdentifier)
        SubElement(lxmlNode, '{%(dc)s}identifier' % namespaces).text = identifier
        return newIdentifier

    def delete(self, identifier):
        return self.all.delete(identifier)

    def process(self, lxmlNode):
        for annotation in filterAnnotations(lxmlNode):
            identifier = getAttrib(annotation, 'rdf:about')
            if identifier.lower().startswith('urn:'):
                identifier = self.urnToUrl(annotation, identifier)
            if not validIdentifier(identifier):
                raise ValidateException("Invalid identifier")

            for hasBody in xpath(annotation, '//oa:hasBody'):
                bodyResource = getAttrib(hasBody, 'rdf:resource')
                if bodyResource:
                    bodyResourceIdentifier = self.urlFor(bodyResource)
                    if self.call['store'].isAvailable(bodyResourceIdentifier, "oacBody") == (True, True):
                        body = parse(self.call['store'].getStream(bodyResourceIdentifier, 'oacBody'))
                        hasBody.append(body.getroot())
                        del hasBody.attrib[expandNs('rdf:resource')]

            for hasTarget in xpath(annotation, "//oa:hasTarget"):
                targetResource = getAttrib(hasTarget, 'rdf:resource')
                if targetResource:
                    targetResourceIdentifier = self.urlFor(targetResource)
                    if self.call['store'].isAvailable(targetResourceIdentifier, "oacConstrainedTarget") == (True, True):
                        body = parse(self.call['store'].getStream(targetResourceIdentifier, 'oacConstrainedTarget'))
                        hasTarget.append(body.getroot())
                        del hasTarget.attrib[expandNs('rdf:resource')]

            for body in xpath(annotation, '//oa:Body'):
                bodyIdentifier = getAttrib(body, 'rdf:about')
                if bodyIdentifier.startswith('urn:'):
                    publishIdentifier = self.urnToUrl(body, bodyIdentifier)
                    yield self.all['store'].add(identifier=publishIdentifier, partname="oacBody", lxmlNode=body)

            for target in xpath(annotation, '//oa:SpecificResource'):
                targetIdentifier = getAttrib(target, 'rdf:about')
                if targetIdentifier.startswith('urn:'):
                    publishIdentifier = self.urnToUrl(target, targetIdentifier)
                    yield self.all['store'].add(identifier=publishIdentifier, partname="oacConstrainedTarget", lxmlNode=target)

            yield self.all['index'].add(identifier=identifier, partname="rdf", lxmlNode=lxmlNode)
