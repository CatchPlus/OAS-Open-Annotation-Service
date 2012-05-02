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

from itertools import chain
from namespaces import xpath, getAttrib, setAttrib
from uuid import uuid4

from oas.utils import filterOacBodies

def urn():
    return 'urn:uuid:'+str(uuid4())

class Deanonymize(Observable):

    def __init__(self, urnGen=None):
        Observable.__init__(self)
        self._urnGen = urnGen if urnGen else urn

    def delete(self, identifier):
        return self.all.delete(identifier)

    def process(self, lxmlNode):
        for node in chain(xpath(lxmlNode, '//oac:Annotation'), xpath(lxmlNode, '//oac:Body'), xpath(lxmlNode, "//oac:ConstrainedTarget")):
            if getAttrib(node, 'rdf:about') == None and getAttrib(node, 'rdf:resource') == None:
                setAttrib(node, 'rdf:about', self._urnGen())

        yield self.all.process(lxmlNode=lxmlNode)
